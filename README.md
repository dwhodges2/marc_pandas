# MARCXML dataframe tools

Simple tools for analysis and querying of MARCXML using Pandas dataframes and Pandera for data validation. Main functions are contained in `marc_pandas_functions.py`. (Work in progress.) 

## Parse MARCXML into dataframe

 - `marc_2_df_store`: Parse MARCXML files from a specified folder into a dataframe, and persist in a Pickle file.
   - Define namespace in `DEFAULT_NS` as needed.  
   - Creates a column for each unique datafield/subfield combination.
   - Uses abbreviated notation MARC field, ind1, ind2, subfield code (e.g., `035__a`)
   - When more then one text node for a given column, concatenate with pipe delimiters.
 - Read a saved pickle into a dataframe using `df = pd.read_pickle(<file>)` and do data things.
 - Examples:
   - `freq_table(df, col)`: Get a list of unique values for a column with the number of records for each.
   - `index_table(df, col)`: Get every given column value with recids for each.
   - `df[['recid', col1, col2 ... ]]`: Filtered dataframe with arbitrary set of columns. 
   - `df[df['336__a'].str.contains('computer dataset', na=False)]`: Filtered by content of a field.
   - Filter columns with regex: `df_regex_filtered(df, r"^7.*")` for all 7XX fields.
- Output any filtered dataframe to CSV: `.to_csv("output_file_path.csv")`
- Output tab-delimited to clipboard: `.to_clipboard()` 
 
##  Dataframe validation

Validate MARCXML dataframe against rules defined in a Pandera data schema.

 - The file `marc_validate_dataframe.py` provides sample of defining a schema and validating a saved dataframe against it.
 - `validation_report(df, schema)`: function to validate and get a table of exceptions with context.
 - See [Pandera documentation](https://pandera.readthedocs.io/en/stable/dataframe_schemas.html) for more info.

Note: For data validation to work properly, set the validation depth environment variable to `DATA_ONLY`:
```
export PANDERA_VALIDATION_DEPTH=DATA_ONLY
```
See https://pandera.readthedocs.io/en/stable/error_report.html
