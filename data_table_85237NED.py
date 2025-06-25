import marimo

__generated_with = "0.14.6"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return (mo,)


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
def _(util):
    data_source_url = "https://opendata.cbs.nl/ODataApi/OData/85237NED"

    def get_metadata():
        metadata_df = util.get_cbs_url(data_source_url)
        return metadata_df

    metadata_df = get_metadata()
    metadata_df
    return (get_metadata,)


@app.cell
def _(mo):
    mo.md(r"""### Construction Years""")
    return


@app.cell
def _(get_metadata, util):
    def get_construction_years():
        # Get the URL for name == "Bouwjaar" from the metadata DataFrame
        metadata_df = get_metadata()
        construction_years_url = metadata_df.loc[metadata_df['name'] == 'Bouwjaar', 'url'].values[0]
        # Fetch the data from the URL
        construction_years_df = util.get_cbs_url(construction_years_url)
        return construction_years_df

    construction_years_df = get_construction_years()
    construction_years_df

    return (construction_years_df,)


@app.cell
def _(mo):
    mo.md(r"""### Time Periods""")
    return


@app.cell
def _(get_metadata, util):
    def get_data_time_periods():
        # Get the data URL for name == "Perioden" from the metadata DataFrame
        metadata_df = get_metadata()
        time_periods_url = metadata_df.loc[metadata_df['name'] == 'Perioden', 'url'].values[0]
        # Fetch the data from the URL
        return util.get_cbs_url(time_periods_url)

    data_time_periods_df = get_data_time_periods()
    data_time_periods_df
    return (data_time_periods_df,)


@app.cell
def _(mo):
    mo.md(r"""### Data Properties""")
    return


@app.cell
def _(get_metadata, util):
    def get_data_properties():
        # Get the URL for name == "DataProperties" from the metadata DataFrame
        metadata_df = get_metadata()
        data_properties_url = metadata_df.loc[metadata_df['name'] == 'DataProperties', 'url'].values[0]
        # Fetch the data from the URL
        return util.get_cbs_url(data_properties_url)

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
def _(get_metadata, util):
    def get_typed_data_set():
        # Get the URL for name == "TypedDataSet" from the metadata DataFrame
        metadata_df = get_metadata()
        typed_data_set_url = metadata_df.loc[metadata_df['name'] == 'TypedDataSet', 'url'].values[0]
        # Fetch the data from the URL
        return util.get_cbs_url(typed_data_set_url)

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
    typed_data_set_df,
    util,
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
                title = util.translate(row['Title'])
                unit = util.translate(row['Unit'])
                # If this title already exists, use the Key to make it unique
                new_name = f"{title} ({unit})"
                if new_name in properties_dict.values():
                    new_name = f"{title} - {row['Key']} ({unit})"
                properties_dict[row['Key']] = new_name
        annotated_data_set_df.rename(columns=properties_dict, inplace=True)

        annotated_data_set_df.rename(columns=lambda x:util.translate(x), inplace=True)
        annotated_data_set_df = annotated_data_set_df.replace(util.translations)

        return annotated_data_set_df

    annotated_data_set_df = get_annotated_data_set()
    annotated_data_set_df
    return


@app.cell
def _(mo):
    mo.md(r"""# Dependencies and Setup""")
    return


@app.cell
def _():
    import requests
    import json
    import pandas as pd
    import util
    return (util,)


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Cache Management

    The data is now cached locally for faster loading. Use the functions below to manage the cache:
    """
    )
    return


@app.cell
def _(mo, util):
    # Cache management controls
    def show_cache_stats():
        stats = util.get_cache_stats()
        return f"""
        **Cache Statistics:**
        - Metadata files: {stats['metadata_files']}
        - Data files: {stats['data_files']}
        - Total size: {stats['total_size_mb']} MB
        - Cache directory: {stats['cache_dir']}
        """

    def clear_cache():
        util.invalidate_cache()
        return "✅ All cache cleared"

    def clear_dataset_cache():
        util.invalidate_cache("https://opendata.cbs.nl/ODataApi/OData/85237NED")
        return "✅ Cache cleared for dataset 85237NED"

    # Display cache stats
    mo.md(show_cache_stats())
    return


if __name__ == "__main__":
    app.run()
