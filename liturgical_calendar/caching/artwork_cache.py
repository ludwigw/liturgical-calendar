import os
from pathlib import Path
import requests
from liturgical_calendar.funcs import get_cache_filename
from PIL import Image
import time
import shutil

# Import get_instagram_image_url from the script (or reimplement if needed)
def get_instagram_image_url(instagram_url):
    if 'instagram.com' in instagram_url:
        url = instagram_url.rstrip('/')
        return f"{url}/media?size=l"
    return None

class ArtworkCache:
    def __init__(self, cache_dir=None):
        self.cache_dir = Path(cache_dir) if cache_dir else Path("./cache")
        self.cache_dir.mkdir(exist_ok=True)
        self.original_dir = self.cache_dir / "original"
        self.original_dir.mkdir(exist_ok=True)

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
        try:
            session = requests.Session()
            headers = {
                'User-Agent': 'Mozilla/5.0',
                'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Sec-Fetch-Dest': 'image',
                'Sec-Fetch-Mode': 'no-cors',
                'Sec-Fetch-Site': 'cross-site',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache'
            }
            if original_instagram_url:
                headers['Referer'] = original_instagram_url
            session.headers.update(headers)
            response = session.get(image_url, timeout=30, stream=True)
            response.raise_for_status()
            with open(cache_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            # Validate as image
            try:
                with Image.open(cache_path) as img:
                    img.verify()  # PIL verifies file integrity
                # Reopen to get size (verify() leaves file closed)
                with Image.open(cache_path) as img:
                    width, height = img.size
                    if upsample and (width < 1080 or height < 1080):
                        # Archive the original file before upsampling
                        orig_backup = self.original_dir / cache_path.name
                        try:
                            shutil.move(str(cache_path), str(orig_backup))
                            with Image.open(orig_backup) as orig_img:
                                print(f"    Upsampling {cache_path.name} ({width}x{height}) to 1080x1080...")
                                upsampled = orig_img.convert('RGB').resize((1080, 1080), Image.LANCZOS)
                                upsampled.save(cache_path, quality=95)
                        except Exception as up_ex:
                            print(f"Error during upsampling or archival: {up_ex}")
                            # If upsampling fails, restore the original to cache (if possible)
                            if not cache_path.exists() and orig_backup.exists():
                                shutil.move(str(orig_backup), str(cache_path))
                            return False
                    elif upsample:
                        # Archive the original even if not upsampled
                        orig_backup = self.original_dir / cache_path.name
                        try:
                            shutil.copy2(str(cache_path), str(orig_backup))
                        except Exception as arch_ex:
                            print(f"Warning: Could not archive original image: {arch_ex}")
            except Exception as e:
                # Not a valid image, delete file
                print(f"Error: Downloaded file is not a valid image: {cache_path} ({e})")
                cache_path.unlink(missing_ok=True)
                return False
            return True
        except Exception as e:
            print(f"Error downloading image from {image_url}: {e}")
            if cache_path.exists():
                cache_path.unlink(missing_ok=True)
            return False

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