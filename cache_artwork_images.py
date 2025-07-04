#!/usr/bin/env python3
"""
Script to download and cache Instagram images from the artwork data.
Downloads images at highest resolution and stores them in ./cache/ directory.
"""

import os
import re
import hashlib
import requests
from urllib.parse import urlparse
from pathlib import Path
import time
import json
from PIL import Image
from shutil import move
from liturgical_calendar.funcs import get_cache_filename
from liturgical_calendar.caching.artwork_cache import ArtworkCache
from liturgical_calendar.config.settings import Settings
import sys
from liturgical_calendar.exceptions import LiturgicalCalendarError
from liturgical_calendar.logging import setup_logging, get_logger

def get_instagram_image_url(instagram_url):
    """
    For Instagram post URLs, append '/media?size=l' to get the 640x640 image directly.
    """
    if 'instagram.com' in instagram_url:
        # Remove any trailing slash for consistency
        url = instagram_url.rstrip('/')
        return f"{url}/media?size=l"
    return None

def check_image_dimensions(image_path):
    """
    Check the dimensions of a downloaded image.
    """
    try:
        with Image.open(image_path) as img:
            width, height = img.size
            return width, height
    except ImportError:
        # If PIL is not available, use file command
        import subprocess
        try:
            result = subprocess.run(['file', image_path], capture_output=True, text=True)
            if 'JPEG' in result.stdout:
                # Extract dimensions from file output
                import re
                match = re.search(r'(\d+)x(\d+)', result.stdout)
                if match:
                    return int(match.group(1)), int(match.group(2))
        except:
            pass
    except Exception as e:
        print(f"    Error checking image dimensions: {e}")
    
    return None, None

def extract_source_urls_from_feasts():
    """
    Extract all source URLs from the feasts object in artwork.py
    """
    source_urls = []
    
    try:
        # Import the feasts object from artwork data
        from liturgical_calendar.data.artwork_data import feasts
        
        def extract_from_dict(data, path=""):
            """Recursively extract source URLs from nested dictionaries and lists"""
            if isinstance(data, dict):
                if 'source' in data and data['source']:
                    source_urls.append({
                        'url': data['source'],
                        'name': data.get('name', 'Unknown'),
                        'path': path
                    })
                for key, value in data.items():
                    extract_from_dict(value, f"{path}.{key}" if path else key)
            elif isinstance(data, list):
                for i, item in enumerate(data):
                    extract_from_dict(item, f"{path}[{i}]" if path else f"[{i}]")
        
        extract_from_dict(feasts)
        
    except ImportError as e:
        print(f"Error importing feasts from artwork.py: {e}")
        return []
    
    return source_urls

def upsample_if_needed(original_path, upsampled_path):
    """
    Move the original image to cache/original and upsample to 1080x1080 if needed, saving the upsampled image in cache/.
    """
    orig_dir = original_path.parent / Settings.ORIGINALS_SUBDIR
    orig_dir.mkdir(exist_ok=True)
    orig_backup = orig_dir / original_path.name
    # Move the original image to cache/original
    move(str(original_path), str(orig_backup))
    with Image.open(orig_backup) as img:
        width, height = img.size
        if width < Settings.ARTWORK_SIZE or height < Settings.ARTWORK_SIZE:
            print(f"    Upsampling {original_path.name} ({width}x{height}) to {Settings.ARTWORK_SIZE}x{Settings.ARTWORK_SIZE}...")
            upsampled = img.resize((Settings.ARTWORK_SIZE, Settings.ARTWORK_SIZE), Image.LANCZOS)
            upsampled.save(upsampled_path, quality=95)
        else:
            print(f"    Copying {original_path.name} ({width}x{height}) - already {Settings.ARTWORK_SIZE} or larger.")
            img.save(upsampled_path, quality=95)

def main():
    # Parse --verbose flag
    verbose = False
    args = sys.argv[1:]
    if '--verbose' in args:
        verbose = True
        args.remove('--verbose')
    setup_logging(level='DEBUG' if verbose else 'INFO')
    logger = get_logger(__name__)
    if verbose:
        print("[INFO] Verbose mode enabled (log level: DEBUG)")
    try:
        logger.info("Starting cache_artwork_images script")
        # Optionally load config file from argument or default location
        config_path = None
        if len(args) > 0 and not args[0].startswith('-'):
            config_path = args[0]
        Settings.load_from_file(config_path)  # Loads config from file/env if present
        logger.info(f"Loaded config from {config_path or 'default'}")
        print("Starting artwork image caching...")
        # Use ArtworkCache for all cache operations
        artwork_cache = ArtworkCache()
        logger.info(f"Cache directory: {artwork_cache.cache_dir.absolute()}")
        print(f"Cache directory: {artwork_cache.cache_dir.absolute()}")
        # Extract all source URLs
        source_entries = extract_source_urls_from_feasts()
        logger.info(f"Found {len(source_entries)} source URLs in artwork data")
        print(f"Found {len(source_entries)} source URLs in artwork data")
        # Track progress
        total_images = len(source_entries)
        cached_images = 0
        failed_images = 0
        skipped_images = 0
        failed_downloads = []
        # Process each source URL
        for i, entry in enumerate(source_entries, 1):
            source_url = entry['url']
            name = entry['name']
            path = entry['path']
            logger.info(f"Processing: {name} ({path}) [{i}/{total_images}]")
            print(f"\n[{i}/{total_images}] Processing: {name} ({path})")
            print(f"  Source URL: {source_url}")
            # Use ArtworkCache for cache filename and path
            cache_path = artwork_cache.get_cached_path(source_url)
            # Check if already cached
            if artwork_cache.is_cached(source_url):
                logger.info(f"Already cached: {cache_path.name}")
                print(f"  ✓ Already cached: {cache_path.name}")
                skipped_images += 1
                continue
            # Download and cache the image
            success = artwork_cache.download_and_cache(source_url)
            if success:
                logger.info(f"Cached: {cache_path.name}")
                print(f"  ✓ Cached: {cache_path.name}")
                cached_images += 1
            else:
                logger.error(f"Failed to cache: {cache_path.name}")
                print(f"  ✗ Failed to cache: {cache_path.name}")
                failed_images += 1
                failed_downloads.append({'url': source_url, 'name': name, 'path': path})
            # Optionally, check image dimensions
            width, height = check_image_dimensions(cache_path)
            if width and height:
                logger.info(f"Downloaded image: {width}x{height} pixels")
                print(f"    Downloaded image: {width}x{height} pixels")
                if width >= 1080 or height >= 1080:
                    print(f"    ✓ High resolution image downloaded")
                elif width >= 640 or height >= 640:
                    print(f"    ⚠ Medium resolution image downloaded")
                else:
                    print(f"    ⚠ Low resolution image downloaded")
            # Add a short delay to avoid rate-limiting
            time.sleep(1)
        print(f"\nSummary:")
        print(f"  Cached images: {cached_images}")
        print(f"  Skipped (already cached): {skipped_images}")
        print(f"  Failed downloads: {failed_images}")
        if failed_downloads:
            print("  Failed URLs:")
            for fail in failed_downloads:
                print(f"    {fail['url']} ({fail['name']}, {fail['path']})")
        # Save failed downloads to a JSON file
        failed_file = artwork_cache.cache_dir / "failed_downloads.json"
        with open(failed_file, 'w') as f:
            json.dump(failed_downloads, f, indent=2)
        logger.info("Artwork caching completed successfully")
    except LiturgicalCalendarError as e:
        logger.error(f"Liturgical Calendar Error: {e}")
        print(f"Liturgical Calendar Error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.exception(f"Error in cache_artwork_images: {e}")
        print(f"Error in cache_artwork_images: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if '--help' in sys.argv or '-h' in sys.argv:
        print("Usage: python cache_artwork_images.py [config.yaml] [--verbose]")
        print("  [config.yaml]  Optional path to config file")
        print("  --verbose      Enable verbose (DEBUG) logging output")
        sys.exit(0)
    main() 