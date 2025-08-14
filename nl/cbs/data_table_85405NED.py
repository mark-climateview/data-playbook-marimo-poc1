import marimo

__generated_with = "0.14.6"
app = marimo.App(width="medium")


@app.cell
def _():
    import sys, os
    if "pyodide" in sys.modules and not globals().get('_IS_IMPORTED', False):
        from pyodide.http import pyfetch
        response = await pyfetch("https://mark-climateview.github.io/data-playbook-marimo-poc1/cbs.zip")
        await response.unpack_archive()    

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
    mo.md(r"""# 85405NED""")
    return


@app.cell
def _(mo):
    description = """

    ### Number of vehicle kilometers

    | | |
    |-|-|
    | name   |  "Number of vehicle kilometers" | 
    | unit   |  "million vehicle-km" | 
    | url    |  "http://opendata.cbs.nl/ODataApi/OData/85405NED" |

    This table contains figures on traffic performance (vehicle kilometers) of Dutch passenger cars, divided by fuel type and age of the vehicle. The table also contains the total number of vehicle kilometers traveled by all passenger cars and an average per vehicle. 

    The table also contains the number of passenger cars in use, this is not a current figure but the number of vehicles that may have been on the road during the reporting year. This concerns active vehicles, vehicles that have failed (due to export or demolition, among other things) and vehicles that have been in the company stock. 

    The vehicle population for which kilometers are estimated is based on the statistics on the motor vehicle fleet. The population of the figures in this table is based on the new selection method for the motor vehicle fleet. The difference between the old and the new selection method is described in a method report, see paragraph 4. The series of kilometers estimated on the basis of the new population is available from reporting year 2018. The series based on the old vehicle population runs up to and including reporting year 2020. The method of estimating kilometres has not changed, only the population.

    The figures for the 2020 reporting year have been corrected for the 'smoothing effect' of the method by means of a correction factor. This smoothing effect flattens out the annual variation in the figures. This gives a distorted picture of periods in which mobility suddenly changes drastically, such as in 2020 as a result of the corona crisis. 

    Data available from: 2018

    Status of the figures:
    The figures in this table for 2018 to 2022 are final and those for 2023 have a provisional status.

    Changes as of 7 November 2024:
    Figures for 2023 have been added.

    When will new figures be available?
    Annually.

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
        metadata_df = get_local_data("85405NED")  # Base dataset metadata
        return metadata_df

    metadata_df = get_metadata()
    metadata_df
    return (get_metadata,)


@app.cell
def _(mo):
    mo.md(r"""### Fuel Types""")
    return


@app.cell
def _(get_local_data):
    def get_fuel_types():
        # Load fuel types data from local data folder
        fuel_types_df = get_local_data("85405NED", "BrandstofsoortVoertuig")
        return fuel_types_df

    fuel_types_df = get_fuel_types()
    fuel_types_df

    return (fuel_types_df,)


@app.cell
def _(mo):
    mo.md(r"""### Vehicle Age Groups""")
    return


@app.cell
def _(get_local_data):
    def get_vehicle_age_groups():
        # Load vehicle age groups data from local data folder
        return get_local_data("85405NED", "LeeftijdVoertuig")

    vehicle_age_groups_df = get_vehicle_age_groups()
    vehicle_age_groups_df
    return (vehicle_age_groups_df,)


@app.cell
def _(mo):
    mo.md(r"""### Time Periods""")
    return


@app.cell
def _(get_local_data):
    def get_data_time_periods():
        # Load time periods data from local data folder
        return get_local_data("85405NED", "Perioden")

    data_time_periods_df = get_data_time_periods()
    data_time_periods_df
    return (data_time_periods_df,)


@app.cell
def _(mo):
    mo.md(r"""### Typed Data Set""")
    return


@app.cell
def _(get_local_data):
    def get_typed_data_set():
        # Load complete typed dataset from local data folder
        return get_local_data("85405NED", "TypedDataSet")

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
    data_time_periods_df,
    fuel_types_df,
    translate,
    translations,
    typed_data_set_df,
    vehicle_age_groups_df,
):
    def get_annotated_data_set():
        # Create a copy of the typed data set
        annotated_data_set_df = typed_data_set_df.copy()

        # Map the vehicle age codes to their titles
        vehicle_ages_dict = {
            row['Key']: row['Title'] for _, row in vehicle_age_groups_df.iterrows()
        }
        annotated_data_set_df.loc[:,"LeeftijdVoertuig"] = annotated_data_set_df["LeeftijdVoertuig"].map(vehicle_ages_dict)

        # Map the fuel type codes to their titles
        fuel_types_dict = {
            row['Key']: row['Title'] for _, row in fuel_types_df.iterrows()
        }    
        annotated_data_set_df.loc[:,"BrandstofsoortVoertuig"] = annotated_data_set_df["BrandstofsoortVoertuig"].map(fuel_types_dict)

        # Map the period codes to their titles and convert to integers
        periods_dict = {
            row['Key']: row['Title'] for _, row in data_time_periods_df.iterrows()
        }
        annotated_data_set_df.loc[:,"Perioden"] = annotated_data_set_df["Perioden"].map(periods_dict)
        annotated_data_set_df["Perioden"] = annotated_data_set_df["Perioden"].astype(int)

        annotated_data_set_df.rename(columns=lambda x:translate(x), inplace=True)
        annotated_data_set_df = annotated_data_set_df.replace(translations)


        return annotated_data_set_df

    annotated_data_set_df = get_annotated_data_set()
    annotated_data_set_df
    return


if __name__ == "__main__":
    app.run()
