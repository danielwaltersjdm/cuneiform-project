"""
fetch_oracc.py

Downloads Neo-Assyrian letter corpora from ORACC as TEI XML ZIP archives.
Scrapes each project's /downloads/ page to find the current ZIP filename,
then downloads it to raw_data/{project_slug}/.

Usage:
  python scripts/fetch_oracc.py
"""

import time
import urllib3
import zipfile
import requests
from pathlib import Path
from bs4 import BeautifulSoup
from tqdm import tqdm

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

RAW_DATA_DIR = Path(__file__).parent.parent / "raw_data" / "neo_assyrian"

SAA_LETTER_PROJECTS = {
    "SAA01 - Correspondence of Sargon II (Part I)":           "saao/saa01",
    "SAA04 - Queries to the Sungod":                          "saao/saa04",
    "SAA05 - Correspondence of Sargon II Officials (Part I)": "saao/saa05",
    "SAA08 - Astrological Reports to Assyrian Kings":         "saao/saa08",
    "SAA09 - Assyrian Prophecies":                            "saao/saa09",
    "SAA10 - Letters from Assyrian Scholars":                 "saao/saa10",
    "SAA15 - Correspondence of Sargon II Officials (Part II)":"saao/saa15",
    "SAA16 - Political Correspondence from Esarhaddon":        "saao/saa16",
    "SAA17 - Neo-Babylonian Correspondence":                   "saao/saa17",
    "SAA18 - The Correspondence of Tiglath-Pileser III":       "saao/saa18",
    "SAA19 - The Correspondence of Sargon II (Part II)":       "saao/saa19",
    "SAA21 - The Correspondence of Assurbanipal":              "saao/saa21",
}

ORACC_BASE = "https://oracc.museum.upenn.edu"
TIMEOUT_SECONDS = 120
RETRY_ATTEMPTS = 3
RETRY_DELAY = 5

# Disable SSL verification for corporate proxy environments
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
SSL_VERIFY = False


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def find_download_url(project_slug: str) -> str | None:
    """Scrape the project downloads page and return the teiCorpus ZIP URL."""
    page_url = f"{ORACC_BASE}/{project_slug}/downloads/"
    try:
        r = requests.get(page_url, verify=SSL_VERIFY, timeout=15)
        r.raise_for_status()
    except requests.RequestException as exc:
        print(f"  Could not fetch downloads page: {exc}")
        return None

    soup = BeautifulSoup(r.text, "html.parser")
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "teiCorpus" in href and href.endswith(".zip"):
            return ORACC_BASE + href if href.startswith("/") else href
    return None


def download_with_progress(url: str, dest: Path) -> bool:
    """Stream-download a file to dest with a tqdm progress bar."""
    for attempt in range(1, RETRY_ATTEMPTS + 1):
        try:
            r = requests.get(url, stream=True, timeout=TIMEOUT_SECONDS, verify=SSL_VERIFY)
            r.raise_for_status()
            total = int(r.headers.get("content-length", 0))
            with open(dest, "wb") as fh, tqdm(
                desc=dest.name, total=total, unit="B",
                unit_scale=True, unit_divisor=1024, leave=False,
            ) as bar:
                for chunk in r.iter_content(chunk_size=8192):
                    fh.write(chunk)
                    bar.update(len(chunk))
            return True
        except requests.RequestException as exc:
            print(f"  Attempt {attempt}/{RETRY_ATTEMPTS} failed: {exc}")
            if attempt < RETRY_ATTEMPTS:
                time.sleep(RETRY_DELAY)
    return False


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {len(SAA_LETTER_PROJECTS)} SAA volumes to {RAW_DATA_DIR}\n")

    for label, slug in SAA_LETTER_PROJECTS.items():
        project_dir = RAW_DATA_DIR / slug.replace("/", "_")
        print(f"[{slug}] {label}")

        # Skip if a TEI XML already exists
        existing = list(project_dir.glob("*teiCorpus*.xml"))
        if existing:
            print(f"  Already downloaded: {existing[0].name} — skipping.\n")
            continue

        # Discover the download URL from the project's downloads page
        url = find_download_url(slug)
        if not url:
            print(f"  ERROR: No teiCorpus ZIP found on downloads page.\n")
            continue
        print(f"  Found: {url}")

        project_dir.mkdir(parents=True, exist_ok=True)
        zip_path = project_dir / Path(url).name

        if not download_with_progress(url, zip_path):
            print(f"  ERROR: Download failed.\n")
            continue

        print(f"  Extracting ...")
        try:
            with zipfile.ZipFile(zip_path, "r") as zf:
                zf.extractall(project_dir)
        except zipfile.BadZipFile as exc:
            print(f"  ERROR: Bad ZIP: {exc}\n")
            continue

        zip_path.unlink()
        extracted = list(project_dir.glob("*.xml"))
        print(f"  Done: {extracted[0].name if extracted else '(no XML found)'}\n")

    print("All downloads complete.")


if __name__ == "__main__":
    main()
