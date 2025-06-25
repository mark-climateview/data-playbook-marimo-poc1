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
    return


@app.cell
def _():
    from util import get_cbs_url, translate, translations, get_cbs_url_paginated
    return get_cbs_url, get_cbs_url_paginated, translate, translations


@app.cell
def _(mo):
    mo.md(r"""# 85236NED""")
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
def _(get_cbs_url):
    data_source_url = "https://opendata.cbs.nl/ODataApi/OData/85236NED"

    def get_metadata():
        metadata_df = get_cbs_url(data_source_url)
        return metadata_df

    metadata_df = get_metadata()
    metadata_df
    return (get_metadata,)


@app.cell
def _(mo):
    mo.md(r"""### Regions""")
    return


@app.cell
def _(get_cbs_url, get_metadata):
    def get_regions():
        # Get the URL for name == "RegioS" from the metadata DataFrame
        metadata_df = get_metadata()
        regions_url = metadata_df.loc[metadata_df['name'] == 'RegioS', 'url'].values[0]
        # Fetch the data from the URL
        regions_df = get_cbs_url(regions_url)
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
def _(get_cbs_url, get_metadata):
    def get_data_time_periods():
        # Get the data URL for name == "Perioden" from the metadata DataFrame
        metadata_df = get_metadata()
        time_periods_url = metadata_df.loc[metadata_df['name'] == 'Perioden', 'url'].values[0]
        # Fetch the data from the URL
        return get_cbs_url(time_periods_url)

    data_time_periods_df = get_data_time_periods()
    data_time_periods_df
    return (data_time_periods_df,)


@app.cell
def _(mo):
    mo.md(r"""### Data Properties""")
    return


@app.cell
def _(get_cbs_url, get_metadata):
    def get_data_properties():
        # Get the URL for name == "DataProperties" from the metadata DataFrame
        metadata_df = get_metadata()
        data_properties_url = metadata_df.loc[metadata_df['name'] == 'DataProperties', 'url'].values[0]
        # Fetch the data from the URL
        return get_cbs_url(data_properties_url)

    data_properties_df = get_data_properties()
    data_properties_df

    return (data_properties_df,)


@app.cell
def _(mo):
    mo.md(r"""### Typed Data Set""")
    return


@app.cell
def _(get_cbs_url_paginated, get_metadata):
    def get_typed_data_set():
        # Get the URL for name == "TypedDataSet" from the metadata DataFrame
        metadata_df = get_metadata()
        typed_data_set_url = metadata_df.loc[metadata_df['name'] == 'TypedDataSet', 'url'].values[0]

        # Use the new aggregate caching function for paginated datasets
        # This will cache the complete dataset with a clean filename
        return get_cbs_url_paginated(typed_data_set_url, page_size=5000)

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
                new_name = f"{title} ({unit})"
                if new_name in properties_dict.values():
                    new_name = f"{title} - {row['Key']} ({unit})"
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
