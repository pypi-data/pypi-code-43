import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import seaborn as sns

from scipy.stats import norm, skew, normaltest, ttest_ind, chi2_contingency

import statsmodels.api as sm
from statsmodels.formula.api import ols
    
# Refer https://stattrek.com/chi-square-test/independence.aspx

def binary_target_run_full_stat_test(df, target_feature_name, p_value_cutoff=0.05):
    
    df_categorical = df.select_dtypes(include=['object', 'category'])
    
    categorical_column_names = list(df_categorical.columns)
    categorical_column_names.remove(target_feature_name)
    numerical_column_names =  [i for i in df.columns if not i in df_categorical.columns]
    imp_feature_df = pd.DataFrame( columns = ['Feature', 'is_important', 'chi_or_T_val'])
    for col_name in categorical_column_names:
        is_feature_important, chi_or_T_val = binary_target_chi_test_for_categorical(df, col_name, target_feature_name, p_value_cutoff)
        imp_feature_df = imp_feature_df.append({'Feature': col_name, 'is_important':is_feature_important, 'chi_or_T_val':chi_or_T_val}, ignore_index=True)
            
    for col_name in numerical_column_names:
        is_feature_important, chi_or_T_val = binary_target_normal_stat_clt_test(df, col_name, target_feature_name, p_value_cutoff)
        imp_feature_df = imp_feature_df.append({'Feature': col_name, 'is_important':is_feature_important, 'chi_or_T_val':chi_or_T_val}, ignore_index=True)
    print('Stat summary info on prective power of each feature')
    print(imp_feature_df)

def binary_target_run_stat_test(df, feature_to_examine, target_feature_name, p_value_cutoff=0.05):
    
    if df[feature_to_examine].dtype.kind=='O':
        binary_target_chi_test_for_categorical(df, feature_to_examine, target_feature_name, p_value_cutoff)
    else: # Column is numeric
        binary_target_normal_stat_clt_test(df, feature_to_examine, target_feature_name, p_value_cutoff)    
        
def binary_target_chi_test_for_categorical(df, feature_to_examine, target_feature_name, p_value_cutoff=0.05):
    
    is_feature_important = False # Initial assumption
    cr_tab = pd.crosstab(df[feature_to_examine],df[target_feature_name])
    chi_stat = chi2_contingency(cr_tab)
    print('Running stats on ' + feature_to_examine)
    print('  Chi statistics is {0:.3f} and  p value is {1:.3f}'.format(chi_stat[0], chi_stat[1]))
    
    if chi_stat[1]<p_value_cutoff:
        print('\tRejecting null hypothesis that ' + feature_to_examine + ' is not significant.')
        print('\tSo Feature has significance and prdective power')
        is_feature_important = True
    else:
        print('\tCannot Reject null hypothesis that ' + feature_to_examine + ' is not significant.')
        print('\tSo may not be significant or has any predictive power')
    print('----------------------------------------------------------------------------------------------------------')
    return is_feature_important, chi_stat[0]
    
def binary_target_normal_stat_clt_test(df, feature_to_examine, target_feature_name, p_value_cutoff=0.05) :

    is_feature_important = False # Initial assumption
    
    mu, sigma = norm.fit(df[feature_to_examine])

    print('Running stats on {0} (mu = {1:.2f} and sigma = {2:.2f})'.format(feature_to_examine, mu, sigma))
    df[target_feature_name] = df[target_feature_name].astype('category')
    
    #cat_unique_list = list(df[target_feature_name].unique())
    
    cat_values_counts = df[target_feature_name].value_counts()
    
    cat_values_counts = cat_values_counts.sort_index()
    
    negative_class_label = cat_values_counts.index[0]
    positive_class_label = cat_values_counts.index[1]
        
    negative_df = df[df[target_feature_name]==negative_class_label][feature_to_examine]
    positive_df = df[df[target_feature_name]==positive_class_label][feature_to_examine]
        
    
    # feature_to_examine Mean and Median of full dataset
    fullset_mean=round(df[feature_to_examine].mean(),2)
    fullset_median=df[feature_to_examine].median()
    
    # feature_to_examine Mean and Median of negative dataset
    negative_median=negative_df.median()
    negative_mean=round(negative_df.mean(),2)
    
    # feature_to_examine Mean and Median of positive dataset
    positive_median=positive_df.median()
    positive_mean=round(positive_df.mean(),2)
    
    negative_means = []
    positive_means = []
    sample_means=[]
    
    negative_median=negative_df.median()
    negative_mean=round(negative_df.mean(),2)
    
    positive_median=positive_df.median()
    positive_mean=round(positive_df.mean(),2)
    
    # Test Central Limit Theorem (CLT)  by sampling
    for _ in range(1000):
        samples = df[feature_to_examine].sample(n=200)
        sampleMean = np.mean(samples)
        sample_means.append(sampleMean)
        
        samples = negative_df.sample(n=100)
        sampleMean = np.mean(samples)
        negative_means.append(sampleMean)
        
        samples = positive_df.sample(n=100)
        sampleMean = np.mean(samples)
        positive_means.append(sampleMean)
        
    fig, ax = plt.subplots(1,3,figsize=(16,6))   
    
    ax[0].axvline(fullset_median, color='blue', linestyle='-')
    ax[0].axvline(fullset_mean, color='blue', linestyle='--')    
    ax[0]=sns.distplot(df[feature_to_examine],bins=15,ax=ax[0])
    xlabel_touse = '{0} [Full dataset Mean:{1:.3f} ,Median:{2:.3f}]'.format(feature_to_examine, fullset_mean, fullset_median)
    ax[0].set_xlabel(xlabel_touse)
    
    ax[1].axvline(positive_median, color='green', linestyle='-')
    ax[1].axvline(positive_mean, color='green', linestyle='--')
    ax[1].axvline(negative_median, color='red', linestyle='-')
    ax[1].axvline(negative_mean, color='red', linestyle='--')
    ax[1]=sns.kdeplot(positive_df, label='Positive',shade=True, ax=ax[1], color="green")
    ax[1]=sns.kdeplot(negative_df, label='Negative', shade=True, ax=ax[1], color="red")
    xlabel_touse = '{0} \n [-ve class Mean:{1:.3f} ,-ve class Median:{2:.3f}]\n[+ve class Mean:{3:.3f} ,+ve class Median:{4:.3f}]'.format(feature_to_examine, negative_mean, negative_median, positive_mean, positive_median)
    ax[1].set_xlabel(xlabel_touse)
    
    ax[2].axvline(positive_median, color='green', linestyle='-')
    ax[2].axvline(positive_mean, color='green', linestyle='--')
    ax[2].axvline(negative_median, color='red', linestyle='-')
    ax[2].axvline(negative_mean, color='red', linestyle='--')        
    ax[2] =sns.kdeplot(positive_means, label='+ve Class',shade=True,ax=ax[2], color="green")
    ax[2] =sns.kdeplot(negative_means, label='-ve Class', shade=True,ax=ax[2], color="red")
    
    ax[2].set_xlabel(feature_to_examine)
    ax[2].set_xlabel(feature_to_examine)
    ax[2].set_ylabel('Kernel Density Estimate')    
    ax[2].set_title('Appled Central Limit Theorem')    
    
    plt.show()
    
    chi_stat, p_value = normaltest(df[feature_to_examine], axis=0)
    
    print("Normal Test for the feature {0} distribution chi_stat={1:.3f} p-value={2:.3f}".format(feature_to_examine, chi_stat, p_value)) 
    if p_value<p_value_cutoff:
        print(f'\tLow p-value(<{p_value_cutoff}) indicates it is unlikely that data came from a normal distribution.(NOT Normal)')
    else:
        print(f'\t**p-value>{p_value_cutoff} indicates it is most likely data came from a normal distribution.')
        
    #Null hypothesis : data came from a normal distribution.    
    # If the p-val is very small, it means it is unlikely that the data came from a normal distribution
    
    print('Note: Skewness Interpretation:- Fairly symmetrical if the skewness is between -0.5 and 0.5')
    fullset_skew = pd.DataFrame.skew(df[feature_to_examine], axis=0)    
    print_skewness_report(fullset_skew, 'Full dataset')
    
    negative_df_skew = pd.DataFrame.skew(negative_df, axis=0)
    print_skewness_report(negative_df_skew, 'Negative dataset')
    
    positive_df_skew = pd.DataFrame.skew(positive_df, axis=0)
    print_skewness_report(positive_df_skew, 'Positive dataset')
    
    #t-test on independent samples
    t2, p2 = ttest_ind(positive_df,negative_df)
    print("Ttest_ind: t={0:.3f} p={1:.3f}".format(t2, p2))
    if p2<p_value_cutoff:
        print('Rejecting null hypothesis that there is no difference in Mean of +ve and -ve Class.(Go for alternative hypothesis)')
        print('\tThe feature ' + feature_to_examine + ' would be a predictive feature. Count it as important feature')
        is_feature_important = True
    else:
        print('Cannot Reject null hypothesis that there is no difference in Mean of +ve and -ve Class')
        print('\tThe feature ' + feature_to_examine + ' may NOT be important or has any predictive power')
    
    print('----------------------------------------------------------------------------------------------------------')
    return is_feature_important, t2
    
def print_skewness_report(df_skew, df_title):
    print("\tSkewness for the {0} {1:.3f}.".format(df_title, df_skew)) 
    if df_skew<0: # Nagative
        print('\t  Left skewed')
        if df_skew<-0.5:
            print('\t    data NOT symmetrical')
        else:
            print('\t    Data seems to be fairly symmetrical')
    elif df_skew>0: # Positive
        print('\t  Right skewed')
        if df_skew>0.5:
            print('\t    data NOT symmetrical')
        else:
            print('\t    Data seems to be fairly symmetrical')
    else:
        print('\t  Highly symmetrical')

def analyse_skew(df): 
    df_categorical = df.select_dtypes(include=['object', 'category'])
    numerical_column_names =  [i for i in df.columns if not i in df_categorical.columns]
    
    skewed_features = df[numerical_column_names].apply(lambda x: skew(x.dropna())).sort_values(ascending=False)
    print("\nSkew in numerical features: \n")
    skewness = pd.DataFrame({'Skew' :skewed_features})
    print(skewness.head(100))
    return skewness
   
def anova_one_way_test(df, target_continuous_column, columns_to_analyse, prob_cut_off = 0.05):
    
    if df[target_continuous_column].dtype.kind=='O':
        raise Exception('Target_column varibale should be numeric. Convert it and try again')
       
    param_for_ols = ''
    for col_name in columns_to_analyse:
        if len(param_for_ols)!=0:
            param_for_ols = param_for_ols + ' + '
        param_for_ols = param_for_ols + col_name
    
    # Add target column at the begining
    param_for_ols = target_continuous_column + ' ~ ' + param_for_ols
    anova_df = sm.stats.anova_lm(ols(param_for_ols, data=df).fit(), typ=2)
    print('------- Anova Summary -------')
    print(anova_df)
    print('-----------------------------')
    for col_name in columns_to_analyse:  
        anova_row = anova_df.loc[col_name]
        f_stat_prob = anova_row['PR(>F)']
        if f_stat_prob < prob_cut_off :
            print('Yes, ' + anova_row.name + ' has predictive power for ' + target_continuous_column + ' since  PR(>F) < ' + str(prob_cut_off))
        else:
            print('No, ' + anova_row.name + ' has NO predictive power for ' + target_continuous_column + ' since  PR(>F) > ' + str(prob_cut_off))
    return anova_df


#https://devdocs.io/statsmodels/examples/notebooks/generated/interactions_anova        
def anova_two_way_test(df, 
                       target_continuous_column, 
                       first_column_to_analyse, 
                       second_column_to_analyse, 
                       prob_cut_off = 0.05):
    jointlm_str = target_continuous_column + ' ~ C(' + first_column_to_analyse + ') * C(' + second_column_to_analyse + ')'
    joint_lm = ols(jointlm_str, data=df).fit()
    
    first_lm_str = target_continuous_column + ' ~ C(' + first_column_to_analyse + ') + C(' + second_column_to_analyse + ')'  
    print('------- Anova Summary of -------\n' + first_lm_str + ' against\n' + jointlm_str)
    print(sm.stats.anova_lm(ols(first_lm_str, data=df).fit(), joint_lm))
    print('-----------------------------------')
    
    primary_str = target_continuous_column + ' ~ C('+first_column_to_analyse+')'
    secondary_str = target_continuous_column + ' ~ C('+first_column_to_analyse+') + C('+second_column_to_analyse+', Sum)'
    print('------- Anova Summary of -------\n' + primary_str + ' against\n' + secondary_str)
    print('-----------------------------------')
    print(sm.stats.anova_lm(ols(primary_str, data=df).fit(),
               ols(secondary_str,data=df).fit()))
    
    primary_str = target_continuous_column + ' ~ C('+second_column_to_analyse+')'
    secondary_str = target_continuous_column + ' ~ C(' + first_column_to_analyse + ') + C('+second_column_to_analyse+', Sum)'
    print('------- Anova Summary of -------\n' + primary_str + ' against\n' + secondary_str)
    print(sm.stats.anova_lm(ols(primary_str, data=df).fit(), ols(secondary_str, data=df).fit()))
    print('-----------------------------------')

# # ks_2samp is a two-sided test for the null hypothesis that 2 independent samples are drawn from the same continuous distribution.  
# https://www.kaggle.com/c/elo-merchant-category-recommendation/discussion/77537    
def ks_2samp(train_df, test_df, p_cutoff=0.05):
    from scipy.stats import ks_2samp
    from tqdm import tqdm

    list_p_value =[]
    return_dict = {}

    train_df_columns = list(train_df.columns)
    
    for i in tqdm(train_df_columns):
        print(i)
        ks_resid = ks_2samp(test_df[i] , train_df[i])[1]
        list_p_value.append(ks_resid)
        return_dict[i] = ks_resid 

    Se = pd.Series(list_p_value, index = train_df_columns).sort_values() 
    list_discarded = list(Se[Se < p_cutoff].index)
    print(list_discarded)
    return list_discarded, return_dict