import marimo

__generated_with = "0.14.6"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _():
    import requests
    import json
    import pandas as pd
    import pyarrow
    return


@app.cell
def _():
    from util import translate, translations, get_local_data, is_running_in_cloud, get_execution_environment, get_environment_info
    return translate, translations, get_local_data, is_running_in_cloud, get_execution_environment, get_environment_info


@app.cell
def _(mo):    
    mo.md(r"""# 85236NED""")
    return


@app.cell
def _(mo, is_running_in_cloud, get_environment_info):
    # Environment Detection Demo
    environment_info = get_environment_info()
    is_cloud = is_running_in_cloud()
    
    mo.md(f"""
    **Environment Detection:**
    - Running in cloud: {is_cloud}
    - Environment: {environment_info}
    """)
    return


@app.cell
def _(mo):
    description = """

    ### Motor vehicles active by vehicle type, postal code, region

    | | |
    |-|-|
    | name   |  "Motorvoertuigen actief; voertuigtype, postcode, regio, 1 januari, 2019-2023" | 
    | unit   |  "number of vehicles" | 
    | url    |  "http://opendata.cbs.nl/ODataApi/OData/85236NED" |

    This table contains figures on active motor vehicles in the Netherlands as of January 1st, broken down by vehicle type, postal code, and region. The data includes:

    - Vehicle types: passenger cars, commercial vehicles (delivery vans, trucks, tractors, special vehicles, buses), motorcycles, and moped-licensed vehicles (mopeds, motorized bicycles, mobility scooters)
    - Regional breakdown: postal codes, municipalities, provinces, COROP areas, and national level
    - Geographic attributes: municipality size class, urbanization level, and regional classifications

    The vehicle population includes only vehicles that were insured and allowed to participate in road traffic during the previous year. Vehicles in business inventory are excluded from the count.

    This dataset provides comprehensive coverage of the Dutch motor vehicle fleet composition across different vehicle categories and geographical levels, enabling detailed analysis of regional transportation patterns.

    Data available from: 2019-2023

    Status of the figures:
    This dataset has been discontinued. The figures cover the period 2019-2023.

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
        metadata_df = get_local_data("85236NED")  # Base dataset metadata
        return metadata_df

    metadata_df = get_metadata()
    metadata_df
    return (get_metadata,)


@app.cell
def _(mo):
    mo.md(r"""### Regions""")
    return


@app.cell
def _(get_local_data):
    def get_regions():
        # Load regions data from local data folder
        regions_df = get_local_data("85236NED", "RegioS")
        return regions_df

    regions_df = get_regions()
    regions = regions_df[regions_df['CategoryGroupID'].isin(range(1,17))]['Title'].tolist()
    regions_df

    return (regions_df,)


@app.cell
def _(mo):
    mo.md(r"""### Time Periods""")
    return


@app.cell
def _(get_local_data):
    def get_data_time_periods():
        # Load time periods data from local data folder
        return get_local_data("85236NED", "Perioden")

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
        return get_local_data("85236NED", "DataProperties")

    data_properties_df = get_data_properties()
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
        return get_local_data("85236NED", "TypedDataSet")

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
    data_properties_df,
    data_time_periods_df,
    regions_df,
    translate,
    translations,
    typed_data_set_df,
):
    def get_annotated_data_set():
        # Create a copy of the typed data set
        annotated_data_set_df = typed_data_set_df.copy()

        # Map the region codes to their titles (only if RegioS column exists)
        regions_dict = {
            row['Key']: row['Title'] for _, row in regions_df.iterrows()
        }
        if "RegioS" in annotated_data_set_df.columns:
            annotated_data_set_df.loc[:,"RegioS"] = annotated_data_set_df["RegioS"].map(regions_dict)

        # Map the period codes to their titles and convert to integers (only if Perioden column exists)
        periods_dict = {
            row['Key']: row['Title'] for _, row in data_time_periods_df.iterrows()
        }
        if "Perioden" in annotated_data_set_df.columns:
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
                # If this title already exists, use the Key to make it unique
                new_name = title
                #new_name = f"{title} ({unit})"
                #if new_name in properties_dict.values():
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
