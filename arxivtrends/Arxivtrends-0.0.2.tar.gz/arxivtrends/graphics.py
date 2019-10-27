"""
the methods of graphics.py are to be used once the parsing loop triggered by the
parse() method is complete, as they concern the (now clean) data loading from
file and graphical visualization.
"""


import pandas as pd
pd.options.mode.chained_assignment = None

import numpy as np
import matplotlib.pyplot as plt
import collections
import re

from methods import *



# not necessary:
#df['years'] = df['years'].astype('int')
#df['pages'] = df['pages'].astype('int')


"""
the scrape method saves the lists of authors of the parsed preprints as strings
in the .csv file once the parsing loop is complete. When we load the data from
the file, we need to turn these strings back into lists of authors. The
string_to_list method splits these strings and removes the bracket characters.
A not None test is unnecessary: all the strings loaded from the file that
scrape() creates have the form '[...]'.
"""
def string_to_list(string):
    pattern = re.compile(r"'(.+?)'")
    matches = pattern.findall(string)
    return [match for match in matches]





"""
method to retrieve the research field from the name of the file .csv containing
the clean data relative to that field. The string representing the research field
is returned as a list of length 1 because we want to use it to give a name to the
index column of the DataFrame into which we load the data (see load_data()).
"""
def get_field_from_file(name_file):
    lst = []
    text = name_file.split('__')[1]
    lst.append(re.sub("_", " ", text))
    return lst





"""
method to load the clean data (created by the scrape() method) from a .csv file
into a DataFrame. We assign the name of the research field to the index column,
turn the type of the 'authors' column from string to list and return the final
DataFrame.
"""
def load_data(name_file):
    df = pd.read_csv(name_file, sep='\t', names=['years', 'authors', 'pages'])
    df.index.names = get_field_from_file(name_file)
    list_authors = [string_to_list(authors) for authors in df['authors'].to_numpy()]
    df = df.drop('authors', axis=1)
    df['authors'] = list_authors
    df['#authors'] = [len(list) for list in df['authors']]
    return df






"""
method to show the bar graph of submitted arXiv preprints in a chosen research
field with at least N authors on a yearly basis.
"""
def plot_N_authors_papers(df, N):
    df2 = df[df['#authors']>N]
    histogram = collections.Counter(df2['years'])

    plt.rcParams['figure.figsize'] = [20, 8]
    bucket_size = 0.8
    plt.bar(histogram.keys(), histogram.values(), bucket_size, align='center', edgecolor='black')
    plt.xlabel('years')
    plt.ylabel('preprints')
    plt.grid(True)
    list_indexes = np.arange(df2['years'].min(), df2['years'].max() + 1, 1)
    list_labels = [str(year) for year in list_indexes]
    plt.xticks(ticks=list_indexes, labels=list_labels, rotation=50)
    plt.title('Preprints in ' + df.index.names[0] + ' by ' + str(N) + ' or more authors')
    #plt.show()





"""
method to show the plot of the mean number of authors (graph above) and mean
number of pages of all submitted arXiv preprints in a chosen research field on a
yearly basis.
"""
def mean_authors_vs_pages(df):
    labels = np.arange(2002, df['years'].max() + 1, 2)
    df2 = df[df['years'] >= 2002]
    df3 = df2.groupby('years')['#authors', 'pages'].mean()

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(6, 7), sharex=True)
    ax1.plot(df3.index, df3['#authors'], marker='o', linewidth=1)
    ax2.plot(df3.index, df3['pages'], marker='o', linewidth=1)
    ax2.set_xlabel('years')
    ax1.set_ylabel('authors')
    ax2.set_ylabel('pages')
    ax2.set_xticks(labels)
    ax1.set_title('Average Number of Authors of ArXiv Preprints by Year')
    ax2.set_title('Average Number of Pages of ArXiv Preprints by Year')
    ax1.grid(True)
    ax2.grid(True)
    fig.tight_layout()
    #plt.show()





"""
method to retrieve the pool of authors from the dataframe containing the information
about the preprints in the research field we selected. The data structure set is
used to make sure that there are no duplicates of names.
"""
def find_pool_authors(df):
    authors_pool = set()
    for authors in df['authors']:
        authors_pool.update(authors)
    return authors_pool





"""
method to count how many arXiv preprints a given author has submitted in a given
year. We use the pandas buildt-in feature of comparing a series against a condition
and obtaining in return a series of True/False values - specifically, whether or
not a preprint was submitted by that auhor in that specific year. The number of
preprints is then just the sum of all the True values.
"""
def find_and_count(df, author, year):
    conditions = (df['years'] == year) & (df['authors'].str.contains(author, regex=False))
    return conditions.sum()





"""
method to build the dataframe containing the number of arXiv preprints submitted
each year by each author. We loop through the two latter parameters and apply the
find_pool_authors method to retrieve the former from the dataframe returned by the
scrape() method. Finally, for each author and year we remove the rows whose data
record show no research activity for that year (authors_df['#preprints'] == 0).
The execution of this method can take several minutes, therefore the dataframe
is also saved into a .csv file that can be loaded for later use (see load_authors_data())
"""
def get_productivity_database(df):
    authors_pool = find_pool_authors(df)
    preprints = 0
    authors_df = pd.DataFrame([], columns = ['author' , 'year', '#preprints'])
    for author in authors_pool:
        for year in range(df['years'].min(), df['years'].max() + 1):
            preprints = find_and_count(df, author, year)
            if preprints == 0:
                continue
            authors_df = authors_df.append({'author':author , 'year':year, '#preprints':preprints}, ignore_index=True)
            authors_df = authors_df.drop(authors_df[authors_df['#preprints'] == 0].index)

            authors_df.index.name = 'Authors - ' + df.index.names[0]
            df_details = get_details(df.index.names[0])
            name_file = 'Arxivtrends_authors__' + df_details + '.csv'
            authors_df.to_csv(name_file,  sep='\t', index = None, header=False)

    return authors_df




def load_authors_data(name_file):
    df = pd.read_csv(name_file, sep='\t', names=['author', 'year', '#preprints'])
    df.index.names = get_field_from_file(name_file)
    return df



'''
method to show the average research production from the authors whose first
arXiv submision dates back to the year that is passed in as the second parameter
- the forst one being the research production dataframe, from which we extract the
data we need. The data extaction consists of three steps:

1) through the pandas method filter() we winnow out the authors whose records
indicate that they started submitting preprints before or after the selected year;

2) through the pandas method groupby() we calculate the mean number of preprints
submitted by the remaining authors on a yearly basis;

3) finally we plot the values of this mean for any year.
'''
def show_average_productivity(authors_df, year, correction_coefficient = 2):
    filtered_df = authors_df.groupby('author').filter(lambda x:x['year'].min() == year)
    filtered_df['#preprints'] = filtered_df['#preprints'].astype(int)
    filtered_df = filtered_df.groupby('year')['#preprints'].mean()

    plt.rcParams['figure.figsize'] = [20, 8]
    plt.plot(filtered_df.index, correction_coefficient*filtered_df, color='green', marker='o', linewidth=1)
    plt.xlabel('years')
    plt.ylabel('preprints')
    plt.grid(True)
    list_indexes = np.arange(year, filtered_df.index.max() + 1, 1)
    list_labels = [str(year) for year in filtered_df.index]
    plt.xticks(ticks=list_indexes, labels=list_labels, rotation=50)
    plt.title('Average research production from authors whose first preprint was submitted in ' + str(year) + '.')
    #plt.show()
