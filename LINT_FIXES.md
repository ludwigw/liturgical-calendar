# Lint Fixes Plan

## Progress Update (Phase 1 Quick Fixes)
- [ ] **Final newlines:** All files except a few __init__.py files have final newlines. The following still need a final newline (C0305):
    - [ ] liturgical_calendar/__init__.py
    - [ ] liturgical_calendar/core/__init__.py
    - [ ] liturgical_calendar/config/__init__.py
    - [ ] liturgical_calendar/image_generation/__init__.py
- [x] **Import order:** All files have correct import order (isort run with black profile).
- [x] **Unused imports:** All unused imports removed (autoflake run with aggressive mode).
- [ ] **Next:** Address C0415 (import outside toplevel), docstrings, logging, exception handling, and other issues in Phase 2/3

## Overview
This document outlines the plan to fix all pylint issues identified in the GitHub Actions workflow. The goal is to achieve a clean pylint score and ensure consistent code quality.

## Current Status (Updated after black formatting)
- [x] **Tests**: All 42 tests pass
- [x] **Dependencies**: All packages install correctly and are up-to-date
- [x] **CLI**: All functionality works
- [x] **Code Formatting**: All files formatted with black
- [ ] **Pylint**: Multiple style and quality issues remain (score: 7.85/10)

## What Was Accomplished in Last Commit
- [x] **Black formatting**: All Python files reformatted with consistent style
- [x] **Dependency updates**: Upgraded Pillow, PyYAML, pylint, astroid, and black for Python 3.12+ compatibility
- [x] **Trailing newlines**: Many files got final newlines added automatically
- [x] **Some import order fixes**: Black may have fixed some import ordering issues

## Remaining Issue Categories and Fix Plan

### Phase 1: Quick Fixes (1-2 hours) - HIGH PRIORITY

#### 1.1 Missing Final Newlines (C0305) - PARTIALLY COMPLETE
- [ ] liturgical_calendar/__init__.py
- [ ] liturgical_calendar/core/__init__.py
- [ ] liturgical_calendar/config/__init__.py
- [ ] liturgical_calendar/image_generation/__init__.py
- [x] All other files have final newlines.

#### 1.2 Import Order (C0411) - COMPLETE
- [x] All files have correct import order (isort run with black profile).

#### 1.3 Unused Imports (W0611) - COMPLETE
- [x] All unused imports removed (autoflake run with aggressive mode).

### Phase 2: Medium Effort (3-4 hours) - MEDIUM PRIORITY

#### 2.1 Missing Docstrings (C0114, C0115, C0116)
- [ ] `liturgical_calendar/logging.py` - Add module docstring
- [ ] `liturgical_calendar/cli.py` - Add module, class, and function docstrings
- [ ] `liturgical_calendar/liturgical.py` - Add function docstring
- [ ] `liturgical_calendar/data/readings_data.py` - Add module docstring
- [ ] `liturgical_calendar/data/feasts_data.py` - Add module docstring
- [ ] `liturgical_calendar/data/artwork_data.py` - Add module docstring
- [ ] `liturgical_calendar/image_generation/layout_engine.py` - Add module docstring
- [ ] `liturgical_calendar/image_generation/pipeline.py` - Add module and class docstrings
- [ ] `liturgical_calendar/image_generation/font_manager.py` - Add module and class docstrings
- [ ] `liturgical_calendar/image_generation/image_builder.py` - Add module and class docstrings
- [ ] `liturgical_calendar/caching/artwork_cache.py` - Add module and function docstrings
- [ ] `liturgical_calendar/caching/image_processor.py` - Add module and function docstrings

#### 2.2 Logging F-string Issues (W1203)
- [ ] `liturgical_calendar/liturgical.py` - 2 instances
- [ ] `liturgical_calendar/cli.py` - 8 instances
- [ ] `liturgical_calendar/core/readings_manager.py` - 8 instances
- [ ] `liturgical_calendar/core/artwork_manager.py` - 6 instances
- [ ] `liturgical_calendar/image_generation/image_builder.py` - 8 instances
- [ ] `liturgical_calendar/image_generation/font_manager.py` - 3 instances
- [ ] `liturgical_calendar/image_generation/pipeline.py` - 6 instances
- [ ] `liturgical_calendar/utils/file_system.py` - 8 instances
- [ ] `liturgical_calendar/caching/image_processor.py` - 12 instances
- [ ] `liturgical_calendar/caching/artwork_cache.py` - 8 instances
- [ ] `liturgical_calendar/services/feast_service.py` - 8 instances
- [ ] `liturgical_calendar/services/image_service.py` - 4 instances
- [ ] `liturgical_calendar/services/config_service.py` - 4 instances

#### 2.3 Exception Handling (W0707, W0718)
- [ ] `liturgical_calendar/liturgical.py` - Use specific exceptions, add `from e`
- [ ] `liturgical_calendar/cli.py` - Use specific exceptions, add `from e`
- [ ] `liturgical_calendar/caching/artwork_cache.py` - Add `from e` to re-raises
- [ ] `liturgical_calendar/caching/image_processor.py` - Add `from e` to re-raises
- [ ] `liturgical_calendar/core/readings_manager.py` - Add `from e` to re-raises
- [ ] `liturgical_calendar/utils/file_system.py` - Add `from e` to re-raises
- [ ] `liturgical_calendar/services/config_service.py` - Add `from e` to re-raises
- [ ] `liturgical_calendar/services/image_service.py` - Add `from e` to re-raises

### Phase 3: Complex Refactoring (6-8 hours) - LOW PRIORITY

#### 3.1 Function Complexity (R0913, R0917, R1702)
- [ ] `liturgical_calendar/cli.py` - Reduce nested blocks (R1702)
- [ ] `liturgical_calendar/image_generation/layout_engine.py` - Reduce function arguments (R0913, R0917)
- [ ] `liturgical_calendar/image_generation/pipeline.py` - Reduce function arguments (R0913, R0917)
- [ ] `liturgical_calendar/image_generation/image_builder.py` - Reduce function arguments (R0913, R0917)
- [ ] `liturgical_calendar/caching/artwork_cache.py` - Reduce function arguments (R0913, R0917)
- [ ] `liturgical_calendar/caching/image_processor.py` - Reduce function arguments (R0913, R0917)
- [ ] `liturgical_calendar/services/image_service.py` - Reduce return statements (R0911)
- [ ] `liturgical_calendar/services/feast_service.py` - Reduce function arguments (R0913, R0917)
- [ ] `liturgical_calendar/core/season_calculator.py` - Reduce return statements (R0911)

#### 3.2 Code Duplication (R0801)
- [ ] Extract common season URL logic
- [ ] Extract common error handling patterns
- [ ] Extract common logging patterns

#### 3.3 Other Issues
- [ ] `liturgical_calendar/funcs.py` - Fix indentation issues (C0325)
- [ ] `liturgical_calendar/exceptions.py` - Remove unnecessary pass statements (W0107)
- [ ] `liturgical_calendar/data/feasts_data.py` - Fix duplicate dictionary key (W0109)
- [ ] `liturgical_calendar/config/settings.py` - Add encoding to file operations (W1514)
- [ ] `liturgical_calendar/liturgical.py` - Fix undefined variable (E0602)

## Implementation Strategy

### Step 1: Quick Fixes (Start Here)
- [x] Fix remaining missing final newlines
- [x] Fix import order issues
- [x] Remove unused imports

### Step 2: Test After Each Phase
- [ ] Run `pylint --rcfile=.pylintrc liturgical_calendar` after each phase
- [ ] Ensure tests still pass: `python -m unittest discover -s tests -p 'test*.py' -v`
- [ ] Commit changes after each phase

### Step 3: Gradual Improvement
- [ ] Focus on one category at a time
- [ ] Use manual fixes for complex issues
- [ ] Prioritize based on impact vs. effort

## Success Criteria
- [ ] Pylint score: 8.0+/10
- [x] All tests passing
- [ ] No critical issues (C, F, E categories)
- [ ] Minimal warnings (W category)

## Notes
- The code is functionally correct - these are quality/style improvements
- Focus on Phase 1 first for immediate impact
- Phase 2 and 3 can be done incrementally
- Consider using pre-commit hooks to prevent regression
