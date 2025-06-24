# Intelligent Caching System for CBS Data

This project now includes an intelligent caching system that significantly speeds up data loading from CBS (Statistics Netherlands) OData APIs.

## How It Works

The caching system automatically:
1. **Fetches data** from CBS APIs on first run
2. **Stores data locally** in efficient Parquet format
3. **Checks timestamps** to detect when source data changes
4. **Serves cached data** when source hasn't changed
5. **Refreshes automatically** when CBS updates their data

## Performance Benefits

- **~10x faster loading** for cached data
- **Reduced API calls** to CBS servers
- **Offline capability** with cached data
- **Bandwidth savings** for repeated analysis

## Cache Structure

```
cache/
├── metadata/          # Dataset metadata and timestamps
│   └── 85237NED_tableinfo.json
└── data/             # Cached data in Parquet format
    ├── 85237NED.parquet
    ├── 85237NED_Bouwjaar.parquet
    ├── 85237NED_Perioden.parquet
    └── 85237NED_TypedDataSet.parquet
```

## Usage

### Automatic Caching (Default)
```python
import util

# Small datasets - standard caching
df = util.get_cbs_url("https://opendata.cbs.nl/ODataApi/OData/85237NED/Bouwjaar")

# Large paginated datasets - aggregate caching
df = util.get_cbs_url_paginated("https://opendata.cbs.nl/ODataApi/OData/85236NED/TypedDataSet")
```

### Paginated Dataset Caching
For large datasets that require pagination (like TypedDataSet endpoints), use the aggregate caching function:

```python
# Intelligent aggregate caching for large datasets
df = util.get_cbs_url_paginated(
    "https://opendata.cbs.nl/ODataApi/OData/85236NED/TypedDataSet",
    page_size=5000  # Optional, default 5000
)
```

**Benefits of Aggregate Caching:**
- Single clean cache file per dataset (e.g., `85236NED_TypedDataSet.parquet`)
- Complete dataset integrity - all pages fetched from same timestamp
- Faster subsequent loads - no need to load multiple fragments
- Cleaner cache directory structure

### Manual Cache Control
```python
# Force refresh (bypass cache)
df = util.get_cbs_url(url, force_refresh=True)
df = util.get_cbs_url_paginated(url, force_refresh=True)

# Disable caching entirely
df = util.get_cbs_url(url, use_cache=False)
df = util.get_cbs_url_paginated(url, use_cache=False)

# Clear specific dataset cache
util.invalidate_cache("https://opendata.cbs.nl/ODataApi/OData/85237NED")

# Clear all caches
util.invalidate_cache()

# Clean up old fragmented cache files
cleaned_count = util.cleanup_fragmented_cache()

# Get cache statistics
stats = util.get_cache_stats()
print(f"Cache size: {stats['total_size_mb']} MB")
print(f"Fragmented files: {stats['fragmented_files']}")
```

## Cache Validation

The system uses CBS's `TableInfos` endpoint to check the `Modified` timestamp:
- If source data timestamp matches cached timestamp → use cache
- If source data is newer → fetch fresh data and update cache
- If API is unavailable → serve stale cache as fallback

## Data Formats

**Parquet** format was chosen for optimal performance:
- **Fast I/O**: ~10x faster than CSV
- **Compression**: ~50% smaller files than CSV
- **Schema preservation**: Maintains data types
- **Cross-platform**: Works across different systems

## Troubleshooting

### Cache Issues
- **Clear cache**: Run `util.invalidate_cache()` to start fresh
- **Check connectivity**: Ensure internet access for timestamp validation
- **Verify permissions**: Ensure write access to cache directory

### Performance
- **First run slow**: Expected behavior - fetching from API
- **Subsequent runs fast**: Should load from cache in <1 second
- **Large datasets**: May take longer to write to cache initially

## Integration with Existing Code

The caching system is **backward compatible** - existing code works unchanged:
- No modifications needed for standard CBS endpoints
- Use `get_cbs_url_paginated()` for large TypedDataSet endpoints
- Optional cache control parameters available
- Cache management UI available in Marimo notebooks

### Migration from Fragment Caching

If you previously had fragmented cache files from paginated requests, they can be cleaned up:

```python
import util

# Clean up all fragmented cache files
cleaned_count = util.cleanup_fragmented_cache()
print(f"Cleaned up {cleaned_count} fragmented files")

# Re-run your data notebooks to generate clean aggregate cache files
```

The system now prioritizes clean, maintainable caching over micro-optimizations, resulting in:
- Better user experience with logical file names
- Improved data consistency and reliability  
- Easier cache management and debugging