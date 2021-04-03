#!/usr/bin/env python3

import os

VOTER_DATABASE_FOLDER = './voter_database'

def get_county(county_id: int, destination_folder: str = VOTER_DATABASE_FOLDER):
    """County ID ranges from 1 to 88, one for each county in Ohio.
    """
    os.system(f'curl https://www6.ohiosos.gov/ords/f?p=VOTERFTP:DOWNLOAD::FILE:NO:2:P2_PRODUCT_NUMBER:{county_id} -o {destination_folder}/{county_id}.csv')

if __name__ == '__main__':
    total_counties = 88
    print(f'downloading voter registration database for all {total_counties} counties')
    os.system(f'mkdir -p {VOTER_DATABASE_FOLDER}')
    for i in range(total_counties):
        get_county(i + 1)
        print(f'\ndownloaded {i + 1} / {total_counties} files.\n')
