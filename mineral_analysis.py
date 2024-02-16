# -*- coding: utf-8 -*-
"""
@author: Jon Elsey (ElseyJ1@cardiff.ac.uk)
"""

from get_composition import check_mineral_composition, average_over_samples
from inout import load_and_filter, get_data_filename, save_to_xlsx, group_output_data
from quality_checking import cation_quality_check
from plotting import get_rectangle_plot_data, make_rectangle_plot

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
data_filename = get_data_filename(fname=False)

# Load in the data and perform simple filtering to remove outliers
oliv_data = load_and_filter(data_filename, mintype='olivine')
ortho_data = load_and_filter(data_filename, mintype='orthopyroxene')
clino_data = load_and_filter(data_filename, mintype='clinopyroxene')

# check the mineral composition - perform the scaling, calculate Fo etc.
oliv_elements, oliv_ratios, oliv_cat_props, oliv_ox_props = \
    check_mineral_composition(oliv_data, mintype='olivine')

ortho_elements, ortho_ratios, ortho_cat_props, ortho_ox_props = \
    check_mineral_composition(ortho_data, mintype='pyroxene')

clino_elements, clino_ratios, clino_cat_props, clino_ox_props = \
    check_mineral_composition(clino_data, mintype='pyroxene')

# quality check for olivine
oliv_data, oliv_elements, oliv_ratios, oliv_cat_props = \
    cation_quality_check(oliv_data, oliv_elements, oliv_ratios,
                         oliv_cat_props)

# perform quality checking, this time for orthopyroxene
ortho_data, ortho_elements, ortho_ratios, ortho_cat_props, = \
    cation_quality_check(ortho_data, ortho_elements,
                         ortho_ratios, ortho_cat_props,
                         mintype='orthopyroxene')

# perform quality checking, this time for clinopyroxene
clino_data, clino_elements, clino_ratios, clino_cat_props, = \
    cation_quality_check(clino_data, clino_elements,
                         clino_ratios, clino_cat_props,
                         mintype='clinopyroxene')

# Now do the same, but averaging over each area.
oliv_agg_data = average_over_samples(oliv_data)

# Repeat the quality control process
oliv_agg_elements, oliv_agg_ratios, oliv_agg_cat_props, oliv_agg_ox_props = \
    check_mineral_composition(oliv_agg_data, mintype='olivine')

# Do the same for orthopyroxene
ortho_agg_data = average_over_samples(ortho_data)

ortho_agg_elements, ortho_agg_ratios, ortho_agg_cat_props, ortho_agg_ox_props = \
    check_mineral_composition(ortho_agg_data, mintype='orthopyroxene')

# And again for clinopyroxene
clino_agg_data = average_over_samples(clino_data)

clino_agg_elements, clino_agg_ratios, clino_agg_cat_props, clino_agg_ox_props = \
    check_mineral_composition(clino_agg_data, mintype='clinopyroxene')

# group up the data to pass into make_rectangle_plot
# x and y are specified here, the defaults are the same as what is written here (Fo and Mg# respectively)
grouped_data = get_rectangle_plot_data(olivine_data=oliv_data, pyroxene_data=ortho_data,
                                       x='Fo', y='Mg#')

oliv_output_data = group_output_data(oliv_agg_data, oliv_agg_elements, oliv_agg_ratios, oliv_agg_cat_props)
ortho_output_data = group_output_data(ortho_agg_data, ortho_agg_elements, ortho_agg_ratios, ortho_agg_cat_props,
                                      mintype='orthopyroxene')
clino_output_data = group_output_data(clino_agg_data, clino_agg_elements, clino_agg_ratios, clino_agg_cat_props,
                                      mintype='clinopyroxene')

output_filename = 'output_data.xlsx'
save_to_xlsx(output_filename, olivdata=oliv_output_data, orthodata=ortho_output_data, clinodata=clino_output_data)

# default - scatter = False
make_rectangle_plot(grouped_data, output_figure_fname, figformat=output_figure_format)
# un-filled rectangle, plotting the datapoints and the rectangle
# make_rectangle_plot(grouped_data, f'rectangle_scatterplot.eps', scatter=True, figformat=figformat)
# filled rectangle, so no need to plot the datapoints in addition
# make_rectangle_plot(grouped_data, 'rectangle_filled.eps', scatter=False, fill=True, figformat=figformat)
