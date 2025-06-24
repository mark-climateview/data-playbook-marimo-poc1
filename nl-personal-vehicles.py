import marimo

__generated_with = "0.14.6"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _(mo):
    mo.md(
        r"""
    # Netherlands - Personal vehicles: traffic performance of locally registered cars


    """
    )
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    ## Data Sources

    ### 85236NED
            name: "Aantal voertuigen"
            unit: "# vehicles"
            url: "http://opendata.cbs.nl/ODataApi/OData/85236NED"

    ### 85237NED
            name: "Aantal voertuigen"
            unit: "# vehicles"
            url: "http://opendata.cbs.nl/ODataApi/OData/85237NED"

    ### 85395NED
            name: "Aantal voertuigkilometers"
            unit: "million vehicle-km"
            url: "http://opendata.cbs.nl/ODataApi/OData/85395NED"

    ### 85238NED
            name: "Aantal voertuigen"
            unit: "# vehicles"
            url: "http://opendata.cbs.nl/ODataApi/OData/85238NED"
    """
    )
    return


@app.cell
def _(mo):
    import data_table_85405NED
    mo.md("### 85405NED")
    return (data_table_85405NED,)


@app.cell
async def _(data_table_85405NED, mo):
    async def import_data_table_85405NED():
        result = await data_table_85405NED.app.embed()
        return result

    data_table_85405NED_result = await import_data_table_85405NED()
    # data_table_85405NED_result.output
    mo.md(data_table_85405NED_result.defs["description"])

    return (data_table_85405NED_result,)


@app.cell
def _(mo):
    mo.md(r"""# National average km per year by fuel type""")
    return


@app.cell
def _(data_table_85405NED_result):

    data_85405NED = data_table_85405NED_result.defs["annotated_data_set_df"]
    # Filter on vehicle age == "Total", Fuel Type != "Total" and year = latest ("2023")
    data_85405NED = data_85405NED[data_85405NED["Vehicle Age"] == "Total"]
    data_85405NED = data_85405NED[data_85405NED["Fuel Type"] != "Total"]
    data_85405NED = data_85405NED[data_85405NED["Period"] == 2023]
    data_85405NED
    return (data_85405NED,)


@app.cell
def _(data_85405NED, mo):
    def get_traffic_performance(fuel_type, year="latest"):
        """Get traffic performance for a specific fuel type for a given year for all vehicle ages."""
        return data_85405NED[(data_85405NED["Fuel Type"] == fuel_type)]["Average Annual Mileage"].values[0]

    # Get average number of km driven per car of the fuel type
    average_petrol_km_per_year = get_traffic_performance("Petrol / Petrol Hybrids / Ethanol")
    average_diesel_km_per_year = get_traffic_performance("Diesel / Diesel Hybrids")
    average_electric_km_per_year = get_traffic_performance("Battery Electric / Hydrogen")
    mo.md(f"""Average km driven per car in 2023:

    - Petrol: {average_petrol_km_per_year} km / year
    - Diesel: {average_diesel_km_per_year} km / year 
    - Electric: {average_electric_km_per_year} km / year

    """)

    return


@app.cell
def _(mo):
    mo.md(r"""# Number of cars regiestered per municipality""")
    return


@app.cell
def _():
    # 2. From dataset 85236NED: Motor vehicles active on January 1; vehicle type, region as of January 1, 2023 take the number of cars regiestered in your municipality.
    # - Let Y = the number of cars registered in your municipality


    return


@app.cell
def _(mo):
    mo.md(r"""# Dependencies and setup""")
    return


@app.cell
def _():
    import requests
    import json
    import pandas as pd

    return


if __name__ == "__main__":
    app.run()
