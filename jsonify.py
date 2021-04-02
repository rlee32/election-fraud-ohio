#!/usr/bin/env python3

# converts all CSVs from state website residing in VOTER_DATABASE_FOLDER to more human friendly json in OUTPUT_FOLDER.
# ignores fields / columns not used in present analysis.

OUTPUT_FOLDER = './jsonified/'

import csv
from download_voter_database import VOTER_DATABASE_FOLDER

def print_header(filepath):
    with open(filepath, 'r') as f:
        csv_reader = csv.reader(f)
        for row in csv_reader:
            header = row
            break
        i = 0
        for col in header:
            print(col, i)
            i += 1

# column indices
DATE_OF_BIRTH = 7
REGISTRATION_DATE = 8
VOTER_STATUS = 9
GENERAL_2020 = 109 # voting record for General Presidential Election 2020. blank means no vote.

def convert_csv(filepath):
    with open(filepath, 'r') as f:
        csv_reader = csv.reader(f)
        line_count = 0
        new_items = []
        for row in csv_reader:
            header = row
            break
        statuses = {}
        votes = {}
        for row in csv_reader:
            voter_status = row[VOTER_STATUS]
            general_2020 = row[GENERAL_2020]
            new_items.append({
                'date_of_birth': row[DATE_OF_BIRTH],
                'registration_date': row[REGISTRATION_DATE],
                'voter_status': voter_status,
                'general_2020': general_2020
            })
            if voter_status not in statuses:
                statuses[voter_status] = 0
            if general_2020 not in votes:
                votes[general_2020] = 0
            statuses[voter_status] += 1
            votes[general_2020] += 1

        print(f'voter statuses: {statuses}')
        print(f'vote types: {votes}')
        return new_items

import sys
import os
import json

if __name__ == '__main__':
    os.system(f'mkdir -p {OUTPUT_FOLDER}')
    filenames = os.listdir(VOTER_DATABASE_FOLDER)
    already_output = set(os.listdir(OUTPUT_FOLDER))
    for f in filenames:
        if f in already_output:
            print(f'skipping {f}; already in {OUTPUT_FOLDER}')
            continue
        if f[-4:] != '.csv':
            continue
        try:
            county_id = int(f.split('.')[0])
            print(f'converting county_id {county_id}')

            filepath = f'{VOTER_DATABASE_FOLDER}/{county_id}.csv'
            new_items = convert_csv(filepath)
            print(f'got {len(new_items)} voters for county_id {county_id}.')
            json.dump(new_items, open(f'{OUTPUT_FOLDER}/{county_id}.json', 'w'), indent=2)
        except:
            print(f'\n\ncould not jsonify county_id {county_id}\n\n')


