"""
This Python module will return the name, season, week number and liturgical
colour for any day in the Gregorian calendar, according to the Anglican
tradition of the Church of England.
"""

import sys
from datetime import datetime, date

from .funcs import get_easter, get_advent_sunday, date_to_days, day_of_week, add_delta_days, colour_code, get_week_number, render_week_name
from .feasts import lookup_feast
from .readings import get_readings_for_date

##########################################################################

def liturgical_calendar(s_date: str, transferred: bool = False):
    """
    Return the liturgical colour for a given day
    This func contains the main logic
    """

    # s_date could in a variety of formats
    # We standardise to f_date as a Date
    if isinstance(s_date, datetime):
        # If datetime, strip it to the date
        f_date = s_date.date()
    elif isinstance(s_date, date):
        # If date, accept it
        f_date = s_date
    elif isinstance(s_date, str):
        # If string, try to parse a YYYY-MM-DD
        f_date = datetime.strptime(s_date, "%Y-%m-%d").date()
    else:
        # Otherwise use today's date
        f_date = date.today()

    # Extract the components from the date
    year = f_date.year
    month = f_date.month
    day = f_date.day
    dayofweek = day_of_week(year, month, day)

    #die "Need to specify year, month and day" unless $y and $m and $d;

    # Calculate some values in Julian date
    days = date_to_days(year, month, day)
    easterm, easterd = get_easter(year)
    easterday = date_to_days(year, easterm, easterd)

    possibles = []

    # "The Church Year consists of two cycles of feasts and holy days: one is
    #  dependent upon the movable date of the Sunday of the Resurrection or
    #  Easter Day; the other, upon the fixed date of December 25, the Feast
    #  of our Lord's Nativity or Christmas Day."
    easter_point = days-easterday
    christmas_point = 0

    # We will store the amount of time until (-ve) or since (+ve) Christmas in
    # christmas_point. Let's make the cut-off date the end of February,
    # since we'll be dealing with Easter-based dates after that, and it
    # avoids the problems of considering leap years.
    if month>2:
        christmas_point = days - date_to_days(year, 12, 25)
    else:
        christmas_point = days - date_to_days(year-1, 12, 25)

    # First, figure out the season.
    season = ''
    weekno = None
    weekday_reading = None

    advent_sunday = get_advent_sunday(year)

    # Break up the liturgical year into seasons, starting at Advent
    # Set weekno=0 to disable week numbers for that season
    if christmas_point >= advent_sunday and christmas_point <= -1:
        season = 'Advent'
        season_url = 'https://en.wikipedia.org/wiki/Advent'
        weekno = 1 + (christmas_point-advent_sunday) // 7
        
    elif christmas_point >= 0 and christmas_point <= 11:
        # The Twelve Days of Christmas.
        season = 'Christmas'
        season_url = 'https://en.wikipedia.org/wiki/Christmastide'
        weekno = 1 + (christmas_point - dayofweek) // 7
    elif christmas_point >= 12 and christmas_point < 40:
        season = 'Epiphany'
        season_url = 'https://en.wikipedia.org/wiki/Epiphany_season'
        weekno = 1 + (christmas_point-12-dayofweek) // 7
    elif easter_point <= -47:
        # Period of Ordinary Time after Epiphany
        season = 'Ordinary Time'
        season_url = 'https://en.wikipedia.org/wiki/Ordinary_Time'
        # weekno = 1 + (christmas_point - 47) // 7
        weekno = get_week_number(f_date) - 5

        # Pre-Lent
        if easter_point > -61 and easter_point <= -47:
            season = 'Pre-Lent'
            season_url = 'https://en.wikipedia.org/wiki/Septuagesima'
            # -48 is start of Lent
            weekno = 1 + (easter_point * -1 - 47) // 7
        elif easter_point > -82 and easter_point < -62:
            weekday_reading = render_week_name('Pre-Lent',  1 + (easter_point * -1 - 47) // 7)[0]

    elif easter_point > -47 and easter_point < -7:
        season = 'Lent'
        season_url = 'https://en.wikipedia.org/wiki/Lent'
        weekno = (easter_point+50-dayofweek) // 7
    elif easter_point >= -7 and easter_point < 0:
        season = 'Holy Week'
        season_url = 'https://en.wikipedia.org/wiki/Holy_Week'
        weekno = 0
    elif easter_point >= 0 and easter_point < 49:
        season = 'Easter'
        season_url = 'https://en.wikipedia.org/wiki/Eastertide'
        weekno = 1+ easter_point // 7
    elif easter_point >= 49 and easter_point < 56:
        # Period of Ordinary Time after Pentecost
        season = 'Pentecost'
        season_url = 'https://en.wikipedia.org/wiki/Ordinary_Time'
        weekno = 0
    else:
        # Period of Ordinary Time after Pentecost
        season = 'Trinity'
        season_url = 'https://en.wikipedia.org/wiki/Ordinary_Time'

        # User Propers for Week Numbers
        weekno = get_week_number(f_date) - 18
        # weekno = (easter_point - 56 - dayofweek) // 7 + 3

        if christmas_point >= advent_sunday - 28 and christmas_point < advent_sunday:
            season = 'Pre-Advent'
            weekno = 1 + -1 * (christmas_point - advent_sunday + 1) // 7

        else:
            weekday_reading = f"Trinity {(easter_point - 56) // 7 + 1}"

        # Trinity Sunday is the first Sunday after Pentecost, and thus not a Proper
        if easter_point >= 56 and easter_point < 63:
            weekno = 0

    weekno = int(weekno) if int(weekno) > 0 else None

    # Now, look for feasts.
    feast_from_easter    = lookup_feast('easter', easter_point)
    feast_from_christmas = lookup_feast('christmas', "%02d-%02d" % (month, day))

    if feast_from_easter:
        possibles.append(feast_from_easter)

    if feast_from_christmas:
        possibles.append(feast_from_christmas)

    # Maybe transferred from yesterday.
    # Call recursively to look for yesterday feast and push to possibles
    if transferred is False:
        yestery, yesterm, yesterd = add_delta_days(days-1)

        transferred_feast = liturgical_calendar(s_date=f"{yestery}-{yesterm}-{yesterd}", transferred=True)

        if transferred_feast:
            transferred_feast['name'] = transferred_feast['name'] + ' (transferred)'
            # Sundays can't be transferred
            if transferred_feast['prec'] != 5:
                possibles.append(transferred_feast)


    # Maybe a Sunday
    # Shouldn't need to trap weekno=0 here, as the weekno increments on
    # a Sunday so it can never be less than 1 on a Sunday
    if dayofweek == 0:
        possibles.append({ 'prec': 5, 'type': 'Sunday', 'name': f"{season} {weekno}" })

    # So, which event takes priority?
    possibles = sorted(possibles, key=lambda x: x['prec'], reverse=True)

    if transferred:
        # If two feasts coincided today, we were asked to find
        # the one which got transferred.
        # But Sundays don't get transferred!
        try:
            if possibles[0] and possibles[0]['prec'] == 5:
                return None
            return possibles[1]
        except IndexError:
            return None

    # Get highest priority feast
    try:
        result = possibles.pop(0)
    except IndexError:
        result = { 'name': '', 'prec': 1 }

    # Render a Week name with or without number
    week, season = render_week_name(season, weekno)

    # Append season info regardless
    result['season'] = season
    result['season_url'] = season_url
    result['weekno'] = weekno
    result['week'] = week
    result['date'] = f_date
    result['weekday_reading'] = weekday_reading 

    # Support for special Sundays which are rose
    if result['name'] in [ 'Advent 3', 'Lent 4' ]:
        result['colour'] = 'rose'

    # If no colour is already set...
    if result.get('colour') is None:
        # If the priority is higher than a Lesser Festival, but not a Sunday...
        if result['prec'] > 4 and result['prec'] != 5:
            # It's a feast day.
            # Feasts are generally white, unless marked differently.
            # But martyrs are red
            if result.get('martyr'):
                result['colour'] = 'red'
            else:
                result['colour'] = 'white'
        else:
            # Not a feast day.
            # Set a default colour for the season
            if season == 'Advent':
                result['colour'] = 'purple'
            elif season == 'Christmas':
                result['colour'] = 'white'
            elif season == 'Epiphany':
                result['colour'] = 'white'
            elif season == 'Lent':
                result['colour'] = 'purple'
            elif season == 'Holy Week':
                result['colour'] = 'red'
            elif season == 'Easter':
                result['colour'] = 'white'
            else:
                # The great fallback:
                result['colour'] = 'green'

    # Two special cases for Christmas-based festivals which
    # depend on the day of the week.
    if result['prec'] == 5: # An ordinary Sunday
        if christmas_point == advent_sunday:
            result['name'] = 'Advent Sunday'
            result['colour'] = 'white'
        elif christmas_point == advent_sunday-7:
            result['name'] = 'Christ the King'
            result['colour'] = 'white'

    # Set colour code
    result['colourcode'] = colour_code(result['colour'])

    if 'readings' not in result:
        result['readings'] = get_readings_for_date(f_date.strftime("%Y-%m-%d"), result)
    else:
        if result['prec'] < 5:
            result['readings'] += get_readings_for_date(f_date.strftime("%Y-%m-%d"), result)

    return result

def main():
    """
    Display liturgical info to a human user
    """

    # Read in args
    if len(sys.argv) > 1:
        mydate = sys.argv[1]
    else:
        mydate = None

    info = liturgical_calendar(mydate)
    for key, value in info.items():
        print(key, ':', value)

if __name__ == '__main__':
    main()
