# Pylint Fixes Checklist

**Current Score:** 8.45/10
**Target Score:** 9.25-10.00/10

## 🔴 HIGH PRIORITY - Easy Fixes (Quick Wins)

### 1. Unused Variables/Arguments (W0612, W0613)
- [ ] **`liturgical_calendar/cli.py:117`** - Remove unused `val_parser`
- [ ] **`liturgical_calendar/cli.py:122`** - Remove unused `ver_parser`
- [ ] **`liturgical_calendar/core/readings_manager.py:136`** - Remove unused `feast_key`
- [ ] **`liturgical_calendar/image_generation/pipeline.py:264`** - Remove unused args: `layout`, `fonts`, `data`
- [ ] **`liturgical_calendar/image_generation/pipeline.py:272`** - Remove unused arg: `img`
- [ ] **`liturgical_calendar/image_generation/layout_engine.py:237`** - Remove unused arg: `padding`
- [ ] **`liturgical_calendar/image_generation/layout_engine.py:302`** - Remove unused args: `text`, `font`, `max_width`
- [ ] **`liturgical_calendar/services/feast_service.py:353-361`** - Remove 9 unused arguments

### 2. Pointless Statements (W0104)
- [x] **`liturgical_calendar/core/season_calculator.py:103-104`** - Remove pointless statements
- [x] **`liturgical_calendar/services/feast_service.py:166`** - Remove pointless statement

### 3. Duplicate Keys (W0109)
- [ ] **`liturgical_calendar/data/feasts_data.py:177`** - Fix duplicate key '02-14'

### 4. Missing Raise From (W0707)
- [ ] **`liturgical_calendar/core/readings_manager.py:211`** - Add `from e` to raise
- [ ] **`liturgical_calendar/utils/file_system.py:105`** - Add `from e` to raise
- [ ] **`liturgical_calendar/utils/file_system.py:184`** - Add `from e` to raise
- [ ] **`liturgical_calendar/services/image_service.py:272`** - Add `from e` to raise
- [ ] **`liturgical_calendar/services/config_service.py:357`** - Add `from e` to raise
- [ ] **`liturgical_calendar/caching/artwork_cache.py:126`** - Add `from e` to raise

### 5. Unspecified Encoding (W1514)
- [ ] **`liturgical_calendar/config/settings.py:61`** - Add `encoding="utf-8"`
- [ ] **`liturgical_calendar/services/config_service.py:335`** - Add `encoding="utf-8"`
- [ ] **`liturgical_calendar/services/config_service.py:350`** - Add `encoding="utf-8"`

### 6. Superfluous Parentheses (C0325)
- [ ] **`liturgical_calendar/funcs.py:179`** - Remove unnecessary parentheses

## 🟡 MEDIUM PRIORITY - Readability Improvements

### 7. No-Else-Return/Continue (R1705, R1724)
- [ ] **`liturgical_calendar/core/season_calculator.py:55`** - Remove unnecessary `elif`
- [ ] **`liturgical_calendar/core/season_calculator.py:77`** - Remove unnecessary `else`
- [ ] **`liturgical_calendar/services/feast_service.py:230`** - Remove unnecessary `elif`
- [ ] **`liturgical_calendar/services/feast_service.py:254`** - Remove unnecessary `else`
- [ ] **`liturgical_calendar/services/image_service.py:345`** - Remove unnecessary `else`
- [ ] **`liturgical_calendar/services/image_service.py:352`** - Remove unnecessary `elif`
- [ ] **`liturgical_calendar/services/image_service.py:369`** - Remove unnecessary `elif`

### 8. Missing Docstrings (C0116, C0114)
- [ ] **`liturgical_calendar/caching/artwork_cache.py:24`** - Add function docstring
- [ ] **`liturgical_calendar/image_generation/font_manager.py:38`** - Add function docstring
- [ ] **`liturgical_calendar/image_generation/font_manager.py:44`** - Add function docstring
- [ ] **`liturgical_calendar/services/feast_service.py:368`** - Add function docstring
- [ ] **`liturgical_calendar/services/feast_service.py:381`** - Add function docstring
- [ ] **`liturgical_calendar/config/settings.py:1`** - Add module docstring

### 9. Import Outside Top Level (C0415)
- [ ] **`liturgical_calendar/funcs.py:216-217`** - Move `hashlib` and `urllib.parse.urlparse` imports to top
- [ ] **`liturgical_calendar/core/readings_manager.py:31`** - Move data imports to top
- [ ] **`liturgical_calendar/core/readings_manager.py:131`** - Move `data.feasts_data.feasts` import to top
- [ ] **`liturgical_calendar/core/artwork_manager.py:81`** - Move `funcs` imports to top
- [ ] **`liturgical_calendar/core/artwork_manager.py:82`** - Move `readings_manager` import to top
- [ ] **`liturgical_calendar/core/artwork_manager.py:190`** - Move `funcs.get_cache_filename` import to top
- [ ] **`liturgical_calendar/core/artwork_manager.py:206`** - Move `datetime.timedelta` import to top
- [ ] **`liturgical_calendar/image_generation/pipeline.py:121`** - Move `datetime` import to top
- [ ] **`liturgical_calendar/image_generation/pipeline.py:145`** - Move `datetime` import to top
- [ ] **`liturgical_calendar/services/feast_service.py:134`** - Move `funcs.get_advent_sunday` import to top
- [ ] **`liturgical_calendar/services/image_service.py:243`** - Move `ImageGenerationPipeline` import to top

## 🟢 LOW PRIORITY - Design Decisions

### 10. Too Many Arguments (R0913, R0917)
- [ ] **`liturgical_calendar/caching/image_processor.py:31`** - 7 args (API design decision)
- [ ] **`liturgical_calendar/image_generation/image_builder.py:75`** - 6 args
- [ ] **`liturgical_calendar/image_generation/layout_engine.py:14`** - 7 args
- [ ] **`liturgical_calendar/image_generation/layout_engine.py:68`** - 9 args
- [ ] **`liturgical_calendar/image_generation/layout_engine.py:121`** - 9 args
- [ ] **`liturgical_calendar/image_generation/layout_engine.py:174`** - 9 args
- [ ] **`liturgical_calendar/image_generation/layout_engine.py:231`** - 9 args
- [ ] **`liturgical_calendar/image_generation/pipeline.py:272`** - 7 args
- [ ] **`liturgical_calendar/services/feast_service.py:138`** - 6 args
- [ ] **`liturgical_calendar/services/feast_service.py:312`** - 10 args
- [ ] **`liturgical_calendar/services/feast_service.py:351`** - 10 args
- [ ] **`liturgical_calendar/services/image_service.py:30`** - 6 args

### 11. Complexity Issues (R0911, R0912, R0914, R0915, R1702)
- [ ] **`liturgical_calendar/cli.py`** - Too many locals (27), branches (38), statements (134), nested blocks (7)
- [ ] **`liturgical_calendar/core/season_calculator.py`** - Too many returns (11), branches (14), locals (37), statements (103)
- [ ] **`liturgical_calendar/core/readings_manager.py`** - Too many nested blocks (6)
- [ ] **`liturgical_calendar/core/artwork_manager.py`** - Too many locals (33), branches (19), statements (62)
- [ ] **`liturgical_calendar/image_generation/image_builder.py`** - Too many locals (22), branches (13)
- [ ] **`liturgical_calendar/image_generation/pipeline.py`** - Too many locals (22)
- [ ] **`liturgical_calendar/image_generation/layout_engine.py`** - Too many locals (24,27,21,30)
- [ ] **`liturgical_calendar/caching/image_processor.py`** - Too many branches (14), statements (53)
- [ ] **`liturgical_calendar/services/feast_service.py`** - Too many locals (22)
- [ ] **`liturgical_calendar/services/image_service.py`** - Too many returns (13), branches (15)

### 12. Other Style Issues
- [ ] **Line too long (C0301)** - 50+ instances across files
- [ ] **Too many lines (C0302)** - Data files (expected for large data structures)
- [ ] **Too few public methods (R0903)** - Simple classes
- [ ] **Too many instance attributes (R0902)** - Complex classes
- [ ] **Global statement (W0603)** - Legacy code in logging.py
- [ ] **Duplicate code (R0801)** - Data/config files (expected)
- [ ] **Broad exception catching (W0718)** - Acceptable in some contexts
- [ ] **Logging f-string interpolation (W1203)** - Many instances

## 📊 Progress Tracking

### High Priority Fixes (1-6)
- [ ] Unused Variables/Arguments: 0/8 completed
- [ ] Pointless Statements: 0/2 completed
- [ ] Duplicate Keys: 0/1 completed
- [ ] Missing Raise From: 0/6 completed
- [ ] Unspecified Encoding: 0/3 completed
- [ ] Superfluous Parentheses: 0/1 completed

### Medium Priority Fixes (7-9)
- [ ] No-Else-Return/Continue: 0/7 completed
- [ ] Missing Docstrings: 0/6 completed
- [ ] Import Outside Top Level: 0/11 completed

### Low Priority Fixes (10-12)
- [ ] Too Many Arguments: 0/12 completed
- [ ] Complexity Issues: 0/10 completed
- [ ] Other Style Issues: 0/8 completed

## 🎯 Expected Impact

- **High Priority Fixes (1-6):** ~21 fixes → **+0.5-1.0 points**
- **Medium Priority Fixes (7-9):** ~24 fixes → **+0.3-0.5 points**
- **Total Potential Improvement:** **+0.8-1.5 points** → **Target: 9.25-10.00/10**

## 📝 Notes

- Focus on High Priority fixes first for maximum impact
- Medium Priority fixes improve code quality and maintainability
- Low Priority fixes are design decisions that may not need changing
- Some issues (like "too many lines" in data files) are expected and can be ignored
- Use `# pylint: disable=...` comments sparingly and only for justified cases
