# TODO: Test Failures and Errors (as of latest test run)

This file summarizes all current test failures and errors, grouped by module. Most are unrelated to the recent artwork caching refactor.

---

## ✅ COMPLETED: test_feast_service.py

**Status: FIXED** - All FeastService test failures have been resolved:
- Fixed Sunday naming regression (now uses week name like "Easter 2" instead of just "Easter")
- Updated mocks to match current SeasonCalculator API
- Fixed Sunday detection bug (dayofweek == 0)
- All FeastService unit tests now pass

## ✅ COMPLETED: test_image_service.py

**Status: FIXED** - All ImageService test failures have been resolved:
- Fixed method signature mismatch: updated ImageService to use correct ArtworkManager methods
- Updated `_select_artwork` method to use `get_artwork_for_date(date_str, feast_info)` instead of non-existent methods
- Updated unit tests to match actual method signatures and simplified fallback logic
- All ImageService unit tests now pass

---

## test_config_service.py

- **FAIL: test_get_default_config_path**
  - AssertionError: Path does not match expected (`/home/testuser/config.json` vs `/home/testuser/.liturgical_calendar/config.json`).
- **ERROR: test_validate_config_creates_directories**
  - OSError: Directory not empty during teardown (cleanup issue).



## test_layout_engine.py

- **FAIL: test_create_artwork_layout_with_next**
  - AssertionError: `layout['show_next']` is False, expected True.

---

**Note:**
- All caching and artwork-related tests pass.
- FeastService tests have been fixed and now pass.
- ImageService tests have been fixed and now pass.
- Remaining failures/errors are likely unrelated to the recent caching refactor and pertain to config and layout logic or their mocks. 