# -*- coding: utf-8 -*-
"""
@author: Jon Elsey (ElseyJ1@cardiff.ac.uk)
"""

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np
from inout import get_data_filename
import pandas as pd
import traceback
from scipy.stats import norm
import os

def filter_for_scatter(data, mintype_x, mintype_y, mintype_z=False, average=False):
    """
    To generate scatterplots where x and y are different mineral types, we need to filter our data so that just data
    which is measured at the same point is visible, otherwise we can't generate such a plot
    (it would no sense as the lengths of the datasets may be different)

    Args:
        data:
        average:
        mintype_x:
        mintype_y:
        mintype_z:

    Returns:
        data: Amended dataset containing just the elements of the datasets that are present for both mineral types.
    """

    return data
def scatter_plot(data, mintype_x, mintype_y, mintype_z=False, var1='Si', var2='Ti', var3=False,
                 marker='x', cbar_orientation='vertical', colourmap='plasma', output_path='./plots'):
    """
    x vs y scatter plot of two variables, with an option to have a third variable included as a symbol colour scale.

    Args:


    Returns:

    """
    if 'average' in mintype_x or 'average' in mintype_y:
        average = True
    else:
        average = False

    if mintype_z and not var3:
        raise ValueError('You need to specify a z-axis sheet name and variable name')
    if var3 and not mintype_z:
        raise ValueError('You need to specify a z-axis sheet name and variable name')
    plt.figure()
    mintype_x = sanitise_mineral_type(mintype_x)
    mintype_y = sanitise_mineral_type(mintype_y)

    # If we have data that has two different mineral types, then we need to restrict
    # our dataset where we have the same measurement ID present in both cases,
    # else one will be "longer" than the other meaning we can't plot them together.

    if mintype_x != mintype_y:
        data = filter_for_scatter(data, mintype_x, mintype_y,
                                  mintype_z=mintype_z, average=average)
    if mintype_z:
        mintype_z = sanitise_mineral_type(mintype_z)

    x_data = data[mintype_x][var1]
    y_data = data[mintype_y][var2]
    if var3:
        z_data = data[mintype_z][var3]

    # If plotting sample average data, then need to split data + 2SD
    if 'average' in mintype_x:
        x_data, uncertainty_x = get_data_and_std(x_data)
        y_data, uncertainty_y = get_data_and_std(y_data)
        if var3:
            z_data, uncertainty_z = get_data_and_std(z_data)

    if not var3 and not average:
        plt.scatter(x_data, y_data, marker=marker)

    elif not var3 and average:
        plt.errorbar(x_data.to_numpy(dtype=float), y_data.to_numpy(dtype=float),
                     xerr=uncertainty_x.to_numpy(dtype=float), yerr=uncertainty_y.to_numpy(dtype=float))

    # If we want to plot 3 variables, things are a bit more complicated. We need to set the symbol colour of each
    # point to some value, corresponding to var3.
    if var3:
        colourmap = plt.cm.get_cmap(colourmap)
        # Set up scaling for our colour bar data
        z_data = z_data.to_numpy(dtype=float)
        scaled_z = (z_data - z_data.min()) / np.ptp(z_data)
        colours = colourmap(scaled_z)
        # Generate scatterplot

        plt.scatter(x_data.to_numpy(dtype=float), y_data.to_numpy(dtype=float)
                        , marker=marker, facecolor=colours)

        if average:
             plt.errorbar(x_data.to_numpy(dtype=float),
                             y_data.to_numpy(dtype=float),
                             xerr=uncertainty_x.to_numpy(dtype=float),
                             yerr=uncertainty_y.to_numpy(dtype=float), marker=marker,
                          fmt='none',
                          ecolor=colours)

        sm = plt.cm.ScalarMappable(cmap=colourmap)
        sm.set_clim(vmin=np.min(z_data), vmax=np.max(z_data))
        cbar = plt.colorbar(sm, ax=plt.gca(), orientation=cbar_orientation)
        zlabel = f'{mintype_z.strip(' ').strip('average').strip('data')} {var3}'
        cbar.set_label(zlabel)

    plt.grid()
    xlabel = f'{mintype_x.strip(' ').strip('average').strip('data')} {var1}'
    ylabel = f'{mintype_y.strip(' ').strip('average').strip('data')} {var2}'
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.show()
    output_filename = f'{mintype_x.strip(' ').strip('average').strip('data')}_{var1}_vs_{mintype_y.strip(' ').strip('average').strip('data')}_{var2}_scatter.png'
    plt.savefig(output_path + '/' + output_filename)
def plot_hist(data, mintype='Olivine data', key='Si', bins=10, gaussian_fit=False,
              normalise=False, grid=True, output_path='./plots'):
    """
    Plot a histogram of a given variable.

    Args:
        data - Excel datasheet we want to look at.
        mintype - The sheet name we want from the Excel spreadsheet, i.e. mineral type + whether it is area or sample
            average e.g. 'Olivine data' for area average, 'Olivine average' for sample average
        key - The element/ratio etc. we want to plot
        bins - Number of bins you want on the histogram
        gaussian_fit - If True, then also plot a Gaussian curve over the top. This forces normalise to be True.
        normalise - if True, then set the y-axis to a probability density function rather than a raw count.
        grid - Whether you want a grid overlaid or not, set to False if not
        output_path - where to save the plot, default is a new folder called 'plots' within the current folder
    """
    # If plotting a Gaussian fit over the top, then we need to normalise the data to create a pdf rather than plotting
    # raw counts
    mintype = sanitise_mineral_type(mintype)
    if gaussian_fit:
        normalise = True
    data_to_plot = data[mintype][key]

    # If plotting sample average data, then need to split data + 2SD
    if 'average' in mintype:
        data_to_plot, uncertainty = get_data_and_std(data_to_plot)

    n, plot_bins, patches = plt.hist(data_to_plot, bins=bins, label='Raw data', density=normalise)
    # Get the correct title based on what data we input
    if 'data' in mintype:
        title = f'Histogram of {mintype.strip("data")} {key}, averaged over areas'
    elif 'average' in mintype:
        title = f'Histogram of {mintype.strip("average")}{key}, whole sample average'
    plt.title(title)

    plt.xlabel(f'{mintype.strip("data").strip('average')}{key}')

    # Set y label based on whether we are doing a PDF or raw counts
    if not gaussian_fit and not normalise:
        plt.ylabel('Frequency')
    else:
        plt.ylabel('Probability density')

    # create the gaussian fit if doing
    if gaussian_fit:
        fit_bins = np.linspace(plot_bins[0], plot_bins[-1], 1000)
        mu, sigma = norm.fit(data_to_plot.astype(float))
        # add mu and sigma to the plot title
        title += f', mean = {np.round(mu, 3)}, sigma = {np.round(sigma, 3)}'
        plt.title(title)
        best_fit_line = norm.pdf(fit_bins, mu, sigma)
        plt.plot(fit_bins, best_fit_line, label=f'Gaussian fit', linewidth=2)
        plt.legend()

    if grid:
        plt.grid()
    # plt.show()

    # Create output path if it does not already exist
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # auto-generate the output filename and then save
    output_filename = f'{mintype.strip(' ').strip('average').strip('data')}_{key}_histogram.png'
    plt.savefig(output_path + '/' + output_filename)


def get_rectangle_plot_data(xdata=False, ydata=False, x='Fo', y='Mg#'):
    """
    Obtain a DataFrame containing x and y data that you wish to plot using make_rectangle_plot.

    Args:
        xdata: DataFrame of olivine data that we want to group.
                      Default False, im which case we try and take both
                      x and y from the pyroxene data.
        ydata: DataFrame of pyroxene data that we want to group.
                       Default False, im which case we try and take both
                       x and y from the olivine data.
        x: Variable name to be added to the output file from the olivine data. Default is 'Fo'.
           If only one of xdata or ydata are DataFrames, then both x and y will
           be loaded from that one file.
        y: Variable name to be added to the output file from the pyroxene data. Default is 'Mg#'.
           If only one of xdata or ydata are DataFrames, then both x and y will
           be loaded from that one file.

    Returns:
        grouped_data: DataFrame of merged data to be passed into plotting.make_rectangle_plot.
    """
    # the plot we want - x axis = olivine Fo, y axis = opx mg#
    # to do this then, we need to create a new dataset, grouping fo and mg# by sample

    # first take just the sample name and x from the olivines.
    if xdata is not False:
        grouped_data = xdata[['Project Path (2)', x]]

        # try and then get y from the pyroxene data, else take it from the olivines.
        if ydata is not False:
            grouped_data = grouped_data.merge(ydata[['Project Path (2)', y]])
        else:
            grouped_data = grouped_data.merge(xdata[['Project Path (2)', y]])

    # try and load in pyroxene data for both x and y otherwise
    elif ydata is not False:
        grouped_data = ydata[['Project Path (2)', x]]
        grouped_data = grouped_data.merge(ydata[['Project Path (2)', y]])

    else:
        raise ValueError('You must pass in data for both the x and y axes')

    return grouped_data


def make_rectangle_plot(grouped_data, fname, scatter=False, fill=False,
                        x='Fo', y='Mg#',
                        x_mineral='Olivine', y_mineral='Opx',
                        figformat='eps'):
    """
    Generate a plot of x (default Fo) vs y (default Mg#) which plots a rectangle
    over the region covered by each area of the mineral.

    Args:
        grouped_data (DataFrame): Pandas DataFrame containing the data you wish
                                  to plot. This will likely be the output of
                                  get_opx_and_fo if using the default values for
                                  x and y.
        fname (str): The name of the file we want to save the plot to.
        scatter (bool, optional): If False, (default) then the rectangle is plotted
                                  without the datapoints that make up that
                                  rectangle. if True, then the datapoints
                                  are plotted also via a scatterplot.
        fill (bool, optional): If False (default), the rectangles are plotted with
                               their outline only. If True, then the rectangles are filled.
        x (str, optional): The variable you wish to plot on the x-axis. Defaults to 'Fo'
        y (str, optional): The variable you wish to plot on the y-axis. Defaults to 'Mg#'.
        x_mineral (str, optional): The mineral type for which you want to get the value of x
                                   from. This is only used for the x-label. Defaults to Olivine.
        y_mineral (str, optional): The mineral type for which you want to get the value of y
                                   from. This is only used for the y-label. Defaults to 'Opx' (orthopyroxene).
        figformat (str, optional): Format we want to solve the figure into. Defaults to 'eps'.
                                   Other formats include 'jpg', 'png' and 'svg'.
    Returns:
        None.
    """

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
    i = 0  # iterator since we are looping over a generator, easier than using enumerate here
    # its purpose is to ensure that the colours are consistent between the scatterplot and
    # the rectangles
    # define colours - since we are just colour coding and not using contours
    # we can use jet
    colours = plt.cm.jet(np.linspace(0, 1, len(grouped_min)))
    if scatter:
        for n, grp in grouped_data.groupby('Project Path (2)'):
            # s = size of marker, marker = type of marker - e.g. 'o' is a circle
            ax.scatter(x=x, y=y, data=grp, label=n, color=colours[i], marker='X', s=20)
            i += 1
    else:
        # do a dummy plot for the legend labels to appear
        for n, grp in grouped_data.groupby('Project Path (2)'):
            # s = size of marker, marker = type of marker - e.g. 'o' is a circle, 's' is a square
            ax.scatter(np.nan, np.nan, label=n, color=colours[i], marker='s', s=20)
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
                               fill=fill, color=colours[i],
                               linewidth=3))
        i += 1

    # set figure visual properties - legends, grids, limits, labels
    # the limits are set to show the whole dataset currently - you can instead
    # set them manually using plt.xlim(<xmin>, <xmax>) and plt.ylim(<ymin>, <ymax>)
    # or use matplotlib's interactive mode to adjust them at runtime
    plt.xlim(grouped_min[f'{x}_min'].min() * 0.99, grouped_max[f'{x}_max'].max() * 1.01)
    plt.ylim(grouped_min[f'{y}_min'].min() * 0.99, grouped_max[f'{y}_max'].max() * 1.01)
    plt.grid()
    plt.xlabel(f'{x_mineral} {x}', fontsize=20)
    plt.ylabel(f'{y_mineral} {y}', fontsize=20)
    # markerscale makes the coloured markers bigger on the legend so we can
    # see them better
    plt.legend(markerscale=3, fontsize=15)
    figure = plt.gcf()
    figure.set_size_inches(10, 6)
    plt.savefig(fname, format=figformat, bbox_inches='tight')
    plt.show()

def load_excel_data_for_plots(path=False):
    fname = get_data_filename(fname=path)
    xls = pd.ExcelFile(fname)
    data = {}
    keys = ['Olivine data', 'Olivine average', 'Cpx data', 'Cpx average', 'Opx data', 'Opx average',
            'Spinel data', 'Spinel average']
    for key in keys:
        try:
            data[key] = pd.read_excel(xls, key)
        except Exception as e:
            print(e)
            print(f'key {key} not found in Excel file - skipping. You wont be able to plot this data')
    return data


def sanitise_mineral_type(mintype):
    """
    Ensure that the mineral type is correct when selecting which plots to make regardless of the input.
    For example, if a user puts 'Cpx' or 'clinopyroxene', then both should work.

    Args:

    Returns:

    """
    # this really should be a regex but I don't have time to do it before I leave so I've just added the two
    # simplest cases for now
    if 'clinopyroxene' in mintype.lower():
        mintype.replace('clinopyroxene', 'Cpx').replace('Clinopyroxene', 'Cpx')
    if 'orthopyroxene' in mintype.lower():
        mintype.replace('orthopyroxene', 'Opx').replace('Orthopyroxene', 'Opx')

    return mintype

def get_data_and_std(data_to_plot):
    # Remove plus minus symbol and split, so we have the data and the uncertainty
    data = data_to_plot.str.replace('±', '', regex=True).str.split(' ', expand=True)
    if len(data.columns) == 3:
        # 3 columns, data, empty (where we got rid of +-), uncertainty
        uncertainty = data[2]
        data = data[0]
    else:
        uncertainty = np.nan
    return data, uncertainty