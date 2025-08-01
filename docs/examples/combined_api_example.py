"""
Example demonstrating the new combined feast and artwork API.

This example shows how to use the get_liturgical_info_with_artwork function
to get combined feast and artwork data with artwork names prioritized over
feast names when available.
"""

from liturgical_calendar.liturgical import get_liturgical_info_with_artwork


def main():
    """Demonstrate the combined API functionality."""

    # Example dates to test
    test_dates = [
        "2024-12-25",  # Christmas Day
        "2024-10-31",  # Halloween/Reformation Day
        "2024-01-15",  # Regular weekday
    ]

    print("Combined Feast and Artwork API Example")
    print("=" * 50)

    for date_str in test_dates:
        print(f"\nDate: {date_str}")

        # Get combined feast and artwork information
        result = get_liturgical_info_with_artwork(date_str)

        print(f"  Name: {result.get('name', 'Unknown')}")
        print(f"  Season: {result.get('season', 'Unknown')}")
        print(f"  Week: {result.get('week', 'Unknown')}")
        print(f"  Colour: {result.get('colour', 'Unknown')}")

        # Show artwork information if available
        artwork = result.get("artwork")
        if artwork:
            print(f"  Artwork: {artwork.get('name', 'No name')}")
            if artwork.get("source"):
                print(f"    Source: {artwork['source']}")
            if artwork.get("url"):
                print(f"    URL: {artwork['url']}")
        else:
            print("  Artwork: None")

        print("-" * 30)


if __name__ == "__main__":
    main()
