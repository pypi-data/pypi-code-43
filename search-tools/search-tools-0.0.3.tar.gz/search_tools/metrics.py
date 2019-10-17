import numpy as np
import pandas as pd

import pyspark.sql.functions as F
import pyspark.sql.types as T

def search(indexed, search_for):
    """
    Given a 1-d array (indexed) and a search 1-d array (search_for),
      returns a 1-d array shaped like search_for where the values in search_for
      appear in indexed; non-matching elements are assigned to -1.
    """
    cross = np.equal(indexed, search_for[:,np.newaxis])
    results = np.argwhere(cross)
    indices = results[:, 0]
    values = results[:, 1]
    output = np.ones_like(search_for) * -1
    output[indices] = values
    return output

def dcg(best, output):
    """Computes discounted cumulative gain
    given ground-truth "best" ranking and output, 
    the re-ranked output of the model.
    """
    positions = np.arange(output.shape[0])
    rels = (positions.max() - positions) + 1
    rels = np.concatenate((rels, np.array([0])))
    
    idx = search(best, output)
    relevances = rels[idx]
    
    i = np.arange(1, len(best)+1)
    
    brp = (2.0 ** relevances)
    
    score = ((brp - 1)/np.log2(i + 1)).sum()
    
    return score

def ndcg(best, output):
    """Computes normalized discounted cumulative gain
    given ground-truth "best" ranking and output, 
    the re-ranked output of the model.
    """
    best, output = np.array(best), np.array(output)
    top_score = dcg(best, best)
    dcg_ = dcg(best, output)
    
    return float(dcg_/top_score)

def ranking_ndcg_at_k(best, other, k=None):
    """
    Computes ndcg at k using raw position
    as relevance score.
    """
    if k is None:
        k = len(other)
    other = other[:k]
    diff = len(other) - len(best)
    if diff == 0:
        pass
    elif diff < 0:
        other += ['_ ' for x in range(np.abs(diff))]
    elif diff > 0:
        best += [' _' for x in range(diff)]
    other = [hash(x) for x in other]
    best = [hash(x) for x in best]
    return ndcg(best, other)
        
    

def get_rankings(df, gt_col, est_col, query_col='query', id_col='pid'):
    """
    Does grouping, aggregation, and sorting of df to get rankings.
    df - a pyspark dataframe
    gt_col - string, the name of the column containing the ground truth relevance for query-pid pair
    est_col - string, the name of the column containing the estimated relevance for query-pid pair
    query_col - string (default 'query'), the name of the column containting the query or search terms or whatever
    id_col - string (default 'pid'), the name of the column containing item id

    returns:
    a pyspark dataframe with a single row per unique query, with columns:
      "query" (string) the query,
      "best_order" (array), list of pids ordered by gt relevance,
      "estimated_order" (array), list of pids ordered by estimated relevance
    """

    sorted_sdf = ( df.groupBy(query_col)
                    .agg(
                    F.sort_array( F.collect_list( F.struct( F.col(gt_col), F.col(id_col)) ), asc = False).alias('best'),
                    F.sort_array( F.collect_list( F.struct( F.col(est_col), F.col(id_col)) ), asc = False).alias('estimated') )  
               )

    return sorted_sdf.select(query_col, 'best.{}'.format(id_col), 'estimated').withColumnRenamed(id_col, 'best_order').select(query_col, 'best_order', 'estimated.{}'.format(id_col)).withColumnRenamed(id_col, 'estimated_order')

ndcg_udf = F.udf(ndcg, T.FloatType())


def dcg_with_rel(relevances, k=None):
    """
    Computes discounted cumulative gain
    given ground-truth relevance values.
    if k is None, computes for all relevances.
    """
    relevances = np.array(relevances)
    if k is None:
        k = len(relevances)
    
    relevances = relevances[:k]
    
    i = np.arange(1, len(relevances)+1)
    
    brp = (2.0 ** relevances)
    
    terms = (brp - 1)/np.log2(i + 1)
    score = terms.sum()
    
    return score

def ndcg_at_k(relevances, k=None):
    """
    Pass in an ordered list of relevances
    and k; returns normalized ndcg score.
    """
    relevances = np.array(relevances)
    best = relevances.copy()
    best[::-1].sort()
    best_dcg = dcg_with_rel(best, k=k)
    if best_dcg == 0.0:
        return 0.0
    dcg = dcg_with_rel(relevances, k=k)
    ndcg = dcg/best_dcg
    return float(ndcg)

def ndcg_at_k_constructor(k):
    """
    Creates and returns a pyspark udf
    that computes ndcg@k for the k passed as argument.
    """

    ndcg_udf = F.udf(lambda x: ndcg_at_k(x, k=k), T.FloatType())
    return ndcg_udf

def ranking_ndcg_at_k_constructor(k):
    """
    Creates and returns a pyspark udf
    that computes ranking ndcg@k for the k passed as argument.
    """

    ndcg_udf = F.udf(lambda x, y: ranking_ndcg_at_k(x, y, k=k), T.FloatType())
    return ndcg_udf
