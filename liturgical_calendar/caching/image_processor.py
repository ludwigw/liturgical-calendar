"""
Image processing utilities for the liturgical calendar project.
"""

import shutil
import time
from pathlib import Path
from typing import Optional

import requests
from PIL import Image
from PIL.Image import Resampling

from liturgical_calendar.config.settings import Settings
from liturgical_calendar.exceptions import (
    ArtworkNotFoundError,
    CacheError,
    ImageGenerationError,
)
from liturgical_calendar.logging import get_logger
from liturgical_calendar.utils.file_system import safe_save_image


class ImageProcessor:
    """Processes images for caching and use in the liturgical calendar."""

    def __init__(self, config=None):
        self.config = config
        self.logger = get_logger(__name__)

    def download_image(
        self,
        url: str,
        cache_path: Path,
        headers: Optional[dict] = None,
        referer: Optional[str] = None,
        max_retries: int = 3,
        retry_delay: float = 5.0,
    ) -> None:
        """
        Download an image from a URL to the given cache path with retry logic.
        Optionally set headers and referer for the request.
        Raises CacheError on failure.
        """
        for attempt in range(max_retries):
            try:
                session = requests.Session()
                req_headers = headers or {
                    "User-Agent": Settings.USER_AGENT,
                    "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.9",
                    "Accept-Encoding": "gzip, deflate, br",
                    "DNT": "1",
                    "Connection": "keep-alive",
                    "Sec-Fetch-Dest": "image",
                    "Sec-Fetch-Mode": "no-cors",
                    "Sec-Fetch-Site": "cross-site",
                    "Cache-Control": "no-cache",
                    "Pragma": "no-cache",
                }
                if referer:
                    req_headers["Referer"] = referer
                session.headers.update(req_headers)
                response = session.get(
                    url, timeout=Settings.REQUEST_TIMEOUT, stream=True
                )
                response.raise_for_status()
                with open(cache_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                self.logger.info("Image downloaded successfully: %s", cache_path)
                return

            except requests.ConnectionError as e:
                if attempt < max_retries - 1:
                    delay = retry_delay * (2**attempt)  # Exponential backoff
                    self.logger.warning(
                        "Network connection error (attempt %s/%s) for %s: %s",
                        attempt + 1,
                        max_retries,
                        url,
                        e,
                    )
                    self.logger.info("Retrying in %.1f seconds...", delay)
                    time.sleep(delay)
                    continue
                self.logger.error(
                    "Failed to download %s after %s attempts due to connection error: %s",
                    url,
                    max_retries,
                    e,
                )
                if cache_path.exists():
                    cache_path.unlink(missing_ok=True)
                raise CacheError(
                    f"Network connection failed after {max_retries} attempts: {e}"
                ) from e

            except requests.Timeout as e:
                if attempt < max_retries - 1:
                    delay = retry_delay * (2**attempt)  # Exponential backoff
                    self.logger.warning(
                        "Request timeout (attempt %s/%s) for %s: %s",
                        attempt + 1,
                        max_retries,
                        url,
                        e,
                    )
                    self.logger.info("Retrying in %.1f seconds...", delay)
                    time.sleep(delay)
                    continue
                self.logger.error(
                    "Failed to download %s after %s attempts due to timeout: %s",
                    url,
                    max_retries,
                    e,
                )
                if cache_path.exists():
                    cache_path.unlink(missing_ok=True)
                raise CacheError(
                    f"Request timeout after {max_retries} attempts: {e}"
                ) from e

            except requests.HTTPError as e:
                # Don't retry HTTP errors (4xx, 5xx) as they're likely permanent
                self.logger.error("HTTP error downloading %s: %s", url, e)
                if cache_path.exists():
                    cache_path.unlink(missing_ok=True)
                raise CacheError(f"HTTP error downloading {url}: {e}") from e

            except Exception as e:
                if attempt < max_retries - 1:
                    delay = retry_delay * (2**attempt)  # Exponential backoff
                    self.logger.warning(
                        "Unexpected error (attempt %s/%s) for %s: %s",
                        attempt + 1,
                        max_retries,
                        url,
                        e,
                    )
                    self.logger.info("Retrying in %.1f seconds...", delay)
                    time.sleep(delay)
                    continue
                self.logger.error(
                    "Failed to download %s after %s attempts due to unexpected error: %s",
                    url,
                    max_retries,
                    e,
                )
                if cache_path.exists():
                    cache_path.unlink(missing_ok=True)
                raise CacheError(f"Unexpected error downloading {url}: {e}") from e

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
            self.logger.info("Image validated successfully: %s", image_path)
            return True
        except Exception as e:
            image_path.unlink(missing_ok=True)
            self.logger.error("File is not a valid image: %s (%s)", image_path, e)
            raise ArtworkNotFoundError(
                f"File is not a valid image: {image_path} ({e})"
            ) from e

    def upsample_image(
        self, original_path: Path, target_path: Path, target_size=None
    ) -> bool:
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
                    self.logger.info(
                        "Upsampling %s (%sx%s) to %sx%s",
                        original_path.name,
                        width,
                        height,
                        target_size[0],
                        target_size[1],
                    )
                    upsampled = img.convert("RGB").resize(
                        target_size, Resampling.LANCZOS
                    )
                    safe_save_image(upsampled, target_path, quality=95)
                    self.logger.info("Image upsampled successfully: %s", target_path)
                    return True
                # No upsampling needed, just copy
                shutil.copy2(str(original_path), str(target_path))
                return False
        except Exception as e:
            self.logger.error("Error during upsampling: %s", e)
            raise ImageGenerationError(f"Error during upsampling: {e}") from e

    def archive_original(self, image_path: Path, archive_dir: Path) -> bool:
        """
        Move or copy the original image to the archive_dir before upsampling or modification.
        Returns True if archived successfully, raises CacheError on failure.
        """
        try:
            archive_dir.mkdir(exist_ok=True, parents=True)
            archive_path = archive_dir / image_path.name
            shutil.move(str(image_path), str(archive_path))
            self.logger.info("Archived original image: %s", archive_path)
            return True
        except Exception as e:
            self.logger.error("Error archiving original image: %s", e)
            raise CacheError(f"Error archiving original image: {e}") from e
