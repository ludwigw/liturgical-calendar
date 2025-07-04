import requests
from PIL import Image
import shutil
import os

from pathlib import Path
from typing import Optional
from liturgical_calendar.config.settings import Settings
from liturgical_calendar.exceptions import (
    ArtworkNotFoundError, ImageGenerationError, CacheError
)
from liturgical_calendar.logging import get_logger

class ImageProcessor:
    """
    Handles low-level image file operations: download, validation, upsampling, and archiving.
    """

    def __init__(self, config=None):
        self.config = config
        self.logger = get_logger(__name__)

    def download_image(self, url: str, cache_path: Path, headers: Optional[dict] = None, referer: Optional[str] = None) -> bool:
        """
        Download an image from a URL to the given cache path.
        Optionally set headers and referer for the request.
        Returns True if successful, raises CacheError on failure.
        """
        try:
            session = requests.Session()
            req_headers = headers or {
                'User-Agent': Settings.USER_AGENT,
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
            if referer:
                req_headers['Referer'] = referer
            session.headers.update(req_headers)
            response = session.get(url, timeout=Settings.REQUEST_TIMEOUT, stream=True)
            response.raise_for_status()
            with open(cache_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            self.logger.info(f"Image downloaded successfully: {cache_path}")
            return True
        except Exception as e:
            if cache_path.exists():
                cache_path.unlink(missing_ok=True)
            self.logger.error(f"Error downloading image from {url}: {e}")
            raise CacheError(f"Error downloading image from {url}: {e}")

    def validate_image(self, image_path: Path) -> bool:
        """
        Validate that the file at image_path is a valid image (using PIL or similar).
        Returns True if valid, raises ArtworkNotFoundError on failure.
        """
        try:
            with Image.open(image_path) as img:
                img.verify()  # PIL verifies file integrity
            # Reopen to get size (verify() leaves file closed)
            with Image.open(image_path) as img:
                _ = img.size
            self.logger.info(f"Image validated successfully: {image_path}")
            return True
        except Exception as e:
            image_path.unlink(missing_ok=True)
            self.logger.error(f"File is not a valid image: {image_path} ({e})")
            raise ArtworkNotFoundError(f"File is not a valid image: {image_path} ({e})")

    def upsample_image(self, original_path: Path, target_path: Path, target_size=None) -> bool:
        """
        Upsample the image at original_path to target_size and save to target_path.
        Returns True if upsampling was performed, raises ImageGenerationError on failure.
        """
        if target_size is None:
            target_size = (Settings.ARTWORK_SIZE, Settings.ARTWORK_SIZE)
        try:
            with Image.open(original_path) as img:
                width, height = img.size
                if width < target_size[0] or height < target_size[1]:
                    self.logger.info(f"Upsampling {original_path.name} ({width}x{height}) to {target_size[0]}x{target_size[1]}")
                    upsampled = img.convert('RGB').resize(target_size, Image.LANCZOS)
                    upsampled.save(target_path, quality=95)
                    self.logger.info(f"Image upsampled successfully: {target_path}")
                    return True
                else:
                    # No upsampling needed, just copy
                    shutil.copy2(str(original_path), str(target_path))
                    return False
        except Exception as e:
            self.logger.error(f"Error during upsampling: {e}")
            raise ImageGenerationError(f"Error during upsampling: {e}")

    def archive_original(self, image_path: Path, archive_dir: Path) -> bool:
        """
        Move or copy the original image to the archive_dir before upsampling or modification.
        Returns True if archived successfully, raises CacheError on failure.
        """
        try:
            archive_dir.mkdir(exist_ok=True, parents=True)
            archive_path = archive_dir / image_path.name
            shutil.move(str(image_path), str(archive_path))
            self.logger.info(f"Archived original image: {archive_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error archiving original image: {e}")
            raise CacheError(f"Error archiving original image: {e}")

    def process_image(self, image_path, output_path, options=None):
        try:
            self.logger.info(f"Processing image: {image_path}")
            # ... existing logic ...
            self.logger.info(f"Image processed successfully: {output_path}")
        except Exception as e:
            self.logger.exception(f"Error processing image {image_path}: {e}")
            raise 