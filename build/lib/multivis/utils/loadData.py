import sys
import pandas as pd
import numpy as np
from os import path

def loadData(filename, DataSheet, PeakSheet):
    """Loads and validates the DataFile and PeakFile from an excel file.

        Parameters
        ----------
        filename : The name of the excel file (.xlsx file) e.g. 'Data.xlsx'.
        DataSheet : The name of the data sheet in the file e.g. 'Data'. The data sheet must contain an 'Idx' and 'Class' column.
        PeakSheet : The name of the peak sheet in the file e.g. 'Peak'. The peak sheet must contain an 'Idx', 'Name', and 'Label' column.

        Returns
        -------
        DataTable: Pandas dataFrame
        PeakTable: Pandas dataFrame
    """

    if path.isfile(filename) is False:
        print("{} does not exist.".format(filename))
        sys.exit()

    if not filename.endswith(".xlsx"):
        print("{} should be a .xlsx file.".format(filename))
        sys.exit()

    # LOAD PEAK DATA
    print("Loading sheet: {}".format(PeakSheet))
    PeakTable = pd.read_excel(filename, sheet_name=PeakSheet)

    # LOAD DATA TABLE
    print("Loading sheet: {}".format(DataSheet))
    DataTable = pd.read_excel(filename, sheet_name=DataSheet)

    # Replace with nans
    DataTable = DataTable.replace(-99, np.nan)
    DataTable = DataTable.replace(".", np.nan)
    DataTable = DataTable.replace(" ", np.nan)

    # Error checks
    DataTable, PeakTable = __checkData(DataTable, PeakTable)

    # Make the Idx column start from 1
    DataTable.index = np.arange(1, len(DataTable) + 1)
    PeakTable.index = np.arange(1, len(PeakTable) + 1)

    print("TOTAL SAMPLES: {} TOTAL PEAKS: {}".format(len(DataTable), len(PeakTable)))
    print("Done!")

    return DataTable, PeakTable

def __checkData(DataTable, PeakTable):

    # Check DataTable for Idx, Class and SampleID
    data_columns = DataTable.columns.values

    if "Idx" not in data_columns:
        print("Data Table does not contain the required 'Idx' column")
        sys.exit()

    if DataTable.Idx.isnull().values.any() == True:
        print("Data Table Idx column cannot contain missing values")
        sys.exit()

    if len(np.unique(DataTable.Idx)) != len(DataTable.Idx):
        print("Data Table Idx numbers are not unique. Please change")
        sys.exit()

    if "Class" not in data_columns:
        print("Data Table does not contain the required 'Class' column")
        sys.exit()

    # Check PeakTable for Idx, Name, Label
    peak_columns = PeakTable.columns.values

    if "Idx" not in peak_columns:
        print("Peak Table does not contain the required 'Idx' column")
        sys.exit()

    if PeakTable.Idx.isnull().values.any() == True:
        print("Peak Table Idx column cannot contain missing values")
        sys.exit()

    if len(np.unique(PeakTable.Idx)) != len(PeakTable.Idx):
        print("Peak Table Idx numbers are not unique. Please change")
        sys.exit()

    if "Name" not in peak_columns:
        print("Peak Table does not contain the required 'Name' column")
        sys.exit()

    if PeakTable.Idx.isnull().values.any() == True:
        print("Peak Table Name column cannot contain missing values")
        sys.exit()

    if len(np.unique(PeakTable.Idx)) != len(PeakTable.Idx):
        print("Peak Table Name numbers are not unique. Please change")
        sys.exit()

    if "Label" not in peak_columns:
        print("Data Table does not contain the required 'Label' column")
        sys.exit()

    # Check that Peak Names in PeakTable & DataTable match
    peak_list = PeakTable.Name
    data_columns = DataTable.columns.values
    temp = np.intersect1d(data_columns, peak_list)

    if len(temp) != len(peak_list):
        print("The Peak Names in Data Table should exactly match the Peak Names in Peak Table. Remember that all Peak Names should be unique.")
        sys.exit()

    return DataTable, PeakTable

