import os
import json
import hashlib
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, Tuple
import requests
import re

try:
    import marimo as mo
    _MARIMO_AVAILABLE = True
except ImportError:
    _MARIMO_AVAILABLE = False


class CBSCacheManager:
    """
    Intelligent caching system for CBS OData API responses.
    Uses timestamp-based validation to only refetch when source data changes.
    """
    
    def __init__(self, cache_dir: str = "./cache"):
        # Use marimo notebook directory if available, otherwise fall back to current directory
        if _MARIMO_AVAILABLE:
            try:
                base_dir = mo.notebook_dir()
            except:
                base_dir = Path.cwd()
        else:
            base_dir = Path.cwd()
        
        # If cache_dir is relative, make it relative to the notebook directory
        if not Path(cache_dir).is_absolute():
            self.cache_dir = base_dir / cache_dir
        else:
            self.cache_dir = Path(cache_dir)
            
        self.metadata_dir = self.cache_dir / "metadata"
        self.data_dir = self.cache_dir / "data"
        
        # Create cache directories
        self.metadata_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_dataset_id(self, url: str) -> str:
        """Extract dataset ID from CBS OData URL."""
        # Extract dataset ID from URL like https://opendata.cbs.nl/ODataApi/OData/85237NED
        # Handle endpoint-specific URLs like .../85237NED/Bouwjaar
        parts = url.rstrip('/').split('/')
        if len(parts) >= 6:  # .../ODataApi/OData/DATASET/endpoint
            dataset_part = parts[5]  # The dataset ID part
            if dataset_part and dataset_part[0].isdigit():  # Dataset IDs start with numbers
                return dataset_part
        return parts[-1]
    
    def _is_paginated_url(self, url: str) -> bool:
        """Check if URL contains pagination parameters."""
        return '$top' in url and '$skip' in url
    
    def _get_base_url_without_pagination(self, url: str) -> str:
        """Remove pagination parameters from URL."""
        return url.split('?')[0] if '?' in url else url
    
    def _get_cache_key(self, url: str) -> str:
        """Generate cache key from URL."""
        # Use URL path for readable cache keys
        dataset_id = self._get_dataset_id(url)
        
        # For paginated URLs, ignore pagination params and use base endpoint
        if self._is_paginated_url(url):
            base_url = self._get_base_url_without_pagination(url)
            url_parts = base_url.rstrip('/').split('/')
            if len(url_parts) >= 7:  # .../ODataApi/OData/DATASET/endpoint
                endpoint = url_parts[6]
                return f"{dataset_id}_{endpoint}"
            else:
                return dataset_id
        
        # Extract endpoint from URL if present
        url_parts = url.rstrip('/').split('/')
        if len(url_parts) >= 7:  # .../ODataApi/OData/DATASET/endpoint
            endpoint = url_parts[6]
            cache_key = f"{dataset_id}_{endpoint}"
        else:
            cache_key = dataset_id
            
        # Add query hash for non-paginated queries
        if '?' in url:
            query_hash = hashlib.md5(url.split('?')[1].encode()).hexdigest()[:8]
            cache_key += f"_{query_hash}"
            
        return cache_key
    
    def _get_table_info_url(self, base_url: str) -> str:
        """Get TableInfos URL from base dataset URL."""
        dataset_id = self._get_dataset_id(base_url)
        return f"https://opendata.cbs.nl/ODataApi/OData/{dataset_id}/TableInfos"
    
    def _fetch_table_info(self, base_url: str) -> Optional[Dict[str, Any]]:
        """Fetch TableInfos metadata for timestamp validation."""
        try:
            table_info_url = self._get_table_info_url(base_url)
            response = requests.get(table_info_url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            if 'value' in data and len(data['value']) > 0:
                return data['value'][0]  # First (and usually only) table info
            return None
        except Exception as e:
            print(f"Warning: Could not fetch TableInfos for {base_url}: {e}")
            return None
    
    def _parse_timestamp(self, timestamp_str: str) -> Optional[datetime]:
        """Parse CBS timestamp format to datetime object."""
        try:
            # CBS uses format like "2025-02-28T02:00:00"
            return datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        except Exception:
            return None
    
    def _get_cached_metadata_path(self, base_url: str) -> Path:
        """Get path for cached TableInfos metadata."""
        dataset_id = self._get_dataset_id(base_url)
        return self.metadata_dir / f"{dataset_id}_tableinfo.json"
    
    def _get_cached_data_path(self, url: str) -> Path:
        """Get path for cached data file."""
        cache_key = self._get_cache_key(url)
        return self.data_dir / f"{cache_key}.parquet"
    
    def _load_cached_metadata(self, base_url: str) -> Optional[Dict[str, Any]]:
        """Load cached TableInfos metadata."""
        metadata_path = self._get_cached_metadata_path(base_url)
        if metadata_path.exists():
            try:
                with open(metadata_path, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return None
    
    def _save_cached_metadata(self, base_url: str, metadata: Dict[str, Any]) -> None:
        """Save TableInfos metadata to cache."""
        metadata_path = self._get_cached_metadata_path(base_url)
        try:
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save metadata cache: {e}")
    
    def _get_base_dataset_url(self, url: str) -> str:
        """Get base dataset URL from any endpoint-specific URL."""
        # For URLs like https://opendata.cbs.nl/ODataApi/OData/85237NED/Bouwjaar
        # Return https://opendata.cbs.nl/ODataApi/OData/85237NED
        dataset_id = self._get_dataset_id(url)
        return f"https://opendata.cbs.nl/ODataApi/OData/{dataset_id}"
        
    def _is_cache_valid(self, url: str, force_refresh: bool = False) -> bool:
        """
        Check if cached data is still valid by comparing timestamps.
        Returns True if cache is valid, False if needs refresh.
        """
        if force_refresh:
            return False
        
        # Check if cached data file exists
        cached_data_path = self._get_cached_data_path(url)
        if not cached_data_path.exists():
            return False
        
        # Get base dataset URL for timestamp comparison
        base_url = self._get_base_dataset_url(url)
        
        # Get current and cached metadata
        current_metadata = self._fetch_table_info(base_url)
        cached_metadata = self._load_cached_metadata(base_url)
        
        if not current_metadata:
            return False
            
        if not cached_metadata:
            self._save_cached_metadata(base_url, current_metadata)
            return False
        
        # Compare Modified timestamps
        current_modified = current_metadata.get('Modified')
        cached_modified = cached_metadata.get('Modified')
        
        if not current_modified or not cached_modified:
            return False
        
        # Update cached metadata if current is newer
        if current_modified != cached_modified:
            self._save_cached_metadata(base_url, current_metadata)
            return False
        
        return True
    
    def get_cached_data(self, url: str, force_refresh: bool = False) -> Optional[pd.DataFrame]:
        """
        Retrieve data from cache if valid, otherwise return None.
        """
        if not self._is_cache_valid(url, force_refresh):
            return None
        
        cached_data_path = self._get_cached_data_path(url)
        try:
            return pd.read_parquet(cached_data_path)
        except Exception as e:
            print(f"Warning: Could not load cached data from {cached_data_path}: {e}")
            return None
    
    def save_data_to_cache(self, url: str, df: pd.DataFrame) -> None:
        """Save DataFrame to cache using Parquet format."""
        cached_data_path = self._get_cached_data_path(url)
        try:
            df.to_parquet(cached_data_path, index=False)
            print(f"Cached data saved to {cached_data_path}")
        except Exception as e:
            print(f"Warning: Could not save data to cache: {e}")
    
    def invalidate_cache(self, url: str = None) -> None:
        """
        Invalidate cache for specific dataset or all cached data.
        """
        if url:
            # Invalidate specific dataset
            dataset_id = self._get_dataset_id(url)
            
            # Remove metadata cache
            metadata_path = self._get_cached_metadata_path(url)
            if metadata_path.exists():
                metadata_path.unlink()
            
            # Remove all data caches for this dataset
            for data_file in self.data_dir.glob(f"{dataset_id}*"):
                data_file.unlink()
            
            print(f"Cache invalidated for dataset {dataset_id}")
        else:
            # Invalidate all caches
            for metadata_file in self.metadata_dir.glob("*"):
                metadata_file.unlink()
            for data_file in self.data_dir.glob("*"):
                data_file.unlink()
            print("All caches invalidated")
    
    def cleanup_fragmented_cache(self, dataset_id: str = None) -> int:
        """
        Clean up fragmented cache files from paginated requests.
        Returns number of files cleaned up.
        """
        cleaned_count = 0
        pattern = r'.*\$top=\d+.*\$skip=\d+.*\.parquet$'
        
        for cache_file in self.data_dir.glob("*.parquet"):
            # Match fragmented cache files
            if re.match(pattern, cache_file.name):
                # If dataset_id specified, only clean files for that dataset
                if dataset_id is None or cache_file.name.startswith(dataset_id):
                    cache_file.unlink()
                    cleaned_count += 1
                    print(f"Cleaned up fragmented cache: {cache_file.name}")
        
        return cleaned_count
    
    def is_aggregate_caching_candidate(self, url: str) -> bool:
        """
        Check if this URL should use aggregate caching (for large paginated datasets).
        Currently applies to TypedDataSet endpoints with pagination.
        """
        return (self._is_paginated_url(url) and 
                'TypedDataSet' in url and
                '$skip=0' in url)  # Only trigger on first page
    
    def get_cached_data(self, url: str, force_refresh: bool = False) -> Optional[pd.DataFrame]:
        """
        Retrieve data from cache if valid, otherwise return None.
        For paginated URLs, returns complete dataset if cached.
        """
        if not self._is_cache_valid(url, force_refresh):
            return None
        
        cached_data_path = self._get_cached_data_path(url)
        try:
            df = pd.read_parquet(cached_data_path)
            return df
        except Exception as e:
            print(f"Warning: Could not load cached data from {cached_data_path}: {e}")
            return None
    
    def save_aggregated_data_to_cache(self, base_url: str, df: pd.DataFrame) -> None:
        """
        Save complete aggregated DataFrame to cache using clean cache key.
        Used for paginated datasets that have been fully fetched and combined.
        """
        cache_key = self._get_cache_key(base_url)
        cached_data_path = self.data_dir / f"{cache_key}.parquet"
        
        try:
            df.to_parquet(cached_data_path, index=False)
            print(f"Cached complete dataset to {cached_data_path}")
            
            # Clean up any existing fragmented cache files for this dataset
            dataset_id = self._get_dataset_id(base_url)
            self.cleanup_fragmented_cache(dataset_id)
            
        except Exception as e:
            print(f"Warning: Could not save aggregated data to cache: {e}")

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        metadata_files = list(self.metadata_dir.glob("*.json"))
        data_files = list(self.data_dir.glob("*.parquet"))
        
        # Count fragmented files separately
        fragmented_files = [f for f in data_files if re.match(r'.*\$top=\d+.*\$skip=\d+.*\.parquet$', f.name)]
        clean_files = [f for f in data_files if f not in fragmented_files]
        
        total_size = sum(f.stat().st_size for f in data_files + metadata_files)
        
        return {
            "metadata_files": len(metadata_files),
            "data_files": len(clean_files),
            "fragmented_files": len(fragmented_files),
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "cache_dir": str(self.cache_dir)
        }