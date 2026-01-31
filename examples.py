import pandas as pd
import os
import marc_pandas_functions as mpf
from dotenv import load_dotenv

# Load config values into os.enivron
load_dotenv()

# default number of rows to print (None = no limit)
pd.set_option("display.max_rows", 20)

DEFAULT_NS = None
# DEFAULT_NS = "http://www.loc.gov/MARC21/slim"

INPUT_FOLDER = os.environ["marc_folder1"]

STORE = "data/dataframe1.pkl"

## Convert folder of MARCXML into a dataframe and store it as a pickle
# mpf.marc_2_df_store(INPUT_FOLDER, STORE)


## Read a pickled MARC dataframe
df = pd.read_pickle(STORE)


# All non-null values of column with recid
x = mpf.index_table(df, "245__a")
print(x)

# Save to CSV
# x.to_csv("index_table_245__a.csv")

# Table of select columns (includes nulls)
print(df[["recid", "269__a"]])

print(mpf.df_regex_filtered(df, "^65.*"))
