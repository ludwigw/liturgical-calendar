"""
Image service for orchestrating image generation operations.

This service layer handles the coordination between artwork selection,
image generation, and output formatting. It provides a clean interface
for generating liturgical calendar images.
"""

import os
from typing import Any, Dict, List, Optional

from liturgical_calendar.exceptions import ImageGenerationError
from liturgical_calendar.logging import get_logger

from ..core.artwork_manager import ArtworkManager
from ..core.readings_manager import ReadingsManager
from ..core.season_calculator import SeasonCalculator
from ..services.feast_service import FeastService


class ImageService:
    """
    Service for managing image generation operations and business logic.

    This service orchestrates the interaction between different components
    (ArtworkManager, ReadingsManager, FeastService) to provide a clean
    interface for image generation.
    """

    def __init__(
        self,
        artwork_manager: Optional[ArtworkManager] = None,
        readings_manager: Optional[ReadingsManager] = None,
        season_calculator: Optional[SeasonCalculator] = None,
        feast_service: Optional[FeastService] = None,
        config: Optional[Any] = None,
    ):
        """
        Initialize the ImageService.

        Args:
            artwork_manager: Optional ArtworkManager instance for dependency injection
            readings_manager: Optional ReadingsManager instance for dependency injection
            season_calculator: Optional SeasonCalculator instance for dependency injection
            feast_service: Optional FeastService instance for dependency injection
            config: Optional configuration object for the pipeline
        """
        self.config = config
        self.artwork_manager = artwork_manager or ArtworkManager(config=config)
        self.readings_manager = readings_manager or ReadingsManager()
        self.season_calculator = season_calculator or SeasonCalculator()
        self.feast_service = feast_service or FeastService(
            season_calculator=self.season_calculator,
            readings_manager=self.readings_manager,
        )
        self.pipeline = None  # Will be initialized lazily when needed
        self.logger = get_logger(__name__)

    def generate_liturgical_image(
        self,
        date_str: str,
        output_path: Optional[str] = None,
        transferred: bool = False,
    ) -> Dict[str, Any]:
        """
        Generate a complete liturgical calendar image for a given date.

        This is the main entry point that orchestrates all image generation operations.

        Args:
            date_str: Date string in YYYY-MM-DD format
            output_path: Optional path for saving the generated image
            transferred: Whether to check for transferred feasts

        Returns:
            Dictionary containing image generation results and metadata
        """
        # Get complete feast information
        feast_info = self.feast_service.get_complete_feast_info(date_str, transferred)

        if not feast_info:
            raise ValueError(f"No feast information found for date: {date_str}")

        # Select appropriate artwork
        artwork_info = self._select_artwork(feast_info)

        # Prepare image generation data
        image_data = self._prepare_image_data(feast_info, artwork_info)

        # Generate the image
        result = self._generate_image(image_data, output_path)

        # Add metadata
        result.update(
            {
                "date": date_str,
                "feast_info": feast_info,
                "artwork_info": artwork_info,
                "success": True,
            }
        )

        return result

    def generate_multiple_images(
        self,
        date_list: List[str],
        output_dir: Optional[str] = None,
        transferred: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Generate multiple liturgical calendar images for a list of dates.

        Args:
            date_list: List of date strings in YYYY-MM-DD format
            output_dir: Optional directory for saving generated images
            transferred: Whether to check for transferred feasts

        Returns:
            List of dictionaries containing image generation results
        """
        results = []

        for date_str in date_list:
            try:
                output_path = None
                if output_dir:
                    output_path = os.path.join(output_dir, f"liturgical_{date_str}.png")
                self.logger.info("Generating image for %s", date_str)
                result = self.generate_liturgical_image(
                    date_str, output_path, transferred
                )
                if result.get("success"):
                    self.logger.info(
                        "Image generated successfully: %s", result.get("file_path")
                    )
                else:
                    self.logger.error(
                        "Image generation failed for %s: %s",
                        date_str,
                        result.get("error", "Unknown error"),
                    )
                results.append(result)
            except (OSError, ValueError, TypeError, RuntimeError) as e:
                self.logger.error("Image generation error for %s: %s", date_str, e)
                results.append({"date": date_str, "success": False, "error": str(e)})

        return results

    def _select_artwork(self, feast_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Select appropriate artwork for the feast.

        Args:
            feast_info: Complete feast information

        Returns:
            Artwork information dictionary
        """
        # Extract date from feast_info
        date_obj = feast_info.get("date")
        if not date_obj:
            # If no date in feast_info, we can't get artwork
            return {}

        date_str = date_obj.strftime("%Y-%m-%d")

        # Use the artwork manager to select artwork for the date
        artwork = self.artwork_manager.get_artwork_for_date(date_str)

        if not artwork:
            # Return empty dict as fallback
            artwork = {}

        return artwork

    def _prepare_image_data(
        self, feast_info: Dict[str, Any], artwork_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Prepare data for image generation.

        Args:
            feast_info: Complete feast information
            artwork_info: Selected artwork information

        Returns:
            Prepared data for image generation
        """
        # Create a combined data structure that includes both feast and artwork info
        # Prioritize artwork name over feast name (same logic as pipeline)
        artwork_name = artwork_info.get("name", "") if artwork_info else ""
        feast_name = feast_info.get("name", "")

        # Use artwork name if available, otherwise fall back to feast name
        primary_name = artwork_name if artwork_name else feast_name

        image_data = {
            # Feast information
            "name": primary_name,  # Now uses artwork-prioritized name
            "season": feast_info.get("season", ""),
            "week": feast_info.get("week", ""),
            "weekno": feast_info.get("weekno"),
            "colour": feast_info.get("colour", "green"),
            "colourcode": feast_info.get("colourcode", "#00FF00"),
            "readings": feast_info.get("readings", {}),
            "date": feast_info.get("date"),
            "weekday_reading": feast_info.get("weekday_reading", ""),
            # Artwork information (for pipeline compatibility)
            "artwork_info": artwork_info,
            "url": artwork_info.get("url", ""),
            "title": artwork_info.get("title", ""),
            "artist": artwork_info.get("artist", ""),
            "cached_file": artwork_info.get("cached_file", ""),
            "artwork_name": artwork_info.get(
                "name", ""
            ),  # Artwork name (renamed to avoid conflict)
        }

        # Add any additional metadata
        if feast_info.get("martyr"):
            image_data["martyr"] = True

        if feast_info.get("type"):
            image_data["feast_type"] = feast_info.get("type")

        return image_data

    def _generate_image(
        self, image_data: Dict[str, Any], output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        # Delayed import to avoid circular dependency with pipeline.py
        # noqa: E402
        # pylint: disable=import-outside-toplevel
        from liturgical_calendar.image_generation.pipeline import (
            ImageGenerationPipeline,
        )

        if not self.config:
            self.logger.error(
                "ImageService requires a configuration object to initialize the pipeline"
            )
            raise ImageGenerationError(
                "ImageService requires a configuration object to initialize the pipeline"
            )

        # Initialize pipeline if not already done
        if self.pipeline is None:
            self.pipeline = ImageGenerationPipeline(self.config)

        # Extract date from image_data
        date_obj = image_data.get("date")
        if not date_obj:
            self.logger.error("No date found in image_data")
            raise ImageGenerationError("No date found in image_data")

        date_str = date_obj.strftime("%Y-%m-%d")

        # Use the pipeline to generate the image
        try:
            # Pass the prepared feast and artwork info to the pipeline
            feast_info = image_data
            artwork_info = image_data.get("artwork_info", {})
            self.logger.info("Starting image generation for %s", date_str)
            file_path = self.pipeline.generate_image(
                date_str, output_path, feast_info, artwork_info
            )
            result = {
                "image_generated": True,
                "image_data": image_data,
                "file_path": str(file_path),
            }
            self.logger.info("Image generated successfully: %s", file_path)
        except Exception as e:
            self.logger.exception("Error generating image for %s: %s", date_str, e)
            raise ImageGenerationError(f"Error generating image: {e}") from e

        return result

    def validate_image_data(self, image_data: Dict[str, Any]) -> bool:
        """
        Validate that image data has required fields.

        Args:
            image_data: The image data to validate

        Returns:
            True if valid, False otherwise
        """
        required_fields = ["name", "season", "colour"]
        return all(field in image_data for field in required_fields)

    def get_image_generation_stats(
        self, results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Get statistics about image generation results.

        Args:
            results: List of image generation results

        Returns:
            Statistics dictionary
        """
        total = len(results)
        successful = sum(1 for r in results if r.get("success", False))
        failed = total - successful

        # Count by season
        season_counts = {}
        for result in results:
            if result.get("success") and "feast_info" in result:
                season = result["feast_info"].get("season", "Unknown")
                season_counts[season] = season_counts.get(season, 0) + 1

        # Count by color
        color_counts = {}
        for result in results:
            if result.get("success") and "feast_info" in result:
                color = result["feast_info"].get("colour", "Unknown")
                color_counts[color] = color_counts.get(color, 0) + 1

        return {
            "total": total,
            "successful": successful,
            "failed": failed,
            "success_rate": successful / total if total > 0 else 0,
            "season_counts": season_counts,
            "color_counts": color_counts,
        }

    def determine_color(
        self, result: dict, season: str, christmas_point: int, advent_sunday: int
    ) -> str:
        """
        Determine the liturgical color for the given result and season.
        Implements the color logic from the main function.
        """
        # Support for special Sundays which are rose
        if result.get("name") in ["Advent 3", "Lent 4"]:
            return "rose"
        # If no color is already set...
        if result.get("colour") is None:
            # If the priority is higher than a Lesser Festival, but not a Sunday...
            if result.get("prec", 0) > 4 and result.get("prec", 0) != 5:
                # It's a feast day.
                # Feasts are generally white, unless marked differently.
                # But martyrs are red
                if result.get("martyr"):
                    return "red"
                return "white"
            # Not a feast day.
            # Set a default color for the season
            if season == "Advent":
                return "purple"
            if season == "Christmas":
                return "white"
            if season == "Epiphany":
                return "white"
            if season == "Lent":
                return "purple"
            if season == "Holy Week":
                return "red"
            if season == "Easter":
                return "white"
            # The great fallback:
            return "green"
        # Two special cases for Christmas-based festivals which depend on the day of the week.
        if result.get("prec") == 5:  # An ordinary Sunday
            if christmas_point == advent_sunday:
                return "white"  # Advent Sunday
            if christmas_point == advent_sunday - 7:
                return "white"  # Christ the King
        return result.get("colour", "green")

    def get_artwork_for_date(
        self, date_str: str, feast_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get artwork for a given date.

        This method provides the same interface as the ArtworkManager.get_artwork_for_date method,
        making it easy to migrate existing code to use the service layer.

        Args:
            date_str: Date string in YYYY-MM-DD format
            feast_info: Optional feast information (if not provided, will be fetched)

        Returns:
            Artwork information dictionary
        """
        if feast_info is None:
            feast_info = self.feast_service.get_complete_feast_info(date_str)

        return self.artwork_manager.get_artwork_for_date(date_str, feast_info)
