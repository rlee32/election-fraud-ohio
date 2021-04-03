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

def convert_csv(filepath):
    with open(filepath, 'r') as f:
        csv_reader = csv.reader(f)
        new_items = []
        for row in csv_reader:
            header = row
            break

        # determine column indices.
        date_of_birth_index = header.index('DATE_OF_BIRTH')
        registration_date_index = header.index('REGISTRATION_DATE')
        voter_status_index = header.index('VOTER_STATUS')
        general_2016_index = header.index('GENERAL-11/08/2016')
        general_2020_index = header.index('GENERAL-11/03/2020')
        general_2000_index = header.index('GENERAL-11/07/2000')
        general_2004_index = header.index('GENERAL-11/02/2004')
        general_2008_index = header.index('GENERAL-11/04/2008')
        general_2012_index = header.index('GENERAL-11/06/2012')

        statuses = {}
        for row in csv_reader:
            voter_status = row[voter_status_index]
            new_items.append({
                'date_of_birth': row[date_of_birth_index],
                'registration_date': row[registration_date_index],
                'voter_status': voter_status,
                'general_2000': row[general_2000_index],
                'general_2016': row[general_2016_index],
                'general_2020': row[general_2020_index],
                'general_2004': row[general_2004_index],
                'general_2008': row[general_2008_index],
                'general_2012': row[general_2012_index],
            })
            if voter_status not in statuses:
                statuses[voter_status] = 0
            statuses[voter_status] += 1

        print(f'voter statuses: {statuses}')
        return new_items

import sys
import os
import json

if __name__ == '__main__':
    os.system(f'mkdir -p {OUTPUT_FOLDER}')
    filenames = os.listdir(VOTER_DATABASE_FOLDER)
    already_output = set(os.listdir(OUTPUT_FOLDER))
    failures = 0
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
            failures += 1
    print(f'failed to jsonify {failures} counties.')

