import marimo

__generated_with = "0.14.6"
app = marimo.App(width="medium")


@app.cell
def _():
    import sys, os
    try:
        if "pyodide" in sys.modules:
            from pyodide.http import pyfetch
            response = await pyfetch("https://mark-climateview.github.io/data-playbook-marimo-poc1/cbs.zip")
            await response.unpack_archive()
    except:
        pass

    import marimo as mo
    return mo, sys


@app.cell
def _():
    import requests
    import json
    import pandas as pd
    import pyarrow
    return


@app.cell
def _():
    from util import translate, translations, get_local_data
    return translate, translations, get_local_data


@app.cell
def _(mo):
    mo.md(r"""# 85237NED""")
    return


@app.cell
def _(mo):
    description = """

    ### Active passenger cars

    | | |
    |-|-|
    | name   |  "Active passenger cars; vehicle characteristics, regions, January 1" | 
    | unit   |  "number of vehicles" | 
    | url    |  "http://opendata.cbs.nl/ODataApi/OData/85237NED" |

    This table contains figures on active passenger cars in the Netherlands as of January 1st, broken down by various vehicle characteristics and regions. The data includes:

    - Vehicle characteristics: construction year, fuel type, curb weight class, and color
    - Ownership details: private owners by age group and business ownership
    - Regional breakdown by all Dutch provinces
    - Number of active vehicles that were eligible to participate in public road traffic

    The vehicle population is based on the Vehicle Registration Database (RDW) and includes Dutch-registered vehicles that were allowed to participate in public road traffic during the previous year. Uninsured vehicles and vehicles in business inventory are excluded from the count.

    Recent updates have improved the classification of hybrid electric vehicles, which may slightly adjust electric vehicle counts compared to previous versions.

    Data available from: 2019

    Status of the figures:
    The figures are updated annually and provide a comprehensive view of the Dutch passenger car fleet composition.

    When will new figures be available?
    Annually, typically updated in the second quarter of the year.

    """
    mo.md(description)
    return


@app.cell
def _(mo):
    mo.md(r"""## Raw Data""")
    return


@app.cell
def _(mo):
    mo.md(r"""### Metadata""")
    return


@app.cell
def _(get_local_data):
    def get_metadata():
        # Load metadata from local data folder
        metadata_df = get_local_data("85237NED")  # Base dataset metadata
        return metadata_df

    metadata_df = get_metadata()
    metadata_df
    return (get_metadata,)


@app.cell
def _(mo):
    mo.md(r"""### Construction Years""")
    return


@app.cell
def _(get_local_data):
    def get_construction_years():
        # Load construction years data from local data folder
        construction_years_df = get_local_data("85237NED", "Bouwjaar")
        return construction_years_df

    construction_years_df = get_construction_years()
    construction_years_df

    return (construction_years_df,)


@app.cell
def _(mo):
    mo.md(r"""### Time Periods""")
    return


@app.cell
def _(get_local_data):
    def get_data_time_periods():
        # Load time periods data from local data folder
        return get_local_data("85237NED", "Perioden")

    data_time_periods_df = get_data_time_periods()
    data_time_periods_df
    return (data_time_periods_df,)


@app.cell
def _(mo):
    mo.md(r"""### Data Properties""")
    return


@app.cell
def _(get_local_data):
    def get_data_properties():
        # Load data properties from local data folder
        return get_local_data("85237NED", "DataProperties")

    def get_regions( df ):
        # From the dataframe get all rows with a parent ID = 2 and return as an array of titles
        regions = df[df['ParentID'] == 2]['Title'].tolist()
        return regions

    data_properties_df = get_data_properties()
    regions = get_regions(data_properties_df)
    data_properties_df
    return (data_properties_df,)


@app.cell
def _(mo):
    mo.md(r"""### Typed Data Set""")
    return


@app.cell
def _(get_local_data):
    def get_typed_data_set():
        # Load complete typed dataset from local data folder
        return get_local_data("85237NED", "TypedDataSet")

    typed_data_set_df = get_typed_data_set()
    typed_data_set_df
    return (typed_data_set_df,)


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Annotated Data Set

    Creates annotated_data_set_df - a copy of typed_data_set_df with all label lookups resolved.
    """
    )
    return


@app.cell
def _(
    construction_years_df,
    data_properties_df,
    data_time_periods_df,
    translate,
    translations,
    typed_data_set_df,
):
    def get_annotated_data_set():
        # Create a copy of the typed data set
        annotated_data_set_df = typed_data_set_df.copy()

        # Map the construction year codes to their titles
        construction_years_dict = {
            row['Key']: row['Title'] for _, row in construction_years_df.iterrows()
        }
        annotated_data_set_df.loc[:,"Bouwjaar"] = annotated_data_set_df["Bouwjaar"].map(construction_years_dict)

        # Map the period codes to their titles and convert to integers
        periods_dict = {
            row['Key']: row['Title'] for _, row in data_time_periods_df.iterrows()
        }
        annotated_data_set_df.loc[:,"Perioden"] = annotated_data_set_df["Perioden"].map(periods_dict)
        annotated_data_set_df["Perioden"] = annotated_data_set_df["Perioden"].astype(int)

        # Map data column names using DataProperties: Key -> "Title (Unit)" 
        # Only rename columns that exist in both the dataframe and DataProperties
        # Use Key as fallback to ensure uniqueness when multiple columns have same Title
        properties_dict = {}
        for _, row in data_properties_df.iterrows():
            if row['Key'] in annotated_data_set_df.columns:
                title = translate(row['Title'])
                unit = translate(row['Unit'])
                new_name = title

                # If this title already exists, use the Key to make it unique
                #new_name = f"{title} ({unit})"
                while new_name in properties_dict.values():
                    new_name = new_name+"_"
                #    new_name = f"{title} - {row['Key']} ({unit})"
                properties_dict[row['Key']] = new_name
        annotated_data_set_df.rename(columns=properties_dict, inplace=True)

        annotated_data_set_df.rename(columns=lambda x:translate(x), inplace=True)
        annotated_data_set_df = annotated_data_set_df.replace(translations)

        return annotated_data_set_df

    annotated_data_set_df = get_annotated_data_set()
    annotated_data_set_df
    return


if __name__ == "__main__":
    app.run()
