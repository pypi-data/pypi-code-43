import pandas as pd
import numpy as np
import re
import json

from IPython.display import display, Markdown, HTML

def attribute_construct(in_data, out_data):
    df = pd.DataFrame({
        'column': np.setdiff1d(out_data.columns.values, in_data.columns.values)
    })

    # split product_name and attribute
    re_product_name = [re.search('^([^\\.]*)\\.(.*)$', a) for a in df.column]
    df['product_name'] = [r.group(1) for r in re_product_name]
    df['attribute_name'] = [r.group(2) for r in re_product_name]

    # Find how nested the attribute is
    re_nested = [re.findall('\\[(\d*)\\]', a) for a in df.attribute_name]
    df['nested_level'] = [(np.array(r).astype(int)+1).prod() for r in re_nested]

    # Strip out the nesting from the attribute
    df['attribute_name'] = [re.sub('\\[\d*\\]', '[*]', a) for a in df.attribute_name]

    return df

def attribute_collapse(attributes):
    max_nested = (
        attributes.groupby(['product_name', 'attribute_name'])[['nested_level']].max().
        reset_index().rename(columns={'nested_level':'max_nested'})
    )
    level_1 = attributes.query('nested_level == 1').drop(columns='nested_level').rename(columns={'column': 'column_0'})
    df_collapsed = pd.merge(max_nested, level_1, how='left', on=['product_name', 'attribute_name'])
    return df_collapsed

def product_name_cost(attributes, analytics):
    c = attributes[['product_name']].drop_duplicates()
    c['cost'] = [analytics.C.provider_cost(c) if c!="inputs" else 0 for c in c.product_name]
    return pd.merge(attributes, c, how='left', on='product_name')

def product_name_matched(attributes, data):
    stacked = (
        data.notna()[attributes.column_0].stack().reset_index().
        rename(columns={'level_0': 'row', 'level_1': 'column_0', 0: 'not_na'})
    )
    stacked = pd.merge(stacked, attributes[['product_name', 'column_0']], how='left', on='column_0')

    stacked = stacked.groupby(['product_name', 'row'])['not_na'].any().reset_index()

    any_match = stacked.groupby('product_name')['not_na'].sum().astype(int).reset_index().rename(columns={'not_na': 'product_name_match'})
    return pd.merge(attributes, any_match, how='left', on='product_name')

def attribute_types(attributes, data):
    types = (
        data[attributes['column_0']].dtypes.reset_index().
        rename(columns={'index': 'column_0', 0:'attribute_type'})
    )
    return pd.merge(attributes, types, how='left', on='column_0')

def attribute_fill(attributes, data) :
    fill = (
        data[attributes['column_0']].replace(r'^\s*$', np.nan, regex=True).count().reset_index().
        rename(columns={'index': 'column_0', 0:'attribute_fill'})
    )
    return pd.merge(attributes, fill, how='left', on='column_0')

def unique_values(attributes, data) :
    unique = (
        data[attributes['column_0']].replace(r'^\s*$', np.nan, regex=True).nunique().reset_index().
        rename(columns={'index': 'column_0', 0:'unique_values'})
    )
    return pd.merge(attributes, unique, how='left', on='column_0')

def most_common_values(attributes, data) :
    def calc_mcv(row):
        return json.dumps(data[row["column_0"]].value_counts()[:5].to_dict())
    attributes["most_common_values"] = attributes.apply(calc_mcv, axis=1)
    return attributes

def cardinality(attributes, data) :
    def calc_card(row):
        cleaned_row = data[row["column_0"]].replace(r'^\s*$', np.nan, regex=True)
        card = cleaned_row.nunique() / cleaned_row.count() * 100.00
        return "{0:.2f}".format(card)
    attributes["cardinality"] = attributes.apply(calc_card, axis=1)
    return attributes

def standard_method(attributes, data, method_name, attr_name):
    values = (
        getattr(data[attributes['column_0']], method_name)(numeric_only=True).reset_index().
        rename(columns={'index': 'column_0', 0: attr_name})
    )
    return pd.merge(attributes, values, how='left', on='column_0')

def attribute_cleanup(attributes, data):
    def percent_format(num):
        return "{0:.2f}".format(num)
    clean = (
        attributes.assign(
            product_match_rate=(attributes.product_name_match.astype(float) / len(data) * 100.0).apply(percent_format),
            attribute_fill_rate=(attributes.attribute_fill.astype(float) / attributes.product_name_match * 100.0).apply(percent_format),
            nunique=attributes.unique_values
        )[['product_name', 'product_match_rate', 'attribute_name', 'attribute_fill_rate', 'attribute_type', 'unique_values', 'most_common_values', 'cardinality', 'std', 'median', 'mean', 'max_value', 'min_value', 'variance']]
    )
    # Assume objects are strings
    return clean

def report(inputs, enriched):
    attributes = attribute_construct(inputs, enriched)
    attributes = attribute_collapse(attributes)
    attributes = product_name_matched(attributes, enriched)
    attributes = attribute_types(attributes, enriched)
    attributes = attribute_fill(attributes, enriched)
    attributes = unique_values(attributes, enriched)
    attributes = most_common_values(attributes, enriched)
    attributes = cardinality(attributes, enriched)
    attributes = standard_method(attributes, enriched, "std", "std")
    attributes = standard_method(attributes, enriched, "median", "median")
    attributes = standard_method(attributes, enriched, "mean", "mean")
    attributes = standard_method(attributes, enriched, "max", "max_value")
    attributes = standard_method(attributes, enriched, "min", "min_value")
    attributes = standard_method(attributes, enriched, "var", "variance")
    attributes = attribute_cleanup(attributes, enriched)

    return attributes
