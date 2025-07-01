# SeasonCalculator Refactoring Decisions

## Overview
Refactored SeasonCalculator to expose only `determine_season(date)` and `week_info(date)`, combining logic from the original `calculate_week_number` and `calculate_weekday_reading` methods.

## Key Decisions Made

### 1. Week-Starting Sunday Logic

**Original calculate_weekday_reading approach:**
```python
# For weekdays, calculate the Sunday's week number
sunday_days = days - dayofweek
sunday_y, sunday_m, sunday_d = add_delta_days(sunday_days)
sunday_days_from_epoch = date_to_days(sunday_y, sunday_m, sunday_d)
sunday_easter_point = sunday_days_from_epoch - easterday
# Then use sunday_easter_point for calculations
```

**Original calculate_week_number approach:**
```python
# Used the current date's easter_point directly
# No special logic for finding the week-starting Sunday
```

**Decision:** Always calculate the week-starting Sunday and use its liturgical points for all calculations.

**Rationale:** This centralizes the boundary logic and ensures consistency between Sunday and weekday readings.

### 2. Christmas Point Calculation for January/February

**Original approach (implicit in the code):**
```python
# The original code handled this correctly but it wasn't explicit
# It used the correct Christmas date based on the year
```

**New approach:**
```python
# For Jan/Feb, use previous year's Christmas
if f_date.month <= 2:
    christmasday = date_to_days(year - 1, 12, 25)
else:
    christmasday = date_to_days(year, 12, 25)
```

**Decision:** Made the January/February Christmas point calculation explicit.

**Rationale:** This ensures Epiphany season is calculated correctly for dates in the new year.

### 3. Trinity Season Reading Keys and Week Naming

**Original calculate_weekday_reading logic:**
```python
if dayofweek == 0:
    weekno = get_week_number(f_date) - 18
    return f"Proper {weekno}"
else:
    trinity_week = (easter_point - 56) // 7 + 1
    return f"Trinity {trinity_week}"
```

**Option A (conditional approach):**
```python
if dayofweek == 0:
    weekday_reading_key = None  # Sunday uses week_name
else:
    trinity_week = (easter_point - 56) // 7 + 1
    weekday_reading_key = f"Trinity {trinity_week}"
```

**Option B (simplified approach):**
```python
# Always calculate Trinity N for weekday_reading_key
trinity_week = (easter_point - 56) // 7 + 1
weekday_reading_key = f"Trinity {trinity_week}"
```

**Initial Decision:** Chose Option B - always set weekday_reading_key to "Trinity N" and week_name to "Proper N" for Trinity season.

**Rationale:** Simplifies the logic. Sundays will use `week_name` anyway, so the `weekday_reading_key` value doesn't matter for them.

**Test Failure and Correction:**
- Tests expect the week_name for Trinity Sunday (the first Sunday after Pentecost) to be "Trinity", not "Proper 1" (or "Proper N").
- The original decision to always use "Proper N" for week_name in Trinity season was incorrect for Trinity Sunday.
- **Final Logic:** For Trinity season, if the easter_point is between 56-62 (Trinity Sunday and first week after Pentecost), set week_name to "Trinity". For subsequent weeks, use "Proper N" as before.

**Rationale for Change:**
- This matches both liturgical convention and test expectations: Trinity Sunday is a unique feast and should be labeled as such, while following Sundays use the Proper numbering.
- This change ensures correctness for both the API and the user-facing output.
- **Key Insight:** The original code in `funcs.py` used easter_point (56-62) to identify Trinity Sunday, not week number. This approach is more reliable across different years.

### 4. Week Number vs Week Name

**Original calculate_week_number:**
```python
# Returned just a number
return weekno
```

**Original calculate_weekday_reading:**
```python
# Returned the rendered week name
return render_week_name('Lent', weekno, easter_point)[0]
```

**Decision:** Always calculate and return the week name, not just the number.

**Rationale:** The week number is only useful in the context of the week name, so we provide the complete information.

### 5. Lent Weekday Logic

**Original calculate_weekday_reading special logic:**
```python
if dayofweek == 0:
    # It's a Sunday, use the current week number
    first_sunday_lent_easter_point = -42
    weeks_from_first_sunday = (easter_point - first_sunday_lent_easter_point + dayofweek) // 7
    weekno = max(1, weeks_from_first_sunday + 1)
    return render_week_name('Lent', weekno, easter_point)[0]
else:
    # It's a weekday, calculate the Sunday's week number
    sunday_days = days - dayofweek
    sunday_y, sunday_m, sunday_d = add_delta_days(sunday_days)
    sunday_days_from_epoch = date_to_days(sunday_y, sunday_m, sunday_d)
    sunday_easter_point = sunday_days_from_epoch - easterday
    first_sunday_lent_easter_point = -42
    sunday_weeks_from_first_sunday = (sunday_easter_point - first_sunday_lent_easter_point) // 7
    sunday_weekno = max(1, sunday_weeks_from_first_sunday + 1)
    return render_week_name('Lent', sunday_weekno, easter_point)[0]
```

**New unified approach:**
```python
# Always calculate based on the week-starting Sunday
first_sunday_lent_easter_point = -42
weeks_from_first_sunday = (sunday_easter_point - first_sunday_lent_easter_point) // 7
weekno = max(1, weeks_from_first_sunday + 1)
week_name = render_week_name('Lent', weekno, sunday_easter_point)[0]
```

**Decision:** Since we always calculate based on the week-starting Sunday, this logic is now unified.

**Rationale:** Eliminates the need for separate weekday vs Sunday logic in Lent.

### 6. Pre-Advent Logic

**Original logic in both methods:**
```python
advent_sunday_abs = date_to_days(year, 12, 25) + advent_sunday
weeks_until_advent = (advent_sunday_abs - days) // 7
if dayofweek == 0 and 0 < weeks_until_advent <= 4:
    return 'Pre-Advent'  # or specific week name
```

**Decision:** Use the same logic in both `determine_season` and `week_info`.

**Rationale:** Ensures consistency between season determination and week naming.

### 7. Christmas/Epiphany Weekday Reading Keys (Edge Case)

**Background:**
The original code did not use week names like "Christmas 1", "Christmas 2", or "Ordinary Time" as weekday reading keys, because these do not exist in the readings data. Instead, it used specific keys for Christmas and Epiphany seasons.

**Correct Mapping:**
- For weekdays in the Christmas season (Dec 25–Jan 5), use **"Christmas"** as the weekday reading key.
- For weekdays in the Epiphany season (Jan 6 onward), use **"Epiphany N"** (where N is the week number) as the weekday reading key.
- Do **not** use "Christmas 1", "Christmas 2", or "Ordinary Time" as weekday reading keys, as these do not exist in the readings data.
- For Ordinary Time (outside of Trinity/Proper weeks), ensure the mapping is to "Epiphany N" or "Trinity N" as appropriate, never "Ordinary Time".

**Rationale:**
This ensures that weekday readings are always looked up using keys that exist in the readings data, matching the original logic and preventing lookup failures for these edge cases.

### 8. Christmas, Epiphany, and Fixed Weekday Readings

- No weekday readings are assigned for:
  - Christmas weeks (Dec 25–Jan 5, including "Christmas 1", "Christmas 2")
  - Epiphany (Jan 6, principal feast)
  - Fixed feast days: Dec 25, 26, 27, 28, Jan 1, Jan 6
- Fixed weekday readings (Dec 29–31, Jan 2–5, Jan 7–12) are not part of the week-based system and are not assigned via `weekday_reading_key`.
- Tests and code: For these dates, `weekday_reading_key` should be `None` and tests should not expect readings to exist.
- Rationale: This matches the lectionary, which assigns either feast readings or fixed readings for these days, not week-based readings.

## Potential Issues to Watch For

1. **Weekday vs Sunday boundary cases**: The original code had different logic for weekdays vs Sundays in some seasons. Our unified approach might affect edge cases.

2. **Lent weekday calculations**: The original had special logic for Lent weekdays that might not be preserved.

3. **Trinity Sunday vs Trinity weekdays**: The original had different numbering systems that we've preserved, but the API change might affect usage.

4. **Pre-Advent timing**: The original logic for determining "N before Advent" might have edge cases we haven't considered.

## Testing Strategy

When tests fail, check:
1. Are we using the correct liturgical points for the week-starting Sunday?
2. Is the Christmas point calculation correct for January/February dates?
3. Are we handling the Trinity Proper N vs Trinity N distinction correctly?
4. Are Lent weekday calculations using the Sunday's week number?
5. Is the Pre-Advent logic working correctly?
