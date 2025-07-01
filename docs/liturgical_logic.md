# Liturgical Calendar Logic and Rationale

## Introduction
The liturgical calendar is a system used by many Christian churches to organize the year around key feasts (special days), seasons (periods with particular themes), and readings from the Bible. Each week, the calendar determines which readings, prayers, and colors are used in worship. This project implements the Anglican liturgical calendar, which is based on a combination of fixed dates (like Christmas) and movable feasts (like Easter, which changes each year).

The code in this project is designed to calculate the correct season, week name, and readings for any given date, following the rules and traditions of the Anglican Communion. Mistakes in these calculations can lead to using the wrong readings or prayers in worship, so accuracy is essential.

## Glossary
- **Feast:** A special day in the church year, often commemorating an event or person.
- **Season:** A period in the church year with a particular theme (e.g., Lent, Easter, Advent).
- **Proper N:** Numbered Sundays after Pentecost/Trinity, used in the Revised Common Lectionary. The number (N) varies depending on the date of Easter.
- **Trinity Sunday:** The Sunday after Pentecost, marking the start of the "Trinity" or "Ordinary" season.
- **Lectionary:** A schedule of scripture readings for each day or week of the year.
- **Cycle:** Refers to the repeating pattern of readings (e.g., 3-year Sunday cycle A/B/C, 2-year weekday cycle 1/2).
- **Easter point/Christmas point:** The number of days between a given date and Easter or Christmas, used for calculating movable feasts and seasons.

## 1. The "Easter Point" and "Christmas Point" System
Many calculations in this project use the concept of an "Easter point" or "Christmas point":
- **Easter point:** The number of days between the current date and Easter Sunday of that year. Used to determine movable feasts and seasons (e.g., Lent, Pentecost, Trinity).
- **Christmas point:** The number of days between the current date and Christmas Day. Used for Christmas season calculations.
- These points allow us to calculate seasons and feasts that move each year, based on the date of Easter or Christmas.
- See `funcs.py` for the calculation functions.

**Example:**
If Easter is March 31, 2024, then April 7, 2024 has an Easter point of 7 (7 days after Easter). Christmas point for December 26 is 1 (1 day after Christmas).

## 2. Season Calculation
### Available Seasons and How They Are Determined
| Season         | How Determined                        | Typical Dates         | Description                        |
|----------------|--------------------------------------|----------------------|-------------------------------------|
| Advent         | 4 Sundays before Christmas           | Late Nov–Dec         | Preparation for Christmas           |
| Christmas      | Dec 25–Jan 5                         | Dec 25–Jan 5         | Celebration of Christ's birth       |
| Epiphany       | Jan 6 onward                         | Jan 6–Feb/Mar        | Manifestation of Christ             |
| Pre-Lent       | 3 Sundays before Lent                | Feb/Mar              | Preparation for Lent                |
| Lent           | Begins Ash Wednesday (46 days before Easter) | Feb/Mar–Apr | Preparation for Easter              |
| Holy Week      | Week before Easter                   | Mar/Apr              | Final week of Lent                  |
| Easter         | Begins Easter Sunday (date varies)   | Mar/Apr–May/Jun      | Celebration of Resurrection         |
| Pentecost      | 50 days after Easter                 | May/Jun              | Gift of the Holy Spirit             |
| Trinity/Proper | After Pentecost/Trinity Sunday       | May/Jun–Nov          | Ordinary Time, numbered weeks       |
| Pre-Advent     | Last 4 Sundays before Advent         | Nov                  | Preparation for Advent              |

Seasons are calculated based on the date's relationship to movable feasts (Easter, Pentecost, Trinity Sunday) and fixed points (Advent, Christmas). The main logic is in `core/season_calculator.py` (see `determine_season`). Edge cases (e.g., Pre-Lent, Pre-Advent, Ash Wednesday) are handled explicitly.

**Example:**
- In 2024, Easter is March 31. Lent begins on Ash Wednesday, February 14 (46 days before Easter). Trinity Sunday is May 26 (8 weeks after Easter).

### Edge Cases
- **Ash Wednesday:** The season changes to Lent, but the week name may still be "1 before Lent" (see Week Naming).
- **Pre-Lent/Pre-Advent:** Special transition weeks before Lent/Advent, with unique naming and readings logic.
- **Pre-Lent Weekday vs Sunday Naming:**
    - The lectionary assigns week-based readings for Pre-Lent weekdays using keys like '5 before Lent', '4 before Lent', ..., '1 before Lent'.
    - However, Sundays only use '2 before Lent' and '1 before Lent' as week names, because the Pre-Lent season is defined as three Sundays before Lent, but weekday readings extend to five weeks.
    - The code includes an override to ensure that for the five weeks before Ash Wednesday, weekdays get the correct 'N before Lent' reading key, matching the lectionary data. This override only applies for n in 1..5; otherwise, the main logic is used.

## 3. Week Naming: Proper N vs. Trinity N
### Why Two Systems?
- **Trinity weeks move:** Trinity Sunday is based on Easter, so the number and dates of Trinity/Proper weeks vary each year. The readings for weekdays after Trinity are keyed as "Trinity N" because they follow the movable feast pattern.
- **Proper Sundays are fixed:** Proper weeks are numbered from the start of the year and are fixed in the lectionary calendar, regardless of when Easter falls. The Sunday readings are keyed as "Proper N".
- The readings match this pattern: Sunday readings use Proper N, weekday readings use Trinity N.

### Calculation Formulas
- **Proper N (Sundays):**
  - Calculated as `get_week_number(date) - 18` (see `funcs.py`).
  - This matches the lectionary's fixed Proper week numbering.
  - Proper weeks are a feature of the post-Pentecost season in the Revised Common Lectionary, and are fixed in the calendar, not based on Easter.
- **Trinity N (Weekdays):**
  - Calculated as `(easter_point - 56) // 7 + 1` (see `season_calculator.py`).
  - Trinity Sunday is 8 weeks (56 days) after Easter. Trinity N weeks start the week after Trinity Sunday.
  - This calculation ensures that weekday readings, which are keyed as "Trinity N", always match the correct week after Trinity, regardless of the civil calendar.

### Sunday-Based Week Naming
- Week names are based on the Sunday season, even for weekdays.
- For any weekday, the code determines the season and week number of the preceding Sunday using the `calculate_sunday_week_info` function (see `season_calculator.py`). This ensures that weekday readings and week names are always consistent with the Sunday that starts the week, even across season transitions or edge cases (e.g., Ash Wednesday, Pre-Lent).
- This can create scenarios where, for example, Ash Wednesday is in the season of Lent but the week name is still "1 before Lent".
- This is intentional and matches liturgical practice and lectionary data.

**Example:**
- If Ash Wednesday falls on February 14, but the preceding Sunday is still in Pre-Lent, the week name for Ash Wednesday will be "1 before Lent" even though the season is Lent.

## 4. Lectionary Cycles
### Sunday Cycle (A/B/C)
- There is a 3-year cycle for Sunday readings: Years A, B, and C.
- Each year focuses on a different Gospel:
  - Year A: Matthew
  - Year B: Mark
  - Year C: Luke
- The cycle is determined by the year modulo 3 (see `readings_manager.py`).

### Weekday Cycle (1/2)
- There is a 2-year cycle for weekday readings: Years 1 and 2.
- Even years use Cycle 1, odd years use Cycle 2.
- The 2-year cycle is designed to cover most of the Bible across two years of daily readings.

### Why This Matters
The distinction between Proper N and Trinity N is necessary because the Sunday and weekday lectionary cycles are independent and keyed differently in the data. This is why the code must calculate both week numbers, depending on context.

**Example:**
- In 2024 (Year B, Cycle 1), the Sunday readings will focus on Mark, and weekday readings will follow Cycle 1.

## 5. Christmas, Epiphany, and Fixed Weekday Readings

- Christmas weeks (Dec 25–Jan 5): No weekday readings are assigned. All days are either feasts or use fixed readings.
- Epiphany (Jan 6): Always a principal feast; never assigned a weekday reading.
- Fixed weekday readings: Dec 29–31, Jan 2–5, and Jan 7–12 have fixed readings, not week-based. These are not assigned by the week-based logic and do not use `weekday_reading_key`.
- Implementation: The code and tests are designed so that for these dates, `weekday_reading_key` is `None` and no readings are expected from the week-based system.

### Christmas Season Feasts and Fixed Readings Table

| Date(s)         | Feast/Fixed Reading                |
|-----------------|------------------------------------|
| Dec 25          | Christmas (Principal Feast)         |
| Dec 26          | St Stephen (Feast)                 |
| Dec 27          | St John the Evangelist (Feast)      |
| Dec 28          | The Holy Innocents (Feast)          |
| Dec 29–31       | Fixed weekday readings              |
| Jan 1           | The Naming and Circumcision of Jesus (Feast) |
| Jan 2–5         | Fixed weekday readings              |
| Jan 6           | Epiphany (Principal Feast)          |
| Jan 7–12        | Fixed weekday readings (until Epiphany 1) |

- **Note:**
  - All days not listed as a specific feast use fixed weekday readings.
  - After Jan 6, the first Sunday is Epiphany 1; fixed weekday readings are used for weekdays before that Sunday.
  - No week-based weekday readings are assigned for any of these dates.

## 6. Code and Church Practice
The code is structured to match the rules and traditions of the Anglican liturgical calendar. This means:
- Calculations are robust to the movable date of Easter and other feasts.
- Week and season names are always consistent with the lectionary and church practice.
- Edge cases and transitions (e.g., Pre-Lent, Pre-Advent, Ash Wednesday) are handled explicitly.

For a sample Anglican calendar to compare with the code's output, see: [Church of England Lectionary](https://www.churchofengland.org/prayer-and-worship/worship-texts-and-resources/common-worship/churchs-year/lectionary)

## 7. For Developers: Implementation Gotchas and Lessons Learned
### 7a. Day-of-Week Indexing: Python vs. Liturgical Calendar
- **Python's `datetime.date.weekday()`** returns `0` for Monday and `6` for Sunday.
- **The liturgical calendar (and lectionary)** treats **Sunday as day 0** (the start of the week).
- **Implication:**
  - You cannot use Python's `weekday()` directly for lectionary logic.
  - Instead, use a custom function (e.g., `day_of_week` in `funcs.py`) that returns `0` for Sunday, `1` for Monday, etc.
- **Lesson:**
  - Always check the day-of-week convention in both your code and your data. Mismatches can cause subtle off-by-one errors, especially in week/season transitions.

### 7b. Movable Feasts and Variable Week Numbers
- The number of Proper/Trinity weeks can vary dramatically depending on the date of Easter.
- Some years may "skip" certain Proper weeks, or start with a higher Proper number (e.g., Proper 7 instead of Proper 4).
- **Lesson:**
  - Never hardcode the number of weeks in a season; always calculate based on Easter and the lectionary rules.

## 8. Further Reading
- For more on the lectionary and liturgical calendar, see:
  - [Church of England: The Lectionary](https://www.churchofengland.org/prayer-and-worship/worship-texts-and-resources/common-worship/churchs-year/lectionary)
  - [Anglican Communion: Liturgical Year](https://www.anglicancommunion.org/media/253799/Liturgical-Year.pdf)
  - [Revised Common Lectionary](https://lectionary.library.vanderbilt.edu/)

---

**If you encounter a confusing calculation or naming rule, check this file and the referenced code sections for rationale and examples.** 