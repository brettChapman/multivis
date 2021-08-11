import sys
import pandas as pd
import numpy as np
from scipy import stats
from itertools import compress
import statsmodels.stats.multitest as smt
import scikits.bootstrap as bootstrap
from sklearn.decomposition import PCA
from .scaler import scaler
from .imputeData import imputeData

class statistics:
    usage = """Generate a table of parametric or non-parametric statistics and merges them with the Peak Table (node table).
        Initial_Parameters
            ----------
            peaktable : Pandas dataframe containing peak data. Must contain 'Name' and 'Label'.
            datatable : Pandas dataframe matrix containing values for statistical analysis

        Methods
            -------
            set_params : Set parameters -
                parametric: Perform parametric statistical analysis, assuming the data is normally distributed (default: True)
                log_data: Perform a log ('natural', base 2 or base 10) on all data prior to statistical analysis (default: (False, 2))
                scale_data: Scale the data ('standard' (centers to the mean and scales to unit variance), 'minmax' (scales between 0 and 1), 'maxabs' (scales to the absolute maximum value), 'robust' (centers to the median and scales to between 25th and 75th quantile range) (default: (True, 'standard'))
                impute_data: Impute any missing values using KNN impute with a set number of nearest neighbours (default: (False, 3))
                group_column_name: The group column name used in the datatable (default: None)
                control_group_name: The control group name in the datatable, if available (default: None)
                group_alpha_CI: The alpha value for group confidence intervals (default: 0.05)
                fold_change_alpha_CI: The alpha value for mean/median fold change confidence intervals (default: 0.05)
                pca_alpha_CI: The alpha value for the PCA confidence intervals (default: 0.05)
                total_missing: Calculate the total missing values per feature (Default: False)
                group_missing: Calculate the missing values per feature per group (if group_column_name not None) (Default: False)
                pca_loadings: Calculate PC1 and PC2 loadings for each feature (Default: True)
                normality_test: Determine normal distribution across whole dataset using Shapiro-Wilk test (pvalues < 0.05 ~ non-normal distribution) (default: True)
                group_normality_test: Determine normal distribution across each group (if group_column_name not None) using Shapiro-Wilk test (pvalues < 0.05 ~ non-normal distribution) (default: True)
                group_mean_CI: Determine the mean with bootstrapped CI across each group (if parametric = True and group_column_name not None) (default: True)
                group_median_CI: Determine the median with bootstrapped CI across each group (if parametric = False and group_column_name not None) (default: True)
                mean_fold_change: Calculate the mean fold change with bootstrapped confidence intervals (if parametric = True, group_column_name not None and control_group_name not None) (default: False)
                median_fold_change: Calculate the median fold change with bootstrapped confidence intervals (if parametric = False, group_column_name not None and control_group_name not None) (default: False) 
                levene_twoGroup: Test null hypothesis that control group and each of the other groups come from populations with equal variances (if group_column_name not None and control_group_name not None) (default: False)
                levene_allGroup: Test null hypothesis that all groups come from populations with equal variances (if group_column_name not None) (default: False)
                oneway_Anova_test: Test null hypothesis that all groups have the same population mean, with included Benjamini-Hochberg FDR (if parametric = True and group_column_name not None) (default: False)
                kruskal_wallis_test: Test null hypothesis that population median of all groups are equal, with included Benjamini-Hochberg FDR (if parametric = False and group_column_name not None) (default: False)
                ttest_oneGroup: Calculate the T-test for the mean across all the data (one group), with included Benjamini-Hochberg FDR (if parametric = True, group_column_name is None or there is only 1 group in the data) (default: False)
                ttest_twoGroup: Calculate the T-test for the mean of two groups, with one group being the control group, with included Benjamini-Hochberg FDR (if parametric = True, group_column_name not None and control_group_name not None) (default: False)
                mann_whitney_u_test: Compute the Mann-Whitney U test to determine differences in distribution between two groups, with one being the control group, with included Benjamini-Hochberg FDR (if parametric = False, group_column_name not None and control_group_name not None) (default: False)
            
            help : Print this help text
            
            calculate : Performs the statistical calculations and outputs the Peak Table (node table) with the results appended.
    """

    def __init__(self, peaktable, datatable):
        peaktable = self.__checkPeakTable(self.__checkData(peaktable))
        datatable = self.__checkData(datatable)

        #Slice the meta-data, and select only peaks from the peaktable for processing, and add the meta-data back
        meta = datatable.T[~datatable.T.index.isin(peaktable['Name'])].T.reset_index(drop=True)
        dat = datatable[peaktable['Name']].reset_index()
        datatable = pd.concat([meta, dat], axis=1).set_index(['index'])
        datatable.index.name = None

        self.__peaktable = peaktable
        self.__datatable = datatable

        self.set_params()

    def help(self):
        print(statistics.usage)

    def set_params(self, parametric=True, log_data=(False,2), scale_data=(False, 'standard'), impute_data=(False, 3), group_column_name=None, control_group_name=None, group_alpha_CI=0.05, fold_change_alpha_CI=0.05, pca_alpha_CI=0.05, total_missing=False, group_missing=False, pca_loadings=True, normality_test=True, group_normality_test=True, group_mean_CI=True, group_median_CI=True, mean_fold_change=False, median_fold_change=False, kruskal_wallis_test=False, levene_twoGroup=False, levene_allGroup=False, oneway_Anova_test=False, ttest_oneGroup=False, ttest_twoGroup=False, mann_whitney_u_test=False):

        parametric, log_data, scale_data, impute_data, group_column_name, control_group_name, group_alpha_CI, fold_change_alpha_CI, pca_alpha_CI, total_missing, group_missing, pca_loadings, normality_test, group_normality_test, group_mean_CI, group_median_CI, mean_fold_change, median_fold_change, oneway_Anova_test, kruskal_wallis_test, levene_twoGroup, levene_allGroup, ttest_oneGroup, ttest_twoGroup, mann_whitney_u_test = self.__paramCheck(parametric, log_data, scale_data, impute_data, group_column_name, control_group_name, group_alpha_CI, fold_change_alpha_CI, pca_alpha_CI, total_missing, group_missing, pca_loadings, normality_test, group_normality_test, group_mean_CI, group_median_CI, mean_fold_change, median_fold_change, oneway_Anova_test, kruskal_wallis_test, levene_twoGroup, levene_allGroup, ttest_oneGroup, ttest_twoGroup, mann_whitney_u_test)

        self.__parametric = parametric;
        self.__log_data = log_data;
        self.__scale_data = scale_data;
        self.__impute_data = impute_data;
        self.__group_column_name = group_column_name;
        self.__control_group_name = control_group_name;
        self.__group_alpha_CI = group_alpha_CI;
        self.__fold_change_alpha_CI = fold_change_alpha_CI;
        self.__pca_alpha_CI = pca_alpha_CI;
        self.__total_missing = total_missing;
        self.__group_missing = group_missing;
        self.__pca_loadings = pca_loadings;
        self.__normality_test = normality_test;
        self.__group_normality_test = group_normality_test;
        self.__group_mean_CI = group_mean_CI;
        self.__group_median_CI = group_median_CI;
        self.__mean_fold_change = mean_fold_change;
        self.__median_fold_change = median_fold_change;
        self.__oneway_Anova_test = oneway_Anova_test;
        self.__kruskal_wallis_test = kruskal_wallis_test;
        self.__levene_twoGroup = levene_twoGroup;
        self.__levene_allGroup = levene_allGroup;
        self.__ttest_oneGroup = ttest_oneGroup;
        self.__ttest_twoGroup = ttest_twoGroup;
        self.__mann_whitney_u_test = mann_whitney_u_test;

    def calculate(self):

        peaktable = self.__peaktable
        datatable = self.__datatable
        parametric = self.__parametric
        log_data = self.__log_data
        scale_data = self.__scale_data
        impute_data = self.__impute_data
        group_column_name = self.__group_column_name
        control_group_name = self.__control_group_name
        group_alpha_CI = self.__group_alpha_CI
        fold_change_alpha_CI = self.__fold_change_alpha_CI
        pca_alpha_CI = self.__pca_alpha_CI
        total_missing = self.__total_missing
        group_missing = self.__group_missing
        pca_loadings = self.__pca_loadings
        normality_test = self.__normality_test
        group_normality_test = self.__group_normality_test
        group_mean_CI = self.__group_mean_CI
        group_median_CI = self.__group_median_CI
        mean_fold_change = self.__mean_fold_change
        median_fold_change = self.__median_fold_change
        kruskal_wallis_test = self.__kruskal_wallis_test
        levene_twoGroup = self.__levene_twoGroup
        levene_allGroup = self.__levene_allGroup
        oneway_Anova_test = self.__oneway_Anova_test
        ttest_oneGroup = self.__ttest_oneGroup
        ttest_twoGroup = self.__ttest_twoGroup
        mann_whitney_u_test = self.__mann_whitney_u_test

        peakNames = list(peaktable['Name'].values)

        meta = datatable.T[~datatable.T.index.isin(peakNames)].T.reset_index(drop=True)

        peakData = datatable[peakNames].reset_index(drop=True)

        (log_bool, log_base) = log_data;

        if log_bool:
            if isinstance(log_base, str) and log_base.lower() == 'natural':
                peakData = peakData.applymap(np.log)
            elif log_base == 2:
                peakData = peakData.applymap(np.log2)
            elif log_base == 10:
                peakData = peakData.applymap(np.log10)
            else:
                print("Error: The chosen log type is invalid.")
                sys.exit()

        (scale_bool, scale_type) = scale_data

        if scale_bool:
            if isinstance(scale_type, str) and scale_type.lower() == 'standard':
                peakData = scaler(peakData, type=scale_type.lower()).reset_index(drop=True)
            elif isinstance(scale_type, str) and scale_type.lower() == 'minmax':
                peakData = scaler(peakData, type=scale_type.lower()).reset_index(drop=True)
            elif isinstance(scale_type, str) and scale_type.lower() == 'maxabs':
                peakData = scaler(peakData, type=scale_type.lower()).reset_index(drop=True)
            elif isinstance(scale_type, str) and scale_type.lower() == 'robust':
                peakData = scaler(peakData, type=scale_type.lower()).reset_index(drop=True)
            else:
                print("Error: The chosen scale type is invalid.")
                sys.exit()

        (impute_bool, k) = impute_data;

        if impute_bool:
            peakData = imputeData(peakData, k=k).reset_index(drop=True)

        if not isinstance(peakData, pd.DataFrame):
            peakData = pd.DataFrame(peakData, columns=list(peakNames)).reset_index(drop=True)

        #Add the meta data back in with the logged, scaled, or imputed data
        datatable = pd.concat([meta, peakData], axis=1).reset_index(drop=True)

        statsData = pd.DataFrame()

        if group_column_name is not None:
            groups = np.unique(datatable[group_column_name].values)
            groupData = []

            # Append each group to a list
            for group in groups:
                groupData.append(datatable.loc[datatable[group_column_name] == group])

        #Iterate over each peak/feature and calculate statistics
        for peakName in peakNames:

            statsDataDict = {}
            groupDict = {}

            df_totalGrpMissing = pd.DataFrame()
            totalGrpMissingTitles = []

            df_meanFold = pd.DataFrame()
            df_medianFold = pd.DataFrame()
            df_mannWhitney = pd.DataFrame()
            df_ttest = pd.DataFrame()
            df_levene_twoGroup = pd.DataFrame()
            df_groupNormality = pd.DataFrame()
            df_grpMeanCI = pd.DataFrame()
            df_grpMedianCI = pd.DataFrame()
            mannWhitneyTitles = []
            ttestTitles = []
            leveneTwoGroupTitles = []

            mannwhitney_pvalue_name = ''
            mannwhitney_statistic_name = ''

            # for each group populate a group dictionary
            if group_column_name is not None:
                for grpIdx, group in enumerate(groupData):

                    # Calculate values missing within each group
                    if group_missing:
                        df_totalGrpMissing = self.__GroupMissing_Calc(group, groups, grpIdx, peakName, totalGrpMissingTitles, df_totalGrpMissing)
                        statsDataDict['GroupMissingValues'] = df_totalGrpMissing

                    x = group[[peakName]].values
                    groupDict[groups[grpIdx]] = x[~np.isnan(x)]

            if control_group_name is not None:
                controlGroup = groupDict[control_group_name];

            if group_column_name is not None:

                for key, group in groupDict.items():

                    if group_normality_test:
                        df_groupNormality = self.__GroupNormality(key, group, df_groupNormality)
                        statsDataDict['GroupNormality'] = df_groupNormality

                    if parametric:
                        if group_mean_CI:
                            df_grpMeanCI = self.__GroupMeanCI(key, group, df_grpMeanCI, group_alpha_CI)
                            statsDataDict['GroupMeanCI'] = df_grpMeanCI
                    else:
                        if group_median_CI:
                            df_grpMedianCI = self.__GroupMedianCI(key, group, df_grpMedianCI, group_alpha_CI)
                            statsDataDict['GroupMedianCI'] = df_grpMedianCI

                    if key != control_group_name and control_group_name is not None:

                        # Merge group and control, accounting for different array lengths by replacing with nan (indices need to be the same length for bootstrapping)
                        groupPairDict = dict(controlGroup=controlGroup, caseGroup=group)
                        groupPair = pd.DataFrame(dict([ (k,pd.Series(v)) for k,v in groupPairDict.items() ]))
                        controlList = np.array(groupPair['controlGroup'].values)
                        caseList = np.array(groupPair['caseGroup'].values)
                        groupList = list(zip(controlList, caseList))

                        if parametric:
                            if ttest_twoGroup:
                                # T-test statistic calculation for two samples (one always being the control)
                                TTEST_twoGroup_statistic, TTEST_twoGroup_pvalue = self.__TTEST_twoGroup(groupList)

                            if mean_fold_change:
                                meanFoldChange = self.__mean_fold(groupList)

                                # Boostrap for confidence intervals for the mean fold change
                                if ((len(group) > 2) and (len(controlGroup) > 2)):
                                    meanFold = lambda x: self.__mean_fold(x)
                                    CIs = bootstrap.ci(data=groupList, statfunction=meanFold, n_samples=500, alpha=fold_change_alpha_CI)
                                else:
                                    CIs = [np.nan, np.nan]
                        else:
                            if mann_whitney_u_test:
                                # Mann-Whitney U statistic calculation for two samples (one always being the control)
                                MannWhitney_statistic, MannWhitney_pvalue = self.__MANN_WHITNEY_U(groupList)

                            if median_fold_change:
                                medianFoldChange = self.__median_fold(groupList)

                                # Boostrap for confidence intervals for the median fold change
                                if ((len(group) > 2) and (len(controlGroup) > 2)):
                                    medianFold = lambda x: self.__median_fold(x)
                                    CIs = bootstrap.ci(data=groupList, statfunction=medianFold, n_samples=500, alpha=fold_change_alpha_CI)
                                else:
                                    CIs = [np.nan, np.nan]

                        if levene_twoGroup:
                            # Levene statistic calculation for two samples (one always being the control)
                            LEVENE_twoGroup_statistic, LEVENE_twoGroup_pvalue = self.__LEVENE_twoGroup(groupList)

                        if parametric:
                            ttest_twoGroup_statistics_name = 'TTEST-twoGroup_statistic_' + str(key)
                            ttest_twoGroup_pvalue_name = 'TTEST-twoGroup_pvalue_' + str(key)

                            ttestTitles.append(ttest_twoGroup_statistics_name)
                            ttestTitles.append(ttest_twoGroup_pvalue_name)

                            mean_fold_change_name = 'MeanFoldChange_' + str(key)
                            mean_fold_change_name_CIlower = 'MeanFoldChange_CI_lower_' + str(key)
                            mean_fold_change_name_CIupper = 'MeanFoldChange_CI_upper_' + str(key)
                            mean_fold_change_name_sig = 'MeanFoldChange_sig_' + str(key)

                        else:
                            mannwhitney_statistic_name = 'MannWhitneyU_statistic_' + str(key)
                            mannwhitney_pvalue_name = 'MannWhitneyU_pvalue_' + str(key)

                            mannWhitneyTitles.append(mannwhitney_statistic_name)
                            mannWhitneyTitles.append(mannwhitney_pvalue_name)

                            median_fold_change_name = 'MedianFoldChange_' + str(key)
                            median_fold_change_name_CIlower = 'MedianFoldChange_CI_lower_' + str(key)
                            median_fold_change_name_CIupper = 'MedianFoldChange_CI_upper_' + str(key)
                            median_fold_change_name_sig = 'MedianFoldChange_sig_' + str(key)

                        levene_twoGroup_statistics_name = 'LEVENE-twoGroup_statistic_' + str(key)
                        levene_twoGroup_pvalue_name = 'LEVENE-twoGroup_pvalue_' + str(key)

                        leveneTwoGroupTitles.append(levene_twoGroup_statistics_name)
                        leveneTwoGroupTitles.append(levene_twoGroup_pvalue_name)

                        if ttest_twoGroup and parametric:
                            if df_ttest.empty:
                                df_ttest = pd.DataFrame({ttest_twoGroup_statistics_name: [TTEST_twoGroup_statistic], ttest_twoGroup_pvalue_name: [TTEST_twoGroup_pvalue]})
                            else:
                                df_ttest = pd.concat([df_ttest, pd.DataFrame({ttest_twoGroup_statistics_name: [TTEST_twoGroup_statistic], ttest_twoGroup_pvalue_name: [TTEST_twoGroup_pvalue]})], axis=1).reset_index(drop=True)

                            statsDataDict['TTEST-twoGroup'] = df_ttest

                        if mann_whitney_u_test and not parametric:
                            if df_mannWhitney.empty:
                                df_mannWhitney = pd.DataFrame({mannwhitney_statistic_name: [MannWhitney_statistic], mannwhitney_pvalue_name: [MannWhitney_pvalue]})
                            else:
                                df_mannWhitney = pd.concat([df_mannWhitney, pd.DataFrame({mannwhitney_statistic_name: [MannWhitney_statistic], mannwhitney_pvalue_name: [MannWhitney_pvalue]})], axis=1).reset_index(drop=True)

                            statsDataDict['MannWhitneyU'] = df_mannWhitney

                        if mean_fold_change and parametric:

                            sigMeanFold = np.add(np.sign(np.multiply(CIs[0], CIs[1])), 1).astype(bool);

                            if df_meanFold.empty:
                                df_meanFold = pd.DataFrame({mean_fold_change_name: [meanFoldChange], mean_fold_change_name_CIlower: CIs[0], mean_fold_change_name_CIupper: CIs[1], mean_fold_change_name_sig: [sigMeanFold]})
                            else:
                                df_meanFold = pd.concat([df_meanFold, pd.DataFrame({mean_fold_change_name: [meanFoldChange], mean_fold_change_name_CIlower: CIs[0], mean_fold_change_name_CIupper: CIs[1], mean_fold_change_name_sig: [sigMeanFold]})], axis=1).reset_index(drop=True)

                            statsDataDict['MeanFoldChange'] = df_meanFold

                        if median_fold_change and not parametric:

                            sigMedianFold = np.add(np.sign(np.multiply(CIs[0], CIs[1])), 1).astype(bool);

                            if df_medianFold.empty:
                                df_medianFold = pd.DataFrame({median_fold_change_name: [medianFoldChange], median_fold_change_name_CIlower: CIs[0], median_fold_change_name_CIupper: CIs[1], median_fold_change_name_sig: [sigMedianFold]})
                            else:
                                df_medianFold = pd.concat([df_medianFold, pd.DataFrame({median_fold_change_name: [medianFoldChange], median_fold_change_name_CIlower: CIs[0], median_fold_change_name_CIupper: CIs[1], median_fold_change_name_sig: [sigMedianFold]})], axis=1).reset_index(drop=True)

                            statsDataDict['MedianFoldChange'] = df_medianFold

                        if levene_twoGroup:
                            if df_levene_twoGroup.empty:
                                df_levene_twoGroup = pd.DataFrame({levene_twoGroup_statistics_name: [LEVENE_twoGroup_statistic], levene_twoGroup_pvalue_name: [LEVENE_twoGroup_pvalue]})
                            else:
                                df_levene_twoGroup = pd.concat([df_levene_twoGroup, pd.DataFrame({levene_twoGroup_statistics_name: [LEVENE_twoGroup_statistic], levene_twoGroup_pvalue_name: [LEVENE_twoGroup_pvalue]})], axis=1).reset_index(drop=True)

                            statsDataDict['LEVENE-twoGroup'] = df_levene_twoGroup

            # Filter dictionary for empty values
            groupDict_filt = {}
            for key, group in groupDict.items():
                if (len(group) > 0):
                    groupDict_filt[key] = group

            # One-way Anova and Kruskal-Wallis test for each group
            if oneway_Anova_test and parametric and group_column_name is not None:
                df_onewayANOVA = self.__oneWayANOVA(groupDict_filt)
                statsDataDict['One-way ANOVA'] = df_onewayANOVA

            if kruskal_wallis_test and not parametric and group_column_name is not None:
                df_KW = self.__kruskalWallis(groupDict_filt)
                statsDataDict['Kruskal-Wallis'] = df_KW

            if levene_allGroup and group_column_name is not None:
                df_levene_allGroup = self.__LEVENE_allGroup(groupDict_filt)
                statsDataDict['LEVENE-allGroup'] = df_levene_allGroup

            peak = datatable[[peakName]]

            if total_missing:
                df_totalMissing = self.__TotalMissing_Calc(peak);

                statsDataDict['TotalMissing'] = df_totalMissing

            pList = peak.values
            pList = pList[~np.isnan(pList)]

            if normality_test:
                df_normality = self.__normality(pList);
                statsDataDict['Normality'] = df_normality

            if ttest_oneGroup:
                df_TTEST = self.__TTEST_oneGroup(pList)
                statsDataDict['TTEST-oneGroup'] = df_TTEST

            if statsData.empty:
                if statsDataDict:
                    statsData = pd.concat(list(statsDataDict.values()), axis=1)
            else:
                if statsDataDict:
                    statsData = pd.concat([statsData, pd.concat(list(statsDataDict.values()), axis=1)], axis=0).reset_index(drop=True)

        if ttest_oneGroup and parametric:
            TTEST_qvalueData = pd.DataFrame()
            pvals = statsData['TTEST-oneGroup_pvalue'].values.flatten()
            mask = np.isfinite(pvals)
            pval_masked = [x for x in compress(pvals, mask)]

            TTEST_BHFDR_qval = np.empty(len(pvals))
            TTEST_BHFDR_qval.fill(np.nan)

            _, TTEST_BHFDR_qval[mask] = smt.multipletests(pval_masked, alpha=0.05, method='fdr_bh')[:2]

            TTEST_qvalueData['TTEST-oneGroup_BHFDR_qvalue'] = pd.Series(TTEST_BHFDR_qval)

            statsData = pd.merge(statsData, TTEST_qvalueData, left_index=True, right_index=True)

        if ttest_twoGroup and parametric and group_column_name is not None:
            TTEST_qvalueData = pd.DataFrame()
            ttestTitles_pvalues = ttestTitles[1:len(ttestTitles):2]

            ttestQvalueNames = []

            for val in ttestTitles_pvalues:
                pvals = statsData[val].values.flatten()
                mask = np.isfinite(pvals)
                pval_masked = [x for x in compress(pvals, mask)]

                Ttest_BHFDR_qval = np.empty(len(pvals))
                Ttest_BHFDR_qval.fill(np.nan)

                _, Ttest_BHFDR_qval[mask] = smt.multipletests(pval_masked, alpha=0.05, method='fdr_bh')[:2]

                val_BHFDR_qvalue = val.replace('pvalue', 'BHFDR_qvalue')

                ttestQvalueNames.append(val_BHFDR_qvalue)

                TTEST_qvalueData[val_BHFDR_qvalue] = pd.Series(Ttest_BHFDR_qval)

            statsData = pd.merge(statsData, TTEST_qvalueData, left_index=True, right_index=True)

        if oneway_Anova_test and parametric and group_column_name is not None:
            onewayANOVA_qvalueData = pd.DataFrame()
            pvals = statsData['onewayANOVA_pvalue'].values.flatten()

            mask = np.isfinite(pvals)
            pval_masked = [x for x in compress(pvals, mask)]

            onewayANOVA_BHFDR_qval = np.empty(len(pvals))
            onewayANOVA_BHFDR_qval.fill(np.nan)

            onewayANOVA_BYFDR_qval = np.empty(len(pvals))
            onewayANOVA_BYFDR_qval.fill(np.nan)

            _, onewayANOVA_BHFDR_qval[mask] = smt.multipletests(pval_masked, alpha=0.05, method='fdr_bh')[:2]

            onewayANOVA_qvalueData['onewayANOVA_BHFDR_qvalue'] = pd.Series(onewayANOVA_BHFDR_qval)

            statsData = pd.merge(statsData, onewayANOVA_qvalueData, left_index=True, right_index=True)

        if kruskal_wallis_test and not parametric and group_column_name is not None:
            KW_qvalueData = pd.DataFrame()
            pvals = statsData['Kruskal–Wallis_pvalue'].values.flatten()
            mask = np.isfinite(pvals)
            pval_masked = [x for x in compress(pvals, mask)]

            KW_BHFDR_qval = np.empty(len(pvals))
            KW_BHFDR_qval.fill(np.nan)

            KW_BYFDR_qval = np.empty(len(pvals))
            KW_BYFDR_qval.fill(np.nan)

            _, KW_BHFDR_qval[mask] = smt.multipletests(pval_masked, alpha=0.05, method='fdr_bh')[:2]

            KW_qvalueData['Kruskal-Wallis_BHFDR_qvalue'] = pd.Series(KW_BHFDR_qval)

            statsData = pd.merge(statsData, KW_qvalueData, left_index=True, right_index=True)

        if mann_whitney_u_test and not parametric and group_column_name is not None:
            MannWhitney_qvalueData = pd.DataFrame()
            mannWhitneyTitles_pvalues = mannWhitneyTitles[1:len(mannWhitneyTitles):2]

            mannWhitneyQvalueNames = []

            for val in mannWhitneyTitles_pvalues:
                pvals = statsData[val].values.flatten()
                mask = np.isfinite(pvals)
                pval_masked = [x for x in compress(pvals, mask)]

                MannWhitney_BHFDR_qval = np.empty(len(pvals))
                MannWhitney_BHFDR_qval.fill(np.nan)

                _, MannWhitney_BHFDR_qval[mask] = smt.multipletests(pval_masked, alpha=0.05, method='fdr_bh')[:2]

                val_BHFDR_qvalue = val.replace('pvalue', 'BHFDR_qvalue')

                mannWhitneyQvalueNames.append(val_BHFDR_qvalue)

                MannWhitney_qvalueData[val_BHFDR_qvalue] = pd.Series(MannWhitney_BHFDR_qval)

            statsData = pd.merge(statsData, MannWhitney_qvalueData, left_index=True, right_index=True)


        if pca_loadings:
            peakData = datatable[peakNames].reset_index(drop=True)
            d_filled = imputeData(peakData, 3)

            #pca, pca_x, pca_loadings = self.__PCA_Calc(d_filled)
            pca, pca_loadings = self.__PCA_Calc(d_filled)
            df_pca_components = pd.DataFrame(pca_loadings, columns=['PC1', 'PC2'])

            bootpc1 = lambda x: self.__boot_pca(x, pca.components_.T, 1)
            bootpc2 = lambda x: self.__boot_pca(x, pca.components_.T, 2)

            PC1_CIs = bootstrap.ci(data=d_filled, statfunction=bootpc1, n_samples=500, alpha=pca_alpha_CI)
            PC2_CIs = bootstrap.ci(data=d_filled, statfunction=bootpc2, n_samples=500, alpha=pca_alpha_CI)

            pc1_lower = np.array(PC1_CIs[0, :]).flatten()
            pc1_upper = np.array(PC1_CIs[1, :]).flatten()
            pc2_lower = np.array(PC2_CIs[0, :]).flatten()
            pc2_upper = np.array(PC2_CIs[1, :]).flatten()

            sigPC1 = np.add(np.sign(np.multiply(pc1_lower, pc1_upper)), 1).astype(bool);
            sigPC2 = np.add(np.sign(np.multiply(pc2_lower, pc2_upper)), 1).astype(bool);

            df_pca_stats = pd.DataFrame({"PC1_lower": pc1_lower, "PC1_upper": pc1_upper, "PC1_sig": sigPC1,
                                         "PC2_lower": pc2_lower, "PC2_upper": pc2_upper, "PC2_sig": sigPC2})

            if not statsData.empty:
                df_pca = pd.merge(statsData, df_pca_components, left_index=True, right_index=True);
                statsData = pd.merge(df_pca, df_pca_stats, left_index=True, right_index=True);
            else:
                statsData = pd.merge(df_pca_components, df_pca_stats, left_index=True, right_index=True);

        if not statsData.empty:
            statsData = pd.merge(peaktable.reset_index(drop=True), statsData, left_index=True, right_index=True)
        else:
            statsData = peaktable.copy()

        return statsData

    def __checkData(self, df):

        if not isinstance(df, pd.DataFrame):
            print("Error: A dataframe was not entered. Please check your data.")

        return df

    def __checkPeakTable(self, PeakTable):

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

    def __paramCheck(self, parametric, log_data, scale_data, impute_data, group_column_name, control_group_name, group_alpha_CI, fold_change_alpha_CI, pca_alpha_CI, total_missing, group_missing, pca_loadings, normality_test, group_normality_test, group_mean_CI, group_median_CI, mean_fold_change, median_fold_change, oneway_Anova_test, kruskal_wallis_test, levene_twoGroup, levene_allGroup, ttest_oneGroup, ttest_twoGroup, mann_whitney_u_test):

        peaks = self.__peaktable
        data = self.__datatable

        meta = data.T[~data.T.index.isin(peaks['Name'])].T.reset_index(drop=True)
        col_list = list(meta.columns)

        if group_column_name is not None:
            group_names = list(set(list(meta[group_column_name].values)))
        else:
            group_names = []

        if not isinstance(parametric, bool):
            print("Error: Parametric not valid. Choose either \"True\" or \"False\".")
            sys.exit()

        if not isinstance(log_data, tuple):
            print("Error: Log data type if not a tuple. Please ensure the value is a tuple (e.g. (True, 2).")
            sys.exit()
        else:
            (log_bool, log_base) = log_data

            if not isinstance(log_bool, bool):
                print("Error: Log data first tuple item is not a boolean value. Choose either \"True\" or \"False\".")
                sys.exit()

            base_types = ['natural', 2, 10]

            if isinstance(log_base, str):
                log_base = log_base.lower()

            if log_base not in base_types:
                print("Error: Log data second tuple item is not valid. Choose one of {}.".format(', '.join(base_types)))
                sys.exit()

        if not isinstance(scale_data, tuple):
            print("Error: Scale data type if not a tuple. Please ensure the value is a tuple (e.g. (True, 'standard').")
            sys.exit()
        else:
            (scale_bool, scale_type) = scale_data

            if not isinstance(scale_bool, bool):
                print("Error: Scale data first tuple item is not a boolean value. Choose either \"True\" or \"False\".")
                sys.exit()

            scale_types = ['standard', 'minmax', 'maxabs', 'robust']

            if isinstance(scale_type, str):
                scale_type = scale_type.lower()

            if scale_type not in scale_types:
                print("Error: Scale data second tuple item is not valid. Choose one of {}.".format(
                    ', '.join(scale_types)))
                sys.exit()

        if not isinstance(impute_data, tuple):
            print("Error: Impute data type if not a tuple. Please ensure the value is a tuple (e.g. (True, 3).")
            sys.exit()
        else:
            (impute_bool, k) = impute_data

            if not isinstance(impute_bool, bool):
                print("Error: Impute data first tuple item is not a boolean value. Choose either \"True\" or \"False\".")
                sys.exit()

            if not isinstance(k, float):
                if not isinstance(k, int):
                    print("Error: Impute data second tuple item, the nearest neighbours k value, is not valid. Choose a float or integer value.")
                    sys.exit()

        if group_column_name is not None:
            if not isinstance(group_column_name, str):
                print("Error: Group column name is not valid. Choose a string value.")
                sys.exit()
            else:
                if group_column_name not in col_list:
                    print("Error: Group column name not valid. Choose one of {}.".format(', '.join(col_list)))
                    sys.exit()

        if control_group_name is not None:
            if not isinstance(control_group_name, str):
                print("Error: Control group name is not valid. Choose a string value.")
                sys.exit()
            else:
                if control_group_name not in group_names:
                    print("Error: Control group name not valid. Choose one of {}.".format(', '.join(group_names)))
                    sys.exit()

        if not isinstance(group_alpha_CI, float):
            print("Error: Group alpha confidence interval is not valid. Choose a float value.")
            sys.exit()

        if not isinstance(fold_change_alpha_CI, float):
            print("Error: Mean/Median fold change alpha confidence interval is not valid. Choose a float value.")
            sys.exit()

        if not isinstance(pca_alpha_CI, float):
            print("Error: PCA alpha confidence interval is not valid. Choose a float value.")
            sys.exit()

        if not isinstance(total_missing, bool):
            print("Error: Total missing is not valid. Choose either \"True\" or \"False\".")
            sys.exit()

        if not isinstance(group_missing, bool):
            print("Error: Group missing is not valid. Choose either \"True\" or \"False\".")
            sys.exit()

        if not isinstance(pca_loadings, bool):
            print("Error: PCA loadings is not valid. Choose either \"True\" or \"False\".")
            sys.exit()

        if not isinstance(normality_test, bool):
            print("Error: Normality test is not valid. Choose either \"True\" or \"False\".")
            sys.exit()

        if not isinstance(group_normality_test, bool):
            print("Error: Group normality test is not valid. Choose either \"True\" or \"False\".")
            sys.exit()

        if not isinstance(group_mean_CI, bool):
            print("Error: Group mean confidence interval is not valid. Choose either \"True\" or \"False\".")
            sys.exit()

        if not isinstance(group_median_CI, bool):
            print("Error: Group median confidence interval is not valid. Choose either \"True\" or \"False\".")
            sys.exit()

        if not isinstance(mean_fold_change, bool):
            print("Error: Mean fold change is not valid. Choose either \"True\" or \"False\".")
            sys.exit()

        if not isinstance(median_fold_change, bool):
            print("Error: Median fold change is not valid. Choose either \"True\" or \"False\".")
            sys.exit()

        if not isinstance(oneway_Anova_test, bool):
            print("Error: One-way Anova test is not valid. Choose either \"True\" or \"False\".")
            sys.exit()

        if not isinstance(kruskal_wallis_test, bool):
            print("Error: Kruskal–Wallis test is not valid. Choose either \"True\" or \"False\".")
            sys.exit()

        if not isinstance(levene_twoGroup, bool):
            print("Error: Levene two group is not valid. Choose either \"True\" or \"False\".")
            sys.exit()

        if not isinstance(levene_allGroup, bool):
            print("Error: Levene all group is not valid. Choose either \"True\" or \"False\".")
            sys.exit()

        if not isinstance(ttest_oneGroup, bool):
            print("Error: T-test one group is not valid. Choose either \"True\" or \"False\".")
            sys.exit()

        if not isinstance(ttest_twoGroup, bool):
            print("Error: T-test two group is not valid. Choose either \"True\" or \"False\".")
            sys.exit()

        if not isinstance(mann_whitney_u_test, bool):
            print("Error: Mann–Whitney U test is not valid. Choose either \"True\" or \"False\".")
            sys.exit()

        return parametric, log_data, scale_data, impute_data, group_column_name, control_group_name, group_alpha_CI, fold_change_alpha_CI, pca_alpha_CI, total_missing, group_missing, pca_loadings, normality_test, group_normality_test, group_mean_CI, group_median_CI, mean_fold_change, median_fold_change, oneway_Anova_test, kruskal_wallis_test, levene_twoGroup, levene_allGroup, ttest_oneGroup, ttest_twoGroup, mann_whitney_u_test

    def __mean_fold(self, groupList):
        (controlGroup, caseGroup) = zip(*groupList)

        if ((len(list(caseGroup)) > 0) and (len(list(controlGroup)) > 0)):
            meanFoldChange = np.nanmean(list(caseGroup)) / np.nanmean(list(controlGroup))
        else:
            meanFoldChange = np.nan

        return meanFoldChange

    def __median_fold(self, groupList):
        (controlGroup, caseGroup) = zip(*groupList)

        if ((len(list(caseGroup)) > 0) and (len(list(controlGroup)) > 0)):
            medianFoldChange = np.nanmedian(list(caseGroup)) / np.nanmedian(list(controlGroup))
        else:
            medianFoldChange = np.nan

        return medianFoldChange

    def __PCA_Calc(self, data):

        pca = PCA(n_components=2)
        pca.fit_transform(data)

        return pca, pca.components_.T

    def __TotalMissing_Calc(self, peak):

        missing = peak.isnull().sum()
        totalMissing = np.multiply(np.divide(missing, peak.shape[0]).tolist(), 100)
        df_totalMissing = pd.DataFrame({'Percent_Total_Missing': totalMissing})

        return df_totalMissing

    def __GroupMissing_Calc(self, group, groups, grpIdx, peakName, totalGrpMissingTitles, df_totalGrpMissing):
        grpMissing = group[[peakName]].isnull().sum()

        totalGrpMissing = np.multiply(np.divide(grpMissing, group[[peakName]].shape[0]).tolist(), 100)

        totalGrpMissingName = 'Percent_Group_'+ str(groups[grpIdx]) +'_Missing'

        totalGrpMissingTitles.append(totalGrpMissingName)

        if df_totalGrpMissing.empty:
            df_totalGrpMissing = pd.DataFrame({totalGrpMissingName: totalGrpMissing})
        else:
            df_totalGrpMissing = pd.concat([df_totalGrpMissing, pd.DataFrame({totalGrpMissingName: totalGrpMissing})], axis=1)

        return df_totalGrpMissing

    def __GroupNormality(self, key, group, df_groupNormality):

        #Calculation of normal distribution for each group
        if len(group) > 2:
            Shapiro_statistic_grp, Shapiro_pvalue_grp = stats.shapiro(group)
        else:
            Shapiro_pvalue_grp = np.nan
            Shapiro_statistic_grp = np.nan

        grpStatName = 'Shapiro_statistic_' + str(key)

        grpPvalName = 'Shapiro_pvalue_' + str(key)

        df_Shapiro = pd.DataFrame({grpStatName: [Shapiro_statistic_grp], grpPvalName: [Shapiro_pvalue_grp]})

        if df_groupNormality.empty:
            df_groupNormality = df_Shapiro
        else:
            df_groupNormality = pd.concat([df_groupNormality, df_Shapiro], axis=1)

        return df_groupNormality

    def __GroupMeanCI(self, key, group, df_grpMCI, grpAlphaCI):

        #Calculate mean and CI of each group
        grpMeanName = 'Group_mean_' + str(key)
        grpMeanCIlowerName = 'Group_mean_CI_lower_' + str(key)
        grpMeanCIupperName = 'Group_mean_CI_upper_' + str(key)
        grpMean_sig_name = 'Group_mean_sig_' + str(key)

        if len(group) > 2:
            grpMean = np.nanmean(group)
            grpMean_CI = bootstrap.ci(data=group, statfunction=np.nanmean, n_samples=500, alpha=grpAlphaCI)
        else:
            if len(group) > 0:
                grpMean = np.nanmean(group)
                grpMean_CI = [np.nan,np.nan]
            else:
                grpMean = np.nan
                grpMean_CI = [np.nan, np.nan]

        sigMean = np.add(np.sign(np.multiply(grpMean_CI[0], grpMean_CI[1])), 1).astype(bool);

        df_grp_dat = pd.DataFrame({grpMeanName: [grpMean], grpMeanCIlowerName: grpMean_CI[0], grpMeanCIupperName: grpMean_CI[1], grpMean_sig_name: [sigMean]})

        if df_grpMCI.empty:
            df_grpMCI = df_grp_dat
        else:
            df_grpMCI = pd.concat([df_grpMCI, df_grp_dat], axis=1)

        return df_grpMCI

    def __GroupMedianCI(self, key, group, df_grpMCI, grpAlphaCI):

        # Calculate median and CI of each group
        grpMedianName = 'Group_median_' + str(key)
        grpMedianCIlowerName = 'Group_median_CI_lower_' + str(key)
        grpMedianCIupperName = 'Group_median_CI_upper_' + str(key)
        grpMedian_sig_name = 'Group_median_sig_' + str(key)

        if len(group) > 2:
            grpMedian = np.nanmedian(group)
            grpMedian_CI = bootstrap.ci(data=group, statfunction=np.nanmedian, n_samples=500, alpha=grpAlphaCI)
        else:
            if len(group) > 0:
                grpMedian = np.nanmedian(group)
                grpMedian_CI = [np.nan, np.nan]
            else:
                grpMedian = np.nan
                grpMedian_CI = [np.nan, np.nan]

        sigMedian = np.add(np.sign(np.multiply(grpMedian_CI[0], grpMedian_CI[1])), 1).astype(bool);

        df_grp_dat = pd.DataFrame({grpMedianName: [grpMedian], grpMedianCIlowerName: grpMedian_CI[0], grpMedianCIupperName: grpMedian_CI[1], grpMedian_sig_name: [sigMedian]})

        if df_grpMCI.empty:
            df_grpMCI = df_grp_dat
        else:
            df_grpMCI = pd.concat([df_grpMCI, df_grp_dat], axis=1)

        return df_grpMCI

    def __kruskalWallis(self, groupDict_filt):

        if (len(groupDict_filt) > 1):
            KW_statistic, KW_pvalue = stats.kruskal(*groupDict_filt.values())
        else:
            KW_statistic = np.nan
            KW_pvalue = np.nan

        df_KW = pd.DataFrame({'Kruskal–Wallis_statistic': [KW_statistic], 'Kruskal–Wallis_pvalue': [KW_pvalue]})

        return df_KW

    def __oneWayANOVA(self, groupDict_filt):

        if (len(groupDict_filt) > 0):
            onewayANOVA_statistic, onewayANOVA_pvalue = stats.f_oneway(*groupDict_filt.values())
        else:
            onewayANOVA_statistic = np.nan
            onewayANOVA_pvalue = np.nan

        df_onewayANOVA = pd.DataFrame({'onewayANOVA_statistic': [onewayANOVA_statistic], 'onewayANOVA_pvalue': [onewayANOVA_pvalue]})

        return df_onewayANOVA

    def __TTEST_oneGroup(self, pList):

        if (len(pList) > 1):
            TTEST_oneGroup_statistic, TTEST_oneGroup_pvalue = stats.ttest_1samp(pList, 0, nan_policy='omit')
        else:
            TTEST_oneGroup_statistic = np.nan
            TTEST_oneGroup_pvalue = np.nan

        df_TTEST_oneGroup = pd.DataFrame({'TTEST-oneGroup_statistic': [TTEST_oneGroup_statistic], 'TTEST-oneGroup_pvalue': [TTEST_oneGroup_pvalue]});

        return df_TTEST_oneGroup

    def __TTEST_twoGroup(self, groupList):
        (controlGroup, caseGroup) = zip(*groupList)

        if ((len(list(caseGroup)) > 0) and (len(list(controlGroup)) > 0)):
            TTEST_twoGroup_statistic, TTEST_twoGroup_pvalue = stats.ttest_ind(list(controlGroup), list(caseGroup), nan_policy='omit')
        else:
            TTEST_twoGroup_statistic = np.nan
            TTEST_twoGroup_pvalue = np.nan

        return TTEST_twoGroup_statistic, TTEST_twoGroup_pvalue

    def __MANN_WHITNEY_U(self, groupList):
        (controlGroup, caseGroup) = zip(*groupList)

        if ((len(list(caseGroup)) > 0) and (len(list(controlGroup)) > 0)):
            MannWhitney_statistic, MannWhitney_pvalue = stats.mannwhitneyu(list(controlGroup), list(caseGroup), alternative="two-sided")
        else:
            MannWhitney_statistic = np.nan
            MannWhitney_pvalue = np.nan

        return MannWhitney_statistic, MannWhitney_pvalue

    def __LEVENE_twoGroup(self, groupList):
        (controlGroup, caseGroup) = zip(*groupList)

        if ((len(list(caseGroup)) > 0) and (len(list(controlGroup)) > 0)):
            LEVENE_twoGroup_statistic, LEVENE_twoGroup_pvalue = stats.levene(list(controlGroup), list(caseGroup))
        else:
            LEVENE_twoGroup_statistic = np.nan
            LEVENE_twoGroup_pvalue = np.nan

        return LEVENE_twoGroup_statistic, LEVENE_twoGroup_pvalue

    def __LEVENE_allGroup(self, groupDict_filt):

        if (len(groupDict_filt) > 0):
            LEVENE_allGroup_statistic, LEVENE_allGroup_pvalue = stats.levene(*groupDict_filt.values())
        else:
            LEVENE_allGroup_statistic = np.nan
            LEVENE_allGroup_pvalue = np.nan

        df_levene_allGroup = pd.DataFrame({'LEVENE-allGroup_statistic': [LEVENE_allGroup_statistic], 'LEVENE-allGroup_pvalue': [LEVENE_allGroup_pvalue]})

        return df_levene_allGroup

    def __normality(self, pList):

        if (len(pList) >= 3):
            Shapiro_statistic, Shapiro_pvalue = stats.shapiro(pList)
        else:
            Shapiro_statistic = np.nan
            Shapiro_pvalue = np.nan

        df_normality = pd.DataFrame({'Shapiro_statistic': [Shapiro_statistic], 'Shapiro_pvalue': [Shapiro_pvalue]})

        return df_normality

    def __boot_pca(self, X, score, n):
        pca = PCA(n_components=2)
        pca.fit_transform(X)
        coeff = pca.components_.T

        rho = np.corrcoef(score[:, n - 1], coeff[:, n - 1], rowvar=False)[0][1]

        if np.sign(rho) == -1:
            C = np.multiply(coeff[:, n - 1], -1)
        else:
            C = np.multiply(coeff[:, n - 1], 1)

        return C