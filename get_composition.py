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

    if 'olivine' in mintype.lower() or 'spinel' in mintype.lower():
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


    if 'spinel' in mintype.lower():
        """
        Spinel calculation
        """
        O_sum_temp2 = (3 / cat_props['sum']) * (
                    2 * elements_out['Ti'] + 1.5 * elements_out['Al'] + 1.5 * elements_out['Cr'] + elements_out['Fe'] + \
                    elements_out['Mn'] + elements_out['Mg'])
        O_def = 4 - O_sum_temp2
        Fe3 = 2 * O_def
        Fe2 = elements_out['Fe'] * (3 / cat_props['sum']) - Fe3
        cat_tot_temp2 = cat_props['sum'] - elements_out['Fe'] + Fe3 + Fe2
        O_sum_temp3 = (3 / cat_tot_temp2) * (
                    2 * elements_out['Ti'] + 1.5 * elements_out['Al'] + 1.5 * elements_out['Cr'] + Fe2 + 1.5 * Fe3 +
                    elements_out['Mn'] + elements_out['Mg'])
        cat_factor = (3 - Fe2 - Fe3) / (elements_out['Ti'] + elements_out['Al'] + elements_out['Cr'] +
                                         elements_out['Mn'] + elements_out['Mg'])

        # overwrite the temporary values with the correct values
        for idx, key in enumerate(elements_out.keys()):
            if key in ['Ti', 'Al', 'Cr', 'Mn', 'Mg', 'Fe']:
                elements_out[key] = elements_out[key] * cat_factor

        # cat_tot = np.sum(np.array([elements_out[key] for key in elements_out.keys() \
        #                            if key in ['Ti', 'Al', 'Cr', 'Mn', 'Mg', 'Fe']]), axis=0) + Fe2 + Fe3
        cat_tot = elements_out['Ti'] + elements_out['Al'] + elements_out['Cr'] + elements_out['Mn'] + elements_out['Mg'] \
                        + elements_out['Fe'] + Fe2 + Fe3
        ox_Ti = 2. * elements_out['Ti']
        ox_Al = 1.5 * elements_out['Al']
        ox_Cr = 1.5 * elements_out['Cr']
        ox_Mn = elements_out['Mn']
        ox_Mg = elements_out['Mg']
        ox_Fe2 = Fe2
        ox_Fe3 = 1.5 * Fe3
        O_sum = ox_Ti + ox_Al + ox_Cr + ox_Mn + ox_Mg + ox_Fe2 + ox_Fe3
        ratios['CrN'] = 100 * elements_out['Cr'] / (elements_out['Cr'] + elements_out['Al'])
        ratios['MgN'] = 100 * elements_out['Mg'] / (Fe2 + elements_out['Mg'])
        ox_props['O_sum'] = O_sum
        cat_props['cat_tot'] = cat_tot

    elif 'olivine' in mintype.lower():
        """
        Olivine calculation
        """
        # Fo=100.*Mg./(Fe+Mg);
        # Fa=100.*Fe./(Fe+Mg);
        ratios['Fo'] = elements_out['Mg'] / (elements_out['Fe'] + elements_out['Mg'])
        ratios['Fe'] = elements_out['Fe'] / (elements_out['Fe'] + elements_out['Mg'])

    elif 'pyroxene' in mintype.lower():
        """
        Pyroxene calculation
        """

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
    # Stick depth column into oxide properties - to keep around for later
    try:
        ox_props['Depth'] = data['Depth']
    except Exception as e:
        print(e)
        print('No depth column found in input data - output will not have it either')
    # turn our dictionaries into Pandas DataFrame objects, so we can manipulate
    # them later with the Pandas library
    elements_out = pd.DataFrame.from_dict(elements_out)
    ratios = pd.DataFrame.from_dict(ratios)
    cat_props = pd.DataFrame.from_dict(cat_props)
    elements_out['Al_IV'] = Al_IV
    ox_props = pd.DataFrame.from_dict(ox_props)

    return elements_out, ratios, cat_props, ox_props


def calc_ratio_uncertainty(ratios):
    """
    Calculate the 2SD and delta (max - min) for the ratios (e.g. Fo).

    Args:
        ratios: Dictionary of ratios to get the standard deviation of.

    Returns:
        ratios: amended dictionary
    """
    keys = [key for key in ratios.keys()]
    for key in keys:
        ratios[f'2SD_{key}'] = np.std(ratios[key]) * 2
        ratios[f'delta_{key}'] = np.max(ratios[key]) - np.min(ratios[key])
    return ratios