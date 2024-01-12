
# -*- coding: utf-8 -*-
"""
Created on Mon Dec  4 12:33:31 2023

@author: jdels
"""

import pandas as pd
import numpy as np
from matplotlib import pyplot as plt

# Three tabs - 'Olivine data', 'Opx data', 'Cpx data'
# (latter two are clinopyroxene and orthopyroxene data)

# read in data and remove NaNs

# this bit of code uses reasonably heavy use of a library called Pandas,
# which works nicely with data in this kind of spreadsheet format, and lets
# us work with the column headers to make sure we group samples/regions

# This is a test comment to see if editing a file in PyCharm updates it in Spyder.
def load_and_filter(input_file, mintype = 'olivine'):
    
    if mintype.lower() == 'olivine':
        sheet_name = 0
    elif mintype.lower() == 'orthopyroxene':
        sheet_name = 1
    elif mintype.lower() == 'clinopyroxene':
        sheet_name = 2
    else:
        raise ValueError('Mineral type should be olivine, orthopyroxene or clinopyroxene.')
    data = pd.read_excel(input_file, sheet_name = sheet_name).dropna()
    
    # First off - remove any data with total >101 or <99%
    data = data[(data.Total > 99) & (data.Total < 101)]
    # Then check mineral composition is sensible - 
    return data
# first define the scaling factors for different chemicals



def check_mineral_composition(data, names = ['Si', 'Ti', 'Al', 'Cr', 'Mn', 
                                     'Mg', 'Ni', 'Fe', 'Ca', 'Na', 'K'], 
                            mintype = 'olivine'):
    
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
        
        props[key] = data[key]/prop_scaling[key]
        
        cat_props[key] = props[key] * cat_scaling[key]
        ox_props[key] = props[key] * ox_scaling[key]

    ox_props['sum'] = np.sum([ox_props[key] for key in ox_props.keys()], axis = 0)
    
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

    cat_props['sum'] = np.sum([elements_out[key] for key in elements_out.keys()], axis = 0)

    ratios = {}

    
    Al_IV = np.zeros(len(elements_out['Si']))
    if 'olivine' in mintype.lower():
        # Fo=100.*Mg./(Fe+Mg);
        # Fa=100.*Fe./(Fe+Mg);
        ratios['Fo'] = elements_out['Mg'] / (elements_out['Fe'] + elements_out['Mg'])
        ratios['Fe'] = elements_out['Fe'] / (elements_out['Fe'] + elements_out['Mg'])
        
    elif 'pyroxene' in mintype.lower():
        
        ratios['En'] = 100 * elements_out['Mg'] / ( elements_out['Ca'] +  elements_out['Mg']
                                         +  elements_out['Fe'])
        ratios['Fs'] = 100 * elements_out['Fe'] / ( elements_out['Ca'] +  elements_out['Mg']
                                         +  elements_out['Fe'])
        ratios['Wo'] = 100 * elements_out['Ca'] / ( elements_out['Ca'] +  elements_out['Mg']
                                         +  elements_out['Fe'])
        ratios['MgN'] = 100 * elements_out['Mg'] / ( elements_out['Mg']
                                         +  elements_out['Fe'])
        for idx, Si_val in enumerate(elements_out['Si']):
            if Si_val < 2:
                
                if Si_val + elements_out['Al'].array[idx] < 2:
                    
                    Al_IV[idx] = elements_out['Al'].array[idx]
                    
                else:
                    Al_IV[idx] = 2 - Si_val
            else:
                Al_IV[idx] = 0
                
    # for idx, key in enumerate(names):
    #     if key not in data.columns:
    #         continue
    #     elements_out[key] = elements_out[key] * (cat_props['sum']/ox_props['sum']) / ox_scaling[key]
    
    # turn our dictionaries into Pandas DataFrame objects so we can manipulate 
    # them later with the Pandas library
    elements_out = pd.DataFrame.from_dict(elements_out)
    ratios = pd.DataFrame.from_dict(ratios)
    cat_props = pd.DataFrame.from_dict(cat_props)
    elements_out['Al_IV'] = Al_IV
    ox_props = pd.DataFrame.from_dict(ox_props)
    
    # Add metadata into our "elements" DataFrame from the initial input
    # elements_out[['Project Path (1)', 'Project Path (2)', 'Project Path (3)']] = \
    #     data[['Project Path (1)', 'Project Path (2)', 'Project Path (3)']]
    
    return elements_out, ratios, cat_props, ox_props
 


def cation_quality_check(data, elements, ratios, cat_props, error = 0.1, mintype = 'olivine'):
    # Error defines the range you're happy with either side of the target 
    # number, roughly 3 for olivine or 4 for pyroxene
    # We want this function to be some kind of middle ground between minimising
    # the error, but not discarding too many data points. 
    
    flag = True
    
    print(f'\n*******************************\nCation number quality checking for {mintype} input data\
          \n*******************************')
    
    # Keep allowing for changes to the error until the user is satisfied with 
    # the number of rejected samples
    while flag:
        init_num_samples = len(cat_props['sum'])
        if 'olivine' in mintype.lower():
            cation_count = 3
            print(f'\nCurrently accepting values within 3 ± {error}\n')

        elif 'pyroxene' in mintype.lower():  
            cation_count = 4
            print(f'\nCurrently accepting values within 4 ± {error}\n')
            
        new_cat_props = cat_props[(cation_count - error < cat_props['sum']) & (cat_props['sum'] < cation_count + error)]
        ratio = 100 * (init_num_samples - len(new_cat_props['sum']))/init_num_samples
        
        print(f"Removed {init_num_samples - len(new_cat_props['sum'])} of " \
              f"{init_num_samples} total samples ({ratio:.3f}%) based on current error limit")
        
        prompt = input('Accept this number of discarded values, or change the error limits?\n')
        yesses = ['y', 'yes', 'accept']
        nos = ['n', 'no', 'change']
       # print('\n') # newline to make it easier to see
        
        # if not happy - make sure the user inputs a numeric value else the code
        # will stay in this loop
        if prompt.lower().rstrip() in nos:
            
            errorflag = True
            
            while errorflag:
                try: 
                    error = float(input('Enter the new desired value for the error: \n'))
                except ValueError:
                    print('Please enter a numeric value for the error\n')
                else:
                    errorflag = False
        
        # else if we are happy then move on
        elif prompt.lower().rstrip() in yesses:
            flag = False
        # else if the user put a numeric value in then use this as the error
        elif prompt.replace('.', '').isnumeric().rstrip(): # replace . as this is a non numeric type
            error = float(prompt)
        # otherwise prompt the user to select a valid response
        else:
            print('Please enter yes, no or a new limit\n')
            
    # work out where the samples were removed and drop these from the DataFrame
    # i.e. discard them
    removed_indices = cat_props.index.difference(new_cat_props.index)
    cat_props = cat_props.drop(removed_indices)
    elements = elements.drop(removed_indices)
    ratios = ratios.drop(removed_indices)
    data = data.drop(removed_indices)
    
    return data, elements, ratios, cat_props
        

# steps above = quality control
# we then need to average over the samples (including this filtering), then perform the mineral analysis again
def average_over_samples(data):
    
    names = ['Si', 'Ti', 'Al', 'Cr', 'Mn', 'Mg', 'Ni', 'Fe', 'Ca', 'Na', 'K']
    # remove elements that aren't in the dataset else the code will throw an error
    for name in names:
        if name not in data.columns:
            names.remove(name)
            
    # get the number of measurements going into each region of each sample
    counts = data.value_counts(['Project Path (2)', 'Project Path (3)'])
    # take the mean of all of the regions of all of the samples, then add the number of 
    # measurements used to get this mean as as new variable
    data = data.groupby(['Project Path (2)', 'Project Path (3)'], sort = False)[names].mean()
    data['counts'] = counts
    return data


def get_opx_and_fo(olivine_data, pyroxene_data, x = 'Fo', y = 'Mg#'): 
    # the plot we want - x axis = olivine Fo, y axis = opx mg#
    # to do this then, we need to create a new dataset, grouping fo and mg# by sample

    
    # first take just the sample name and Fo from the olivines
    grouped_data = olivine_data[['Project Path (2)', x]]
    grouped_data = grouped_data.merge(pyroxene_data[['Project Path (2)', y]])
    # grouped_data.merge(clino_data[['Project Path (2)', 'Mg#']])
    return grouped_data
    
def make_rectangle_plot(grouped_data, scatter = False, fill = False,
                        x = 'Fo', y = 'Mg#',
                        x_mineral = 'Olivine', y_mineral = 'Opx'):
    
    grouped_data = get_opx_and_fo(oliv_data, ortho_data, x = x, y = y)
    # get min and max values
    grouped_min = grouped_data.groupby(['Project Path (2)']).min()
    grouped_min = grouped_min.rename(columns={x: f"{x}_min", y: f"{y}_min"})
    grouped_max = grouped_data.groupby(['Project Path (2)']).max()
    grouped_max = grouped_max.rename(columns={x: f"{x}_max", y: f"{y}_max"})
    # put into one DataFrame for convenience
    min_max = grouped_min.join(grouped_max)
    
    # create subplots - we use matplotlib's pyplot sub-library here, which
    # is designed to have similar syntax and functionality to MATLAB
    fig, ax = plt.subplots()
    i = 0 # iterator since we are looping over an iterator, easier than using enumerate here
          # its purpose is to ensure that the colours are consistent between the scatterplot and
          # the rectangles
    # define colours - since we are just colour coding and not using contours 
    # we can use jet 
    colours = plt.cm.jet(np.linspace(0, 1, len(grouped_min)))
    if scatter:
        for n, grp in grouped_data.groupby('Project Path (2)'):
            # s = size of marker, marker = type of marker - e.g. 'o' is a circle
            ax.scatter(x = x, y = y, data = grp, label = n, color = colours[i], marker = 'X', s = 20)
            i += 1
    else:
        # do a dummy plot for the legend labels to appear
        for n, grp in grouped_data.groupby('Project Path (2)'):
            # s = size of marker, marker = type of marker - e.g. 'o' is a circle, 's' is a square
            ax.scatter(np.nan, np.nan, label = n, color = colours[i], marker = 's', s = 20)
            i += 1 
    i = 0
    
    # add the rectangles by looping through each row of our dataframe 
    # (which has one row for each sample with the max and min values)
    # syntax for the rectangle is Rectangle((origin_x, origin_y), width, height)
    # so we first need to calculate the width and height
    # we can optionally fill the rectangle using fill = True or False,
    # which is an optional argument to make_rectangle_plot()
    for idx, val in min_max.iterrows():
        width = val[f'{x}_max'] - val[f'{x}_min']
        height = val[f'{y}_max'] - val[f'{y}_min']
        ax.add_patch(Rectangle((val[f'{x}_min'], val[f'{y}_min']), width, height,
                               fill = fill, color = colours[i],
                               linewidth = 3))
        i += 1
        
    # set figure visual properties - legends, grids, limits, labels
    # the limits are set to show the whole dataset currently - you can instead 
    # set them manually using plt.xlim(<xmin>, <xmax>) and plt.ylim(<ymin>, <ymax>)
    plt.xlim(grouped_min[f'{x}_min'].min() * 0.99 , grouped_max[f'{x}_max'].max() * 1.01)
    plt.ylim(grouped_min[f'{y}_min'].min() * 0.99, grouped_max[f'{y}_max'].max() * 1.01)
    plt.grid()
    plt.xlabel(f'{x_mineral} {x}', fontsize=20)
    plt.ylabel(f'{y_mineral} {y}', fontsize=20)
    # markerscale makes the coloured markers bigger on the legend so we can 
    # see them better
    plt.legend(markerscale = 3, fontsize = 15)
    
    
# take all of the stuff we calculated previously and write each into an output
# spreadsheet 
def save_to_xlsx(data):
    #Sample name; area name; the number of datapoints averaged; 
    # average concentrations for each of the elements measured (plus its total);
    # mineral formula of this average.
    
    pass
    
    
    
    
# everything below here actually runs the code. the "if name = main" section 
# means the below will only run if you run this script directly, but not if you 
# import it into another script (e.g. if you just want the functions, but want
# to put the analysis in another script for neatness/ease of reading)
if __name__ == '__main__':
    # this section uses the functions we defined earlier and calls them to 
    # perform the analysis
    
    # load in the data from the spreadsheet and separate each tab into a different
    # DataFrame
    oliv_data = load_and_filter('Data compilation U1601C.xlsx', mintype = 'olivine')
    ortho_data = load_and_filter('Data compilation U1601C.xlsx', mintype = 'orthopyroxene')
    clino_data = load_and_filter('Data compilation U1601C.xlsx', mintype = 'clinopyroxene') 
    
    # check the mineral composition - perform the scaling, calculate Fo etc. 
    oliv_elements, oliv_ratios, oliv_cat_props, oliv_ox_props = \
        check_mineral_composition(oliv_data, mintype = 'olivine')
        
    ortho_elements, ortho_ratios, ortho_cat_props, ortho_ox_props = \
        check_mineral_composition(ortho_data, mintype = 'pyroxene')
        
    clino_elements, clino_ratios, clino_cat_props, clino_ox_props = \
        check_mineral_composition(clino_data, mintype = 'pyroxene')

    
    oliv_data, oliv_elements, oliv_ratios, oliv_cat_props = cation_quality_check(oliv_data, oliv_elements, oliv_ratios, oliv_cat_props)
    clino_data, clino_elements, clino_ratios, clino_cat_props, = cation_quality_check(clino_data, clino_elements, clino_ratios, clino_cat_props,
                         mintype = 'clinopyroxene')


    oliv_agg_data = average_over_samples(oliv_data)
    
    oliv_agg_elements, oliv_agg_ratios, oliv_agg_cat_props, oliv_agg_ox_props = \
        check_mineral_composition(oliv_agg_data, mintype = 'olivine')
    
    
    ortho_agg_data = average_over_samples(ortho_data)
    
    ortho_agg_elements, ortho_agg_ratios, ortho_agg_cat_props, ortho_agg_ox_props = \
        check_mineral_composition(ortho_agg_data, mintype = 'orthopyroxene')
    
    
    import matplotlib.pyplot as plt
    from matplotlib.collections import PatchCollection
    from matplotlib.patches import Rectangle
    grouped_data = get_opx_and_fo(oliv_data, ortho_data)
    
    # default - scatter = False
    make_rectangle_plot(grouped_data)
    make_rectangle_plot(grouped_data, scatter = True)
    make_rectangle_plot(grouped_data, scatter = False, fill = True)













