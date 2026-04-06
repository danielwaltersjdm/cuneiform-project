"""
fetch_papyri.py

Downloads target papyri collections from papyri/idp.data GitHub repository.
Fetches EpiDoc XML files for:
  - P.Zen (Zenon Archive) — 77 files
  - P.Oxy (Oxyrhynchus) — ~10,000 files across 72 volumes
  - P.Mich (Michigan / Karanis) — ~2,000 files across 19 volumes
  - HGV translations — ~1,000 numbered XML files

Output: raw_data/papyri/{collection}/

Usage:
  python scripts/fetch_papyri.py
  python scripts/fetch_papyri.py --collection p.zen.pestm
  python scripts/fetch_papyri.py --collection p.oxy --max-files 500
"""

import argparse
import time
from pathlib import Path

import os

import requests
import urllib3

urllib3.disable_warnings()

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).parent.parent
RAW_DIR      = PROJECT_ROOT / "raw_data" / "papyri"

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}
BASE_API = "https://api.github.com/repos/papyri/idp.data/contents"

# Target collections: (local_name, github_path, is_flat)
# is_flat=True  → files are directly in the path (no subdirectories)
# is_flat=False → files are in subdirectories (one per volume)
COLLECTIONS = {
    # Tier 1 / 2 — main targets
    "p.zen.pestm":    ("DDB_EpiDoc_XML/p.zen.pestm",    True),   # Zenon Archive (77 files)
    "p.oxy":          ("DDB_EpiDoc_XML/p.oxy",           False),  # Oxyrhynchus (~10k files)
    "p.mich":         ("DDB_EpiDoc_XML/p.mich",          False),  # Michigan/Karanis (~818 files)
    "hgv_trans":      ("HGV_trans_EpiDoc",               True),   # HGV translations (~1000 files)
    # Tier 2 — additional targets
    "p.eleph":        ("DDB_EpiDoc_XML/p.eleph",         True),   # Elephantine (31 files)
    "p.eleph.wagner": ("DDB_EpiDoc_XML/p.eleph.wagner",  True),   # Elephantine Wagner (4 files)
    "t.vindol":       ("DDB_EpiDoc_XML/t.vindol",        False),  # Vindolanda tablets
    "t.vindon":       ("DDB_EpiDoc_XML/t.vindon",        False),  # Vindonissa tablets
    "p.ness":         ("DDB_EpiDoc_XML/p.ness",          False),  # Nessana papyri
    # Tier 2 — newly discovered
    "p.babatha":      ("DDB_EpiDoc_XML/p.babatha",       True),   # Babatha archive (28 files)
    "p.dura":         ("DDB_EpiDoc_XML/p.dura",          True),   # Dura-Europos (139 files)
    "p.cair.zen":     ("DDB_EpiDoc_XML/p.cair.zen",      True),   # Cairo Zenon (5 files)
    "p.iand.zen":     ("DDB_EpiDoc_XML/p.iand.zen",      True),   # Iandana Zenon (82 files)
}

RATE_LIMIT_SLEEP = 0.05   # seconds between API requests
RETRY_SLEEP      = 10     # seconds on rate-limit hit


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def api_get(url: str) -> list | dict | None:
    """GET a GitHub API URL with retry on rate limit."""
    for attempt in range(5):
        r = requests.get(url, headers=HEADERS, verify=False, timeout=30)
        if r.status_code == 200:
            return r.json()
        if r.status_code == 403:
            reset = int(r.headers.get("X-RateLimit-Reset", time.time() + RETRY_SLEEP))
            wait = max(reset - time.time(), 1)
            print(f"  Rate limit hit. Waiting {wait:.0f}s...")
            time.sleep(wait)
        else:
            print(f"  HTTP {r.status_code}: {url}")
            return None
    return None


def download_file(url: str, dest: Path) -> bool:
    """Download a raw file from GitHub."""
    if dest.exists():
        return True  # Already downloaded
    for attempt in range(3):
        try:
            r = requests.get(url, verify=False, timeout=30)
            if r.status_code == 200:
                dest.write_bytes(r.content)
                return True
            if r.status_code == 429:
                time.sleep(RETRY_SLEEP)
        except requests.RequestException:
            time.sleep(2)
    return False


def list_files_flat(github_path: str) -> list[tuple[str, str]]:
    """List (name, download_url) for a flat directory."""
    data = api_get(f"{BASE_API}/{github_path}")
    if not data or not isinstance(data, list):
        return []
    return [(f["name"], f["download_url"]) for f in data if f.get("type") == "file"]


def list_files_nested(github_path: str) -> list[tuple[str, str]]:
    """List (name, download_url) for a directory containing subdirectories."""
    subdirs = api_get(f"{BASE_API}/{github_path}")
    if not subdirs or not isinstance(subdirs, list):
        return []
    all_files = []
    for entry in subdirs:
        if entry.get("type") != "dir":
            continue
        time.sleep(RATE_LIMIT_SLEEP)
        files = api_get(entry["url"])
        if not files:
            continue
        for f in files:
            if f.get("type") == "file":
                all_files.append((f["name"], f["download_url"]))
    return all_files


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def fetch_collection(name: str, max_files: int | None = None):
    github_path, is_flat = COLLECTIONS[name]
    out_dir = RAW_DIR / name
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n[{name}] Listing files from {github_path}...")
    if is_flat:
        files = list_files_flat(github_path)
    else:
        files = list_files_nested(github_path)

    print(f"  {len(files):,} files found.")

    if max_files:
        files = files[:max_files]
        print(f"  Limited to {max_files} files.")

    already = len(list(out_dir.glob("*.xml")))
    if already > 0:
        print(f"  {already:,} files already downloaded.")

    ok = skip = fail = 0
    for i, (fname, url) in enumerate(files):
        dest = out_dir / fname
        if dest.exists():
            skip += 1
            continue
        success = download_file(url, dest)
        if success:
            ok += 1
        else:
            fail += 1
            print(f"  FAIL: {fname}")
        if (i + 1) % 500 == 0:
            print(f"  Progress: {i+1}/{len(files)} — {ok} ok, {skip} skip, {fail} fail")
        time.sleep(0.02)

    print(f"  Done: {ok} downloaded, {skip} skipped, {fail} failed -> {out_dir}")


# APIS sequential institutions (files named institution.apis.N.xml, N=1,2,3,...)
APIS_SEQUENTIAL = {
    # name: max_id_to_try
    "michigan":    3700,
    "columbia":    5000,
    "oxford-ipap": 2000,
    "berkeley":    3000,
    "chicago":     1000,
    "oslo":         200,
    "upenn":        500,
}

# APIS listing institutions (files have non-sequential IDs; use GitHub dir listing)
APIS_LISTING = [
    "duke",
    "yale",
    "princeton",
    "stanford",
    "nyu",
    "toronto",
    "lund",
    "gothenburg",
    "hermitage",
    "wisconsin",
    "leidenpapinst",
    "trimithis",
    "petra",
    "fordham",
    "perkins",
    "psr",
    "pts",
    "pullman",
    "sacramento",
    "uts",
    "berenike",
    "britmus",
    "nyu",
]

APIS_COLLECTIONS = {**{k: (k, v) for k, v in APIS_SEQUENTIAL.items()},
                    **{k: (k, None) for k in APIS_LISTING}}

APIS_BASE = "https://raw.githubusercontent.com/papyri/idp.data/master/APIS/{institution}/xml/{institution}.apis.{n}.xml"


def fetch_apis_sequential(institution: str, max_id: int):
    """Download APIS XML files for an institution by sequential ID."""
    out_dir = RAW_DIR / "apis" / institution
    out_dir.mkdir(parents=True, exist_ok=True)

    existing = {f.stem for f in out_dir.glob("*.xml")}
    print(f"\n[APIS/{institution}] Downloading IDs 1-{max_id} ({len(existing):,} already present)...")

    ok = skip = fail = 0
    consecutive_404 = 0

    for n in range(1, max_id + 1):
        fname = f"{institution}.apis.{n}.xml"
        if fname.replace(".xml", "") in existing:
            skip += 1
            consecutive_404 = 0
            continue

        url = APIS_BASE.format(institution=institution, n=n)
        dest = out_dir / fname

        r = requests.get(url, verify=False, timeout=20,
                         headers={"Authorization": f"token {GITHUB_TOKEN}"})
        if r.status_code == 200:
            dest.write_bytes(r.content)
            ok += 1
            consecutive_404 = 0
        elif r.status_code == 404:
            consecutive_404 += 1
            fail += 1
            if consecutive_404 >= 50:
                print(f"  Stopped at ID {n} (50 consecutive 404s)")
                break
        else:
            fail += 1

        if (ok + skip) % 500 == 0 and (ok + skip) > 0:
            print(f"  Progress: {n}/{max_id} - {ok} ok, {skip} skip, {fail} fail")
        time.sleep(0.03)

    print(f"  Done: {ok} downloaded, {skip} skipped, {fail} 404/fail -> {out_dir}")


def fetch_apis_listing(institution: str, max_files: int | None = None):
    """Download APIS XML files using GitHub dir listing (for non-sequential IDs)."""
    github_path = f"APIS/{institution}/xml"
    out_dir = RAW_DIR / "apis" / institution
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n[APIS/{institution}] Listing via GitHub API...")
    files = list_files_flat(github_path)
    if not files:
        print(f"  No files found (check path: {github_path})")
        return

    # Filter XML only
    files = [(n, u) for n, u in files if n.endswith(".xml")]
    print(f"  {len(files):,} files found.")

    if max_files:
        files = files[:max_files]

    ok = skip = fail = 0
    for i, (fname, url) in enumerate(files):
        dest = out_dir / fname
        if dest.exists():
            skip += 1
            continue
        success = download_file(url, dest)
        if success:
            ok += 1
        else:
            fail += 1
        if (i + 1) % 200 == 0:
            print(f"  Progress: {i+1}/{len(files)} - {ok} ok, {skip} skip, {fail} fail")
        time.sleep(0.02)

    print(f"  Done: {ok} downloaded, {skip} skipped, {fail} failed -> {out_dir}")


def fetch_apis_collection(name: str, max_files: int | None = None):
    """Route to sequential or listing downloader based on institution type."""
    if name in APIS_SEQUENTIAL:
        max_id = max_files or APIS_SEQUENTIAL[name]
        fetch_apis_sequential(name, max_id)
    elif name in APIS_LISTING:
        fetch_apis_listing(name, max_files)
    else:
        print(f"  Unknown APIS institution: {name}")


def main():
    all_apis = list(APIS_SEQUENTIAL.keys()) + APIS_LISTING
    parser = argparse.ArgumentParser(description="Download papyri.info EpiDoc XML collections.")
    parser.add_argument("--collection",
                        choices=list(COLLECTIONS.keys()) + all_apis + ["all", "apis"],
                        default="all")
    parser.add_argument("--max-files", type=int, default=None,
                        help="Limit files per collection (for testing)")
    args = parser.parse_args()

    if args.collection == "apis":
        for name in all_apis:
            fetch_apis_collection(name, args.max_files)
    elif args.collection in all_apis:
        fetch_apis_collection(args.collection, args.max_files)
    else:
        targets = list(COLLECTIONS.keys()) if args.collection == "all" else [args.collection]
        for name in targets:
            fetch_collection(name, args.max_files)

    print("\nAll downloads complete.")


if __name__ == "__main__":
    main()
