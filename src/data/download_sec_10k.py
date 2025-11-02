# ABOUTME: Script to download SEC 10-K filings for mega-cap tech companies
# ABOUTME: Downloads latest annual reports from SEC EDGAR for fundamental analysis

import os
import requests
import time
from pathlib import Path
from typing import List, Dict
from tqdm import tqdm


# SEC requires user agent for API access
HEADERS = {
    "User-Agent": "Investment Research Agent demo@arklex.com",
    "Accept-Encoding": "gzip, deflate",
}


def get_latest_10k_url(ticker: str, cik: str) -> tuple:
    """
    Get the latest 10-K filing URL for a company.

    Args:
        ticker: Stock ticker symbol
        cik: SEC CIK number (must be 10 digits with leading zeros)

    Returns:
        Tuple of (filing_url, fiscal_year) or (None, None) if not found
    """
    try:
        # Get company submissions data from SEC
        submissions_url = f"https://data.sec.gov/submissions/CIK{cik}.json"
        response = requests.get(submissions_url, headers=HEADERS, timeout=10)
        response.raise_for_status()

        data = response.json()
        filings = data["filings"]["recent"]

        # Find the most recent 10-K filing
        for i, form_type in enumerate(filings["form"]):
            if form_type == "10-K":
                accession_number = filings["accessionNumber"][i].replace("-", "")
                primary_document = filings["primaryDocument"][i]
                filing_date = filings["filingDate"][i]

                # Construct the filing URL
                filing_url = (
                    f"https://www.sec.gov/Archives/edgar/data/{cik.lstrip('0')}/"
                    f"{accession_number}/{primary_document}"
                )

                return (filing_url, filing_date[:4])  # Return URL and fiscal year

        return (None, None)

    except Exception as e:
        print(f"❌ Error fetching 10-K URL for {ticker}: {e}")
        return (None, None)


def download_file(url: str, destination: str, desc: str = "") -> bool:
    """
    Download a file from URL to destination.

    Args:
        url: URL to download from
        destination: Local file path to save to
        desc: Description for progress bar

    Returns:
        True if successful, False otherwise
    """
    try:
        print(f"📥 Downloading: {Path(destination).name}")
        print(f"   From: {url}")

        response = requests.get(url, headers=HEADERS, stream=True, timeout=60)
        response.raise_for_status()

        total_size = int(response.headers.get("content-length", 0))

        with open(destination, "wb") as f, tqdm(
            total=total_size, unit="B", unit_scale=True, desc=f"   {desc}"
        ) as pbar:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                pbar.update(len(chunk))

        print(f"✅ Downloaded: {Path(destination).name}\n")
        return True

    except Exception as e:
        print(f"❌ Error downloading {url}: {e}\n")
        return False


def download_sec_10k_filings(output_dir: str = "./data/pdfs/sec_10k") -> Dict[str, any]:
    """
    Download latest 10-K filings for mega-cap tech companies.

    Args:
        output_dir: Directory to save 10-K files

    Returns:
        Dictionary with download statistics
    """
    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # 7 Mega-cap tech companies with their CIK numbers
    companies = [
        {"ticker": "AAPL", "name": "Apple Inc.", "cik": "0000320193"},
        {"ticker": "MSFT", "name": "Microsoft Corporation", "cik": "0000789019"},
        {"ticker": "NVDA", "name": "NVIDIA Corporation", "cik": "0001045810"},
        {"ticker": "GOOGL", "name": "Alphabet Inc.", "cik": "0001652044"},
        {"ticker": "AMZN", "name": "Amazon.com Inc.", "cik": "0001018724"},
        {"ticker": "META", "name": "Meta Platforms Inc.", "cik": "0001326801"},
        {"ticker": "TSLA", "name": "Tesla Inc.", "cik": "0001318605"},
    ]

    print("=" * 70)
    print("SEC 10-K Filings Downloader - Mega-Cap Tech")
    print("=" * 70)
    print(f"Output directory: {output_dir}")
    print(f"Total companies: {len(companies)}\n")

    stats = {
        "total": len(companies),
        "successful": 0,
        "failed": 0,
        "downloaded_files": [],
    }

    for company in companies:
        ticker = company["ticker"]
        name = company["name"]
        cik = company["cik"]

        print(f"🔍 Processing {ticker} ({name})...")

        # Get the latest 10-K URL
        filing_url, fiscal_year = get_latest_10k_url(ticker, cik)

        if not filing_url:
            print(f"❌ Could not find 10-K for {ticker}\n")
            stats["failed"] += 1
            continue

        # Determine file extension from URL
        if filing_url.endswith(".htm") or filing_url.endswith(".html"):
            file_ext = ".html"
        else:
            file_ext = ".txt"

        filename = f"{ticker}_10K_FY{fiscal_year}{file_ext}"
        destination = os.path.join(output_dir, filename)

        # Skip if file already exists
        if os.path.exists(destination):
            file_size = os.path.getsize(destination)
            if file_size > 1000:  # File larger than 1KB - assume valid
                print(f"⏭️  Skipping (already exists): {filename}")
                print(f"   Size: {file_size / 1024:.1f} KB")
                print(f"   Fiscal Year: {fiscal_year}\n")
                stats["successful"] += 1
                stats["downloaded_files"].append(filename)
                time.sleep(0.1)  # SEC rate limiting - be polite
                continue

        # Download the file
        success = download_file(filing_url, destination, desc=f"{ticker} 10-K")

        if success:
            stats["successful"] += 1
            stats["downloaded_files"].append(filename)
        else:
            stats["failed"] += 1

        # SEC rate limiting - be respectful (10 requests/second limit)
        time.sleep(0.15)

    # Print summary
    print("=" * 70)
    print("Download Summary")
    print("=" * 70)
    print(f"✅ Successful: {stats['successful']}/{stats['total']}")
    print(f"❌ Failed: {stats['failed']}/{stats['total']}")
    print("\nDownloaded 10-K Filings:")
    for filename in stats["downloaded_files"]:
        file_path = os.path.join(output_dir, filename)
        if os.path.exists(file_path):
            size_kb = os.path.getsize(file_path) / 1024
            print(f"  • {filename} ({size_kb:.1f} KB)")

    return stats


if __name__ == "__main__":
    download_sec_10k_filings()
