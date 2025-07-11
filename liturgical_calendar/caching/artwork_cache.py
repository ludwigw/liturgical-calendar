"""
Artwork caching utilities for the liturgical calendar project.
"""

import shutil
import time
from pathlib import Path

from PIL import Image

from liturgical_calendar.config.settings import Settings
from liturgical_calendar.exceptions import (
    ArtworkNotFoundError,
    CacheError,
    ImageGenerationError,
)
from liturgical_calendar.funcs import get_cache_filename
from liturgical_calendar.logging import get_logger

from .image_processor import ImageProcessor


# Import get_instagram_image_url from the script (or reimplement if needed)
def get_instagram_image_url(instagram_url):
    """Convert an Instagram post URL to a direct image URL for downloading."""
    if "instagram.com" in instagram_url:
        url = instagram_url.rstrip("/")
        return f"{url}/media?size=l"
    return None


class ArtworkCache:
    """Caches and manages artwork images for the liturgical calendar."""

    def __init__(self, cache_dir=None):
        self.cache_dir = Path(cache_dir) if cache_dir else Path(Settings.CACHE_DIR)
        self.original_dir = self.cache_dir / Settings.ORIGINALS_SUBDIR
        self.processor = ImageProcessor()
        self.logger = get_logger(__name__)
        self.cache_dir.mkdir(exist_ok=True, parents=True)
        self.original_dir.mkdir(exist_ok=True, parents=True)

    def get_cached_path(self, source_url):
        """Return the expected cache file path for a given source URL."""
        cache_filename = get_cache_filename(source_url)
        return self.cache_dir / cache_filename

    def is_cached(self, source_url):
        """Check if the image for the given source URL is already cached."""
        return self.get_cached_path(source_url).exists()

    def download_and_cache(
        self,
        source_url,
        _original_instagram_url=None,
        upsample=True,
        max_retries=3,
        retry_delay=5.0,
    ):
        """
        Download an image from the source URL and save it to the cache. Returns True if successful.
        - For Instagram URLs, use the direct image link.
        - After download, validate as image. If invalid, delete and return False.
        - Optionally upsample to 1080x1080 if smaller, archiving the original first.
        - Includes retry logic for network failures.
        """
        cache_path = self.get_cached_path(source_url)

        # Check if already cached
        if cache_path.exists():
            self.logger.info(
                "Image already cached for %s, skipping download", source_url
            )
            return True

        # Convert Instagram URLs to direct image URLs
        download_url = source_url
        if "instagram.com" in source_url:
            direct_url = get_instagram_image_url(source_url)
            if direct_url:
                download_url = direct_url
                self.logger.info(
                    "Converting Instagram URL to direct image URL: %s -> %s",
                    source_url,
                    download_url,
                )
            else:
                self.logger.warning(
                    "Could not convert Instagram URL to direct image URL: %s",
                    source_url,
                )

        try:
            # Use retry logic from ImageProcessor
            self.processor.download_image(
                download_url,
                cache_path,
                max_retries=max_retries,
                retry_delay=retry_delay,
            )
            if upsample:
                with Image.open(cache_path) as img:
                    width, height = img.size
                if width < 1080 or height < 1080:
                    archived = self.processor.archive_original(
                        cache_path, self.original_dir
                    )
                    if not archived:
                        self.logger.error(
                            "Could not archive original image before upsampling: %s",
                            cache_path,
                        )
                        raise CacheError(
                            f"Could not archive original image before upsampling: {cache_path}"
                        )
                    orig_backup = self.original_dir / cache_path.name
                    self.processor.upsample_image(orig_backup, cache_path, (1080, 1080))
                else:
                    self.processor.archive_original(cache_path, self.original_dir)
                    archived_path = self.original_dir / cache_path.name
                    shutil.copy2(str(archived_path), str(cache_path))
            self.logger.info("Cache saved for key: %s", source_url)
            return True
        except (CacheError, ArtworkNotFoundError, ImageGenerationError) as e:
            self.logger.error("Download/cache error for %s: %s", source_url, e)
            return False
        except (OSError, ValueError, TypeError) as e:
            self.logger.exception(
                "Unexpected error in download_and_cache for %s: %s", source_url, e
            )
            raise CacheError(f"Unexpected error in download_and_cache: {e}") from e

    def get_cache_info(self, source_url):
        """Return info about the cached file (size, modified time, dimensions if image)."""
        cache_path = self.get_cached_path(source_url)
        if not cache_path.exists():
            return None
        info = {
            "path": str(cache_path),
            "size": cache_path.stat().st_size,
            "modified": time.ctime(cache_path.stat().st_mtime),
        }
        try:
            with Image.open(cache_path) as img:
                info["dimensions"] = img.size
        except (OSError, ValueError, TypeError):
            info["dimensions"] = None
        return info

    def cleanup_old_cache(self, max_age_days=30):
        """Remove cached files older than max_age_days."""
        now = time.time()
        removed = []
        for file in self.cache_dir.iterdir():
            if file.is_file():
                age_days = (now - file.stat().st_mtime) / 86400
                if age_days > max_age_days:
                    file.unlink()
                    removed.append(str(file))
        self.logger.info("Removed %s old cache files", len(removed))
        return removed

    def cache_multiple_artwork(self, source_urls, max_retries=3, retry_delay=5.0):
        """
        Cache multiple artwork URLs and return success/failure counts for monitoring.

        Args:
            source_urls: List of source URLs to cache
            max_retries: Maximum number of retry attempts for each download
            retry_delay: Base delay between retries (exponential backoff)

        Returns:
            dict: {'success': int, 'failed': int, 'total': int, 'failed_urls': list}
        """
        total = len(source_urls)
        success_count = 0
        failed_count = 0
        failed_urls = []

        self.logger.info("Starting batch cache operation for %s artwork items", total)

        for i, url in enumerate(source_urls, 1):
            self.logger.info("Processing artwork %s/%s: %s", i, total, url)
            try:
                success = self.download_and_cache(
                    url, max_retries=max_retries, retry_delay=retry_delay
                )
                if success:
                    success_count += 1
                    self.logger.info("Successfully cached artwork %s/%s", i, total)
                else:
                    failed_count += 1
                    failed_urls.append(url)
                    self.logger.warning(
                        "Failed to cache artwork %s/%s: %s", i, total, url
                    )
            except (OSError, ValueError, TypeError) as e:
                failed_count += 1
                failed_urls.append(url)
                self.logger.error(
                    "Exception while caching artwork %s/%s: %s - %s", i, total, url, e
                )

        result = {
            "success": success_count,
            "failed": failed_count,
            "total": total,
            "failed_urls": failed_urls,
        }

        self.logger.info(
            "Batch cache operation completed: %s successful, %s failed out of %s total",
            success_count,
            failed_count,
            total,
        )
        return result
