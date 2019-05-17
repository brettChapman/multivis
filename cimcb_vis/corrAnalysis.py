from scipy import stats
from tqdm import tqdm
import numpy as np
import pandas as pd

def corrAnalysis(multi_peaks, multi_blocks, correlationType):

    if "Name" in multi_peaks.columns:
        X = multi_blocks[multi_peaks['Name']]


        df_corr = pd.DataFrame()
        df_pval = pd.DataFrame()

        for i in tqdm(X.columns):

            corrList = []
            pvalList = []

            for a in X.columns:

                if correlationType == "pearson":
                    corr, pval = stats.pearsonr(X[i].values, X[a].values)
                elif correlationType == "spearman":
                    corr, pval = stats.spearmanr(X[i].values, X[a].values)

                corrList.append(corr)
                pvalList.append(pval)

            if df_corr.empty:
                df_corr = pd.DataFrame(np.column_stack(corrList), columns=X.columns)
                df_pval = pd.DataFrame(np.column_stack(pvalList), columns=X.columns)
            else:
                dat_corr = pd.DataFrame(np.column_stack(corrList), columns=X.columns)
                df_corr = pd.concat([df_corr, dat_corr]);

                dat_pval = pd.DataFrame(np.column_stack(pvalList), columns=X.columns)
                df_pval = pd.concat([df_pval, dat_pval]);

        df_corr.index = X.columns
        df_pval.index = X.columns

        return df_corr, df_pval
    else:
        print("No \"Name\" column in the Peak table")