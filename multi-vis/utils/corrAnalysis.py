from scipy import stats
from tqdm import tqdm
import numpy as np
import pandas as pd

def corrAnalysis(X, correlationType):

    df_corr = pd.DataFrame()
    df_pval = pd.DataFrame()

    for i in tqdm(X.columns):

        corrList = []
        pvalList = []

        for a in X.columns:

            mask = ~np.isnan(X[i].values) & ~np.isnan(X[a].values)
            x = X[i].values[mask]
            y = X[a].values[mask]

            if correlationType == "pearson":
                corr, pval = stats.pearsonr(x, y)
            elif correlationType == "spearman":
                corr, pval = stats.spearmanr(x, y)
            elif correlationType == "kendalltau":
                corr, pval = stats.kendalltau(x, y)

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