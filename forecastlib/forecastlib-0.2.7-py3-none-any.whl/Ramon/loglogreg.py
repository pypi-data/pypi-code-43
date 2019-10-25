from copy import deepcopy

import pandas as pd
import numpy as np
import scipy as sp
import statsmodels.api as sm
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.gridspec as gridspec
from mpl_toolkits.axes_grid1 import make_axes_locatable
import seaborn as sns

# Data preparation
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler, FunctionTransformer

# Linear Regression - Voting Regressors Learning
from sklearn import linear_model
from sklearn.ensemble import VotingRegressor


np.set_printoptions(suppress=True, precision=5)
sns.set(font_scale=1.5)
sns.set_style("whitegrid", {'axes.grid': False})
plt.rcParams['figure.figsize'] = (12, 8)
lw = 10
ms = 22
alpha_graph = 0.3
colors = sns.color_palette()


campaigns_to_train = ['C201501', 'C201502', 'C201503', 'C201504', 'C201505', 'C201506', 'C201507', 'C201508', 'C201509',
                      'C201510', 'C201511', 'C201512', 'C201513', 'C201514', 'C201515', 'C201516', 'C201517', 'C201601', 'C201602', 'C201603',
                   'C201604', 'C201605', 'C201606', 'C201607', 'C201608', 'C201609', 'C201610', 'C201611', 'C201612',
                   'C201613', 'C201614', 'C201615', 'C201616', 'C201617', 'C201701', 'C201702', 'C201703', 'C201704',
                   'C201705', 'C201706', 'C201707', 'C201708', 'C201709', 'C201710', 'C201711', 'C201712', 'C201713',
                   'C201714', 'C201715', 'C201716', 'C201717', 'C201801', 'C201802', 'C201803', 'C201804', 'C201805', 'C201806', 'C201807', 'C201808',
                     'C201809', 'C201810', 'C201811', 'C201812', 'C201813', 'C201814', 'C201815', 'C201816',
                     'C201817']

campaigns_to_test = ['C201901', 'C201902', 'C201903', 'C201904', 'C201905', 'C201906', 'C201907', 'C201908',
                     'C201909', 'C201910']

campaigns_total = campaigns_to_train + campaigns_to_test


def normalize_log_sigma(sigma):
    '''
    Creates an instance of log-normalizing function given a sigma.

    The two standard deviation division is for exploratory purposes. It comes from a recommendation of Andrew Gellman when
    comparing continous variables to variation of dummy variables. This normalization makes the size effects of the coefficients
    comparable.

    Args:
        sigma (float): the standard deviation for the features that are going to be normalized

    Returns:
        normalized_log (function): An instance of the normalization log function
    '''

    def normalize_log(x, sigma=1.0):
        return np.log(x + 1) / (2 * sigma)

    return normalize_log


def normalize(x):
    return x / (2 * np.std(x))


def load_data_base_predictions(data_frame, classifiers):
    '''
    Loads the data_frame with the Absolute Deviation, Relative Error and Accuracy from the classifiers.
    Note that for this to work the value "classifier.keys" should already be on the data frame. This is achieved
    in this notebook by training the model first. This function then enters into the pictures just to fill the rest
    of the data frame with convenient quantities that can be calculated manually otherwise.

    Args:
        data_frame: A pandas data frame. It contains the data with the features that we are training.
        classifiers (dic): A dictionary where key is the name of the classifier and the item can be whathever as it is not used
        in this particular function.
    '''
    for key in classifiers.keys():
        data_frame['Absolute Deviation ' + key] = np.abs(data_frame['Actual UPA'] - data_frame[key])
        data_frame['Relative Error ' + key] = data_frame['Absolute Deviation ' + key] / data_frame['Actual UPA']
        data_frame['Accuracy ' + key] = 1 - data_frame['Relative Error ' + key]
        # CLOVER
    key = 'Model UPA'
    data_frame['Absolute Deviation ' + key] = np.abs(data_frame['Actual UPA'] - data_frame[key])
    data_frame['Relative Error ' + key] = data_frame['Absolute Deviation ' + key] / data_frame['Actual UPA']
    data_frame['Accuracy ' + key] = 1 - data_frame['Relative Error ' + key]


def build_concept_and_brand_per_page(data_frame):
    '''
    Builds the features of Concepts per Page, Brands per Page and the categorical feature Brand Page
    for a given data frame.

    Args:
        data_frame: A pandas data frame. It contains the data with the features that we are training.
    '''
    x = data_frame.groupby(['Campaign', 'Page']).nunique()[['Concept', 'Brand']]
    y = x.reset_index()

    data_frame['Concepts per page'] = np.full(shape=data_frame.shape[0], fill_value=np.nan)
    data_frame['Brands per page'] = np.full(shape=data_frame.shape[0], fill_value=np.nan)
    data_frame['Brand page'] = np.full(shape=data_frame.shape[0], fill_value='No')

    for index, row in y.iterrows():
        index_campaign = data_frame['Campaign'].isin([row['Campaign']])
        index_page = data_frame['Page'].isin([row['Page']])
        index_to_change = index_campaign & index_page
        data_frame.loc[index_to_change, 'Concepts per page'] = row['Concept']
        data_frame.loc[index_to_change, 'Brands per page'] = row['Brand']
        if row['Brand'] == 1.0:
            data_frame.loc[index_to_change, 'Brand page'] = 'Yes'


def plot_groupby_variable(section, data_frame, classifiers, return_data_base=False):
    sns.set(font_scale=2.5)
    sns.set_style("whitegrid", {'axes.grid': False})
    plt.rcParams['figure.figsize'] = (18, 8)

    fig = plt.figure(figsize=(18, 8))
    ax = fig.add_subplot(111)

    dic_aux = {}

    variable_to_group = [section]

    for key in classifiers.keys():
        null_value = data_frame[key].isnull()
        x = 1 - data_frame.groupby(variable_to_group).sum()['Absolute Deviation ' + key] / \
            data_frame.groupby(variable_to_group).sum()['Actual UPA']
        dic_aux[key] = 100 * x

    df_combined = pd.DataFrame(data=dic_aux, index=x.index)
    df_combined.iloc[:, :].plot.bar(ax=ax)

    ax.set_ylim([0, 100.0])
    ax.set_ylabel('Accuracy (%)')

    ax.set_title('Accuracy')
    ax.axhline(50, ls='--', color='blue', label='Clover Average')
    ax.axhline(60, ls='--', color='green', label='Good Forecaster')
    ax.axhline(70, ls='--', color='red', label='Amazing Forecast')

    if return_data_base:
        return df_combined


def show_data_base_accuracy(data_frame, classifiers, just_accuracy=False):
    for key in classifiers.keys():
        not_null = ~data_frame[key].isnull()
        x = data_frame['Absolute Deviation ' + key].sum() / data_frame[not_null]['Actual UPA'].sum()
        accuracy = 1 - x
        print(key, accuracy)
        if not just_accuracy:
            x = data_frame['Absolute Deviation ' + key].sum() / data_frame['Actual UPA'].sum()
            print('including nulls', key, 1 - x)
            x = data_frame['Absolute Deviation ' + key].mean()
            print('Mean Absolute deviation', key, x)
            x = data_frame['Relative Error ' + key].mean()
            print('Mean relative error', key, x)
            print('UPA null', data_frame[~not_null]['Actual UPA'].sum())
            print('Total UPA and ratio', data_frame['Actual UPA'].sum(),
                  100 * data_frame[~not_null]['Actual UPA'].sum() / data_frame['Actual UPA'].sum())
            print('- - - - -')

    return accuracy


def data_frameact_data(data_frame, training_indexes, testing_indexes, continuous_features,
                       categorical_features, log_space_x=False, verbose=True):
    '''
    Extracts the data from a Pandas data frame

    Args:
        training_indexes (np.array): The indexes of the data frame that correspond to the examples in the
        training set.
        testing_indexes (np.array): The indexes of the data frame that correspond to the examples in the
        test set.
        continous_features (list): A list with the continuous features, they have to be columns of the data_frame
        categorical features (list): A list with the categorical features, they have to be columns of the data_frame
        log_space (bool): whether we want log space either the UPA space of the space of the continuous features.

    Returns:
        X_train (np.array): An array with the training features to be used with a Sklearn object with a fit method
        X_test (np.array): An array with the test features (to make predictions) to be used with a Sklearn object with predict method
        ct  (Sklearn object): An object that contains the transformation that was used for this particular segmentation
    '''
    # Get local data frames to extract the data from
    local_df_train = data_frame[training_indexes]
    local_df_test = data_frame[testing_indexes]

    # Which columns would be extracted
    columnns_to_extract = continuous_features + categorical_features
    n_continuous_features = len(continuous_features)
    n_categorical_features = len(categorical_features)

    # Chose in which space to have the input continous features
    if log_space_x:
        sigma = local_df_train[continuous_features].to_numpy().std(axis=0)
        continuous_transformer = FunctionTransformer(normalize_log_sigma(sigma), validate=True)
    else:
        continuous_transformer = StandardScaler(with_mean=False, with_std=False)

        # Extract all the possible values the categorical values can take
    categories = []
    for categorical_feature in categorical_features:
        union_set = set(local_df_train[categorical_feature]).union(set(local_df_test[categorical_feature]))
        feature_categories_set = list(union_set)
        categories.append(feature_categories_set)

    # Debugging purposes verbose
    if verbose:
        print('n_cont', n_continuous_features)
        print('n_categorical', n_categorical_features)
        print('continous', continuous_features)
        print('categories', categorical_features)

    # One-hot-encoder
    hot_enc = OneHotEncoder(categories=categories, drop=None, sparse=False, handle_unknown='error')

    # Column transformer
    columns_cont = [i for i in range(n_continuous_features)]
    columns_cat = [n_continuous_features + i for i in range(n_categorical_features)]

    transformers = [('log', continuous_transformer, columns_cont),
                    ("hot", hot_enc, columns_cat)]
    ct = ColumnTransformer(transformers=transformers)

    # Extract and transform training data
    df_X_train = local_df_train[columnns_to_extract]
    ct.fit(df_X_train)
    X_train = ct.transform(df_X_train)

    # Extract and transform test data
    df_X_test = local_df_test[columnns_to_extract]
    X_test = ct.transform(df_X_test)

    return X_train, X_test, ct


def train_network_segmentation(data_frame, segment_depth, offers, classifiers, continuous_features,
                               categorical_features, campaigns_to_train, campaigns_to_test,
                               verbose=True, log_space_y=True, log_space_x=True, restrictions=True):
    '''
    Trains a data set (that means it fits the model and creates a column in the data frame with the prediction)
    over a particular segment_depth (i.e. Category, Sector, Segment, Type, Concept)

    A very IMPORTANT part of this function is the datat that we exclude from training as it distorts the model.

    Args:
        segment_depth (string): Category, Sector, Segment, Type or Concept (this has to be a column of the data frame)
        offers (list): A list with a collection of strings of the offers that will be trained (e.g. ['SD', 'NO'] trains a model
        for the Straigth Discount and Sector)
        classifiers (dic): A dictionary whose items are Sklearn regressors.
        continous_features (list): A list with the continuous features, they have to be columns of the data_frame
        categorical features (list): A list with the categorical features, they have to be columns of the data_frame
        log_space (bool): whether we want log space either the UPA space of the space of the continuous features.
        restrictions (bool): Whether certain restrictions should be used in the training set. IMPORTANT TO HAVE THEM.

    Returns:
      classifiers_dictionary (dic): A dictionary with the classifiers used at each level
      transformations_dictionary (dic): A dicitionary that encapsulates the feature extraction method that is used at each level.
    '''

    index_test = data_frame['Campaign'].isin(campaigns_to_test)
    index_train = data_frame['Campaign'].isin(campaigns_to_train)

    # If using multiple classifiers the function will a pick a model that does best in the following campaigns.
    campaings_to_validate = ['C201813', 'C201814', 'C201815', 'C201816', 'C201817']
    index_validation = data_frame['Campaign'].isin(campaings_to_validate)

    # Remove data from training set that fuflills certain conditions
    if restrictions:
        no_zero_on_training = data_frame['Actual UPA'] != 0  # Remove 0s for training (not from test)
        only_defined_discount = ~data_frame['Discount'].isnull()  # Discount has to be defined
        exclude_negative_discount = data_frame['Discount'] >= 0.0  # Negative discount sounds weird, trash it!
        exclude_discounts_above_100 = (data_frame['Discount'] < 1.0)  # Too high discounts will make us broke
        no_offer_with_discounts = (data_frame['Offer'] == 'NO') & (
                    data_frame['Discount'] > 0)  # Things that should not go together
        # Actually remove the indexes
        index_train = index_train & no_zero_on_training & exclude_negative_discount \
                      & exclude_discounts_above_100 & exclude_negative_discount & ~no_offer_with_discounts

    # This is the level: Category, Sector, Segment, Type
    level_set = set(data_frame[segment_depth])
    # The offers
    offer_index = data_frame['Offer'].isin(offers)

    # Build transformer functions if the predictions happen in the log-space
    if log_space_y:
        f = np.log
        g = np.exp
    else:
        f = lambda x: x  # Identity
        g = lambda x: x

    # We store the dictionaries and transformers here
    classifiers_dictionary = {}
    transformations_dictionary = {}

    for level in level_set:
        if verbose:
            print('*****************************************')
            print(level)

        # Get the indexes of only this segment_depth level to restrict training and testing
        index_level = data_frame[segment_depth].isin([level])
        df_level = data_frame[index_level]
        training_indexes = index_train & index_level & offer_index
        testing_indexes = index_test & index_level & offer_index
        validation_indexes = index_validation & index_level & offer_index

        n_training = np.sum(training_indexes)
        n_test = np.sum(testing_indexes)
        # If there is training data then train
        local_df_train = data_frame[training_indexes]

        # Do not train segments that have less than 3 data points for training or no test data on them.
        n_min = 3
        if n_training > n_min and n_test > 0:
            # Extract the features from the data base
            aux = extract_data(data_frame, training_indexes, testing_indexes, continuous_features,
                               categorical_features, log_space_x=log_space_x, verbose=verbose)
            # This is the data that we will use to train
            X_train, X_test, ct = aux
            y_train = f(local_df_train['Actual UPA'].to_numpy())
            if verbose:
                print('Training size', X_train.shape)
                print('Test size', X_test.shape)

            # We store the column transfomer that we use at that particular level
            transformations_dictionary[level] = deepcopy(ct)

            # Now we create predictions for each of the predictions in the classifiers
            classifiers_per_level = {}
            classifiers_errors = []
            classifiers_y_pred = []
            classifiers_per_level_list = []

            for key_string, reg in classifiers.items():
                # Fit and predict
                reg.fit(X_train, y_train)
                # Store the classifier
                classifiers_per_level[key_string] = deepcopy(reg)

                # Predict for both training and test
                y_pred_train = g(reg.predict(X_train))
                y_pred = g(reg.predict(X_test))

                # Store the values
                data_frame.loc[training_indexes, key_string] = y_pred_train
                data_frame.loc[testing_indexes, key_string] = y_pred

                # Extract the validation data
                y_validation_prediction = data_frame.loc[validation_indexes, key_string]
                y_validation_value = data_frame.loc[validation_indexes, 'Actual UPA']

                # Calculate the accuracy for this classifier in the validation set
                error = np.abs(y_validation_prediction - y_validation_value).sum()

                # Store the predictions and classifiers
                classifiers_errors.append(np.copy(error))
                classifiers_y_pred.append(np.copy(y_pred))
                classifiers_per_level_list.append(deepcopy(reg))

            # Get the best classifier as the one that did best in the validation set (min error)
            arg = np.argmin(classifiers_errors)
            y_pred_best = classifiers_y_pred[arg]
            data_frame.loc[testing_indexes, 'best'] = y_pred_best
            classifiers_per_level['best'] = classifiers_per_level_list[arg]

            # Store the classifiers
            classifiers_dictionary[level] = deepcopy(classifiers_per_level)
        else:
            classifiers_dictionary[level] = None
            if verbose:
                print('Not enough data  n_min = ' + str(n_min))
                print('Training size', n_training)
                print('Test size', n_test)

    return classifiers_dictionary, transformations_dictionary


def train_everything(data_frame, classifiers, offer_group_parameters, training_window, log_space_y=True, log_space_x=True, verbose=False):
    '''
Trains the model for each of the offers from a given data_frame

Args:
    classifiers (dic): A dictionary whose items are Sklearn regressors.
    offer_group_parameteres (tuple):  A tuple with a collection of which offers are trained at what hierachical level, an example

    offer_group_parameters = [(['SD'], 'Sector', (continuous_features, categorical_features)),
                      (['NO'], 'Sector', (continuous_features[1:-1], categorical_features)),
                      (['COB', 'DSO', 'PWP', 'GWP', 'SET'], 'Category', (continuous_features, categorical_features))]

    Here this means that the 'SD' offer was trained at the sector level with continious and categorical features in the given tuple.

    Probably could be better encapsulated as an Object.

    training_window (tuple):  (campaigns_to_train, campaigns_to_test) a tuple with the campaigns that will be trained and the
    campaigns that will be tested


Returns:
  dictionary_of_training_data (dic): A dictionary containing the feature processing objects and classifiers for
  each of the levels and offers.
'''
    dictionary_of_training_data = {}

    for key in classifiers.keys():
        x = np.full(data_frame.shape[0], fill_value=np.nan)
        data_frame[key] = x

    # Where to train
    campaigns_to_train, campaigns_to_test = training_window

    # Segment
    for offer_group, segment_depth, features in offer_group_parameters:
        if verbose:
            print('ooooooooooooooo')
            print(offer_group)
            print('oooooooooooooooo')
        continuous_features, categorical_features = features
        aux = train_network_segmentation(data_frame, segment_depth, offer_group, classifiers, continuous_features,
                                         categorical_features, campaigns_to_train, campaigns_to_test,
                                         verbose=verbose, log_space_y=log_space_y, log_space_x=log_space_x)
        # Store the data
        dictionary_of_training_data[tuple(offer_group)] = aux

    classifiers['best'] = None
    load_data_base_predictions(data_frame, classifiers)

    df_test = data_frame[data_frame['Campaign'].isin(campaigns_to_test)]

    accuracy = show_data_base_accuracy(df_test, classifiers, just_accuracy=True)

    dictionary_of_training_data['Total accuracy'] = accuracy
    return dictionary_of_training_data

pd.options.mode.chained_assignment = None
categories = list({'Accessories', 'Colour Cosmetics', 'Fragrances', 'Hair Care', 'Other Category',
                   'Personal Care', 'Skin Care', 'Wellness'})
data_base_dictionary_features = {}
countries = {'uk', 'sweden', 'netherlands', 'uk', 'norway', 'finland'}
countries = {'uk'}

file_directory = r'.\data_bases_prediction\features_'
format_type = '.xlsx'

for country in countries:
    print(country)
    file_name = file_directory + country + format_type
    dfs = pd.read_excel(file_name, sheet_name=None)
    df = dfs['data']  # This is the name of the sheet
    n_before_cleaning = df.shape[0]

    df.loc[:, 'country'] = country

    values = {'Key Section': 'No section', 'Key Offer': 'No key offer', 'Offer': 'NO', 'Focus': 'No focus',
              'S&S': 'No S&S',
              'Featuring': 'No featuring', 'Price shelf': 'No price shelf'}

    df.fillna(value=values, inplace=True)

    df.loc[:, 'country'] = country

    # Make the campaign a string
    if country in ['sweden', 'finland', 'norway']:
        df['Campaign'] = ['C' + str(x) for x in df['Campaign']]
    else:
        df['Campaign'] = ['C' + str(x)[:-2] for x in df['Campaign']]

    # Correct the focus of things with no offer to F3
    if True:
        focus_index = (df['Focus'] == 'No') & (df['Offer'] == 'NO')
        df.loc[focus_index, ['Focus']] = 'F3'
        # The ones with high discount in the back cover and plataform are F1
        index_high_discount = (df['Focus'] == 'No') & (df['Discount'] >= 0.40) & \
                              (df['Key Section'].isin(['BC', 'PLT']))
        df.loc[index_high_discount, ['Focus']] = 'F1'

    only_catalogue = (df['Source of Sales'] == 'CTLG')
    index = only_catalogue

    removed = 100 * (1 - df[index].shape[0] / n_before_cleaning)
    df.loc[:, 'removed'] = removed
    print('removed', removed)

    # Mer price to float
    df = df[index]
    df['MER price'] = pd.to_numeric(df['MER price'])
    df['Page'] = pd.to_numeric(df['Page'])

    # Create a code variable
    df['Code variable'] = df['Code'].apply(str)
    data_base_dictionary_features[country] = df

file_directory = r'.\data_bases_prediction\upa_'
format_type = '.xlsx'

data_base_dictionary_upa = {}

layout_dictionary = {'1 product on layout': 1, '2 products on layout': 2, '3 products on layout': 3,
                     '4-6 products on layout': 4, '7+ products on layout': 5}

activity_dic = {'1-Top activity': 2, '2-Above average activity': 1, '3-Below average activity': 0}

for country in countries:
    print(country)
    file_name = file_directory + country + format_type
    dfs = pd.read_excel(file_name, sheet_name=None)
    df = dfs['data']  # This is the name of the sheet

    # Replace blanks with Python NA
    values = {'Novelty variable': 'No', 'Scratch&Sniff variable': 'No', 'Visual Focus Variable':
        'No', 'Dependency variable': 'No', 'Offer/Discount variable': 'No', 'Key Section Grouped variable': 'No',
              'Key Offer Grouped variable': 'No', 'Model Wearing variable': 'No'}
    df.fillna(value=values, inplace=True)

    # Change the name of columns
    columns_rename = {'Concept': 'Concept_upa', 'Category': 'category_upa', 'Sector': 'sector_upa',
                      'Focus': 'focus_upa',
                      'Description': 'description_upa', 'Brand': 'brand_upa', 'Set/Sample': 'set_sample_upa',
                      'Status': 'status_upa', 'Sub-brand': 'sub_brand_upa', 'Type': 'type_upa',
                      'Segment': 'segment_upa'}
    df.rename(columns=columns_rename, inplace=True)

    # Create temporal variables
    df['Layout Density variable numerical'] = df['Layout Density variable'].apply(lambda x: layout_dictionary[x])
    # df['Activity rank variable  numerical'] = df['Activity rank variable'].apply(lambda x:activity_dic[x])
    df['Numerical Campaign'] = df['Campaign'].apply(lambda x: int(x[-2:]))

    # Add Seasons
    season_dic = {1: 'first', 2: 'first', 3: 'first', 4: 'first', 5: 'second', 6: 'second', 7: 'second', 8: 'second',
                  9: 'second',
                  10: 'third', 11: 'third', 12: 'third', 13: 'third', 14: 'fourth', 15: 'fourth', 16: 'fourth',
                  17: 'fourth'}
    season_dic_num = {1: 1, 2: 1, 3: 1, 4: 1, 5: 2, 6: 2, 7: 2, 8: 2, 9: 2,
                      10: 3, 11: 3, 12: 3, 13: 3, 14: 4, 15: 4, 16: 4, 17: 4}
    df['Season'] = df['Numerical Campaign'].apply(lambda x: season_dic[x])
    df['Numerical Season'] = df['Numerical Campaign'].apply(lambda x: season_dic_num[x])

    df.fillna(value=values, inplace=True)
    data_base_dictionary_upa[country] = df

# country = 'uk_2019'

complete_data_bases_dic = {}
for country in countries:
    df_features = data_base_dictionary_features[country]
    df_upa = data_base_dictionary_upa[country]
    df_result = pd.merge(df_features, df_upa, how='inner', on=['Code', 'Campaign'])
    df_result['Product'] = df_result['Discount'] * df_result['MER price']
    build_concept_and_brand_per_page(df_result)
    complete_data_bases_dic[country] = df_result


import warnings
warnings.filterwarnings('ignore')

fit_intercept = True
log_space_x = True
log_space_y = True
verbose = False
continuous_features = ['Discount', 'MER price', 'Layout Density variable numerical', 'Concepts per page', 'Product']
categorical_features = ['Focus', 'Featuring', 'S&S', 'Key Section', 'Price shelf', 'Numerical Season', 'Code variable', 'Brand']
#categorical_features = []

ereg = VotingRegressor(estimators=[('Elastic Net', linear_model.ElasticNetCV(fit_intercept=fit_intercept)),
                                   ('Ridge', linear_model.RidgeCV(alphas=np.logspace(-3, 1.5, 10), fit_intercept=fit_intercept)),
                                   ('Laso', linear_model.LassoCV(fit_intercept=fit_intercept))])

classifiers = {'Elastic Net UPA': linear_model.ElasticNetCV(fit_intercept=fit_intercept),
               'Ridge UPA':linear_model.RidgeCV(alphas=np.logspace(-3, 1.5, 10), fit_intercept=fit_intercept),
               'Laso UPA': linear_model.LassoCV(fit_intercept=fit_intercept),
               'Voting': ereg}

offer_group_parameters = [(['SD'], 'Sector', (continuous_features, categorical_features)),
                          (['NO'], 'Sector', (continuous_features[1:-1], categorical_features)),
                          (['COB', 'DSO', 'PWP', 'GWP', 'SET'], 'Category', (continuous_features, categorical_features))]

country =  'uk'
data_frame = complete_data_bases_dic[country]

training_window  = (campaigns_to_train, campaigns_to_test)
data_dic = train_everything(data_frame, classifiers, offer_group_parameters, training_window,
                    log_space_y=log_space_y, log_space_x=log_space_x, verbose=verbose)


data_dic.save_csv("dump.csv")