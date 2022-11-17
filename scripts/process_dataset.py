import os

import click
import pandas as pd
import tqdm
from dotenv import find_dotenv, load_dotenv
from geopy.geocoders import MapBox
from loguru import logger
from retry import retry

load_dotenv(find_dotenv('secrets.env'))


MAPBOX_TOKEN = os.environ.get('MAPBOX_TOKEN')
assert MAPBOX_TOKEN, 'Please, configure "secrets.env" file with MAPBOX_TOKEN variable.'

GEOLOCATOR = MapBox(api_key=MAPBOX_TOKEN)


@retry(tries=5, delay=1, backoff=2)
def geocode(addr):
    return GEOLOCATOR.geocode(addr, country='US', timeout=5)


def add_coordinates_to_data(data: pd.DataFrame, address_col: str):
    data['lon'], data['lat'] = None, None
    for idx, row in tqdm.tqdm(data.iterrows(), total=len(data)):
        lon, lat = parse_coordinates(row, address_col=address_col)
        data.loc[idx, ['lon', 'lat']] = [lon, lat]


def parse_coordinates(row: pd.Series, address_col: str) -> dict:
    data = [None, None]
    try:
        location = geocode(row[address_col]).raw
        if location is not None and 'center' in location:
            data = location['center']
    except Exception as e:
        logger.warning(str(e))
    finally:
        return data


def normalize_address(addr):
    return ','.join([x.strip().lower() for x in addr.split(',')])


def extract_mapbox_friendly_address(addr):
    return ', '.join(['new york', addr])


@click.command()
@click.option('--infile', type=click.Path(exists=True, dir_okay=False), required=True)
@click.option('--outfile', type=click.Path(exists=True, dir_okay=False), required=True)
@click.option('--address-col', default='ADDRESS')
def main(infile: str, outfile: str, address_col: str):
    normalized_address_col = f'Normalized_{address_col}'
    mapbox_address_col = f'Mapbox_{address_col}'

    data = pd.read_csv(infile)
    data[normalized_address_col] = data[address_col].map(normalize_address)
    data[mapbox_address_col] = data[normalized_address_col].map(
        extract_mapbox_friendly_address
    )
    add_coordinates_to_data(data, address_col=address_col)

    location_found_cnt = data['lon'].notna().sum()
    logger.info(
        f'Parsed coordinates for {location_found_cnt} out of {len(data)} ({location_found_cnt / len(data) * 100:.2f}%) objects'
    )

    data.to_csv(outfile, index=False)


if __name__ == '__main__':
    main()
