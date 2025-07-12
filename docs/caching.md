# Caching

## Overview
- The caching system stores downloaded artwork and generated images to speed up repeated operations and avoid redundant downloads.
- Caching is managed by the `ArtworkCache` and `ImageProcessor` classes.
- **Auto-caching**: The system automatically downloads missing artwork when generating images, eliminating the need for manual cache setup.

## Cache Management
- Cached files are stored in the directory specified by `CACHE_DIR` (default: `cache/`).
- Original images are archived in `ORIGINALS_SUBDIR` before upsampling.
- The cache is validated and cleaned up using `CACHE_CLEANUP_DAYS` and (optionally) `MAX_CACHE_SIZE`.
- The cache can be manually cleaned or inspected using provided methods in `ArtworkCache`.

## Auto-Caching (First Run Support)
- **Automatic Download**: When generating an image, if required artwork is not cached, it's automatically downloaded.
- **Smart Targeting**: Only downloads artwork needed for the specific date being generated (not the entire cache).
- **Fallback Strategy**: If no artwork exists for the requested date, downloads the next available artwork.
- **Configurable**: Can be disabled via `--no-auto-cache` CLI flag or `AUTO_CACHE_ARTWORK` setting.

### Auto-Caching Examples
```bash
# First run - automatically downloads required artwork
python -m liturgical_calendar.cli generate 2024-12-25

# Disable auto-caching for offline environments
python -m liturgical_calendar.cli generate --no-auto-cache

# Progressive cache building - only downloads what you use
python -m liturgical_calendar.cli generate 2024-12-25  # Downloads Christmas artwork
python -m liturgical_calendar.cli generate 2024-12-26  # Downloads Boxing Day artwork
```

## Manual Cache Management
- **Batch Download**: Use `cache-artwork` command to download all artwork at once.
- **Cache Inspection**: Browse the `cache/` directory or use cache info methods.
- **Cache Cleanup**: Use `cleanup_old_cache()` method to remove old files.

### Manual Caching Example
```bash
# Download all artwork (useful for offline environments)
python -m liturgical_calendar.cli cache-artwork
```

## Configuration
- All cache settings are in `Settings` (see `config.yaml`):
  - `CACHE_DIR`, `ORIGINALS_SUBDIR`, `MAX_CACHE_SIZE`, `CACHE_CLEANUP_DAYS`
  - `AUTO_CACHE_ARTWORK`: Enable/disable automatic caching (default: true)
- You can override these via YAML or environment variables.

## Benefits
- **First-Run Ready**: No manual setup required for new users
- **Efficient**: Only downloads artwork you actually use
- **Progressive**: Cache builds up organically over time
- **Bandwidth Friendly**: Minimal network usage
- **Storage Efficient**: Only caches what's needed

## See Also
- `docs/architecture.md` for system overview
- `docs/api_reference.md` for class/method details
- `docs/examples/` for cache management scripts
