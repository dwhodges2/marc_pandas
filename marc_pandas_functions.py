import os
from lxml import etree
import pandas as pd
import pandera.pandas as pa
# from tabulate import tabulate


from dotenv import load_dotenv

# Load config values into os.enivron
load_dotenv()

# default number of rows to print (None = no limit)
pd.set_option("display.max_rows", None)
# pd.set_option("display.max_rows", 20)


INPUT_FOLDER = os.environ["marc_folder1"]

DEFAULT_NS = None
# DEFAULT_NS = "http://www.loc.gov/MARC21/slim"
STORE = "data/dataframe.pkl"


def main():
    # marc_2_df_store(INPUT_FOLDER)

    MARC_DATA = pd.read_pickle(STORE)

    # x = index_table(MARC_DATA, "245__a")
    x = freq_table(MARC_DATA, "982__a")

    print(x)

    quit()


### Functions


def marc_2_df_store(input_folder, out_file=STORE):
    newtree = combine_xml_files(input_folder)
    root = newtree.getroot()
    cols = [("recid", "controlfield[@tag='001']")]
    cols += get_cols(root, record_name="record", default_ns=DEFAULT_NS)
    marcdf = make_df(
        root,
        cols,
    )
    marcdf.to_pickle(STORE)


def namespacer(xpath, nsprefix):
    """convert non-namespaced xpath to namespaced"""
    if nsprefix:
        return "/".join([f"{nsprefix}:{s}" for s in xpath.split("/")])
    return xpath


def datafield_to_xpath(tag_abbrev):
    """Expand a MARC tag abbreviation into a full XPath expression."""
    tag = tag_abbrev[0:3]
    ind1 = tag_abbrev[3].replace("_", "")
    ind2 = tag_abbrev[4].replace("_", "")
    code = tag_abbrev[5]
    xpath = f"datafield[@tag='{tag}'][@ind1='{ind1}'][@ind2='{ind2}']/subfield[@code='{code}']"
    return xpath


def tag_notation(attribs, subfield):
    """Convert datafield and subfield attributes into compact notation XXXiis (e.g., 035__a)"""

    ind1, ind2 = "_", "_"  # null notation default
    if attribs["ind1"]:
        ind1 = attribs["ind1"]
    if attribs["ind2"]:
        ind2 = attribs["ind2"]

    tag_abbrev = f"{attribs['tag']}{ind1}{ind2}{subfield['code']}"

    xpath = f"datafield[@tag='{attribs['tag']}'][@ind1='{attribs['ind1']}'][@ind2='{attribs['ind2']}']/subfield[@code='{subfield['code']}']"
    return (tag_abbrev, xpath)


def text_from_xpath(element, xpath_query, delim="|", default_ns=None):
    """Extract text from an XML element using an XPath query."""

    if default_ns:
        try:
            # print(f"***** XPATH = {namespacer(xpath_query, 'd')}/text()")
            return delim.join(
                element.xpath(
                    f"{namespacer(xpath_query, 'd')}/text()",
                    namespaces={"d": default_ns},
                )
            )
        except Exception as e:
            print(f"*** ERROR: {e}")
            return ""
    else:
        try:
            return delim.join(element.xpath(f"{xpath_query}/text()"))
        except Exception:
            return ""


def exists_xpath(element, xpath_query):
    """Check if an XML element exists using an XPath query."""
    try:
        result = element.xpath(xpath_query)
        return len(result) > 0
    except Exception:
        return False


def get_cols(xmltree, record_name="record", default_ns=None):
    ns_xpath = ""
    if default_ns:
        ns_xpath = "{" + default_ns + "}"
        record_name = ns_xpath + record_name
    cols = set()
    print(ns_xpath + "datafield")
    for child in xmltree:  # a record
        if child.tag == record_name:
            for field in child:
                if field.tag == ns_xpath + "datafield":
                    datafield_attribs = field.attrib

                    subfields = field.findall(ns_xpath + "subfield")
                    for s in subfields:
                        # print(s.tag, s.attrib)
                        cols.add(tag_notation(datafield_attribs, s.attrib))
                # elif field.name == "controlfield":
                # print(attribs)

    return sorted(list(cols))


def make_df(
    xmltree, cols, store="dataframe.pkl", record_name="record", default_ns=None
):
    if default_ns:
        record_name = "{" + default_ns + "}" + record_name

    col_heads = [c[0] for c in cols]
    print(f"Column heads: {col_heads}")
    data = []
    for child in xmltree:
        # print(child.tag)
        if child.tag == record_name:
            row = []
            for c in cols:
                # print(f"* Getting xpath from {c[1]} with ns={default_ns}")
                if text_from_xpath(child, c[1], default_ns=default_ns):
                    # print(text_from_xpath(child, c[1], default_ns=default_ns))
                    row.append(text_from_xpath(child, c[1], default_ns=default_ns))
                else:
                    row.append(None)
            data.append(row)

    df = pd.DataFrame(data, columns=col_heads)

    return df


def combine_xml_files(folder_path, root_tag="collection"):
    combined_root = etree.Element(root_tag)
    combined_tree = etree.ElementTree(combined_root)

    for filename in os.listdir(folder_path):
        if filename.endswith(".xml"):  # Or '.html' for HTML files
            file_path = os.path.join(folder_path, filename)
            try:
                tree = etree.parse(file_path)
                file_root = tree.getroot()
                for child in file_root:
                    combined_root.append(child)
            except etree.XMLSyntaxError as e:
                print(f"Error parsing {file_path}: {e}")
            except FileNotFoundError:
                print(f"File not found: {file_path}")
    return combined_tree


def freq_table(df, col):
    try:
        return df[col].value_counts()
    except KeyError:
        print(f"** Frequency table key error: There is no column {col}!")


def index_table(df, col, idcol=0, dropna=True):
    recid_col = df.columns[0]
    try:
        if dropna:
            return df[[recid_col, col]].dropna(subset=[col])
        return df[[recid_col, col]]
    except KeyError:
        print(f"** Index table key error: There is no column {col}!")


def field_report(df, col):
    print(f"Index for {col}:")
    print(index_table(df, col))
    print(f"Frequency table for {col}:")
    print(freq_table(df, col))
    # print("Dataframe info:")
    # print(df.info())


def get_df_failed_rows(dataframe, schema, verbose=False):
    """Validate a dataframe against a schema; returns a dataframe of failed rows with error context."""
    fails = validate_dataframe(dataframe, schema, verbose=verbose)
    if fails is not None:
        failed_rows = get_failed_rows(dataframe, fails)
        return failed_rows


def get_failed_rows(dataframe, failure_cases):
    """For a dataframe and a failure_cases Pandera object, return a dataframe of the rows with validation failures with error context."""

    failures_with_context = pd.merge(
        failure_cases, dataframe, left_on="index", right_index=True, how="left"
    ).drop_duplicates(
        subset=["index", "column", "check"]
    )  # Drop duplicates if needed for clarity

    # Add a column containing the value of the error context column
    failures_with_context["value"] = failures_with_context.apply(
        lambda row: row[row["column"]], axis=1
    )
    return failures_with_context[["recid", "column", "check", "value"]]


def validate_dataframe(dataframe, schema, verbose=False):
    """
    Validate dataframe against a data schema, returning failure cases table (pa.errors.SchemaErrors.failure_cases) if any.

    Args:
        dataframe: Pandas dataframe
        schema: Padera data schema
    """
    print("Validating DataFrame:")
    try:
        schema.validate(dataframe, lazy=True)
        return None
    except pa.errors.SchemaErrors as e:
        if verbose:
            print(f"Validation failed:\n{e}")
        return e.failure_cases
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def validation_report(dataframe, data_schema):
    # cols_to_validate = list(data_schema.columns.keys())
    fails = validate_dataframe(dataframe, data_schema)
    if fails is not None:
        # newcols = cols_to_validate
        # newcols.append("column")
        # return get_failed_rows(dataframe, fails)[newcols]
        return get_failed_rows(dataframe, fails)


def get_repeated_fields(dataframe, delim="\|"):
    # Pipe character indicates concatenation of repeated fields within a record
    counts = {}
    for col in dataframe.columns:
        counts[col] = dataframe[col].str.contains(delim, case=False, na=False).sum()
    dupe_series = pd.Series(counts, name="dupe_count")
    return dupe_series[dupe_series > 0]  # only include those non-zero


if __name__ == "__main__":
    main()
