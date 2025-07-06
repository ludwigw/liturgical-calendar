import csv
import pprint
import re
from collections import defaultdict

# Map RCL CSV filenames to lectionary years
RCL_FILES = {
    "A": "../data/Year A - All Seasons_25-26.csv",
    "B": "../data/Year B - All Seasons_26-27.csv",
    "C": "../data/Year C - All Seasons_24-25.csv",
}

# Map RCL CSV liturgical names to internal keys
RCL_TO_INTERNAL = {
    "First Sunday of Advent": "Advent 1",
    "Second Sunday of Advent": "Advent 2",
    "Third Sunday of Advent": "Advent 3",
    "Fourth Sunday of Advent": "Advent 4",
    "First Sunday after Christmas Day": "Christmas 1",
    "Second Sunday after Christmas Day": "Christmas 2",
    "Baptism of the Lord": "Epiphany 1",
    "First Sunday after the Epiphany": "Epiphany 1",
    "Second Sunday after the Epiphany": "Epiphany 2",
    "Third Sunday after the Epiphany": "Epiphany 3",
    "Fourth Sunday after the Epiphany": "Epiphany 4",
    "Transfiguration Sunday": "1 before Lent",
    "First Sunday in Lent": "Lent 1",
    "Second Sunday in Lent": "Lent 2",
    "Third Sunday in Lent": "Lent 3",
    "Fourth Sunday in Lent": "Lent 4",
    "Fifth Sunday in Lent": "Lent 5",
    "Palm Sunday": "Palm Sunday",
    "Resurrection of the Lord": "Easter 1",
    "Second Sunday of Easter": "Easter 2",
    "Third Sunday of Easter": "Easter 3",
    "Fourth Sunday of Easter": "Easter 4",
    "Fifth Sunday of Easter": "Easter 5",
    "Sixth Sunday of Easter": "Easter 6",
    "Seventh Sunday of Easter": "Easter 7",
    "Day of Pentecost": "Pentecost",
    "Trinity Sunday": "Trinity",
    # Add more mappings as needed
}

# Feasts mapping (RCL name to internal feast key and info)
FEASTS_RCL_TO_INTERNAL = {
    "Epiphany of the Lord": ("christmas", "01-06", "Epiphany"),
    "Presentation of the Lord": (
        "christmas",
        "02-02",
        "Presentation of Christ at the Temple",
    ),
    "Annunciation of the Lord": ("christmas", "03-25", "The Annunciation of our Lord"),
    "Holy Name of Jesus": (
        "christmas",
        "01-01",
        "The Naming and Circumcision of Jesus",
    ),
    "Ascension of the Lord": ("easter", 39, "Ascension"),
    "Holy Cross": ("christmas", "09-14", "Holy Cross Day"),
    "All Saints Day": ("christmas", "11-01", "All Saints"),
    "Visitation of Mary to Elizabeth": (
        "christmas",
        "05-31",
        "The Visit of the Blessed Virgin Mary to Elizabeth",
    ),
    "Liturgy of the Palms": ("easter", -7, "Palm Sunday"),
    "Monday of Holy Week": ("easter", -6, "Holy Monday"),
    "Tuesday of Holy Week": ("easter", -5, "Holy Tuesday"),
    "Wednesday of Holy Week": ("easter", -4, "Holy Wednesday"),
    "Maundy Thursday": ("easter", -3, "Maundy Thursday"),
    "Good Friday": ("easter", -2, "Good Friday"),
    "Holy Saturday": ("easter", -1, "Holy Saturday"),
    "Pentecost": ("easter", 49, "Pentecost"),
    "Trinity Sunday": ("easter", 56, "Trinity"),
    "Christmas": ("christmas", "12-25", "Christmas"),
    # Add more as needed
}

# Helper to normalize RCL keys


def normalize_rcl_key(lit_name):
    lit_name = lit_name.strip('"')
    m = re.match(r"Proper (\d+)", lit_name)
    if m:
        return f"Proper {m.group(1)}"
    if lit_name.startswith("Reign of Christ") or lit_name.startswith("Christ the King"):
        return "Proper 29"
    if lit_name.startswith("Trinity Sunday"):
        return "Trinity"
    if lit_name.startswith("Palm Sunday") or lit_name.startswith(
        "Liturgy of the Passion"
    ):
        return "Palm Sunday"
    if lit_name.startswith("Day of Pentecost"):
        return "Pentecost"
    if lit_name.startswith("Transfiguration Sunday"):
        return "1 before Lent"
    if lit_name.startswith("First Sunday after Christmas Day"):
        return "Christmas 1"
    if lit_name.startswith("Second Sunday after Christmas Day"):
        return "Christmas 2"
    if lit_name.startswith("Baptism of the Lord") or lit_name.startswith(
        "First Sunday after the Epiphany"
    ):
        return "Epiphany 1"
    if lit_name.startswith("Second Sunday after the Epiphany"):
        return "Epiphany 2"
    if lit_name.startswith("Third Sunday after the Epiphany"):
        return "Epiphany 3"
    if lit_name.startswith("Fourth Sunday after the Epiphany"):
        return "Epiphany 4"
    if lit_name.startswith("First Sunday in Lent"):
        return "Lent 1"
    if lit_name.startswith("Second Sunday in Lent"):
        return "Lent 2"
    if lit_name.startswith("Third Sunday in Lent"):
        return "Lent 3"
    if lit_name.startswith("Fourth Sunday in Lent"):
        return "Lent 4"
    if lit_name.startswith("Fifth Sunday in Lent"):
        return "Lent 5"
    if lit_name.startswith("First Sunday of Advent"):
        return "Advent 1"
    if lit_name.startswith("Second Sunday of Advent"):
        return "Advent 2"
    if lit_name.startswith("Third Sunday of Advent"):
        return "Advent 3"
    if lit_name.startswith("Fourth Sunday of Advent"):
        return "Advent 4"
    if lit_name.startswith("Resurrection of the Lord"):
        return "Easter 1"
    if lit_name.startswith("Second Sunday of Easter"):
        return "Easter 2"
    if lit_name.startswith("Third Sunday of Easter"):
        return "Easter 3"
    if lit_name.startswith("Fourth Sunday of Easter"):
        return "Easter 4"
    if lit_name.startswith("Fifth Sunday of Easter"):
        return "Easter 5"
    if lit_name.startswith("Sixth Sunday of Easter"):
        return "Easter 6"
    if lit_name.startswith("Seventh Sunday of Easter"):
        return "Easter 7"
    return lit_name


def parse_rcl_csv(filename):
    readings = {}
    with open(filename, newline="", encoding="utf-8") as csvfile:
        for _ in range(4):
            next(csvfile)
        reader = csv.DictReader(csvfile)
        for row in reader:
            if "Liturgical Date" not in row or not row["Liturgical Date"].strip():
                continue
            lit_name = row["Liturgical Date"].strip()
            key = normalize_rcl_key(lit_name)
            readings[key] = [
                row["First reading"].strip(),
                row["Second reading"].strip(),
                row["Gospel"].strip(),
                row["Psalm"].strip(),
            ]
    return readings


def main():
    # Build sunday_readings
    sunday_readings = defaultdict(dict)
    feast_readings = defaultdict(lambda: defaultdict(dict))
    for year, csvfile in RCL_FILES.items():
        rcl = parse_rcl_csv(csvfile)
        for rcl_key, readings in rcl.items():
            internal_key = RCL_TO_INTERNAL.get(rcl_key, rcl_key)
            # Sundays
            if internal_key in [
                "Advent 1",
                "Advent 2",
                "Advent 3",
                "Advent 4",
                "Christmas 1",
                "Christmas 2",
                "Epiphany 1",
                "Epiphany 2",
                "Epiphany 3",
                "Epiphany 4",
                "1 before Lent",
                "Lent 1",
                "Lent 2",
                "Lent 3",
                "Lent 4",
                "Lent 5",
                "Palm Sunday",
                "Easter 1",
                "Easter 2",
                "Easter 3",
                "Easter 4",
                "Easter 5",
                "Easter 6",
                "Easter 7",
                "Pentecost",
                "Trinity",
            ] or internal_key.startswith("Proper"):
                sunday_readings[internal_key][year] = readings
            # Feasts
            if rcl_key in FEASTS_RCL_TO_INTERNAL:
                rel, pointer, feast_name = FEASTS_RCL_TO_INTERNAL[rcl_key]
                feast_readings[rel][pointer] = {
                    "name": feast_name,
                    "readings": readings,
                }
    # Write readings_data.py
    readings_py = "# Auto-generated from Vanderbilt RCL\n" "sunday_readings = "
    readings_path = "../build/readings_data.py"
    with open(readings_path, "w", encoding="utf-8") as f:
        f.write(readings_py)
        pprint.pprint(dict(sunday_readings), stream=f, width=120)
        f.write("\n")
    # Write feasts_data.py
    feasts_py = "# Auto-generated from Vanderbilt RCL\n" "feasts = "
    feasts_path = "../build/feasts_data.py"
    with open(feasts_path, "w", encoding="utf-8") as f:
        f.write(feasts_py)
        pprint.pprint(
            {k: dict(v) for k, v in feast_readings.items()}, stream=f, width=120
        )
        f.write("\n")
    print(
        f"Wrote {len(sunday_readings)} Sundays and {sum(len(v) for v in feast_readings.values())} feasts."
    )
    print("Output: ../build/readings_data.py, ../build/feasts_data.py")


if __name__ == "__main__":
    main()
