# steps above = quality control
# we then need to average over the samples (including this filtering), then perform the element analysis again
import pandas as pd
import numpy as np
def average_over_areas(data):
    """
    Average over the samples to obtain a new DataFrame which contains the same data,
    but as an average for each *area* within a given sample.

    Args:
        data: input DataFrame that you wish to average over.

    Returns:
        data: as input argument data, but now with the areas averaged.
    """
    names = ['Depth', 'Si', 'Ti', 'Al', 'Cr', 'Mn', 'Mg', 'Ni', 'Fe', 'Ca', 'Na', 'K'
             ]
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

def average_over_samples(agg_data, oxides=True):
    """
    Average over the samples to obtain a new DataFrame which contains the same data,
    but as an average for each *sample*.

    Args:
        data: input DataFrame that you wish to average over, which should be of the area averages.

    Returns:
        data: as input argument data, but now with the samples averaged.
    """
    if oxides:
        names = ['Depth', 'Si', 'Ti', 'Al', 'Cr', 'Mn', 'Mg', 'Ni', 'Fe', 'Ca', 'Na', 'K']
    # remove elements that aren't in the dataset else the code will throw an error
        for name in names:
            if name not in agg_data.columns:
                names.remove(name)
        # calculate 2sd and deltas
    else:
        names = [name for name in agg_data.columns]
        # remove some that we don't want to average
        names_to_remove = ['counts']
        for name in names:
            if name in names_to_remove:
                names.remove(name)

    # calculate 2 * standard deviation of the data to be averaged, and the max - min
    sd = {}
    delta = {}
    for element in names:
        sd[f'2SD_{element}'] = agg_data[element].groupby('Project Path (2)').std() * 2
        delta[f'delta_{element}'] = (agg_data[element].groupby('Project Path (2)').max() -
                                        agg_data[element].groupby('Project Path (2)').min())

    # get the number of areas going into each region of each sample
    counts = agg_data.value_counts(['Project Path (2)'], sort=False)
    # take the mean of all the regions of all the samples, then add the number of
    # measurements used to get this mean as a new variable
    agg_data = agg_data.groupby(['Project Path (2)'], sort=False)[names].mean()
    # only need to generate the counts column once so do it when we analyse the oxide data

    if oxides:
        counts.index = counts.index.get_level_values(0)
        agg_data['counts'] = counts#.set_index(agg_data.index)['count']

    for element in names:
        if element in ['Depth']:
            continue
        # write the standard deviation into the variable by first converting to str
        agg_data[element] = agg_data[element].round(4).astype(str) + ' ± ' + sd[f'2SD_{element}'].round(3).astype(str)
        agg_data[f'delta_{element}'] = delta[f'delta_{element}']

    sample_average_data = agg_data
    return sample_average_data
