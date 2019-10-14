import pandas as pd
import numpy as np


def extract_chromosome_counts(ssm_or_cnsm_df):
    """
    Returns a mutations per chromosome feature set from an SSM or CNSM DataFrame.
    :param ssm_or_cnsm_df: A pandas DataFrame of SSM or CNSM
    :return: The feature matrix containing mutations per chromosome counts of each donor
    """
    if "icgc_mutation_id" in ssm_or_cnsm_df.columns:
        ssm_or_cnsm_df = ssm_or_cnsm_df[["icgc_donor_id", "icgc_mutation_id", "chromosome"]]
        ssm_or_cnsm_df = ssm_or_cnsm_df.drop_duplicates()
    else:
        ssm_or_cnsm_df = ssm_or_cnsm_df[["icgc_donor_id", "chromosome"]].reset_index()
        ssm_or_cnsm_df = ssm_or_cnsm_df.drop_duplicates()
    ssm_or_cnsm_df = ssm_or_cnsm_df.groupby(["icgc_donor_id", "chromosome"]).count().reset_index()
    donors = ssm_or_cnsm_df["icgc_donor_id"].unique()
    chromosomes = ssm_or_cnsm_df["chromosome"].unique()
    if "icgc_mutation_id" in ssm_or_cnsm_df.columns:
        helper_list = [list(a) for a in zip(ssm_or_cnsm_df["icgc_donor_id"], ssm_or_cnsm_df["chromosome"],
                       ssm_or_cnsm_df["icgc_mutation_id"])]
    else:
        helper_list = [list(a) for a in zip(ssm_or_cnsm_df["icgc_donor_id"], ssm_or_cnsm_df["chromosome"],
                                            ssm_or_cnsm_df["index"])]
    feature_df = pd.DataFrame(0, index=donors, columns=chromosomes, dtype="int16")
    for cn in helper_list:
        feature_df.at[cn[0], cn[1]] = cn[2]

    return feature_df


def extract_gene_affected_counts(ssm_df):
    """
    Returns a gene affected feature set from an SSM DataFrame.
    :param ssm_df: A pandas DataFrame of SSM
    :return: The feature matrix containing gene affected counts of each donor
    """
    if "icgc_mutation_id" in ssm_df.columns:
        ssm_df = ssm_df[["icgc_donor_id", "icgc_mutation_id", "gene_affected"]]
        ssm_df = ssm_df.drop_duplicates()
    else:
        ssm_df = ssm_df[["icgc_donor_id", "chromosome"]].reset_index()
        ssm_df = ssm_df.drop_duplicates()
    ssm_df = ssm_df.groupby(["icgc_donor_id", "gene_affected"]).count().reset_index()
    print(ssm_df)
    donors = ssm_df["icgc_donor_id"].unique()
    genes = ssm_df["gene_affected"].unique()
    if "icgc_mutation_id" in ssm_df.columns:
        helper_list = [list(a) for a in zip(ssm_df["icgc_donor_id"], ssm_df["gene_affected"],
                       ssm_df["icgc_mutation_id"])]
    else:
        helper_list = [list(a) for a in zip(ssm_df["icgc_donor_id"], ssm_df["gene_affected"],
                                            ssm_df["index"])]
    feature_df = pd.DataFrame(0, index=donors, columns=genes, dtype="int16")
    for mut in helper_list:
        feature_df.at[mut[0], mut[1]] = mut[2]

    return feature_df


def extract_expression_features(expr_df, gene_model, type):
    """
    Returns a gene expression feature set from an EXP-A or EXP-S DataFrame.
    :param expr_df: A pandas DataFrame of EXP-A or EXP-S
    :param gene_model: The gene model. E.G. Ensembl.
    :param type: The type of expression values. Either "normalized_read_count" or "normalized_expression_value"
    :return: The feature matrix containing the gene expression of each donor
    """
    expr_df = expr_df[["icgc_donor_id", "gene_model", "gene_id", type]]
    expr_df = expr_df[expr_df["gene_model"] == gene_model]
    expr_df = expr_df.drop("gene_model", axis=1)
    expr_df[type] = expr_df[type].astype("float16")
    expr_df = expr_df.drop_duplicates()

    print(expr_df.shape)

    donors = expr_df["icgc_donor_id"].unique()
    genes = expr_df["gene_id"].unique()
    helper_list = [list(a) for a in
                   zip(expr_df["icgc_donor_id"], expr_df["gene_id"], expr_df[type])]
    feature_df = pd.DataFrame(0, index=donors, columns=genes, dtype="float16")
    for expr in helper_list:
        feature_df.at[expr[0], expr[1]] = expr[2]

    return feature_df


def drop_correlated_features(df, corr=0.95):
    """
    Drop features with a higher correlation than corr.
    :param df: The feature matrix as a pandas DataFrame
    :param corr: The correlation threshold
    :return: The new feature matrix as a pandas DataFrame.
    """
    # Create correlation matrix
    corr_matrix = df.corr().abs()
    # Select upper triangle of correlation matrix
    upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(np.bool))
    # Find index of feature columns with correlation greater than 0.95
    to_drop = [column for column in upper.columns if any(upper[column] > corr)]

    return df.drop(df[to_drop], axis=1)
