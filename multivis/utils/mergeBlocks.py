import sys
import copy
import numpy as np
import pandas as pd

def mergeBlocks(peak_blocks, data_blocks, mergeType):
    """Merge multiple Peak and Data Tables from different datasets, and consolidates any statistical results
    generated from the multivis.utils.statistics package in relation to each block.

        Parameters
        ----------
        peak_blocks : A dictionary of Pandas Peak Table dataframes from different datasets indexed by dataset type.
        data_blocks : A dictionary of Pandas Data Table dataframes from different datasets indexed by dataset type.
        mergeType : The type of merging to perform. Either by 'SampleID' or 'Index'.

        Returns
        -------
        DataTable: Merged Pandas dataFrame
        PeakTable: Merged Pandas dataFrame (with any statistical results generated by multivis.utils.statistics consolidated into each block)
    """

    peak_blocks = __checkData(peak_blocks)
    data_blocks = __checkData(data_blocks)

    blocks = list(data_blocks.keys())

    df_peaks = pd.DataFrame()
    df_data = pd.DataFrame()

    for idx, block in enumerate(blocks):

        peak = peak_blocks[block]
        data = data_blocks[block]

        peak_columns = peak.columns

        if 'Name' not in peak_columns:
            print("Error: No \"Name\" column in {} peak block".format(block))
            sys.exit()

        if 'Label' not in peak_columns:
            print("Error: No \"Label\" column in {} peak block".format(block))
            sys.exit()

        if df_peaks.empty:
            df_peaks = peak.copy(deep=True)
            df_peaks.insert(len(df_peaks.columns), "Block", block)
        else:
            peak_dat = peak.copy(deep=True)
            peak_dat.insert(len(peak_dat.columns), "Block", block)

            df_peaks = pd.concat([df_peaks, peak_dat], ignore_index=True).reset_index(drop=True)

        if df_data.empty:
            df_data = data.copy(deep=True)

            if mergeType.lower() == 'sampleid':
                if 'SampleID' not in df_data.columns:
                    print("Error: No \"SampleID\" column in {} data block".format(block))
                    sys.exit()
            elif mergeType.lower() == 'index':
                if 'SampleID' in df_data.columns:
                    df_data = df_data.drop(['SampleID'], axis=1).reset_index(drop=True)
        else:
            if mergeType.lower() == 'sampleid':
                if 'SampleID' in data.columns:

                    x = data[["SampleID"] + list(peak['Name'].values)].reset_index(drop=True)

                    df_data = pd.merge(df_data, x, left_on="SampleID", right_on="SampleID").reset_index(drop=True)
            elif mergeType.lower() == 'index':
                x = data[list(peak['Name'].values)].reset_index(drop=True)

                df_data = pd.merge(df_data, x, left_index=True, right_index=True).reset_index(drop=True)

    df_peaks['Idx'] = df_peaks.index

    if 'Idx' in peak_columns:
        df_peaks = df_peaks[list(peak_columns)+list(['Block'])]
    else:
        df_peaks = df_peaks[list(['Idx'])+list(peak_columns) + list(['Block'])]

    # Merges any statistical results for each peak into each block
    df_peaks = __merge_multiple_statistics(df_peaks)

    return df_peaks, df_data

def __checkData(data):

    if not isinstance(data, dict):
            print("Error: A dictionary was not entered. Please check your data.")
            sys.exit()
    else:
            df = data[list(data.keys())[0]]

            if not isinstance(df, pd.DataFrame):
                print("Error: A dataframe was not entered into the dictionary. Please check your data.")
                sys.exit()

    return data

def __merge_statistic(MergedPeakTable, stat_name):
    merged_peak_stats = copy.deepcopy(MergedPeakTable)

    column_name_list = list(filter(lambda x: x.startswith(stat_name), merged_peak_stats.columns))

    if column_name_list:
        blocks = list(set(merged_peak_stats['Block']))

        merged_column_list = set([])
        for column_name in column_name_list:
            column_name_array = column_name.split('_')
            merged_column_list.add('_'.join(column_name_array[:-1]))

        merged_column_list = list(merged_column_list)
        merged_column_list.sort()

        for column in merged_column_list:
            stats = []
            for block_idx, block in enumerate(blocks):
                column_name = column + '_' + block

                # if true then these are case columns
                if column_name in column_name_list:
                    stats.extend(list(merged_peak_stats[merged_peak_stats['Block'] == block][column_name]))
                else:
                    # else the column doesn't exist and is a control group, therefore check the data types
                    # in the other columns to infer the values to use for the control block
                    if block_idx - 1 >= 0:
                        other_column_name = column + '_' + blocks[block_idx - 1]
                    else:
                        other_column_name = column + '_' + blocks[block_idx + 1]

                    bool_type = False
                    for x in list(merged_peak_stats[other_column_name]):
                        if type(x) == bool:
                            bool_type = True
                            break

                    if bool_type:
                        tmp_stats = [False] * merged_peak_stats[merged_peak_stats['Block'] == block].shape[0]
                    else:
                        tmp_stats = [np.nan] * merged_peak_stats[merged_peak_stats['Block'] == block].shape[0]
                    stats.extend(list(tmp_stats))

            merged_peak_stats[column] = stats

        merged_peak_stats = merged_peak_stats.drop(columns=column_name_list, axis=1)

    return merged_peak_stats

def __merge_multiple_statistics(MergedPeakTable):
    stat_types = ['MeanFoldChange', 'MedianFoldChange', 'Group_mean', 'Group_median', 'TTEST-twoGroup', 'MannWhitneyU', 'LEVENE-twoGroup']

    multi_block_stats = copy.deepcopy(MergedPeakTable)

    for stat in stat_types:
        multi_block_stats = __merge_statistic(multi_block_stats, stat)

    return multi_block_stats