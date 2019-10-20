import pandas as pd
from pandas_log import enable


df = pd.read_csv("../examples/pokemon.csv")

with enable(True):
    df.query("type_1=='Fire' or type_2=='Fire'").drop(
        "type_1", axis=1
    ).nlargest(1, "total")
#     # Wont fix df2 = df.copy()
#
#
# wont write to stdout df.head()
df.query("legendary==0")
# FIX 1: df.copy().query("legendary==0")
# Probably all objects that are df need to be updated
