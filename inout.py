import tkinter as tk
from tkinter import filedialog
import pandas as pd


def get_data_filename(fname=False):
    """
    Get data filename using the file browser and return it.

    Args:
        fname: False by default. If replaced with a string, then
               the function will return this string instead
               (for use if e.g. doing automation over many files)
    Returns:
        File name of the data file to be loaded into load_and_filter.
    """
    if not fname:
        print('Opening file browser')
        root = tk.Tk()
        root.wm_attributes('-topmost', 1)  # alongside parent=root, ensures window is always on top
        root.withdraw()
        return filedialog.askopenfilename(parent=root)
    else:
        return fname


def load_and_filter(input_file, mintype='olivine'):
    """
    Load in data from an Excel spreadsheet, choose one of the sheets to convert to
    a Pandas DataFrame based on the mineral type, and perform a simple threshold filter
    to remove outliers.


    Args:
        input_file: Excel spreadsheet containing mineral data to be loaded in.
        mintype: Mineral type that you want to load in.
                 Assuming that the input files are the same format as
                 the initial file Johan specified, this chooses which
                 specific sheet in the spreadsheet we want.
                 The spreadsheet has three tabs - 'Olivine data', 'Opx data', 'Cpx data'.
                 Therefore, mintype should likely be 'Olivine', 'Opx' or 'Cpx'.
    Returns:
        data: pandas DataFrame containing the data read in from the Excel spreadsheet
              for the mineral specified by mintype.

    """
    if mintype.lower() == 'olivine':
        sheet_name = 0
    elif mintype.lower() == 'orthopyroxene':
        sheet_name = 1
    elif mintype.lower() == 'clinopyroxene':
        sheet_name = 2
    else:
        raise ValueError('Mineral type should be olivine, orthopyroxene or clinopyroxene.')
    data = pd.read_excel(input_file, sheet_name=sheet_name).dropna()

    # First off - remove any data with total >101 or <99%
    data = data[(data.Total > 99) & (data.Total < 101)]
    # Then check mineral composition is sensible -
    return data


def group_output_data(oxides, elements, ratios, cat_props, mintype='olivine'):
    """
    Load in the aggregated data for the oxides and for the mineral formula calculation
    and group them into one DataFrame so we can write them out.
    Args:
        oxides: DataFrame of the aggregated oxides data.
        elements: DataFrame of the mineral formula calculation.
        ratios: DataFrame of cation ratios (Fo/Mg#).
        cat_props: DataFrame of cation numbers, from which we want the total.

    Returns:
        output_data: combined DataFrame.
    """
    # first we need to rename the columns in the oxides data
    oxides['Oxide total'] = oxides.drop('counts', axis=1).sum(axis=1, numeric_only=True)

    oxides.rename(columns={'Na': 'NaO2', 'Mg': 'MgO', 'Al': 'Al2O3', 'Si': 'SiO2', 'Ca': 'CaO',
                           'Ti': 'TiO2', 'Cr': 'Cr2O3', 'Mn': 'MnO', 'Fe': 'FeO', 'Ni': 'NiO'}, inplace=True)
    oxides = oxides.reset_index()
    elements = elements.reset_index(drop=True)
    ratios = ratios.reset_index(drop=True)
    cat_props = cat_props.reset_index(drop=True)
    if 'olivine' in mintype:
        ratios_col = ratios['Fo']
    elif 'pyroxene' in mintype:
        ratios_col = ratios['Mg#']
    else:
        raise ValueError('Mintype must be "olivine" or contain "pyroxene"')
    cations_col = cat_props.rename(columns={'sum': 'Cation sum'})
    output_data = pd.concat([oxides, elements, ratios_col, cations_col['Cation sum']], axis=1)
    return output_data


def setup_output(data):
    """
    Perform a few tidy-up steps on the data we wish to write out. Specifically,
    move the number of points averaged column to the end, and rename some of the
    less-obvious columns.

    Args:
        data: Input Pandas DataFrame we want to tidy up.

    Returns:
        data: the amended input DataFrame.
    """
    column_to_move = data.pop("counts")
    data.insert(len(data.columns), "counts", column_to_move)
    data = data.reset_index()  # reset index so we can rename the path columns
    data.rename(columns={'Project Path (2)': 'Sample', 'Project Path (3)': 'Area',
                         'counts': 'Number of datapoints averaged'}, inplace=True)
    return data


def save_to_xlsx(path, olivdata=False, orthodata=False, clinodata=False):
    """
    Save data for the different mineral types into an Excel spreadsheet at location <path>.
    This will save to different sheets within the spreadsheet for each mineral type passed in.

    Args:
        path: Location/filename you want to save the output data to.
        olivdata: Olivine data, if it exists. Default False, will save the data
                  to the spreadsheet if a Pandas DataFrame is passed in.
        orthodata: As above, but for orthopyroxene data.
        clinodata: As above, but for clinopyroxene data.

    Returns:
        None
    """
    # Sample name; area name; the number of datapoints averaged;
    # average concentrations for each of the elements measured (plus its total);
    # mineral formula of this average.
    # first create ExcelWriter object
    writer = pd.ExcelWriter(path)
    if olivdata is not False:
        olivdata = setup_output(olivdata)
        olivdata.to_excel(writer, sheet_name='Olivine data', index=False)

    if orthodata is not False:
        orthodata = setup_output(orthodata)
        orthodata.to_excel(writer, sheet_name='Opx data', index=False)

    if clinodata is not False:
        clinodata = setup_output(clinodata)
        clinodata.to_excel(writer, sheet_name='Cpx data', index=False)
    writer.close()
