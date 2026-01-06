import marc_pandas_functions as mpf
import pandas as pd

# Report all the MARC fields that repeat within records.

MARC_DATA = pd.read_pickle("data/dataframe.pkl")

# pd.set_option("display.max_rows", None)


x = mpf.get_repeated_fields(MARC_DATA)

print(x)
