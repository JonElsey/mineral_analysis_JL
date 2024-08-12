# -*- coding: utf-8 -*-
"""
@author: Jon Elsey (ElseyJ1@cardiff.ac.uk)
"""

from get_composition import check_mineral_composition
from averaging import average_over_areas, average_over_samples
from inout import load_and_filter, get_data_filename, save_to_xlsx, group_output_data
from quality_checking import cation_quality_check
from plotting_functions import get_rectangle_plot_data, make_rectangle_plot

# load in the data from the spreadsheet and separate each tab into a different
# DataFrame. This will prompt you to select a file from whatever file browser
# your system uses. If you want to specify a filename directly (e.g. if automating
# the analysis of many data files), you can add fname = '<your_file_name>' as an
# argument to get_data_filename.

"""
Variables that handle input/output are stored here.
"""
output_data_fname = 'output_data.xlsx'
output_figure_fname = 'rectangle_plot.eps'
output_figure_format = 'eps'  # eps to save to eps, png to save to png, etc.
# Replace False with '<your_filename>' if you don't want to use the browser
# (e.g. if automating this with a script)
data_filename = get_data_filename(fname='INPUT_depthtest.xls')

# Load in the data and perform simple filtering to remove outliers
mintypes = ['olivine', 'orthopyroxene', 'clinopyroxene', 'spinel']
recplot = False
# store data in a dictionary with the key as the mineral type
data = {}
elements = {}
ratios = {}
cat_props = {}
ox_props = {}
# likewise aggregated data
agg_data = {}
agg_elements = {}
agg_ratios = {}
agg_cat_props = {}
agg_ox_props = {}
sample_average_data = {}
sample_average_elements = {}
sample_average_cat_props = {}
sample_average_ratios = {}

# Main analysis loop.
for mintype in mintypes:
    print(f'Analysing {mintype} data...')

    # Load in and perform data filtering - ensure that things are within sensible limits
    data[mintype] = load_and_filter(data_filename, mintype=mintype)
    # check the mineral composition - perform the scaling, calculate Fo etc.
    elements[mintype], ratios[mintype], cat_props[mintype], ox_props[mintype] = \
        check_mineral_composition(data[mintype], mintype=mintype)

    # quality checking
    data[mintype], elements[mintype], ratios[mintype], cat_props[mintype] = \
        cation_quality_check(data[mintype], elements[mintype], ratios[mintype],
                             cat_props[mintype], mintype=mintype)

    # Now do the same, but averaging over each area, with the quality-checked data only.
    agg_data[mintype] = average_over_areas(data[mintype])

    # Repeat the composition calculation
    agg_elements[mintype], agg_ratios[mintype], agg_cat_props[mintype], agg_ox_props[mintype] = \
        check_mineral_composition(agg_data[mintype], mintype=mintype)

    # Final averaging process - do averaging for the whole sample now.
    sample_average_data[mintype] = average_over_samples(agg_data[mintype])
    sample_average_ratios[mintype] = average_over_samples(agg_ratios[mintype],
                                                         oxides=False)
    sample_average_cat_props[mintype] = average_over_samples(agg_cat_props[mintype],
                                                             oxides=False)
    sample_average_elements[mintype] = average_over_samples(agg_ox_props[mintype],
                                                            oxides=False)

    # Generate output file - first group together all the data
    output_data = group_output_data(agg_data[mintype], agg_elements[mintype], agg_ratios[mintype],
                                    agg_cat_props[mintype], mintype=mintype)
    # likewise for the sample average data
    sample_avg_output_data = group_output_data(sample_average_data[mintype], sample_average_elements[mintype],
                                               sample_average_ratios[mintype],
                                    sample_average_cat_props[mintype], mintype=mintype, sampleavg=True)
    output_filename = 'output_data.xlsx'
    save_to_xlsx(output_filename, output_data, avgdata=sample_avg_output_data, mintype=mintype)

if recplot:
    xtype = 'olivine'
    ytype = 'clinopyroxene'
    # group up the data to pass into make_rectangle_plot
    # x and y are specified here, the defaults are the same as what is written here (Fo and Mg# respectively)

    grouped_data = get_rectangle_plot_data(xdata=data[xtype], ydata=data[ytype],
                                           x='Fo', y='Mg#')
    make_rectangle_plot(grouped_data, output_figure_fname, figformat=output_figure_format)

    # default - scatter = False
# un-filled rectangle, plotting the datapoints and the rectangle
# make_rectangle_plot(grouped_data, f'rectangle_scatterplot.eps', scatter=True, figformat=figformat)
# filled rectangle, so no need to plot the datapoints in addition
# make_rectangle_plot(grouped_data, 'rectangle_filled.eps', scatter=False, fill=True, figformat=figformat)
