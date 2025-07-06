"""
File system utilities for safe file operations with error handling.

This module provides utilities for:
- Disk space checking before file operations
- Safe file writing with cleanup on failure
- Permission and file system error handling
"""

import os
import shutil
from pathlib import Path
from typing import Callable, Optional, Union

from liturgical_calendar.logging import get_logger

logger = get_logger(__name__)


def check_disk_space(
    directory: Union[str, Path], required_bytes: int, min_free_mb: int = 10
) -> bool:
    """
    Check if there's sufficient disk space for a file operation.

    Args:
        directory: Directory to check disk space for
        required_bytes: Estimated bytes needed for the operation
        min_free_mb: Minimum free space in MB (default: 10MB)

    Returns:
        True if sufficient space is available

    Raises:
        OSError: If insufficient disk space
    """
    try:
        usage = shutil.disk_usage(str(directory))
        min_free_bytes = max(min_free_mb * 1024 * 1024, 2 * required_bytes)

        if usage.free < min_free_bytes:
            msg = (
                f"Insufficient disk space in {directory}: "
                f"{usage.free/1024/1024:.1f}MB free, need at least "
                f"{min_free_bytes/1024/1024:.1f}MB"
            )
            logger.error(msg)
            raise OSError(msg)

        logger.debug(f"Disk space check passed: {usage.free/1024/1024:.1f}MB free")
        return True

    except Exception as e:
        logger.error(f"Error checking disk space in {directory}: {e}")
        raise


def safe_write_file(
    file_path: Union[str, Path],
    write_func: Callable[[Path], None],
    estimated_size: int = 1024 * 1024,
    min_free_mb: int = 10,
) -> bool:
    """
    Safely write a file with error handling and cleanup.

    Args:
        file_path: Path where the file should be written
        write_func: Function that performs the actual write operation
        estimated_size: Estimated size of the file in bytes
        min_free_mb: Minimum free space in MB

    Returns:
        True if write was successful

    Raises:
        OSError: For file system errors
        Exception: For other errors during write
    """
    file_path = Path(file_path)
    temp_path = None

    try:
        # Ensure directory exists
        file_path.parent.mkdir(exist_ok=True, parents=True)

        # Check disk space
        check_disk_space(file_path.parent, estimated_size, min_free_mb)

        # Create temporary file with original extension preserved
        temp_path = file_path.with_name(f"{file_path.stem}.tmp{file_path.suffix}")

        # Perform the write operation
        write_func(temp_path)

        # Atomic move to final location
        temp_path.replace(file_path)

        logger.info(f"File written successfully: {file_path}")
        return True

    except (PermissionError, OSError) as e:
        logger.error(f"File system error writing {file_path}: {e}")
        _cleanup_partial_file(temp_path)
        raise OSError(f"File system error writing {file_path}: {e}") from e

    except Exception as e:
        logger.error(f"Error writing {file_path}: {e}")
        _cleanup_partial_file(temp_path)
        raise


def safe_save_image(
    image,
    file_path: Union[str, Path],
    quality: int = 95,
    estimated_size: Optional[int] = None,
) -> bool:
    """
    Safely save a PIL image with error handling.

    Args:
        image: PIL Image object to save
        file_path: Path where the image should be saved
        quality: JPEG quality (1-100)
        estimated_size: Estimated file size in bytes (auto-calculated if None)

    Returns:
        True if save was successful
    """
    file_path = Path(file_path)

    # Auto-calculate estimated size if not provided
    if estimated_size is None:
        width, height = image.size
        estimated_size = width * height * 3 + 1024 * 1024  # RGB + 1MB margin

    def write_image(temp_path):
        image.save(temp_path, quality=quality)

    return safe_write_file(file_path, write_image, estimated_size)


def _cleanup_partial_file(file_path: Optional[Path]) -> None:
    """
    Clean up a partial file if it exists.

    Args:
        file_path: Path to the file to clean up
    """
    if file_path and file_path.exists():
        try:
            file_path.unlink()
            logger.debug(f"Cleaned up partial file: {file_path}")
        except Exception as e:
            logger.error(f"Failed to cleanup partial file {file_path}: {e}")


def ensure_directory(
    directory: Union[str, Path], create_if_missing: bool = True
) -> Path:
    """
    Ensure a directory exists and is writable.

    Args:
        directory: Directory path to check/create
        create_if_missing: Whether to create the directory if it doesn't exist

    Returns:
        Path object for the directory

    Raises:
        OSError: If directory cannot be created or is not writable
    """
    directory = Path(directory)

    if not directory.exists():
        if create_if_missing:
            try:
                directory.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created directory: {directory}")
            except Exception as e:
                logger.error(f"Cannot create directory {directory}: {e}")
                raise OSError(f"Cannot create directory {directory}: {e}") from e
        else:
            raise OSError(f"Directory does not exist: {directory}")

    # Check if directory is writable
    if not os.access(directory, os.W_OK):
        raise OSError(f"Directory is not writable: {directory}")

    return directory
