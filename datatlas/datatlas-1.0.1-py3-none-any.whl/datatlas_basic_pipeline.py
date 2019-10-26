
"""
[TITLE]
Author: 
Updated Date: 

CRISP-DM stands for CRoss-Industry Process for Data Mining

1) Business understanding
    * What is the right question and hypothesis?
    * How will success and performance be measured?
2) Data understanding
3) Data preparation
4) Modeling
5) Evaluation
6) Deployment

"""


############################## THE QUESTION & OBJECTIVE ##############################
"""


"""


############################## IMPORT LIBRARIES ##############################
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import hello_atlas as atl


############################## LOAD DATA ##############################

### Via CSV ###
df = pd.read_csv(r"directory")

### Via API ###
# https://www.peterbe.com/plog/best-practice-with-retries-with-requests
# Troubleshooting: requests library, hotspot or WiFi NOT VPN, status code output by request

### Via other file ###
with open ('test.txt','r') as f:
    file_contents = f.read()


############################## EXPLORATORY DATA ANALYSIS ##############################

# Geopandas
atlas_gpd_code = atl.get_geopandas_code()

### Correlation Check ###
corr_matrix = df.corr()


############################## DATA PREPARATION ##############################

atlas_features = atl.get_feature_engineering_notes()

# https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.rename.html
# https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.replace.html


### Tidy Data ###

# Melt - when column headers are values, not variable names
# id_vars - columns you don't want to transform
# value_vars - columns you want to transform
# var_name - column name of the variable you're transforming
# value_name - columne name of the values that will go under the variable column you've just created
pd.melt(df, id_vars='passthru_columns', value_vars=None, var_name='variable_header', value_name='value_header')


# Splitting columns using string split when multiple variables are stored in one column
df[['new_column1','new_column2']] = (df['original_column']
                                     .str
                                     .split('_',expand=True))

# Pivot - when column values are variables and should be headers
# index - columns you don't want to transform
# columns - columns you want to transform
# values - column to populate using the pivot
df = df.pivot_table(index=['col1','col2','col3'],
                    columns='col_to_pivot',
                    values='col_to_populate'
                   )
df.reset_index() #  At this point, the data will look wonky so reset the index



### Feature selection ###

### Feature engineering ###

def comparison_result(row):
    if row['columnA'] < row['columnB']:
        return 'Increase'
    if row['columnA'] == row['columnB']:
        return 'Same'
    if row['columnA'] > row['columnB']:
        return 'Decrease'
    return 'Other'

df['columnC'] = df.apply(lambda row: comparison_result(row), axis=1)


### For categorical and ordinal features where some of the unique values are low frequency, group the lower frequency values into an 'Other' group/dummy feature
df['column_name'] = ['high_frequency_value' if x == 'high_frequency_value' else 'Other' for x in X['column_name']]



### Create lots of new features that represent the two-way interactions between all features
from itertools import combinations
from sklearn.preprocessing import PolynomialFeatures

def add_interactions(df):
        # Get feature names
        combos = list(combinations(list(df.columns),2))
        colnames = list(df.columns) + ['_'.join(x) for x in combos]
        
        # Find interactions
        poly = PolynomialFeatures(interaction_only=True, include_bias=False)
        df = poly.fit_transform(df)
        df = pd.DataFrame(df)
        df.columns = colnames
        
        # Remove interaction terms with all 0 values - because these represent the dummy features that were created from original categorical features
        noint_indicies = [i for i, x in enumerate(list((df == 0).all())) if x]
        df = df.drop(df.columns[noint_indicies], axis=1)
        
        return df
    
    
### Principal component analysis (PCA) - transforms all the features into 10 magical features
from sklearn.decomposition import PCA

pca = PCA(n_components=10)
X_pca = pd.DataFrame(pca.fit_transform(X))



### Feature selection using KBest function from scikit-learn
### Unit variant method - looks at outcome and relationship with each of the features

import sklearn.feature_selection

select = sklearn.feature_selection.SelectKBest(k=20)
selected_features = select.fit(X_train, y_train)
indices_selected = selected_features.get_support(indicies=True)
colnames_selected = [X.columns[i] for i in indicies_selected]

X_train_selected = X_train[colnames_selected]
X_test_selected = X_test[colnames_selected]
    
    



### Unbalanced classes ###


### Data cleansing ###

# Datetime
import datetime
ex_date_1 = "01-03-2019"
ex_date_2 = datetime.datetime.strptime(ex_date_1, "%d-%m-%Y")


# Duplicates
# https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.drop_duplicates.html
df.drop_duplicates

# Nulls
# https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.fillna.html
# https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.dropna.html

# Replace nulls with particular values using dictionary
value_map = {'ColumnA': 0, 'ColumnB': 0}
df.fillna(value = value_map)

# Convert string categories into numbers
data_map = {True:1, False:0}
df['column_name'] = df['column_name'].map(data_map)


# Imputing
# https://scikit-learn.org/stable/modules/generated/sklearn.impute.SimpleImputer.html

from sklearn.impute import SimpleImputer

### missing_values indicates which values to replace
### strategy indicates what to replace the missing values with
fill_0 = SimpleImputer(missing_values='NaN', strategy="mean")

### fit_transform is a function in the SimpleImputer module
df = fill_0.fit_transform(df)

### note that doing this imputation using the split data means that the mean for train and test are likely different
X_train = fill_0.fit_transform(X_train)
X_test = fill_0.fit_transform(X_test)





# One hot encoding categorical features
# https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.get_dummies.html
def one_hot_encode(df, categorical_cols_list):
    for column in categorical_cols_list:
        dummies = pd.get_dummies(df[column], prefix=column, dummy_na=False) # Make the dummy features
        df = df.drop(column,1) # Drop the original features
        df = pd.concat([df, dummies], axis=1) # Add the dummy features 
    return df

categorical_cols_list = []
df = one_hot_encode(df, categorical_cols_list)



# Outliers
# https://towardsdatascience.com/5-ways-to-detect-outliers-that-every-data-scientist-should-know-python-code-70a54335a623
# https://towardsdatascience.com/a-brief-overview-of-outlier-detection-techniques-1e0b2c19e561

outliers_method = 'iqr'
numerical_cols_list = []

# Outliers: Tukey inter quartile range
def iqr_outliers(df,numerical_cols_list):
    all_outliers = []    
    for column in numerical_cols_list:
        X = df[column]
        q1, q3 = np.percentile(X, [25,75])
        iqr = q3-q1
        floor = q1 - 1.5*iqr
        ceiling = q3 + 1.5*iqr
        
        all_outliers += list(X.index[(X < floor)|(X > ceiling)]) # List of outlier indices
           
    all_outliers = list(set(all_outliers)) # Remove duplicate indices
    removed_rows = df.loc[all_outliers,:] # Pop a df with the outlier rows
    df.drop(all_outliers, axis=0, inplace=True) # Remove the outlier rows from the original df
        
    return df, removed_rows
    

# Outliers: Kernel density estimation
def kde_outliers(df, numerical_cols_list):
    from sklearn.preprocessing import scale
    from statsmodels.nonparametric.kde import KDEUnivariate
    all_outliers = [] 
    for column in numerical_cols_list:
        X = df[column]
        x_scaled = scale(list(map(float,X)))
        kde = KDEUnivariate(x_scaled)
        kde.fit(bw="scott", fft=True)
        pred = kde.evaluate(x_scaled)
        
        n = sum(pred < 0.05)
        all_outliers += list(np.asarray(pred).argsort()[:n])
        
    all_outliers = list(set(all_outliers)) # Remove duplicate indices
    removed_rows = df.loc[all_outliers,:] # Pop a df with the outlier rows
    df.drop(all_outliers, axis=0, inplace=True) # Remove the outlier rows from the original df
    
    return df, removed_rows


if outliers_method == 'iqr':
    df, removed_outlier_rows = iqr_outliers(df,numerical_cols_list)
if outliers_method == 'kde':
    df, removed_outlier_rows = kde_outliers(df,numerical_cols_list)
    print(np.sort(kde_values))



# Scaling numerical features
# https://towardsdatascience.com/normalization-vs-standardization-quantitative-analysis-a91e8a79cebf
        
        
# Identify only numerical features & their column names
numeric_columns_df = df.select_dtypes(exclude='object')
numeric_column_names = list(numeric_columns_df.columns)

# Drop the original numerical features
df = df.drop(numeric_column_names, axis=1)

# Normalise the numerical features
from sklearn.preprocessing import MinMaxScaler
normaliser = MinMaxScaler()
numeric_columns_df = normaliser.fit_transform(numeric_columns_df)
numeric_columns_df = pd.DataFrame(numeric_columns_df)
numeric_columns_df.columns = numeric_column_names

# Join the normalised numerical features back onto the input df to replace the original features
df = pd.merge(df, numeric_columns_df, left_index=True, right_index=True, how='left')
            








############################## MODELLING ##############################

# Train/test split
# https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.train_test_split.html

from sklearn.model_selection import train_test_split

column_features = ['column1', 'column2', 'column3', 'etc',]
column_label = ['outcome']

X = df[column_features]
y = df[column_label]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.30, random_state=42, stratify=y)



### Function that trains the model and outputs performance measures and predictions
def train_model(name, model, X, y):
    '''
    Input:
        1) String to label the outputs
        2) Initialised model
        3) Features df
        4) Label df
    Output:
        1) The trained model
        2) List of model performance scores
        3) Confusion matrix
        4) Predictions in a df with original indices
    '''
    from sklearn.metrics import precision_score, recall_score, roc_auc_score, f1_score
    from sklearn.model_selection import cross_val_score, cross_val_predict
    from sklearn.metrics import confusion_matrix

    ### Note down the original indices
    y_indices = list(y.index)
    
    ### Convert dfs to arrays
    X = X.values
    y = y.values.ravel()
    
    ### Fit the model
    model.fit(X, y)
    
    ### Get predictions from the fitted model
    y_hat = cross_val_predict(model, X, y, cv=3)
    
    ### Convert the predictions to a df column with the original indices
    yhat_df = pd.DataFrame(y_hat, index=y_indices, columns=[name+'_prediction'])
    
    ### Get performance scores
    c_matrix = confusion_matrix(y, y_hat)
    accuracy = cross_val_score(model, X, y, cv=5, scoring='accuracy')
    accuracy = accuracy.mean()
    precision = precision_score(y, y_hat)
    recall = recall_score(y, y_hat)
    f1 = f1_score(y, y_hat)
    aucroc = roc_auc_score(y, y_hat)
    scores = [name, accuracy, precision, recall, f1, aucroc]
    
    return model, scores, c_matrix, yhat_df


### Call the function using logistic regression for example
from sklearn.linear_model import LogisticRegression
log_reg = LogisticRegression(class_weight='balanced', random_state=42)
model_log_reg, scores_log_reg, _, pred_log_reg = train_model('log_reg', log_reg, X_train, y_train)






############################## EVALUATION ##############################
atlas_model_eval = atl.get_model_eval_notes()


### Finding area under the ROC curve
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

def find_model_perf(X_train, y_train, X_test, y_test):
    model = LogisticRegression()
    model.fit(X_train, y_train)
    y_hat = [x[l]] for x in model.predict_proba(X_test)]
    auc = roc_auc_score(y_test, y_hat)
    
    return auc



### Plot a ROC curve
from sklearn.metrics import roc_curve

fpr, tpr, thresholds = roc_curve(y_train, y_train_pred)

def plot_roc_curve(fpr, tpr, label=None):
    plt.plot(fpr, tpr, linewidth=2, label=label)
    plt.plot([0,1],[0,1], 'k--')
    [...] # add axis labels & grid
    
plot_roc_curve(fpr, tpr)
plt.show()



### Cross validation (K-fold) accuracy score

from sklearn.model_selection import KFold
from sklearn.model_seletion import cross_val_score

k_fold = KFold(n_splits=10, shuffle=True, random_state=0)
scoring = 'accuracy'

classifier = RandomForestClassifier(n_estimators=13)
score = cross_val_score(classifier, train_data, target, cv=k_fold, n_jobs=1, scoring=scoring)
round(np.mean(score)*100, 2)





### Example syntax for tuning the regularization hyperparameter to fix overfitting

### Initially train a logistic regression model

from sklearn.linear_model import LogisticRegression
lr_model = LogisticRegression(C=0.7, random_state=42)   # Set regularization hyperparameter to 0.7 as a start
lr_model.fit(X_train, Y_train.ravel())

# Ignore future warnings
from warnings import simplefilter
simplefilter(action='ignore', category=FutureWarning)


# Create a loop that finds the regularization hyperparameter value that returns the best recall score

C_start = 0.1
C_end = 5
C_inc = 0.1

C_values, recall_scores = [], []

C_val = C_start
best_recall_score = 0
while(C_val < C_end):
    C_values.append(C_val)
    lr_model_loop = LogisticRegression (C=C_val, random_state=42)
    lr_model_loop.fit(X_train, Y_train.ravel())
    lr_predict_loop_test = lr_model_loop.predict(X_test)
    recall_score = metrics.recall_score(Y_test, lr_predict_loop_test)
    recall_scores.append(recall_score)
    if (recall_score > best_recall_score):
        best_recall_score = recall_score
        best_lr_predict_test = lr_predict_loop_test
        
    C_val = C_val + C_inc

best_score_C_val = C_values[recall_scores.index(best_recall_score)]
print("1st max value of {0:.3f} occured at C={1:.3f}".format(best_recall_score, best_score_C_val))

# Viewing the recall scores with different regularization hyperparameters in a nice line graph
import matplotlib.pyplot as plt
%matplotlib inline
plt.plot(C_values, recall_scores, "-")
plt.xlabel("C value")
plt.ylabel("Recall score")






############################## VISUALISATION ##############################

# Bokeh
atlas_bokeh_code = atl.get_bokeh_code()






################################################################################

def get_bokeh_code():
    
    bokeh_code = """
    
    ### Create basic line graph
    
    from bokeh.plotting import figure, output_file, show
    # figure - creates plots
    # output_file - specify html file name
    # show - generates the actual file
    
    x = [1,2,3,4,5]
    y = [4,6,2,4,3]
    
    ### Specify the file name
    output_file('basic_line_graph.html')
    
    ### Plot specs
    p = figure(
            title='Example Line Graph'
            ,x_axis_label = 'X Axis'
            ,y_axis_label = 'Y Axis'
            )
    
    ### Add glyphs
    p.line(x, y
           ,legend='Line'
           ,line_width=2
           )
    
    ### Generate
    show(p)
    
    
    
    ### Create basic bar chart
    
    import pandas as pd
    from bokeh.plotting import figure, output_file, show, ColumnDataSource, save
    from bokeh.models.tools import HoverTool
    from bokeh.transform import factor_cmap
    from bokeh.palettes import Blues8
    
    df = pd.read_csv('cars.csv')
    
    source = ColumnDataSource(df) # instead of assigning many variables
    
    car_list=source.data['Car'].tolist() # for the figure size specs
    
    output_file('basic_barchart_02.html')
    
    # Plot specs
    p = figure(
            y_range=car_list # change to list instead of df series variable
            ,plot_width=800
            ,plot_height=600
            ,title='Example Bar Chart 02'
            ,x_axis_label = 'Horsepower'
            ,tools="pan,box_select,zoom_in,zoom_out,save,reset"
            )
    
    # Horizontal bar glyphs
    p.hbar(
           y='Car' # change from variable to the label name instead
           ,right='Horsepower' #same as above
           ,left=0
           ,height=0.4
           ,color=factor_cmap(
                   'Car' #title
                   ,palette=Blues8
                   ,factors=car_list) # use the same car list variable as above
           ,fill_alpha=0.9
           ,source=source # defined earlier
           ,legend='Car'
           )
    
    
    # Legend
    p.legend.orientation='vertical'
    p.legend.location='top_right'
    p.legend.label_text_font_size='10px'
    
    
    # Hovertool
    hover = HoverTool()
    hover.tooltips = '''
    <div>
        <h3>@Car</h3>
        <div><strong>Price: </strong>@Price</div>
        <div><strong>HP: </strong>@Horsepower</div>
        <div><img src="@Image" alt="" width="200" /></div>
    </div>
    '''
    p.add_tools(hover)
    
    #show(p)
    save(p) # just save it and won't automatically show in web browser
    
    
    
    ### Bokeh interactive Google map
    ### https://www.youtube.com/watch?v=P60qokxPPZc
    
    ### Import libraries
    from bokeh.io import output_file, show
    from bokeh.models import GMapPlot, GMapOptions, ColumnDataSource, Circle, PanTool, WheelZoomTool, BoxSelectTool, Range1d, LinearColorMapper, ColorBar
    
    ### Pick out only the features we want to map
    map_df = df[['latitude','longitude','price']]
    
    ### Get the centre of London coordinates for the map option later
    #london_centre_lat = map_df['latitude'].mean() # 51.509676507471305
    #london_centre_lon = map_df['longitude'].mean() # -0.12652643050182724
    #map_options = GMapOptions(lat=london_centre_lat, lng=london_centre_lon,
    #                          map_type='roadmap', zoom=3)
    
    
    map_options = GMapOptions(lat=51.5074, lng=-0.1278,
                              map_type='roadmap', zoom=3)
    
    
    ### Google maps API key
    api_key = 'AIzaSyBfojwcUos6WzbkD32yDP0Tz3zIf2Rv2jU'
    
    ### Build the Google map
    plot = GMapPlot(x_range=Range1d(),
                    y_range=Range1d(),
                    map_options=map_options,
                    api_key=api_key)
    
    ### Add the interactive tools
    plot.add_tools(PanTool(), WheelZoomTool(), BoxSelectTool())
    
    ### Feed in the data including coordinates and radius
    baseline = map_df['price'].min()-1.0
    scale = 2.5
    source = ColumnDataSource(data=dict(lat = map_df['latitude'].tolist(),
                                        lon = map_df['longitude'].tolist(),
                                        rad = [(i-baseline) / scale for i in map_df['price'].tolist()]
                                        ))
    
    circle = Circle(x='lon',
                    y='lat',
                    size='rad',
                    fill_color='blue',
                    fill_alpha=0.3,
                    line_color=None
                    )
    
    
    ### Add the circles to the map
    plot.add_glyph(source, circle)
    
    
    #output_file('London_AirBnB.html')
    output_file(r"C:\Users\shaom\Desktop\Machine_Learning\AirBnB\London_AirBnB.html")
    show(plot)
    
    
    """
    return bokeh_code


def get_geopandas_code():

    geopandas_code = """
    
    ### Import libraries
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import seaborn as sns
    import geopandas as gpd
    import pysal as ps
    
    
    ### Natural earth data
    
    ### http://www.naturalearthdata.com/downloads/110m-cultural-vectors/110m-admin-0-countries/
    countries = gpd.read_file("zip://ne_110m_admin_0_countries.zip")
    ### http://www.naturalearthdata.com/downloads/110m-cultural-vectors/110m-populated-places/
    cities = gpd.read_file("zip://ne_110m_populated_places.zip")
    ### http://www.naturalearthdata.com/downloads/50m-physical-vectors/50m-rivers-lake-centerlines/
    rivers = gpd.read_file("zip://ne_50m_rivers_lake_centerlines.zip")
    
    
    ### Basic plot of geometric shapes - in this case, it's a map of Earth
    countries.plot()
    
    ### Geodataframes always have one column called geometry which can contain a point, linestring, or polygon
    ### Can combine multi-part geometries - https://shapely.readthedocs.io/en/stable/manual.html#geometric-objects
    countries.geometry # polygon
    cities.geometry # point
    rivers.geometry # linestring
    
    ### Syntax is similar to regular pandas
    africa = countries[countries['continent']=='Africa']
    africa.plot()
    
    
    ### Construct geometric shapes from scratch
    from shapely.geometry import Point, Polygon, LineString
    point = Point(1,1)
    line = LineString([ (1,1) , (3,4) ])
    polygon = Polygon([ (1,1) , (2,2) , (2,1) ])
    
    
    ### Get area attribute of polygons
    countries.geometry.area.sum() # 21496.990987992744
    africa.area.sum() # 2562.3020167468485
    polygon.area # 0.5
    
    
    '''
    Coordinate Reference Systems (CRS)
    https://docs.qgis.org/2.8/en/docs/gentle_gis_introduction/coordinate_reference_systems.html
    http://geopandas.org/projections.html
    * Determines how to map 2D (planar) coordinates of geometry objects to actual places on (non-planar) Eart
    * Note that geopandas uses pyproj/proj4 libraries to handle re-projections - http://geopandas.readthedocs.io/en/latest/projections.html
    '''
    
    ### Get CRS attribute of geometry data
    countries.crs # {'init': 'epsg:4326'}
    
    ### Convert to another reference system - Mercator for example
    countries_mercator = countries[(countries['name'] != 'Antarctica')] # Mercator doesn't like poles so remove Antarctica
    
    #countries_mercator.crs = {'init':'epsg:4326'}
    countries_mercator.to_crs({'init':'epsg:3395'}) # Set the new CRS
    
    countries_mercator.plot()
    
    
    """
    return geopandas_code
    

def get_feature_engineering_notes():
    
    feature_engineering_notes = """
        
    1) High % missing values
        * remove the feature
        * or encode the fact that values are missing as a feature (e.g. people who don't disclose their age are more likely to do xyz)
    
    2) Low variation
        * remove the feature
        * if values have different scales, use standard deviation to standardise
    
    3) Pairwise correlation
        * when 2 features are highly correlated
        * drop one of them, keep the one with higher correlation coefficient to with the target
    
    4) Correlation with the target
        * if low correlation, remove the feature
    
    5) Forward selection
        * Identify the best variable (e.g. based on model accuracy)
        * Add the next best variable to the model
        * And so on until some predefined criteria is satisfied
    
    6) Backward elimination
        * Start with all the variables included in the model
        * Drop the least useful variable (e.g. based on the smallest drop in model accuracy)
        * And so on until some predefined criteria is satisfied
    
    7) Stepwise selection
        * same as forward selection but variable can also be dropped if it's deemed as not useful anymore after a certain number of steps
    
    8) LASSO
        * Least Absolute Shrinkage and Selection Operator
        * An algorithm for creating a regularised linear model
    
    9) Tree-based
        * Use forests of trees to evaluate the importance of features
        * Fit a number of randomised decision trees on various sub-examples of the dataset and use averaging to rank order features
    
    
    Unbalanced Classes
    * Check number of labels in training set and make sure it matches reality
    * Stratify
    * Hyperparameter class_weight=balanced
    
    Principal component analysis (PCA)
    * Transforms datasets with high dimensionality into principal components that summarize the variance that underlies the data.
    * Each principal component is calculated by finding the linear combination of features that maximizes variance, while also ensuring zero correlation with the previously calculated principal components
    * Good for if the dataset has too many features or if features are highly correlated
    * Downside is that it makes models harder to interpret since it converts business data into a bunch of numbers and generically named 'PCA_1' features
    
    """
    return feature_engineering_notes


def get_model_eval_notes():
    
    model_eval_notes = """
    
    accuracy = TP + TN / everything
    
    recall = TP / TP + FN 
        *aka probability of a true result
        *aka true positive rate
        *aka sensitivity
        
    precision = TP / TP + FP
        *aka when the model said yes, how often was that right?
        
    auc-roc
        *true positive rate vs false positive rates
        *higher AUC better
        *0.5 means no class seperation
        *0 means wrong every time
        
    Overfitting
    * when accuracy on training data is >95% but test data is <75%
    * regularization hyperparameter
    * cross validation
    
    """
    return model_eval_notes


























