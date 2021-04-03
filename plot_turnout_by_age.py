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

ELECTION_FIELD = 'general_2020'
ELECTION_DATE = '2020-11-03'

def votes_by_age(county_id: int):
    """Reads voter data in json format and outputs votes aggregated by age for the specified election. """
    data = json.load(open(f'{JSON_FOLDER}/{county_id}.json', 'r'))
    by_age = {}
    for d in data:
        registration_age = get_age(d['registration_date'], ELECTION_DATE)
        if registration_age < 0:
            continue
        age = get_age(d['date_of_birth'], ELECTION_DATE)
        if age > 150:
            print(f'skipping unreasonable age {age}; data: {d}')
            continue
        if age not in by_age:
            by_age[age] = {'registered': 0, 'voted': 0}
        by_age[age]['registered'] += 1
        if d[ELECTION_FIELD].strip():
            by_age[age]['voted'] += 1
    return by_age

OUTPUT_FOLDER = './voters_by_age/'
import sys
import os

from matplotlib import pyplot as plt

if __name__ == '__main__':
    if len(sys.argv) > 1:
        county_id = int(sys.argv[1])

        by_age = votes_by_age(county_id)
        sorted_by_age = list(by_age.items())
        sorted_by_age.sort()
        age = [x[0] for x in sorted_by_age]
        voted = [by_age[x[0]]['voted'] for x in sorted_by_age]
        registered = [by_age[x[0]]['registered'] for x in sorted_by_age]
        plt.plot(age, voted)
        plt.plot(age, registered)
        plt.xlabel(f'Age')
        plt.ylabel('Voters or votes')
        plt.title(f'Ohio Voters or Votes vs. Age')
        plt.show()

        sys.exit()

    filenames = os.listdir(JSON_FOLDER)
    MINIMUM_REGISTERED_VOTERS = 50 # per age group
    MINIMUM_TOTAL_VOTERS = None # per county
    isolated_colors = None # plots these county ids in different colors from the rest
    print(f'plotting age groups with minimum of {MINIMUM_REGISTERED_VOTERS} registered voters.')
    counties_plotted = 0
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
            if isolated_colors:
                if county_id in isolated_colors:
                    plt.plot([age[i] for i in ii if registered[i] > MINIMUM_REGISTERED_VOTERS], [key[i] for i in ii if registered[i] > MINIMUM_REGISTERED_VOTERS], 'r')
                else:
                    plt.plot([age[i] for i in ii if registered[i] > MINIMUM_REGISTERED_VOTERS], [key[i] for i in ii if registered[i] > MINIMUM_REGISTERED_VOTERS], 'b')
            else:
                plt.plot([age[i] for i in ii if registered[i] > MINIMUM_REGISTERED_VOTERS], [key[i] for i in ii if registered[i] > MINIMUM_REGISTERED_VOTERS])
            counties_plotted += 1
        except:
            print(f'could not plot county_id {county_id}')
    print(f'plotted {counties_plotted} counties.')
    if MINIMUM_TOTAL_VOTERS is not None:
        print(f'skipped counties with less than {MINIMUM_TOTAL_VOTERS} voters.')
    plt.xlabel(f'Age (ages with less than {MINIMUM_REGISTERED_VOTERS} registered voters are hidden)')
    plt.ylabel('Normalized voter turnout (votes / registered voters / overall turnout fraction)')
    plt.title(f'Ohio Voter Turnout vs. Age ({counties_plotted} of {len(filenames)} counties; each line = 1 county)')

    plt.show()



