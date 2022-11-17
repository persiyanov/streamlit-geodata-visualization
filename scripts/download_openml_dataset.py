import os

import click
import openml
import pandas as pd


def load_dataset(id: int) -> pd.DataFrame:
    # https://www.openml.org/search?type=data&status=active&sort=match&id=<id>
    dataset = openml.datasets.get_dataset(id)
    data, _, _, _ = dataset.get_data(
        target=dataset.default_target_attribute, dataset_format='dataframe'
    )
    return data


def save_data(data: pd.DataFrame, dest: str, sample_n: int):
    data.to_csv(os.path.join(dest, 'data.csv'), index=False)
    data.sample(sample_n).to_csv(os.path.join(dest, 'data_small.csv'), index=False)


@click.command()
@click.option('--id', default=43633, help='OpenML dataset ID', type=int)
@click.option(
    '--dest',
    type=click.Path(exists=True, file_okay=False),
    default='.',
    help='Destination directory',
)
@click.option(
    '--sample-n',
    default=20_000,
    help='Number of samples for small version of dataset',
    type=int,
)
def main(id: int, dest: str, sample_n: int):
    data = load_dataset(id)
    save_data(data, dest, sample_n)


if __name__ == '__main__':
    main()
