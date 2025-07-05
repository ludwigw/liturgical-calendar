import csv
import json
import os
from collections import defaultdict
from liturgical_calendar.data.readings_data import sunday_readings
from liturgical_calendar.data.feasts_data import feasts as feast_data
import re
import difflib
import html

# Map RCL CSV filenames to lectionary years
RCL_FILES = {
    'A': '../data/Year A - All Seasons_25-26.csv',
    'B': '../data/Year B - All Seasons_26-27.csv',
    'C': '../data/Year C - All Seasons_24-25.csv',
}

# Map RCL CSV liturgical names to sunday_readings keys
RCL_TO_INTERNAL = {
    'First Sunday of Advent': 'Advent 1',
    'Second Sunday of Advent': 'Advent 2',
    'Third Sunday of Advent': 'Advent 3',
    'Fourth Sunday of Advent': 'Advent 4',
    'First Sunday after Christmas Day': 'Christmas 1',
    'Second Sunday after Christmas Day': 'Christmas 2',
    'Baptism of the Lord': 'Epiphany 1',
    'First Sunday after the Epiphany': 'Epiphany 1',
    'Second Sunday after the Epiphany': 'Epiphany 2',
    'Third Sunday after the Epiphany': 'Epiphany 3',
    'Fourth Sunday after the Epiphany': 'Epiphany 4',
    'Transfiguration Sunday': '1 before Lent',
    'First Sunday in Lent': 'Lent 1',
    'Second Sunday in Lent': 'Lent 2',
    'Third Sunday in Lent': 'Lent 3',
    'Fourth Sunday in Lent': 'Lent 4',
    'Fifth Sunday in Lent': 'Lent 5',
    'Palm Sunday': 'Palm Sunday',
    'Resurrection of the Lord': 'Easter 1',
    'Second Sunday of Easter': 'Easter 2',
    'Third Sunday of Easter': 'Easter 3',
    'Fourth Sunday of Easter': 'Easter 4',
    'Fifth Sunday of Easter': 'Easter 5',
    'Sixth Sunday of Easter': 'Easter 6',
    'Seventh Sunday of Easter': 'Easter 7',
    'Day of Pentecost': 'Pentecost',
    'Trinity Sunday': 'Trinity',
    # Add more mappings as needed
}

# Define new match buckets
BUCKETS = [
    (100, 100, '100%'),
    (95, 99, '95-99%'),
    (85, 95, '85-95%'),
    (65, 85, '65-85%'),
    (45, 65, '45-65%'),
    (0, 45, '0-45%'),
]

def get_bucket(score):
    for low, high, label in BUCKETS:
        if low <= score < high or (score == 100 and high == 100):
            return label
    return '0-45%'

# Helper to normalize reading strings for comparison
def normalize_reading(reading):
    if not reading:
        return ''
    # Remove asterisks and content in parentheses
    reading = re.sub(r'\([^)]*\)', '', reading)
    reading = reading.replace('*', '')
    # Replace ' or ' and ';' with ','
    reading = reading.replace(' or ', ',').replace(';', ',')
    # Remove brackets
    reading = reading.replace('[', '').replace(']', '')
    # Remove all non-alphanumeric except colons and commas
    reading = re.sub(r'[^a-zA-Z0-9:,]', ' ', reading)
    # Lowercase and strip
    reading = reading.lower().strip()
    # Sort comma-separated readings
    parts = [p.strip() for p in reading.split(',') if p.strip()]
    parts.sort()
    return ','.join(parts)

def normalize_rcl_key(lit_name):
    # Remove quotes
    lit_name = lit_name.strip('"')
    # Standardize Proper names: 'Proper 10 (15)' -> 'Proper 10'
    m = re.match(r"Proper (\d+)", lit_name)
    if m:
        return f"Proper {m.group(1)}"
    # Standardize Reign of Christ/Christ the King
    if lit_name.startswith("Reign of Christ") or lit_name.startswith("Christ the King"):
        return "Proper 29"
    # Standardize Trinity Sunday
    if lit_name.startswith("Trinity Sunday"):
        return "Trinity"
    # Standardize Palm Sunday/Liturgy of the Passion
    if lit_name.startswith("Liturgy of the Passion") or lit_name.startswith("Palm Sunday"):
        return "Palm Sunday"
    # Standardize Pentecost
    if lit_name.startswith("Day of Pentecost"):
        return "Pentecost"
    # Standardize 1 before Lent/Transfiguration
    if lit_name.startswith("Transfiguration Sunday"):
        return "1 before Lent"
    # Standardize Christmas 1/2
    if lit_name.startswith("First Sunday after Christmas Day"):
        return "Christmas 1"
    if lit_name.startswith("Second Sunday after Christmas Day"):
        return "Christmas 2"
    # Standardize Epiphany 1/2/3/4
    if lit_name.startswith("Baptism of the Lord") or lit_name.startswith("First Sunday after the Epiphany"):
        return "Epiphany 1"
    if lit_name.startswith("Second Sunday after the Epiphany"):
        return "Epiphany 2"
    if lit_name.startswith("Third Sunday after the Epiphany"):
        return "Epiphany 3"
    if lit_name.startswith("Fourth Sunday after the Epiphany"):
        return "Epiphany 4"
    # Standardize Lent 1-5
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
    # Standardize Advent 1-4
    if lit_name.startswith("First Sunday of Advent"):
        return "Advent 1"
    if lit_name.startswith("Second Sunday of Advent"):
        return "Advent 2"
    if lit_name.startswith("Third Sunday of Advent"):
        return "Advent 3"
    if lit_name.startswith("Fourth Sunday of Advent"):
        return "Advent 4"
    # Standardize Easter 1-7
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
    # 1 before Lent
    if lit_name.startswith("Transfiguration Sunday"):
        return "1 before Lent"
    # 1 before Advent
    if lit_name.startswith("Christ the King") or lit_name.startswith("Reign of Christ"):
        return "1 before Advent"
    # Fallback: return as-is
    return lit_name

def parse_rcl_csv(filename):
    readings = {}
    lit_dates = set()
    with open(filename, newline='', encoding='utf-8') as csvfile:
        # Skip the first four lines (empty + 3 metadata)
        for _ in range(4):
            next(csvfile)
        # Print the next five lines after the header (for debug)
        for i in range(5):
            line = csvfile.readline()
            print(f"  Line {i+1} after header: {line.rstrip()}")
        # Reset file pointer to after header
        csvfile.seek(0)
        for _ in range(4):
            next(csvfile)
        reader = csv.DictReader(csvfile)
        for row in reader:
            if 'Liturgical Date' not in row or not row['Liturgical Date'].strip():
                continue
            lit_name = row['Liturgical Date'].strip()
            lit_dates.add(lit_name)
            key = normalize_rcl_key(lit_name)
            # Reorder to match internal: [OT, Epistle, Gospel, Psalm]
            readings[key] = [
                row['First reading'].strip(),
                row['Second reading'].strip(),
                row['Gospel'].strip(),
                row['Psalm'].strip(),
            ]
    print(f"  Unique Liturgical Dates in {filename}: {sorted(lit_dates)}")
    return readings

def string_similarity(a, b):
    return difflib.SequenceMatcher(None, a, b).ratio()

def expand_verse_range(verse_str):
    # Expand a string like '1-3,5,7-8' to a set of ints {1,2,3,5,7,8}
    verses = set()
    for part in verse_str.split(','):
        part = part.strip()
        if '-' in part:
            try:
                start, end = part.split('-', 1)
                verses.update(range(int(start), int(end)+1))
            except Exception:
                continue
        else:
            try:
                verses.add(int(part))
            except Exception:
                continue
    return verses

def parse_reading(reading):
    # Remove parentheticals
    reading = re.sub(r'\([^)]*\)', '', reading)
    # Lowercase, remove asterisks, brackets, and extra whitespace
    reading = reading.replace('*', '').replace('[', '').replace(']', '').lower().strip()
    # Split on 'or' for alternates
    alternates = [alt.strip() for alt in re.split(r'\s+or\s+', reading) if alt.strip()]
    parsed = []
    for alt in alternates:
        # Try to parse book, chapter, verses
        m = re.match(r'([1-3]?[a-zA-Z ]+)\s+(\d+):(.*)', alt)
        if m:
            book = m.group(1).strip()
            chapter = m.group(2).strip()
            verses = m.group(3).replace(' ', '')
            # Remove a/b suffixes for partial match
            verses = re.sub(r'([0-9]+)[ab]', r'\1', verses)
            # Expand verse ranges to sets
            verse_set = expand_verse_range(verses.replace(';', ',').replace('.', ','))
            parsed.append({'book': book, 'chapter': chapter, 'verses': verse_set, 'raw': alt})
        else:
            parsed.append({'book': alt, 'chapter': '', 'verses': set(), 'raw': alt})
    return parsed

def split_rcl_reading_alternates(reading):
    # Split on ' or ' and also on ' Psalm ' (for OT+Psalm in one cell)
    # Also handle cases like 'Book X or Book Y Psalm Z' -> ['Book X', 'Book Y Psalm Z']
    if not reading:
        return ['']
    # First split on ' or '
    parts = [p.strip() for p in re.split(r'\s+or\s+', reading) if p.strip()]
    # For each part, if it contains ' Psalm ' (and is not just a Psalm), split further
    alternates = []
    for part in parts:
        # If 'Psalm' appears not at the start, split into OT and Psalm
        m = re.match(r'^(.*?)(Psalm .*)$', part, re.IGNORECASE)
        if m and not part.lower().startswith('psalm'):
            alternates.append(m.group(1).strip())
            alternates.append(m.group(2).strip())
        else:
            alternates.append(part)
    return alternates

def best_reading_match(rcl_reading, internal_reading):
    rcl_parsed = parse_reading(rcl_reading)
    internal_parsed = parse_reading(internal_reading)
    best_score = 0
    best_category = None
    best_details = None
    for r in rcl_parsed:
        for i in internal_parsed:
            if r['book'] == i['book']:
                if r['chapter'] == i['chapter']:
                    if r['verses'] and i['verses']:
                        overlap = len(r['verses'] & i['verses']) / max(1, len(r['verses'] | i['verses']))
                        score = overlap
                        if overlap == 1.0:
                            category = 'Exact'
                            details = ''
                        else:
                            missing = r['verses'] - i['verses']
                            extra = i['verses'] - r['verses']
                            if missing and not extra:
                                category = 'Missing Verses'
                                details = f"Missing: {sorted(missing)}"
                            elif extra and not missing:
                                category = 'Extra Verses'
                                details = f"Extra: {sorted(extra)}"
                            else:
                                category = 'Different Verses'
                                details = f"Missing: {sorted(missing)}, Extra: {sorted(extra)}"
                        if score > best_score:
                            best_score = score
                            best_category = category
                            best_details = details
                    else:
                        # No verses to compare, fallback to string similarity
                        sim = difflib.SequenceMatcher(None, r['raw'], i['raw']).ratio()
                        if sim > best_score:
                            best_score = sim
                            best_category = 'String Mismatch'
                            best_details = ''
                else:
                    # Book matches, chapter differs
                    sim = difflib.SequenceMatcher(None, r['raw'], i['raw']).ratio()
                    if sim > best_score:
                        best_score = sim
                        best_category = 'Different Chapter'
                        best_details = f"RCL: {r['chapter']}, Internal: {i['chapter']}"
            else:
                # Book differs
                sim = difflib.SequenceMatcher(None, r['raw'], i['raw']).ratio()
                if sim > best_score:
                    best_score = sim
                    best_category = 'Different Book'
                    best_details = f"RCL: {r['book']}, Internal: {i['book']}"
    return int(round(best_score * 100)), best_category, best_details

def best_reading_match_with_alternates(rcl_reading, internal_reading):
    # Try all alternates in rcl_reading, return the best match
    alternates = split_rcl_reading_alternates(rcl_reading)
    best = (0, None, None, None)  # (score, alt, category, details)
    for alt in alternates:
        score, category, details = best_reading_match(alt, internal_reading)
        if score > best[0]:
            best = (score, alt, category, details)
    return best  # (score, alt, category, details)

def compare_readings(rcl, internal):
    diffs = defaultdict(dict)
    match_buckets = {label: 0 for _, _, label in BUCKETS}
    mismatch_categories = defaultdict(list)
    for week, rcl_readings in rcl.items():
        if week not in internal:
            diffs[week]['missing_in_internal'] = rcl_readings
            continue
        for i, label in enumerate(['OT', 'Epistle', 'Gospel', 'Psalm']):
            rcl_val = rcl_readings[i]
            internal_val = internal[week][i] if week in internal and len(internal[week]) > i else ''
            percent, best_alt, category, details = best_reading_match_with_alternates(rcl_val, internal_val)
            bucket = get_bucket(percent)
            match_buckets[bucket] += 1
            if percent < 100:
                diffs[week][label] = {
                    'expected': rcl_val,
                    'found': internal_val,
                    'match_percent': percent,
                    'category': category,
                    'details': details,
                    'best_alt': best_alt
                }
                if category:
                    mismatch_categories[category].append({
                        'week': week,
                        'label': label,
                        'expected': rcl_val,
                        'found': internal_val,
                        'match_percent': percent,
                        'details': details,
                        'best_alt': best_alt
                    })
    return diffs, match_buckets, mismatch_categories

def get_feast_readings_by_name(name):
    # Try to find a feast by name in feast_data (search both 'easter' and 'christmas' dicts)
    for season in feast_data:
        for key, feast in feast_data[season].items():
            if isinstance(feast, dict) and feast.get('name'):
                if feast['name'].lower().strip() == name.lower().strip():
                    return feast.get('readings', [])
    return []

def get_feast_readings_by_rcl_key(rcl_key, rcl=None):
    # Map RCL keys to feast names as best as possible
    mapping = {
        'Holy Name of Jesus': 'The Naming and Circumcision of Jesus',
        'Presentation of the Lord': 'Presentation of Christ at the Temple',
        'Annunciation of the Lord': 'The Annunciation of our Lord',
        'Epiphany of the Lord': 'Epiphany',
        'Ascension of the Lord': 'Ascension',
        'Holy Cross': 'Holy Cross Day',
        'All Saints Day': 'All Saints',
        'Visitation of Mary to Elizabeth': 'The Visit of the Blessed Virgin Mary to Elizabeth',
        'Liturgy of the Palms': 'Palm Sunday',
        'Monday of Holy Week': 'Holy Monday',
        'Tuesday of Holy Week': 'Holy Tuesday',
        'Wednesday of Holy Week': 'Holy Wednesday',
        # Add more mappings as needed
    }
    # Special handling for Nativity of the Lord Propers
    if rcl_key.startswith('Nativity of the Lord - Proper') and rcl is not None:
        from liturgical_calendar.data.feasts_data import feasts as feast_data
        christmas_readings = get_feast_readings_by_name('Christmas')
        if not christmas_readings or len(christmas_readings) != 4:
            return []
        propers = ['Nativity of the Lord - Proper I', 'Nativity of the Lord - Proper II', 'Nativity of the Lord - Proper III']
        best_score = -1
        best_readings = []
        for proper in propers:
            rcl_readings = rcl.get(proper)
            if rcl_readings and len(rcl_readings) == 4:
                score = sum(best_reading_match(a, b)[0] for a, b in zip(rcl_readings, christmas_readings))
                if score > best_score:
                    best_score = score
                    best_readings = christmas_readings
        return best_readings
    feast_name = mapping.get(rcl_key, rcl_key)
    readings = get_feast_readings_by_name(feast_name)
    return readings

def merge_internal_with_feasts(rcl, internal):
    # For each week in RCL, if not in internal, try to get feast readings
    merged = dict(internal)
    for week in rcl:
        if week not in merged:
            feast_readings = get_feast_readings_by_rcl_key(week, rcl)
            if feast_readings and len(feast_readings) == 4:
                merged[week] = feast_readings
    return merged

def main():
    all_diffs = {}
    all_buckets = {label: 0 for _, _, label in BUCKETS}
    human_summary = []
    all_category_counts = defaultdict(int)
    html_lines = []
    html_lines.append('<html><head><meta charset="utf-8"><title>RCL Comparison Report</title>')
    html_lines.append('<style>body{font-family:sans-serif;} table{border-collapse:collapse;margin-bottom:1em;} th,td{border:1px solid #ccc;padding:4px;} summary{font-weight:bold;} details{margin-bottom:1em;} .summary-table td,.summary-table th{border:none;}')
    html_lines.append('summary.year-summary { font-size: 1.3em; margin-left: 0; }')
    html_lines.append('summary.category-summary { font-size: 1.1em; margin-left: 1em; }')
    html_lines.append('summary.subcategory-summary { font-size: 1em; margin-left: 2em; }')
    html_lines.append('</style>')
    html_lines.append('</head><body>')
    html_lines.append('<h1>RCL Comparison Report</h1>')
    per_year_html = []
    for year, csvfile in RCL_FILES.items():
        rcl = parse_rcl_csv(csvfile)
        internal = {}
        for week in rcl:
            if week in sunday_readings and year in sunday_readings[week]:
                internal[week] = sunday_readings[week][year]
        merged_internal = merge_internal_with_feasts(rcl, internal)
        print(f"Year {year}:")
        print(f"  RCL weeks: {sorted(list(rcl.keys()))}")
        print(f"  Internal weeks: {sorted([k for k in sunday_readings if year in sunday_readings[k]])}")
        diffs, buckets, mismatch_categories = compare_readings(rcl, merged_internal)
        all_diffs[year] = diffs
        for k in all_buckets:
            all_buckets[k] += buckets[k]
        # Human-readable summary for this year
        human_summary.append(f"Year {year}:")
        missing = [(week, diffs[week]['missing_in_internal']) for week in diffs if 'missing_in_internal' in diffs[week]]
        if missing:
            human_summary.append("  Missing in Internal:")
            for week, readings in missing:
                human_summary.append(f"    {week}: {readings}")
        else:
            human_summary.append("  No missing weeks in internal data.")
        human_summary.append("")
        # Add categorized mismatches
        human_summary.append("  Mismatches by Category:")
        for cat in sorted(mismatch_categories.keys()):
            count = len(mismatch_categories[cat])
            all_category_counts[cat] += count
            human_summary.append(f"    {cat}: {count}")
            for m in mismatch_categories[cat]:
                human_summary.append(f"      {m['week']} [{m['label']}]: {m['expected']} vs {m['found']} (match: {m['match_percent']}%) {m['details']}")
        human_summary.append("")
        per_year_html.append(f'<details open><summary class="year-summary">Year {html.escape(year)}</summary>')
        missing = [(week, diffs[week]['missing_in_internal']) for week in diffs if 'missing_in_internal' in diffs[week]]
        if missing:
            per_year_html.append('<details><summary class="category-summary">Missing in Internal</summary>')
            per_year_html.append('<table><tr><th>Week</th><th>Readings</th></tr>')
            for week, readings in missing:
                per_year_html.append('<tr><td>{}</td><td>{}</td></tr>'.format(html.escape(week), html.escape(str(readings))))
            per_year_html.append('</table></details>')
        else:
            per_year_html.append('<p>No missing weeks in internal data.</p>')
        per_year_html.append('<details><summary class="category-summary">Mismatches by Category</summary>')
        for cat in sorted(mismatch_categories.keys()):
            count = len(mismatch_categories[cat])
            per_year_html.append(f'<details><summary class="subcategory-summary">{html.escape(cat)} ({count})</summary>')
            per_year_html.append('<table><tr><th>Week</th><th>Label</th><th>Expected</th><th>Found</th><th>Match %</th><th>Details</th></tr>')
            for m in mismatch_categories[cat]:
                expected_display = html.escape(m['expected'])
                if m.get('best_alt') and m['best_alt'] != m['expected']:
                    expected_display += f'<br/><em>(best match: {html.escape(m["best_alt"])})</em>'
                per_year_html.append('<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>'.format(
                    html.escape(m['week']), html.escape(m['label']), expected_display, html.escape(m['found']), m['match_percent'], html.escape(m['details'])))
            per_year_html.append('</table></details>')
        per_year_html.append('</details>')
        per_year_html.append('</details>')
    # Now generate the summary tables with correct values
    total_readings = sum(all_buckets.values())
    html_lines.append('<h2>High-Level Summary</h2>')
    html_lines.append('<table class="summary-table">')
    html_lines.append(f'<tr><th>Total readings compared</th><td>{total_readings}</td></tr>')
    html_lines.append(f'<tr><th>100% match</th><td>{all_buckets["100%"]}</td></tr>')
    html_lines.append(f'<tr><th>95-99% match</th><td>{all_buckets["95-99%"]}</td></tr>')
    html_lines.append(f'<tr><th>85-95% match</th><td>{all_buckets["85-95%"]}</td></tr>')
    html_lines.append(f'<tr><th>65-85% match</th><td>{all_buckets["65-85%"]}</td></tr>')
    html_lines.append(f'<tr><th>45-65% match</th><td>{all_buckets["45-65%"]}</td></tr>')
    html_lines.append(f'<tr><th>&lt;45% match</th><td>{all_buckets["0-45%"]}</td></tr>')
    html_lines.append('</table>')
    html_lines.append('<h2>Overall Mismatch Category Counts</h2>')
    html_lines.append('<table class="summary-table">')
    html_lines.append('<tr><th>Category</th><th>Count</th><th>Percent of Total</th></tr>')
    for cat in sorted(all_category_counts.keys()):
        percent = (all_category_counts[cat] / total_readings * 100) if total_readings else 0
        html_lines.append(f'<tr><td>{html.escape(cat)}</td><td>{all_category_counts[cat]}</td><td>{percent:.1f}%</td></tr>')
    html_lines.append('</table>')
    # Add per-year details after summary
    html_lines.extend(per_year_html)
    html_lines.append('</body></html>')
    # --- Write HTML to ../build/ ---
    output_html = os.path.join('../build', 'compare_rcl_report.html')
    with open(output_html, 'w', encoding='utf-8') as f:
        f.write('\n'.join(html_lines))
    print(f"HTML report written to {output_html}")
    # --- Write JSON to ../build/ ---
    output_json = os.path.join('../build', 'compare_rcl_report.json')
    json_data = {
        'all_diffs': all_diffs,
        'all_buckets': all_buckets,
        'all_category_counts': dict(all_category_counts),
        'total_readings': total_readings
    }
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2)
    print(f"JSON report written to {output_json}")

if __name__ == '__main__':
    main() 