def cation_quality_check(data, elements, ratios, cat_props, error=0.01, mintype='olivine'):
    """
    Perform a quality check on the data to remove elements that we don't wish to keep,
    based on a user-specified error threshold applied to the cation total.

    Args:
        data: DataFrame that you wish to perform the quality checking on.
        elements: DataFrame containing the elements that were obtained from
                  get_composition.check_mineral_composition.
        ratios:
        cat_props: DataFrame of cation properties used to perform the quality check.
        error: Default error threshold for the quality check. The user is
               prompted whether to accept this default threshold, or change it.
               Roughly 3 +- error for olivine, 4 +- error for pyroxene.
        mintype: Mineral type being analysed. Default 'olivine'. If mintype has
                 the substring 'pyroxene' within it, the target cation count is
                 set to  4, else it is 3 if it has the substring 'olivine'.
                 e.g. 'clinopyroxene' contains the substring 'pyroxene', so it
                 will be set to 4.

    Returns:
        data: as input argument data, but with errors removed.
        elements: as input argument elements, but with errors removed.
        ratios: as input argument ratios, but with errors removed.
        cat_props: as input argument cat_props, but with errors removed.

    """

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

        elif 'pyroxene' in mintype.lower() or 'spinel' in mintype.lower():
            cation_count = 4
            print(f'\nCurrently accepting values within 4 ± {error}\n')

        new_cat_props = cat_props[(cation_count - error < cat_props['sum']) & (cat_props['sum'] < cation_count + error)]
        ratio = 100 * (init_num_samples - len(new_cat_props['sum'])) / init_num_samples

        print(f"Removed {init_num_samples - len(new_cat_props['sum'])} of " \
              f"{init_num_samples} total samples ({ratio:.3f}%) based on current error limit")

        prompt = input('Accept this number of discarded values, or change the error limits?\n')
        yesses = ['y', 'yes', 'accept']
        nos = ['n', 'no', 'change']

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
        elif prompt.replace('.', '').rstrip().isnumeric():  # replace . as this is a non numeric type
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
