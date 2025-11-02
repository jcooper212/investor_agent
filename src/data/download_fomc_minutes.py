# ABOUTME: Script to download Federal Reserve FOMC meeting minutes
# ABOUTME: Downloads publicly available FOMC minutes from 2024-2025 for policy analysis

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


def download_fomc_minutes(output_dir: str = "./data/pdfs/fomc") -> Dict[str, any]:
    """
    Download FOMC meeting minutes from 2024-2025.

    Args:
        output_dir: Directory to save PDF files

    Returns:
        Dictionary with download statistics
    """
    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # FOMC minutes URLs (publicly available from federalreserve.gov)
    fomc_minutes = [
        {
            "name": "FOMC_Minutes_2024_Jan.pdf",
            "url": "https://www.federalreserve.gov/monetarypolicy/files/fomcminutes20240131.pdf",
            "description": "FOMC Minutes - January 30-31, 2024",
            "date": "2024-01-31",
        },
        {
            "name": "FOMC_Minutes_2024_Mar.pdf",
            "url": "https://www.federalreserve.gov/monetarypolicy/files/fomcminutes20240320.pdf",
            "description": "FOMC Minutes - March 19-20, 2024",
            "date": "2024-03-20",
        },
        {
            "name": "FOMC_Minutes_2024_May.pdf",
            "url": "https://www.federalreserve.gov/monetarypolicy/files/fomcminutes20240501.pdf",
            "description": "FOMC Minutes - April 30 - May 1, 2024",
            "date": "2024-05-01",
        },
        {
            "name": "FOMC_Minutes_2024_Jun.pdf",
            "url": "https://www.federalreserve.gov/monetarypolicy/files/fomcminutes20240612.pdf",
            "description": "FOMC Minutes - June 11-12, 2024",
            "date": "2024-06-12",
        },
        {
            "name": "FOMC_Minutes_2024_Jul.pdf",
            "url": "https://www.federalreserve.gov/monetarypolicy/files/fomcminutes20240731.pdf",
            "description": "FOMC Minutes - July 30-31, 2024",
            "date": "2024-07-31",
        },
        {
            "name": "FOMC_Minutes_2024_Sep.pdf",
            "url": "https://www.federalreserve.gov/monetarypolicy/files/fomcminutes20240918.pdf",
            "description": "FOMC Minutes - September 17-18, 2024",
            "date": "2024-09-18",
        },
        {
            "name": "FOMC_Minutes_2024_Nov.pdf",
            "url": "https://www.federalreserve.gov/monetarypolicy/files/fomcminutes20241107.pdf",
            "description": "FOMC Minutes - November 6-7, 2024",
            "date": "2024-11-07",
        },
        {
            "name": "FOMC_Minutes_2024_Dec.pdf",
            "url": "https://www.federalreserve.gov/monetarypolicy/files/fomcminutes20241218.pdf",
            "description": "FOMC Minutes - December 17-18, 2024",
            "date": "2024-12-18",
        },
    ]

    print("=" * 70)
    print("Federal Reserve FOMC Minutes Downloader")
    print("=" * 70)
    print(f"Output directory: {output_dir}")
    print(f"Total documents to download: {len(fomc_minutes)}\n")

    stats = {
        "total": len(fomc_minutes),
        "successful": 0,
        "failed": 0,
        "downloaded_files": [],
    }

    for minute in fomc_minutes:
        destination = os.path.join(output_dir, minute["name"])

        # Skip if file already exists
        if os.path.exists(destination):
            file_size = os.path.getsize(destination)
            if file_size > 1000:  # File larger than 1KB - assume valid
                print(f"⏭️  Skipping (already exists): {minute['name']}")
                print(f"   Size: {file_size / 1024:.1f} KB")
                print(f"   Date: {minute['date']}\n")
                stats["successful"] += 1
                stats["downloaded_files"].append(minute["name"])
                continue

        # Download the file
        success = download_file(minute["url"], destination)

        if success:
            stats["successful"] += 1
            stats["downloaded_files"].append(minute["name"])
        else:
            stats["failed"] += 1

    # Print summary
    print("=" * 70)
    print("Download Summary")
    print("=" * 70)
    print(f"✅ Successful: {stats['successful']}/{stats['total']}")
    print(f"❌ Failed: {stats['failed']}/{stats['total']}")
    print("\nDownloaded FOMC Minutes:")
    for filename in stats["downloaded_files"]:
        file_path = os.path.join(output_dir, filename)
        if os.path.exists(file_path):
            size_kb = os.path.getsize(file_path) / 1024
            print(f"  • {filename} ({size_kb:.1f} KB)")

    return stats


if __name__ == "__main__":
    download_fomc_minutes()
