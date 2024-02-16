import numpy as np
import pandas as pd


def check_mineral_composition(data, names=('Si', 'Ti', 'Al', 'Cr', 'Mn',
                                           'Mg', 'Ni', 'Fe', 'Ca', 'Na', 'K'),
                              mintype='olivine'):
    """
    Determine the mineral formula for the specified mineral type.

    Args:
        data: Pandas DataFrame containing the loaded-in data from inout.load_and_filter.
        names: Element names to check for. In the file provided, all of these are included
               except potassium (K).
        mintype: Mineral type (default 'olivine') for which to perform this analysis.
                 Used as the output element ratios we want to obtain are different
                 depending on mineral type.

    Returns:
        elements_out: Pandas DataFrame containing the results of the mineral composition calculation.
        ratios: Pandas DataFrame containing the calculated element ratios (e.g. MgN, Wo, En, Fs)
        cat_props: Pandas DataFrame of cation properties. Should sum to 3 (for olivine) or 4 (for pyroxene).
        ox_props: Pandas DataFrame of oxygen numbers for each element.
    """

    # scale factors taken from Johan's MATLAB code
    prop_scalefactors = [60.08, 79.9, 101.96, 151.99, 70.94, 40.305, 74.7, 71.85, 56.08, 61.98, 94.2]
    cat_scalefactors = [1, 1, 2, 2, 1, 1, 1, 1, 1, 2, 2]
    ox_scalefactors = [2, 2, 3, 3, 1, 1, 1, 1, 1, 1, 1]
    props = {}
    cat_props = {}
    ox_props = {}
    prop_scaling = {}
    cat_scaling = {}
    ox_scaling = {}
    elements_out = {}

    # write the scaling factors and resulting values into dictionaries
    # in case we need them later
    for idx, key in enumerate(names):
        # skip elements where we don't have data - e.g. potassium in the file Johan sent
        if key not in data.columns:
            continue

        prop_scaling[key] = prop_scalefactors[idx]
        cat_scaling[key] = cat_scalefactors[idx]
        ox_scaling[key] = ox_scalefactors[idx]

        props[key] = data[key] / prop_scaling[key]

        cat_props[key] = props[key] * cat_scaling[key]
        ox_props[key] = props[key] * ox_scaling[key]

    ox_props['sum'] = np.sum([ox_props[key] for key in ox_props.keys()], axis=0)

    if 'olivine' in mintype.lower():
        ox_factor = 4 / ox_props['sum']

    elif 'pyroxene' in mintype.lower():
        ox_factor = 6 / ox_props['sum']

    else:
        raise ValueError('Rock type not recognised, should be "olivine" or "pyroxene"')

    for idx, key in enumerate(names):
        # skip elements where we don't have data - e.g. potassium in the file Johan sent
        if key not in data.columns:
            continue

        elements_out[key] = ox_factor * cat_props[key]

    cat_props['sum'] = np.sum([elements_out[key] for key in elements_out.keys()], axis=0)

    ratios = {}

    Al_IV = np.zeros(len(elements_out['Si']))
    if 'olivine' in mintype.lower():
        # Fo=100.*Mg./(Fe+Mg);
        # Fa=100.*Fe./(Fe+Mg);
        ratios['Fo'] = elements_out['Mg'] / (elements_out['Fe'] + elements_out['Mg'])
        ratios['Fe'] = elements_out['Fe'] / (elements_out['Fe'] + elements_out['Mg'])

    elif 'pyroxene' in mintype.lower():

        ratios['En'] = elements_out['Mg'] / (elements_out['Ca'] + elements_out['Mg']
                                             + elements_out['Fe'])  # * 100
        ratios['Fs'] = elements_out['Fe'] / (elements_out['Ca'] + elements_out['Mg']
                                             + elements_out['Fe'])  # * 100
        ratios['Wo'] = elements_out['Ca'] / (elements_out['Ca'] + elements_out['Mg']
                                             + elements_out['Fe'])
        ratios['Mg#'] = elements_out['Mg'] / (elements_out['Mg']  # * 100
                                              + elements_out['Fe'])  # * 100
        for idx, Si_val in enumerate(elements_out['Si']):
            if Si_val < 2:

                if Si_val + elements_out['Al'].array[idx] < 2:

                    Al_IV[idx] = elements_out['Al'].array[idx]

                else:
                    Al_IV[idx] = 2 - Si_val
            else:
                Al_IV[idx] = 0

    # turn our dictionaries into Pandas DataFrame objects, so we can manipulate
    # them later with the Pandas library
    elements_out = pd.DataFrame.from_dict(elements_out)
    ratios = pd.DataFrame.from_dict(ratios)
    cat_props = pd.DataFrame.from_dict(cat_props)
    elements_out['Al_IV'] = Al_IV
    ox_props = pd.DataFrame.from_dict(ox_props)

    return elements_out, ratios, cat_props, ox_props


# steps above = quality control
# we then need to average over the samples (including this filtering), then perform the mineral analysis again
def average_over_samples(data):
    """
    Average over the samples to obtain a new DataFrame which contains the same data,
    but as an average for each area.

    Args:
        data: input DataFrame that you wish to average over.

    Returns:
        data: as input argument data, but now with the samples averaged.
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
    return data
