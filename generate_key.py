#!/usr/bin/env python3

# looks at all available counties and computes a conversion key that can be used to predict actual turnout from registrations.

OUTPUT_FILE = './key.json'

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

if __name__ == '__main__':
    filenames = os.listdir(JSON_FOLDER)
    MINIMUM_TOTAL_VOTERS = None # per county
    counties_used = 0
    turnouts = {} # maps age to a list of conversion key (normalized turnout) values.
    for f in filenames:
        if f[-5:] != '.json':
            continue
        try:
            county_id = int(f.split('.')[0])
            by_age = votes_by_age(county_id)
            sorted_by_age = list(by_age.items())
            sorted_by_age.sort()
            age = [x[0] for x in sorted_by_age]
            voted = [by_age[x]['voted'] for x in age]
            registered = [by_age[x]['registered'] for x in age]
            overall_turnout = sum(voted) / sum(registered)
            print(f'county {county_id} has {sum(registered)} registered voters')
            if MINIMUM_TOTAL_VOTERS is not None and sum(registered) < MINIMUM_TOTAL_VOTERS:
                continue
            ii = range(len(registered))
            key = [voted[i] / registered[i] / overall_turnout for i in ii]
            for i in ii:
                a = age[i]
                if a not in turnouts:
                    turnouts[a] = []
                turnouts[a].append(key[i])
            counties_used += 1
        except Exception as e:
            print(f'could not use county_id {county_id}')
            print(e)
    print(f'used {counties_used} counties.')

    if MINIMUM_TOTAL_VOTERS is not None:
        print(f'skipped counties with less than {MINIMUM_TOTAL_VOTERS} voters.')

    # finally, write out key as json.
    for age in turnouts:
        counts = turnouts[age]
        avg = sum(counts) / len(counts)
        turnouts[age] = avg

    json.dump(turnouts, open(OUTPUT_FILE, 'w'))
    print(f'wrote key to {OUTPUT_FILE}')
