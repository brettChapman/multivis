import sys
import pandas as pd
import collections

def mergeBlocks(peak_blocks, data_blocks):
    """Merge multiple Peak and Data Tables from different datasets.

        Parameters
        ----------
        peak_blocks : A dictionary of Pandas Peak Table dataframes from different datasets indexed by dataset type.
        data_blocks : A dictionary of Pandas Data Table dataframes from different datasets indexed by dataset type.

        Returns
        -------
        DataTable: Merged Pandas dataFrame
        PeakTable: Merged Pandas dataFrame
    """

    peak_blocks = __checkData(peak_blocks)
    data_blocks = __checkData(data_blocks)

    blocks = list(data_blocks.keys())

    df_peaks = pd.DataFrame()
    df_data = pd.DataFrame()

    sampleIDcheck = []
    compare = lambda x, y: collections.Counter(x) == collections.Counter(y)
    for idx, block in enumerate(blocks):

        peak = peak_blocks[block]
        data = data_blocks[block]

        if 'Name' not in peak.columns:
            print("Error: No \"Name\" column in {} peak block".format(block))
            sys.exit()

        if 'Label' not in peak.columns:
            print("Error: No \"Label\" column in {} peak block".format(block))
            sys.exit()

        if df_peaks.empty:
            df_peaks = peak.copy(deep=True)
            df_peaks.insert(len(df_peaks.columns), "Block", block)
        else:
            peak_dat = peak.copy(deep=True)
            peak_dat.insert(len(peak_dat.columns), "Block", block)
            df_peaks = pd.concat([df_peaks, peak_dat], sort=False).reset_index(drop=True)

        if df_data.empty:
            df_data = data.copy(deep=True)

            if 'SampleID' in df_data.columns:
                sampleIDcheck.append(list(df_data['SampleID'].values))
            else:
                print("Error: No \"SampleID\" column in {} data block".format(block))
                sys.exit()
        else:
            if 'SampleID' in data.columns:

                if len(sampleIDcheck) == 1:
                    sampleIDcheck.append(list(data['SampleID'].values))

                    if not (compare(sampleIDcheck[0], sampleIDcheck[1])):
                        print("Error: SampleID order or values are not consistant across data blocks. Please check")
                        sys.exit()

                    sampleIDcheck = []
                    sampleIDcheck.append(list(data['SampleID'].values))

                x = data[["SampleID"] + list(peak['Name'].values)]

                df_data = pd.merge(df_data, x, left_on="SampleID", right_on="SampleID").reset_index(drop=True)

    df_peaks['Idx'] = df_peaks.index

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