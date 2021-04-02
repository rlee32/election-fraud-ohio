#!/usr/bin/env python3

# aggregates voters by age.

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
OUTPUT_FOLDER = './by_age/'
import json

def general_2020_by_age(county_id: int):
    """Reads voter data in json format and outputs votes aggregated by age for the 2020 general election. """
    data = json.load(open(f'{JSON_FOLDER}/{county_id}.json', 'r'))
    by_age = {}
    for d in data:
        registration_age = get_age(d['registration_date'], '2020-11-03')
        if registration_age < 0:
            continue
        age = get_age(d['date_of_birth'], '2020-11-03')
        if age not in by_age:
            by_age[age] = {'registered': 0, 'voted': 0}
        by_age[age]['registered'] += 1
        if d['general_2020'].strip():
            by_age[age]['voted'] += 1
    return by_age


OUTPUT_FOLDER = './voters_by_age/'
import sys
import os

from matplotlib import pyplot as plt

if __name__ == '__main__':
    filenames = os.listdir(JSON_FOLDER)
    MINIMUM_REGISTERED_VOTERS = 50
    print(f'plotting age groups with minimum of {MINIMUM_REGISTERED_VOTERS} registered voters.')
    counties_plotted = 0
    for f in filenames:
        if f[-5:] != '.json':
            continue
        try:
            county_id = int(f.split('.')[0])
            by_age = general_2020_by_age(county_id)
            sorted_by_age = list(by_age.items())
            sorted_by_age.sort()
            plt.plot([x[0] for x in sorted_by_age if by_age[x[0]]['registered'] > MINIMUM_REGISTERED_VOTERS], [by_age[x[0]]['voted'] / by_age[x[0]]['registered'] for x in sorted_by_age if by_age[x[0]]['registered'] > MINIMUM_REGISTERED_VOTERS])
            counties_plotted += 1
        except:
            print(f'could not plot county_id {county_id}')
    print(f'plotted {counties_plotted} counties.')
    plt.xlabel('age')
    plt.ylabel('ratio of votes to registered voters')
    plt.title(f'Ohio Voter Turnout vs. Age ({counties_plotted} counties; each line = 1 county)')
    plt.show()



