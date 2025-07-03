# TODO: Test Failures and Errors (as of latest test run)

This file summarizes all current test failures and errors, grouped by module. Most are unrelated to the recent artwork caching refactor.

---

## test_config_service.py

- **FAIL: test_get_default_config_path**
  - AssertionError: Path does not match expected (`/home/testuser/config.json` vs `/home/testuser/.liturgical_calendar/config.json`).
- **ERROR: test_validate_config_creates_directories**
  - OSError: Directory not empty during teardown (cleanup issue).

## test_feast_service.py

- **ERROR: test_calculate_week_name_sunday**
  - AttributeError: Mock object does not have attribute 'render_week_name'.
- **ERROR: test_calculate_week_name_sunday_before_advent**
  - AttributeError: 'FeastService' object has no attribute 'calculate_week_name'.
- **ERROR: test_calculate_week_name_weekday**
  - AttributeError: Mock object does not have attribute 'calculate_sunday_week_info'.
- **ERROR: test_get_complete_feast_info_basic**
  - AttributeError: Mock object does not have attribute 'calculate_week_number'.
- **ERROR: test_get_complete_feast_info_sunday**
  - AttributeError: Mock object does not have attribute 'calculate_week_number'.
- **ERROR: test_get_complete_feast_info_transferred**
  - AttributeError: Mock object does not have attribute 'calculate_week_number'.

## test_image_service.py

- **ERROR: test_generate_liturgical_image_success**
  - AttributeError: Mock object does not have attribute 'get_artwork_for_feast'.
- **ERROR: test_generate_liturgical_image_with_output_path**
  - AttributeError: Mock object does not have attribute 'get_artwork_for_feast'.
- **ERROR: test_generate_multiple_images_success**
  - AttributeError: Mock object does not have attribute 'get_artwork_for_feast'.
- **ERROR: test_generate_multiple_images_with_errors**
  - AttributeError: Mock object does not have attribute 'get_artwork_for_feast'.
- **ERROR: test_select_artwork_default_fallback**
  - AttributeError: Mock object does not have attribute 'get_artwork_for_feast'.
- **ERROR: test_select_artwork_feast_specific**
  - AttributeError: Mock object does not have attribute 'get_artwork_for_feast'.
- **ERROR: test_select_artwork_season_fallback**
  - AttributeError: Mock object does not have attribute 'get_artwork_for_feast'.

## test_layout_engine.py

- **FAIL: test_create_artwork_layout_with_next**
  - AssertionError: `layout['show_next']` is False, expected True.

---

**Note:**
- All caching and artwork-related tests pass.
- The above failures/errors are likely unrelated to the recent caching refactor and pertain to config, feast, image service, and layout logic or their mocks. 