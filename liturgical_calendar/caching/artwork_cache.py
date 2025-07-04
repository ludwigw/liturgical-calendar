import os
from pathlib import Path
import requests
from liturgical_calendar.funcs import get_cache_filename
from PIL import Image
import time
import shutil
from .image_processor import ImageProcessor
from liturgical_calendar.config.settings import Settings

# Import get_instagram_image_url from the script (or reimplement if needed)
def get_instagram_image_url(instagram_url):
    if 'instagram.com' in instagram_url:
        url = instagram_url.rstrip('/')
        return f"{url}/media?size=l"
    return None

class ArtworkCache:
    def __init__(self, cache_dir=None):
        self.cache_dir = Path(cache_dir) if cache_dir else Path(Settings.CACHE_DIR)
        self.cache_dir.mkdir(exist_ok=True)
        self.original_dir = self.cache_dir / Settings.ORIGINALS_SUBDIR
        self.original_dir.mkdir(exist_ok=True)
        self.processor = ImageProcessor()

    def get_cached_path(self, source_url):
        """Return the expected cache file path for a given source URL."""
        cache_filename = get_cache_filename(source_url)
        return self.cache_dir / cache_filename

    def is_cached(self, source_url):
        """Check if the image for the given source URL is already cached."""
        return self.get_cached_path(source_url).exists()

    def download_and_cache(self, source_url, original_instagram_url=None, upsample=True):
        """
        Download an image from the source URL and save it to the cache. Returns True if successful.
        - For Instagram URLs, use the direct image link.
        - After download, validate as image. If invalid, delete and return False.
        - Optionally upsample to 1080x1080 if smaller, archiving the original first.
        """
        cache_path = self.get_cached_path(source_url)
        if cache_path.exists():
            return True
        # Instagram direct image URL logic
        image_url = source_url
        if 'instagram.com' in source_url:
            direct_url = get_instagram_image_url(source_url)
            if direct_url:
                image_url = direct_url
        # Download
        headers = None
        referer = original_instagram_url if original_instagram_url else None
        if not self.processor.download_image(image_url, cache_path, headers, referer):
            return False
        # Validate
        if not self.processor.validate_image(cache_path):
            return False
        # Upsample if needed
        if upsample:
            try:
                with Image.open(cache_path) as img:
                    width, height = img.size
                if width < 1080 or height < 1080:
                    # Archive original
                    archived = self.processor.archive_original(cache_path, self.original_dir)
                    if not archived:
                        print(f"Warning: Could not archive original image before upsampling: {cache_path}")
                        return False
                    # Upsample
                    orig_backup = self.original_dir / cache_path.name
                    if not self.processor.upsample_image(orig_backup, cache_path, (1080, 1080)):
                        print(f"Error: Upsampling failed for {orig_backup}")
                        return False
                else:
                    # Archive even if not upsampled
                    self.processor.archive_original(cache_path, self.original_dir)
                    # Restore the file to the main cache path
                    archived_path = self.original_dir / cache_path.name
                    shutil.copy2(str(archived_path), str(cache_path))
            except Exception as e:
                print(f"Error during upsampling/archive: {e}")
                return False
        return True

    def get_cache_info(self, source_url):
        """Return info about the cached file (size, modified time, dimensions if image)."""
        cache_path = self.get_cached_path(source_url)
        if not cache_path.exists():
            return None
        info = {
            'path': str(cache_path),
            'size': cache_path.stat().st_size,
            'modified': time.ctime(cache_path.stat().st_mtime),
        }
        try:
            with Image.open(cache_path) as img:
                info['dimensions'] = img.size
        except Exception:
            info['dimensions'] = None
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
        return removed 