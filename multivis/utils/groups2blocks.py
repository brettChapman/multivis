import sys
import pandas as pd
import copy
import string

def groups2blocks(PeakTable, DataTable, group_column_name):
    """Slices the data by group/class name into blocks for later identification of multi-block associations, and places
        the data into a dictionary indexed by group/class name.

        Parameters
        ----------
        PeakTable : Pandas dataframe containing the feature/peak data. Must contain 'Name' and 'Label'.
        DataTable : Pandas dataframe matrix containing values. The data must contain a column separating out the different groups in the data (e.g. Class)
        group_column_name : The group column name used in the datatable (e.g. Class)

        Returns
        -------
        DataBlocks: A dictionary containing DataTables indexed by group names
        PeakBlocks: A dictionary containing PeakTables indexed by group names
    """
    DataTable = __checkDataTable(DataTable, group_column_name)
    PeakTable = __checkPeakTable(PeakTable)

    matrix_data = copy.deepcopy(DataTable)

    group_names = list(set(matrix_data[group_column_name]))
    block_name_prefixes = list(string.ascii_uppercase)

    DataBlocks = dict({})
    PeakBlocks = dict({})

    for group_idx, group in enumerate(group_names):

        peak_data = copy.deepcopy(PeakTable)

        feature_list = []

        for feature_idx, name in enumerate(list(peak_data['Name'].values)):
            feature_list.append(str(block_name_prefixes[group_idx]) + str(feature_idx + 1))

        sliced_matrix = matrix_data.loc[matrix_data[group_column_name] == group]

        meta = sliced_matrix.T[~sliced_matrix.T.index.isin(peak_data['Name'])].T.reset_index(drop=True)

        # Drop the group column name from the meta data, to avoid ambiguity later when merging the data
        meta = meta.drop([group_column_name], axis=1)

        sliced_matrix = sliced_matrix[list(peak_data['Name'])].reset_index(drop=True)

        peak_data['Name'] = pd.Series(feature_list)

        sliced_matrix.rename(columns=dict(zip(list(sliced_matrix.columns), list(peak_data['Name']))), inplace=True)

        sliced_matrix = sliced_matrix.dropna(axis=1, how='all').reset_index(drop=True)

        sliced_matrix = pd.concat([meta, sliced_matrix], axis=1).reset_index(drop=True)

        peak_data = peak_data[peak_data['Name'].isin(sliced_matrix.columns)]

        DataBlocks[group] = sliced_matrix.reset_index(drop=True)
        PeakBlocks[group] = peak_data.reset_index(drop=True)

    return PeakBlocks, DataBlocks

def __checkPeakTable(PeakTable):

    if not isinstance(PeakTable, pd.DataFrame):
        print("Error: A pandas dataframe was not entered for the PeakTable. Please check your data.")
        sys.exit()

    if "Name" not in PeakTable.columns:
        print("Error: \"Name\" column not in Peak Table. Please check your data.")
        sys.exit()

    if "Label" not in PeakTable.columns:
        print("Error: \"Label\" column not in Peak Table. Please check your data.")
        sys.exit()

    # Do not assume the peaks/nodes have been indexed correctly. Remove any index columns and reindex.
    column_list = [column.lower() for column in PeakTable.columns]
    if 'idx' in column_list:
        index = column_list.index('idx')
        column_name = PeakTable.columns[index]
        PeakTable = PeakTable.drop(columns=[column_name])

    if 'index' in column_list:
        index = column_list.index('index')
        column_name = PeakTable.columns[index]
        PeakTable = PeakTable.drop(columns=[column_name])

    PeakTable = PeakTable.reset_index(drop=True)

    PeakTable.index.name = 'Idx'

    PeakTable = PeakTable.reset_index()

    return PeakTable

def __checkDataTable(data, group_column_name):

    if not isinstance(data, pd.DataFrame):
        print("Error: A pandas dataframe was not entered for the DataTable. Please check your data.")
        sys.exit()

    if group_column_name not in data.columns:
        print("Error: Data does not contain the specified group column name {}. Please check your data.".format(''.join(group_column_name)))
        sys.exit()

    return data