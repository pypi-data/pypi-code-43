

"""
[TITLE]
Author: 
Updated Date: 

Tokenisation
Splitting strings into individual words & symbols

Stemming
Normalising tokens into its base form or root form

Lemmatisation
Similar to stemming but outputs a proper word.

Parts of Speech (POS)
Used to tag the different types of words and the role they play in a sentence

Stopwords
Words that are not useful for NLP

Named Entity Recognition (NER)
Further tagging of nouns to determine what category they fall into - e.g. person, organisation, location, etc

Syntax Tree
Represents the syntactic structure of sentences or strings To render a syntax tree in a notebook, you'll need to download ghostscript

Chunking
Picking up individual pieces of information and grouping them into bigger pieces

"""

############################## THE QUESTION & OBJECTIVE ##############################
"""


"""


########## IMPORT LIBRARIES ##########
import pandas as pd
import numpy as np
import nltk
import spacy as spy


########## LOAD DATA ##########

### Via CSV ###
df = pd.read_csv(r"directory")

### Via API ###
# https://www.peterbe.com/plog/best-practice-with-retries-with-requests
# Troubleshooting: requests library, hotspot or WiFi NOT VPN, status code output by request

### Via other file ###
with open ('test.txt','r') as f:
    file_contents = f.read()


############################## EXPLORATORY DATA ANALYSIS ##############################



############################## DATA PREPARATION ##############################

### Feature selection ###



### Feature engineering ###



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



# MY::import should happen outside of the function loop maybe?
def text_cleanup(text, remove_stopwords=False, lemma=False, stem=False, twitter=False):
    
    # Lowercase, remove leading & lagging white space
    text = text.lower().strip()
    
    if remove_stopwords == True:
        
        # Tokenize the text - outputs list of words
        from nltk.tokenize import word_tokenize
        tokens = word_tokenize(text)
        
        # Remove stopwords and punctuation from the tokens list & rejoin into a string
        from nltk.corpus import stopwords
        import string
        stopwords = list(stopwords.words('english'))
        punctuations = string.punctuation
        tokens = [token for token in tokens if token not in stopwords and token not in punctuations]
        text = " ".join(tokens)
    
    if lemma == True:
        from nltk.stem import WordNetLemmatizer
        lemmatizer = WordNetLemmatizer()
        text = " ".join([lemmatizer.lemmatize(x) for x in text.split()])

    if stem == True:
        from nltk.stem import PorterStemmer
        stemmer = PorterStemmer()
        text = " ".join([stemmer.stem(x)for x in text.split()])

    if twitter == True:
        
        # Replace urls with 'URL'
        text = re.sub('((www\.[^\s]+)|(https?://[^\s]+))','URL', text)
        
        # Replace users with 'User'
        text = re.sub('@[^\s]+','USER', text)
        
        # Convert '#topic' to 'topic'
        text = re.sub(r'#([^\s]+)', r'\1', text)
        text = re.sub(' +',' ', text)
        
        #Replace &quot; parsing issue with appropriate " sign
        text = text.replace("&quot;", "'")
        
        #Replace &amp; parsing issue with appropriate & 
        text = text.replace("&amp;", "&")
        
        #Remove :: characters for label fields
        text = text.replace("::", "")

    return text


df['new_column'] = df['column'].astype(str).apply(lambda x: text_cleanup(x, remove_stopwords=True, lemma=True)



############################## MODELLING ##############################

# Train/test split
# https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.train_test_split.html

from sklearn.model_selection import train_test_split

column_features = ['column1', 'column2', 'column3', 'etc',]
column_label = ['outcome']

X = df[column_features]
y = df[column_label]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.30, random_state=42, stratify=y)



############################## EVALUATION ##############################



############################## VISUALISATION ##############################




