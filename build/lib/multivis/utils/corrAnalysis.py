import sys
from scipy import stats
from tqdm import tqdm
import numpy as np
import pandas as pd

def corrAnalysis(df_data, correlationType):
    """Performs correlation analysis on a given matrix of values.

        Parameters
        ----------
        df_data : A Pandas dataframe matrix of values
        correlationType : The correlation type to apply. Either 'Pearson', 'Spearman' or 'KendallTau'

        Returns
        -------
        df_corr : Pandas dataframe matrix of all correlation coefficients
        df_pval : Pandas dataframe matrix of all correlation pvalues
    """

    df_data, correlationType = __checkData(df_data.astype(float), correlationType)

    df_corr = pd.DataFrame()
    df_pval = pd.DataFrame()

    for i in tqdm(df_data.columns):

        corrList = []
        pvalList = []

        for a in df_data.columns:

            mask = ~np.isnan(df_data[i].values) & ~np.isnan(df_data[a].values)
            x = df_data[i].values[mask]
            y = df_data[a].values[mask]

            if correlationType.lower() == "pearson":
                corr, pval = stats.pearsonr(x, y)
            elif correlationType.lower() == "spearman":
                corr, pval = stats.spearmanr(x, y)
            elif correlationType.lower() == "kendalltau":
                corr, pval = stats.kendalltau(x, y)

            corrList.append(corr)
            pvalList.append(pval)

        if df_corr.empty:
            df_corr = pd.DataFrame(np.column_stack(corrList), columns=df_data.columns)
            df_pval = pd.DataFrame(np.column_stack(pvalList), columns=df_data.columns)
        else:
            dat_corr = pd.DataFrame(np.column_stack(corrList), columns=df_data.columns)
            df_corr = pd.concat([df_corr, dat_corr]);

            dat_pval = pd.DataFrame(np.column_stack(pvalList), columns=df_data.columns)
            df_pval = pd.concat([df_pval, dat_pval]);

    df_corr.index = df_data.columns
    df_pval.index = df_data.columns

    return df_corr, df_pval

def __checkData(df_data, correlationType):

    if correlationType.lower() not in ["pearson", "spearman", "kendalltau"]:
        print("Error: Correlation type not valid. Choose either \"Pearson\", \"Spearman\" or \"KendallTau\".")
        sys.exit()

    if not isinstance(df_data, pd.DataFrame):
        print("Error: A dataframe was not entered. Please check your data.")
        sys.exit()

    return df_data, correlationType