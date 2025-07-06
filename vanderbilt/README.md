# Vanderbilt Lectionary Comparison & Data Integration

This folder contains tools and data for comparing the Revised Common Lectionary (RCL) readings from the Vanderbilt Divinity School with the internal Anglican lectionary data structures used in this project. It also provides scripts to generate new internal data files from the Vanderbilt source (though they don’t work).

## Folder Structure

- `data/` — Raw Vanderbilt RCL CSV files for Years A, B, and C
- `src/` — Scripts for parsing, comparing, and generating data
- `build/` — Generated reports and Python data files (ignored by git)

## Approach

1. **Parsing Vanderbilt RCL Data:**
   - The CSVs from Vanderbilt are parsed, skipping metadata/header lines, to extract the four readings (OT, Psalm, Epistle, Gospel) for each Sunday and major feast.
2. **Key Mapping & Normalization:**
   - RCL liturgical names are mapped to the internal keys used by the Anglican lectionary codebase (e.g., "First Sunday after Epiphany" → "Epiphany 1").
   - Feasts and holy days are mapped using a custom dictionary, and alternate names are handled.
   - Readings are normalized to account for alternates ("or"), verse ranges, and parentheticals.
3. **Comparison & Reporting:**
   - The main comparison script (`src/compare_rcl_to_sunday_readings.py`) generates a detailed HTML report (`build/compare_rcl_report.html`) showing how closely the internal data matches the RCL for each week and reading slot.
   - Mismatches are categorized (e.g., different book, different verses, missing verses) and summarized at the top of the report.
4. **Data Generation:**
   - The `src/build_liturgical_data_from_vanderbilt.py` script generates new `readings_data.py` and `feasts_data.py` files in `build/`, using the mapped and normalized data from the Vanderbilt CSVs. The output of this script is pretty useless though.

## How to Use

1. **Run the Comparison:**
   ```sh
   cd vanderbilt/src
   PYTHONPATH=../.. python compare_rcl_to_sunday_readings.py
   ```
   - View the HTML report in `../build/compare_rcl_report.html`.

2. **Generate Internal Data Files:**
   ```sh
   cd vanderbilt/src
   PYTHONPATH=../.. python build_liturgical_data_from_vanderbilt.py
   ```
   - This will create `../build/readings_data.py` and `../build/feasts_data.py`.

## Analysis: How Close Are the Readings?

- **Exact Matches:**
  - The majority of Sundays and major feasts match the RCL readings exactly (100% match in the report).
- **Near Matches:**
  - Some readings are very close (95–99%), usually due to minor verse range differences or alternate readings.
- **Partial Matches:**
  - A significant number of readings are partial matches (50–94%), often due to:
    - Alternate readings ("or" options) in the RCL not present internally
    - Differences in verse ranges (e.g., RCL includes more/fewer verses)
    - Parenthetical or optional verses
    - Different book or chapter selections for the same Sunday
- **Poor Matches or Missing:**
  - Some readings are missing or have major differences, typically because:
    - The internal data lacks certain feasts or special services present in the RCL
    - Naming mismatches (e.g., "Nativity of the Lord - Proper I/II/III" vs. "Christmas")
    - The RCL provides multiple sets of readings for a single day (e.g., Christmas Propers), but the internal data only has one
    - The RCL includes readings for weekdays or minor feasts not tracked internally

## Main Reasons for Mismatches

- **Alternate Readings:** RCL often provides "or" options; the script matches the best alternate but may not match all.
- **Verse Range Differences:** RCL and internal data may include different verse spans for the same reading.
- **Naming/Key Differences:** Some Sundays or feasts are named differently or mapped to different keys.
- **Missing Data:** Some feasts or Sundays present in the RCL are not present in the internal data, and vice versa.
- **Multiple Services:** Some days (e.g., Christmas, Epiphany) have multiple sets of readings in the RCL, but only one in the internal data.

---

For questions or to extend the mapping/normalization logic, see the scripts in `src/` or the HTML report for detailed diagnostics.
