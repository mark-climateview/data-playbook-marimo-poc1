#!/usr/bin/env python3
"""
Data Fetcher Script for CBS Open Data

This script fetches data from CBS (Statistics Netherlands) APIs and saves it 
to the local data/ folder. This replaces the live API + caching approach with
a local data folder approach that works better with Marimo Community Cloud.

Usage:
    uv run data_fetcher.py          # Fetch all known datasets
    uv run data_fetcher.py --refresh # Force refresh all data
    uv run data_fetcher.py --dataset 85236NED  # Fetch specific dataset
"""

import argparse
import sys, os
from pathlib import Path
from util import get_cbs_url, get_cbs_url_paginated, get_cache_stats

# Known datasets and their endpoints that we need to fetch
DATASETS = {
    "85236NED": {
        "name": "Motor vehicles by type and region",
        "endpoints": [
            "",  # Base metadata
            "DataProperties",
            "Perioden", 
            "RegioS",
            "TypedDataSet"  # Large dataset - needs pagination
        ]
    },
    "85237NED": {
        "name": "Active passenger cars by characteristics",
        "endpoints": [
            "",  # Base metadata
            "Bouwjaar",
            "DataProperties", 
            "Perioden",
            "TypedDataSet"  # Large dataset - needs pagination
        ]
    },
    "85405NED": {
        "name": "Vehicle kilometers by fuel type and age",
        "endpoints": [
            "",  # Base metadata
            "BrandstofsoortVoertuig",
            "LeeftijdVoertuig",
            "Perioden",
            "TypedDataSet"  # Large dataset - needs pagination
        ]
    }
}

def get_data_dir():
    """Get the data directory path."""
    return Path(__file__).parent / "data"

def fetch_dataset(dataset_id, force_refresh=False):
    """
    Fetch all endpoints for a specific dataset.
    
    Args:
        dataset_id: Dataset ID (e.g., "85236NED")
        force_refresh: Force refresh even if data exists
    """
    if dataset_id not in DATASETS:
        print(f"Unknown dataset: {dataset_id}")
        print(f"Known datasets: {', '.join(DATASETS.keys())}")
        return False
    
    dataset_info = DATASETS[dataset_id]
    base_url = f"https://opendata.cbs.nl/ODataApi/OData/{dataset_id}"
    data_dir = get_data_dir()
    
    print(f"\nFetching dataset {dataset_id}: {dataset_info['name']}")
    print(f"Data will be saved to: {data_dir}")
    
    # Ensure data directory exists
    data_dir.mkdir(exist_ok=True)
    
    success_count = 0
    total_count = len(dataset_info['endpoints'])
    
    for endpoint in dataset_info['endpoints']:
        try:
            if endpoint == "":
                # Base metadata endpoint
                endpoint_url = base_url
                filename = f"{dataset_id}.parquet"
            else:
                # Specific endpoint
                endpoint_url = f"{base_url}/{endpoint}"
                filename = f"{dataset_id}_{endpoint}.parquet"
            
            output_path = data_dir / filename
            
            # Skip if file exists and not forcing refresh
            if output_path.exists() and not force_refresh:
                print(f"  ✓ {filename} (already exists)")
                success_count += 1
                continue
            
            print(f"  Fetching {endpoint if endpoint else 'metadata'}...")
            
            # Use appropriate fetching method
            if endpoint == "TypedDataSet":
                # Large dataset - use pagination
                df = get_cbs_url_paginated(endpoint_url, force_refresh=force_refresh)
            else:
                # Regular endpoint
                df = get_cbs_url(endpoint_url, force_refresh=force_refresh)
            
            if df is not None and not df.empty:
                # Save directly to data folder
                df.to_parquet(output_path, index=False)
                print(f"  ✓ {filename} ({len(df)} records)")
                success_count += 1
            else:
                print(f"  ✗ {filename} (no data returned)")
                
        except Exception as e:
            print(f"  ✗ {filename} (error: {e})")
    
    print(f"Completed {dataset_id}: {success_count}/{total_count} endpoints successful")
    return success_count == total_count

def fetch_all_datasets(force_refresh=False):
    """Fetch all known datasets."""
    print("Fetching all CBS datasets...")
    
    total_success = 0
    total_datasets = len(DATASETS)
    
    for dataset_id in DATASETS:
        if fetch_dataset(dataset_id, force_refresh):
            total_success += 1
    
    print(f"\n=== Summary ===")
    print(f"Successfully fetched: {total_success}/{total_datasets} datasets")
    
    # Show cache stats for reference
    try:
        stats = get_cache_stats()
        print(f"Cache directory: {stats['cache_dir']}")
        print(f"Cache size: {stats['total_size_mb']} MB")
    except:
        pass
    
    data_dir = get_data_dir()
    data_files = list(data_dir.glob("*.parquet"))
    total_size = sum(f.stat().st_size for f in data_files) / (1024 * 1024)
    print(f"Data directory: {data_dir}")
    print(f"Data files: {len(data_files)}")
    print(f"Data size: {total_size:.2f} MB")
    
    return total_success == total_datasets

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Fetch CBS data to local data folder")
    parser.add_argument("--dataset", help="Specific dataset to fetch (e.g., 85236NED)")
    parser.add_argument("--refresh", action="store_true", help="Force refresh all data")
    parser.add_argument("--list", action="store_true", help="List available datasets")
    
    args = parser.parse_args()
    
    if args.list:
        print("Available datasets:")
        for dataset_id, info in DATASETS.items():
            print(f"  {dataset_id}: {info['name']}")
        return
    
    try:
        if args.dataset:
            success = fetch_dataset(args.dataset, args.refresh)
        else:
            success = fetch_all_datasets(args.refresh)
        
        if success:
            print("\n✓ All data fetching completed successfully!")
            sys.exit(0)
        else:
            print("\n✗ Some data fetching failed.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
