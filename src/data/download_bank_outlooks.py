# ABOUTME: Script to download investment bank outlook reports
# ABOUTME: Downloads 2025 market outlooks from JPMorgan, Goldman Sachs, Morgan Stanley

import os
import requests
from pathlib import Path
from typing import List, Dict
from tqdm import tqdm


def download_file(url: str, destination: str) -> bool:
    """
    Download a file from URL to destination.

    Args:
        url: URL to download from
        destination: Local file path to save to

    Returns:
        True if successful, False otherwise
    """
    try:
        print(f"📥 Downloading: {Path(destination).name}")
        print(f"   From: {url}")

        response = requests.get(url, stream=True, timeout=60, allow_redirects=True)
        response.raise_for_status()

        total_size = int(response.headers.get("content-length", 0))

        with open(destination, "wb") as f, tqdm(
            total=total_size, unit="B", unit_scale=True, desc="   Progress"
        ) as pbar:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                pbar.update(len(chunk))

        print(f"✅ Downloaded: {Path(destination).name}\n")
        return True

    except Exception as e:
        print(f"❌ Error downloading {url}: {e}\n")
        return False


def download_bank_outlooks(output_dir: str = "./data/pdfs/bank_outlooks") -> Dict[str, any]:
    """
    Download 2025 market outlook reports from major investment banks.

    Args:
        output_dir: Directory to save PDF files

    Returns:
        Dictionary with download statistics
    """
    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Investment bank outlook reports (publicly available)
    # Note: These URLs may change over time as new reports are published
    reports = [
        {
            "name": "JPMorgan_Market_Outlook_2025.pdf",
            "url": "https://am.jpmorgan.com/content/dam/jpm-am-aem/global/en/insights/market-insights/wmr/mi-outlook-q1-2025.pdf",
            "description": "J.P. Morgan Market Outlook 2025",
            "firm": "JPMorgan",
        },
        {
            "name": "Goldman_Sachs_Investment_Outlook_2025.pdf",
            "url": "https://privatewealth.goldmansachs.com/outlook/2025-isg-outlook.pdf",
            "description": "Goldman Sachs Investment Strategy Group Outlook 2025",
            "firm": "Goldman Sachs",
        },
        {
            "name": "Morgan_Stanley_Market_Outlook_2025.pdf",
            "url": "https://www.morganstanley.com/im/publication/insights/articles/article_thebeatfeb2025.pdf",
            "description": "Morgan Stanley - The BEAT February 2025",
            "firm": "Morgan Stanley",
        },
    ]

    print("=" * 70)
    print("Investment Bank Market Outlook Downloader")
    print("=" * 70)
    print(f"Output directory: {output_dir}")
    print(f"Total reports to download: {len(reports)}\n")

    stats = {
        "total": len(reports),
        "successful": 0,
        "failed": 0,
        "downloaded_files": [],
    }

    for report in reports:
        destination = os.path.join(output_dir, report["name"])

        # Skip if file already exists
        if os.path.exists(destination):
            file_size = os.path.getsize(destination)
            if file_size > 1000:  # File larger than 1KB - assume valid
                print(f"⏭️  Skipping (already exists): {report['name']}")
                print(f"   Size: {file_size / 1024:.1f} KB")
                print(f"   Firm: {report['firm']}\n")
                stats["successful"] += 1
                stats["downloaded_files"].append(report["name"])
                continue

        # Download the file
        success = download_file(report["url"], destination)

        if success:
            stats["successful"] += 1
            stats["downloaded_files"].append(report["name"])
        else:
            stats["failed"] += 1

    # Print summary
    print("=" * 70)
    print("Download Summary")
    print("=" * 70)
    print(f"✅ Successful: {stats['successful']}/{stats['total']}")
    print(f"❌ Failed: {stats['failed']}/{stats['total']}")
    print("\nDownloaded Investment Bank Outlooks:")
    for filename in stats["downloaded_files"]:
        file_path = os.path.join(output_dir, filename)
        if os.path.exists(file_path):
            size_kb = os.path.getsize(file_path) / 1024
            print(f"  • {filename} ({size_kb:.1f} KB)")

    print("\n⚠️  Note: Some bank outlook URLs may change or require access.")
    print("   If downloads fail, check the firm's investor relations website.")

    return stats


if __name__ == "__main__":
    download_bank_outlooks()
