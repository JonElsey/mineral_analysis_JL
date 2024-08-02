# steps above = quality control
# we then need to average over the samples (including this filtering), then perform the mineral analysis again
import pandas as pd
import numpy as np
def average_over_areas(data):
    """
    Average over the samples to obtain a new DataFrame which contains the same data,
    but as an average for each area.

    Args:
        data: input DataFrame that you wish to average over.

    Returns:
        data: as input argument data, but now with the areas averaged.
    """
    names = ['Si', 'Ti', 'Al', 'Cr', 'Mn', 'Mg', 'Ni', 'Fe', 'Ca', 'Na', 'K']
    # remove elements that aren't in the dataset else the code will throw an error
    for name in names:
        if name not in data.columns:
            names.remove(name)

    # get the number of measurements going into each region of each sample
    counts = data.value_counts(['Project Path (2)', 'Project Path (3)'])
    # take the mean of all the regions of all the samples, then add the number of
    # measurements used to get this mean as a new variable
    data = data.groupby(['Project Path (2)', 'Project Path (3)'], sort=False)[names].mean()
    data['counts'] = counts
    agg_data = data
    return agg_data

def average_over_samples(agg_data):
    """
    Average over the samples to obtain a new DataFrame which contains the same data,
    but as an average for each *sample*.

    Args:
        data: input DataFrame that you wish to average over, which should be of the area averages.

    Returns:
        data: as input argument data, but now with the samples averaged.
    """
    names = ['Si', 'Ti', 'Al', 'Cr', 'Mn', 'Mg', 'Ni', 'Fe', 'Ca', 'Na', 'K']
    # remove elements that aren't in the dataset else the code will throw an error
    for name in names:
        if name not in agg_data.columns:
            names.remove(name)

    # get the number of areas going into each region of each sample
    counts = agg_data.value_counts(['Project Path (2)']).reset_index()
    # take the mean of all the regions of all the samples, then add the number of
    # measurements used to get this mean as a new variable
    agg_data = agg_data.groupby(['Project Path (2)'], sort=False)[names].mean()
    agg_data['counts'] = counts.set_index(agg_data.index)['count']
    # calculate 2sd and deltas
    for mineral in names:
        agg_data[f'2SD_{mineral}'] = np.std(agg_data[mineral]) * 2
    for mineral in names:
        agg_data[f'delta_{mineral}'] = agg_data[mineral].max() - agg_data[mineral].min()

    sample_average_data = agg_data
    return sample_average_data
