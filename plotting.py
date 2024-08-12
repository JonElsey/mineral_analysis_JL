# -*- coding: utf-8 -*-
"""
@author: Jon Elsey (ElseyJ1@cardiff.ac.uk)
"""

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np

def plot_vars(var1, var2):
    pass

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

