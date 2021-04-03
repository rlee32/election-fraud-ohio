#!/usr/bin/env python3

# plots prediction vs actual votes in specified county.

def str_to_int(date):
    """Converts date in form YYYY-MM-DD to and integer of form YYYYMMDD. """
    return int(date.replace('-', ''))

def get_age(start_date, end_date):
    """Returns integer age given dates in form YYYY-MM-DD. """
    start = str_to_int(start_date)
    end = str_to_int(end_date)
    diff = end - start
    if diff < 0:
        return diff / 10000.0
    else:
        return int(diff / 10000)

from jsonify import OUTPUT_FOLDER as JSON_FOLDER
import json

ELECTION_YEAR = 2020 # choose presidential election years from 2000 - 2020

ELECTION_DAY = {
    2020: '03',
    2016: '08',
    2012: '06',
    2008: '04',
    2004: '02',
    2000: '07'
}

ELECTION_DATE = f'{ELECTION_YEAR}-11-{ELECTION_DAY[ELECTION_YEAR]}'
ELECTION_FIELD = f'general_{ELECTION_YEAR}'

def votes_by_age(county_id: int):
    """Reads voter data in json format and outputs votes aggregated by age for the specified election. """
    data = json.load(open(f'{JSON_FOLDER}/{county_id}.json', 'r'))
    by_age = {}
    for d in data:
        registration_age = get_age(d['registration_date'], ELECTION_DATE)
        if registration_age < 0:
            continue
        age = get_age(d['date_of_birth'], ELECTION_DATE)
        if age < 18:
            print(f'skipping underage {age}; data: {d}')
            continue
        if age > 150:
            print(f'skipping unreasonable age {age}; data: {d}')
            continue
        if age not in by_age:
            by_age[age] = {'registered': 0, 'voted': 0}
        by_age[age]['registered'] += 1
        if d[ELECTION_FIELD].strip():
            by_age[age]['voted'] += 1
    return by_age

import sys
import os

from matplotlib import pyplot as plt

from generate_key import OUTPUT_FILE as KEY_FILE

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('arguments: county_id')
        sys.exit()

    county_id = int(sys.argv[1])

    # Finally, plot predicted vs. actual votes.
    by_age = votes_by_age(county_id)
    sorted_by_age = list(by_age.items())
    sorted_by_age.sort()

    age = [x[0] for x in sorted_by_age]
    voted = [by_age[x[0]]['voted'] for x in sorted_by_age]
    registered = [by_age[x[0]]['registered'] for x in sorted_by_age]

    overall_turnout = sum(voted) / sum(registered)
    key = json.load(open(KEY_FILE, 'r'))
    ii = range(len(registered))
    prediction = [key[str(age[i])] * overall_turnout * registered[i] for i in ii]

    MINIMUM_REGISTERED_VOTERS = 50 # per age group
    print(f'plotting age groups with minimum of {MINIMUM_REGISTERED_VOTERS} registered voters.')
    plt.plot([age[i] for i in ii if registered[i] > MINIMUM_REGISTERED_VOTERS], [voted[i] for i in ii if registered[i] > MINIMUM_REGISTERED_VOTERS], 'r-')
    plt.plot([age[i] for i in ii if registered[i] > MINIMUM_REGISTERED_VOTERS], [prediction[i] for i in ii if registered[i] > MINIMUM_REGISTERED_VOTERS], 'b:')

    plt.xlabel(f'Age (ages with less than {MINIMUM_REGISTERED_VOTERS} registered voters are hidden)')
    plt.ylabel('Votes (blue is prediction, red is actual)')
    plt.title(f'{ELECTION_YEAR} Ohio County ID {county_id}: Prediction of Votes Cast vs. Age')
    plt.show()


    plt.show()



