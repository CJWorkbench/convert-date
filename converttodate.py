"""
This module converts a string column to a datetime column.
Inputting a numerical column will throw an error.
"""

date_input_map = 'AUTO|Date (U.S.) MM/DD/YYYY|Date (E.U.) DD/MM/YYYY'.lower().split('|')

# Map to pd.to_datetime() parameters
input_settings_map = {
    'auto': {
        'infer_datetime_format': True,
        'format': None
    },
    'date (u.s.) mm/dd/yyyy': {
        'infer_datetime_format': False,
        'format': '%m/%d/%Y'
    },
    'date (e.u.) dd/mm/yyyy': {
        'infer_datetime_format': False,
        'format': '%d/%m/%Y'
    }
}

def render(table, params):
    # No processing if no columns selected
    if not params['colnames']:
        return table

    columns = [c.strip() for c in params['colnames'].split(',')]
    type_date = date_input_map[params['type_date']]
    type_null = params['type_null']

    # For now, numerical types are not supported. Throw error if any input columns are numerical
    if any([np.issubdtype(dtype, np.number) for dtype in table[columns].dtypes if str(dtype) != 'category']):
        return 'Cannot convert numerical columns.'

    for column in columns:
        # For now, re-categorize after replace. Can improve performance by operating
        # directly on categorical index, if needed
        if table[column].dtype.name == 'category':
            table[column] = prep_cat(table[column])
            table[column] = pd.to_datetime(table[column].astype(str), errors='coerce',
                                           format=input_settings_map[type_date]['format'],
                                           infer_datetime_format=input_settings_map[type_date]['infer_datetime_format'],
                                           exact=False, cache=True)
        # Object
        else:
            table[column] = pd.to_datetime(table[column], errors='coerce',
                                           format=input_settings_map[type_date]['format'],
                                           infer_datetime_format=input_settings_map[type_date]['infer_datetime_format'],
                                           exact=False, cache=True)

    if not type_null:
        result = find_errors(table[columns])
        if result:
            return result

    return table

def prep_cat(series):
    if '' not in series.cat.categories:
        series.cat.add_categories('', inplace=True)
    if any(series.isna()):
            series.fillna('', inplace=True)
    return series

def find_errors(table):
    error_map = {}
    for column in table.columns:
        error_map[column] = table[column][table[column].isnull()].index

    num_errors = 0

    for errors in error_map.values():
        num_errors += len(errors)

    if num_errors > 0:
        first_column = list(error_map.keys())[0]
        first_row = error_map[first_column][0]
        return f"Format error in row {first_row + 1} of '{first_column}'. " \
                f'Overall, there are {num_errors} errors in {len(error_map.keys())} columns. ' \
                f"Select 'non-dates to null' to set these cells to null"
    return
