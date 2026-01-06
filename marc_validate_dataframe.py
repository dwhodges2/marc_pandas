import marc_pandas_functions as mpf
import pandas as pd
import pandera.pandas as pa
from pandera.engines.pandas_engine import DateTime


MARC_DATA = pd.read_pickle("data/dataframe.pkl")

pd.set_option(
    "display.max_rows", None
)  # Or set to int for max number of rows to display

# To do only data validation, set environment variable:
# export PANDERA_VALIDATION_DEPTH=DATA_ONLY
# See https://pandera.readthedocs.io/en/stable/error_report.html


## Define specs used for column validation

# General date format used to validate date-only columns
datetime_spec = pa.Column(
    DateTime(to_datetime_kwargs={"format": "%Y-%m-%d"}),
    coerce=True,
    nullable=True,
)
geolocate_spec = pa.Column(
    str,
    pa.Check.str_matches(
        r"^\-?[\d\.]+$",
    ),
    coerce=True,
    nullable=True,
)

## Create schema to validate dataframe against

data_schema = pa.DataFrameSchema(
    {
        "recid": pa.Column(int),
        "269__a": datetime_spec,
        "269__b": datetime_spec,
        "342_0c": geolocate_spec,
        "342_0d": geolocate_spec,
    }
)


## Validate against schema and get report of records with errors

x = mpf.validation_report(MARC_DATA, data_schema)
print(x)
