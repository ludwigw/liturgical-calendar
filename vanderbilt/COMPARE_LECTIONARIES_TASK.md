
# 🧠 AI Engineer Task: Compare Lectionary Readings

## 🎯 Goal
Verify whether the contents of a Python dictionary (`sunday_readings`) match the **Sunday principal service readings** of:

1. The **Revised Common Lectionary (RCL)** from the **Consultation on Common Texts (CCT)**.
2. The **Church of England (Common Worship)** lectionary.

---

## 📄 Script Details

The file defines a dictionary like:

```python
sunday_readings = {
    'Advent 1': {
        'A': ['Isaiah 2:1-5', 'Romans 13:11-14', 'Matthew 24:36-44', 'Psalm 122'],
        ...
    },
    ...
}
```

- Keys are named Sundays (e.g., `"Advent 1"`, `"Christmas 1"`, etc.)
- Each sub-dictionary holds readings for Year `"A"`, `"B"`, and `"C"` with four readings:
  1. Old Testament
  2. Epistle
  3. Gospel
  4. Psalm

---

## 🔍 Tasks

### 1. Load Lectionary Sources

- **RCL (Revised Common Lectionary)**
  - Source: [https://www.commontexts.org/rcl/](https://www.commontexts.org/rcl/)
  - Or structured version: [https://lectionary.library.vanderbilt.edu/](https://lectionary.library.vanderbilt.edu/)

- **Church of England (Common Worship)**
  - Source: [Church of England Lectionary](https://www.churchofengland.org/prayer-and-worship/worship-texts-and-resources/common-worship/churchs-year/lectionary)

### 2. Compare with `sunday_readings`

For each Sunday:
- Match Sunday name (e.g., `"Advent 1"`) and Year (A/B/C)
- Compare the four readings:
  - Report **missing readings**
  - Report **extra readings**
  - Report **mismatches** (e.g., different Psalm ranges)
  - Consider variations like `"Baruch 5:1-9 or Malachi 3:1-4"` as valid if either matches

### 3. Report Differences

Format differences as a structured report:

```json
{
  "Advent 2": {
    "Year B": {
      "Psalm": {
        "expected": "Psalm 85:1-2, 8-13",
        "found": "Psalm 85:1-2, 8"
      }
    }
  }
}
```

### 4. Summary Stats (Optional)

- % of Sundays covered
- % of readings that match exactly
- Count of each discrepancy type

---

## ✅ Deliverables

- Python script or notebook for comparison
- Difference report (JSON, CSV, or Markdown)
- Summary of findings
