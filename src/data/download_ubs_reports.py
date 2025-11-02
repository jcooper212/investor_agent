# ABOUTME: Script to download UBS House View reports
# ABOUTME: Downloads publicly available UBS investment research PDFs

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

        response = requests.get(url, stream=True, timeout=30)
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


def download_ubs_reports(output_dir: str = "./data/pdfs") -> Dict[str, any]:
    """
    Download UBS House View reports.

    Args:
        output_dir: Directory to save PDF files

    Returns:
        Dictionary with download statistics
    """
    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # UBS House View report URLs (publicly available)
    reports = [
        {
            "name": "UBS_House_View_June_2025.pdf",
            "url": "https://advisors.ubs.com/mediahandler/media/697651/UBS House View for April  2025.pdf",
            "description": "UBS House View - April 2025",
        },
        {
            "name": "UBS_House_View_March_2025.pdf",
            "url": "https://advisors.ubs.com/mediahandler/media/692405/UBS House View for March 2025.pdf",
            "description": "UBS House View - March 2025",
        },
        {
            "name": "UBS_House_View_November_2024.pdf",
            "url": "https://advisors.ubs.com/mediahandler/media/675057/UBS House View November 2024.pdf",
            "description": "UBS House View - November 2024",
        },
        {
            "name": "UBS_House_View_June_2024.pdf",
            "url": "https://advisors.ubs.com/mediahandler/media/648061/UBS House View June 2024.pdf",
            "description": "UBS House View - June 2024",
        },
    ]

    print("=" * 70)
    print("UBS House View Report Downloader")
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
                print(f"   Size: {file_size / 1024:.1f} KB\n")
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
    print("\nDownloaded files:")
    for filename in stats["downloaded_files"]:
        file_path = os.path.join(output_dir, filename)
        if os.path.exists(file_path):
            size_kb = os.path.getsize(file_path) / 1024
            print(f"  • {filename} ({size_kb:.1f} KB)")

    return stats


if __name__ == "__main__":
    download_ubs_reports()
