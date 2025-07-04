# Caching

## Overview
- The caching system stores downloaded artwork and generated images to speed up repeated operations and avoid redundant downloads.
- Caching is managed by the `ArtworkCache` and `ImageProcessor` classes.

## Cache Management
- Cached files are stored in the directory specified by `CACHE_DIR` (default: `cache/`).
- Original images are archived in `ORIGINALS_SUBDIR` before upsampling.
- The cache is validated and cleaned up using `CACHE_CLEANUP_DAYS` and (optionally) `MAX_CACHE_SIZE`.
- The cache can be manually cleaned or inspected using provided methods in `ArtworkCache`.

## Configuration
- All cache settings are in `Settings` (see `config.yaml`):
  - `CACHE_DIR`, `ORIGINALS_SUBDIR`, `MAX_CACHE_SIZE`, `CACHE_CLEANUP_DAYS`
- You can override these via YAML or environment variables.

## Clearing or Inspecting the Cache
- To clear old or invalid files, use the `cleanup_old_cache()` method in `ArtworkCache`.
- To inspect cache contents, browse the `cache/` directory or use cache info methods.

## See Also
- `docs/architecture.md` for system overview
- `docs/api_reference.md` for class/method details
- `docs/examples/` for cache management scripts 