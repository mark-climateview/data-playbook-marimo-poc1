import marimo

__generated_with = "0.14.6"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _(mo):
    mo.md(r"""# Netherlands - Personal vehicles: traffic performance of locally registered cars""")
    return


@app.cell
def _(mo):
    parameters = [
        "stock_personal_vehicles_petrol",
        "stock_personal_vehicles_diesel",
        "stock_personal_vehicles_natural_gas",
        "stock_personal_vehicles_lpg",
        "stock_personal_vehicles_bev",
        "stock_personal_vehicles_hydrogen",
    ]

    md = "Calculates operations of personal vehicles for the following fuel types:\n\n"
    for p in parameters:
        md += f"- `{p}`\n"

    mo.md(md)
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    # 1. Calculate national average km per year by fuel type

    From dataset 85405NED: Traffic performance of passenger cars, fuel extended, age, 

    - `X = average number of km driven per car of the fuel type`
    """
    )
    return


@app.cell
def _(data_table_85405NED_result, pd):



    def get_traffic_performance(fuel_type):
        """Get traffic performance for a specific fuel type for a given year for all vehicle ages."""
        data_85405NED = data_table_85405NED_result.defs["annotated_data_set_df"]
        data_85405NED = data_85405NED[data_85405NED["Vehicle Age"] == "Total"]
        data_85405NED = data_85405NED[data_85405NED["Fuel Type"] != "Total"]
        data_85405NED = data_85405NED[data_85405NED["Period"] == 2023]
        return data_85405NED[(data_85405NED["Fuel Type"] == fuel_type)]["Average Annual Mileage"].values[0]

    # Get average number of km driven per car of the fuel type
    average_petrol_km_per_year = get_traffic_performance("Petrol / Petrol Hybrids / Ethanol")
    average_diesel_km_per_year = get_traffic_performance("Diesel / Diesel Hybrids")
    average_electric_km_per_year = get_traffic_performance("Battery Electric / Hydrogen")
    average_plug_in_hybrid_km_per_year = get_traffic_performance("Plug-in hybrides")
    average_lpg_km_per_year = get_traffic_performance("LPG / LPG Hybrids")
    average_cng_km_per_year = get_traffic_performance("CNG / CNG Hybrids / LNG")

    # convert the above set of averages into a dataframe
    pd.DataFrame({
        "Fuel Type": [
            "Petrol / Petrol Hybrids / Ethanol",
            "Diesel / Diesel Hybrids",
            "Battery Electric / Hydrogen",
            "Plug-in hybrides",
            "LPG / LPG Hybrids",
            "CNG / CNG Hybrids / LNG"
        ],
        "Average Annual Mileage (km)": [
            average_petrol_km_per_year,
            average_diesel_km_per_year,
            average_electric_km_per_year,
            average_plug_in_hybrid_km_per_year,
            average_lpg_km_per_year,
            average_cng_km_per_year
        ]
    })
    return (
        average_cng_km_per_year,
        average_diesel_km_per_year,
        average_electric_km_per_year,
        average_lpg_km_per_year,
        average_petrol_km_per_year,
    )


@app.cell
def _(mo):
    mo.md(
        r"""
    # 2. Calculate number of cars registered per municipality

    From dataset 85236NED: Motor vehicles active on January 1; vehicle type, region as of January 1, 2023 

     - `Y = the number of cars registered in your municipality`
    """
    )
    return


@app.cell
def _(data_table_85236NED_result, pd):

    def get_cars_registered(region, year="2023"):
        """Get number of cars registered in a region for a given year."""
        data_85236NED = data_table_85236NED_result.defs["annotated_data_set_df"]
        data_85236NED = data_85236NED[data_85236NED["Regions (None)"] == region]
        data_85236NED = data_85236NED[data_85236NED["Period (None)"] == 2023]

        # Filter the dataset for the specific municipality and year
        if not data_85236NED.empty:
            return data_85236NED["Passenger Car (number)"].values[0]
        else:
            return None

    registered_cars = {}
    for region in data_table_85236NED_result.defs["regions"]:
        registered_cars[region] = get_cars_registered(region)

    # Return registered_cars as a DataFrame
    pd.DataFrame(list(registered_cars.items()), columns=["Region", "Registered Cars"])


    return (registered_cars,)


@app.cell
def _(mo):
    mo.md(
        r"""
    # 3. Calculate national distribution of cars by fuel type

    From dataset 85237NED: Passenger cars active; vehicle characteristics, regions, January 1 

      - Get the distribution of passenger cars per fuel type nationally.
      - `Z = the share of passenger cars of your fuel type`
    """
    )
    return


@app.cell
def _(data_table_85237NED_result, pd):

    def get_fuel_type_distribution(fuel_type_column, year="2023"):
        """Get number of cars registered in a region for a given year."""
        data_85237NED = data_table_85237NED_result.defs["annotated_data_set_df"]
        data_85237NED = data_85237NED[data_85237NED["Construction Year (None)"] == "Total all construction years"]
        data_85237NED = data_85237NED[data_85237NED["Period (None)"] == 2023]

        if not data_85237NED.empty:
            return data_85237NED[fuel_type_column].values[0]
        else:
            return None    


    passenger_cars_distribution_total = get_fuel_type_distribution("Total (number)")
    passenger_cars_distribution_petrol = get_fuel_type_distribution("Gasoline (number)") / passenger_cars_distribution_total
    passenger_cars_distribution_diesel = get_fuel_type_distribution("Diesel (number)") / passenger_cars_distribution_total
    passenger_cars_distribution_lpg = get_fuel_type_distribution("LPG (number)") / passenger_cars_distribution_total
    passenger_cars_distribution_electricity = get_fuel_type_distribution("Electricity (number)") / passenger_cars_distribution_total
    passenger_cars_distribution_cng = get_fuel_type_distribution("CNG (number)") / passenger_cars_distribution_total
    passenger_cars_distribution_other_unknown = get_fuel_type_distribution("Other/Unknown (number)") / passenger_cars_distribution_total

    # convert the above set of distributions into a dataframe
    df = pd.DataFrame({
        "Fuel Type": [
            "Petrol",
            "Diesel",
            "LPG",
            "Electricity",
            "CNG",
            "Other/Unknown"
        ],
        "Distribution (%)": [
            passenger_cars_distribution_petrol * 100,
            passenger_cars_distribution_diesel * 100,
            passenger_cars_distribution_lpg * 100,
            passenger_cars_distribution_electricity * 100,
            passenger_cars_distribution_cng * 100,
            passenger_cars_distribution_other_unknown * 100
        ]
    })
    df['Distribution (%)'] = df['Distribution (%)'].map('{:,.2f}'.format)
    df

    return (
        passenger_cars_distribution_cng,
        passenger_cars_distribution_diesel,
        passenger_cars_distribution_electricity,
        passenger_cars_distribution_lpg,
        passenger_cars_distribution_other_unknown,
        passenger_cars_distribution_petrol,
    )


@app.cell
def _(mo):
    mo.md(
        r"""
    # 4. Calculate number of cars per fuel type per region

    Apply the national shares per fuel type to the number of cars registered in your municipality to get the number of cars per fuel  type in your municipality.

    - `numbercars_fueltype = Y * Z`
    """
    )
    return


@app.cell
def _(
    data_table_85236NED_result,
    passenger_cars_distribution_cng,
    passenger_cars_distribution_diesel,
    passenger_cars_distribution_electricity,
    passenger_cars_distribution_lpg,
    passenger_cars_distribution_other_unknown,
    passenger_cars_distribution_petrol,
    pd,
    registered_cars,
):

    def get_number_fuel_types(region):
        return {
            "Petrol": registered_cars[region] * passenger_cars_distribution_petrol,
            "Diesel": registered_cars[region] * passenger_cars_distribution_diesel,
            "LPG": registered_cars[region] * passenger_cars_distribution_lpg,
            "Electricity": registered_cars[region] * passenger_cars_distribution_electricity,
            "CNG": registered_cars[region] * passenger_cars_distribution_cng,
            "Other/Unknown": registered_cars[region] * passenger_cars_distribution_other_unknown,
        }

    def get_number_fuel_types_all_regions():
        number_fuel_types = {}
        for region in data_table_85236NED_result.defs["regions"]:
            number_fuel_types[region] = get_number_fuel_types(region)
        return number_fuel_types

    
    number_fuel_types = get_number_fuel_types_all_regions()

    pd.DataFrame.from_dict(number_fuel_types, orient='index').reset_index().rename(columns={'index': 'Region'})

    return (number_fuel_types,)


@app.cell
def _(mo):
    mo.md(
        r"""
    # 5. Calculate operations of cars per fuel type per region

    Multiply the number of cars per fuel type with the average yearly km for that fuel type.

    -  `operations_fueltype = numbercars_fueltype * X`
    """
    )
    return


@app.cell
def _(
    average_cng_km_per_year,
    average_diesel_km_per_year,
    average_electric_km_per_year,
    average_lpg_km_per_year,
    average_petrol_km_per_year,
    data_table_85236NED_result,
    number_fuel_types,
    pd,
):

    def get_vehicle_operations(region):
        return {
            "stock_personal_vehicles_petrol": number_fuel_types[region]["Petrol"] * average_petrol_km_per_year,
            "stock_personal_vehicles_diesel": number_fuel_types[region]["Diesel"] * average_diesel_km_per_year,
            "stock_personal_vehicles_lpg": number_fuel_types[region]["LPG"] * average_lpg_km_per_year,
            "stock_personal_vehicles_bev": number_fuel_types[region]["Electricity"] * average_electric_km_per_year,
            "stock_personal_vehicles_hydrogen": 0, # this number is not available in the dataset, assuming 0
            "stock_personal_vehicles_natural_gas": number_fuel_types[region]["CNG"] * average_cng_km_per_year,
        }
    
    def get_vehicle_operations_all_regions():
        vehicle_operations = {}
        for region in data_table_85236NED_result.defs["regions"]:
            vehicle_operations[region] = get_vehicle_operations(region)
        return vehicle_operations


    vehicle_operations = get_vehicle_operations_all_regions()

    pd.DataFrame.from_dict(vehicle_operations, orient='index').reset_index().rename(columns={'index': 'Region'}).round(0)

    return


@app.cell
def _(mo):
    mo.md(
        r"""

    ---

    ---

    # Data Sources
    """
    )
    return


@app.cell
def _(mo):
    import data_table_85405NED
    mo.md("## 85405NED")
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
    import data_table_85236NED
    mo.md("## 85236NED")
    return (data_table_85236NED,)


@app.cell
async def _(data_table_85236NED, mo):
    async def import_data_table_85236NED():
        result = await data_table_85236NED.app.embed()
        return result

    data_table_85236NED_result = await import_data_table_85236NED()
    mo.md(data_table_85236NED_result.defs["description"])
    return (data_table_85236NED_result,)


@app.cell
def _(mo):
    import data_table_85237NED
    mo.md("## 85237NED")
    return (data_table_85237NED,)


@app.cell
async def _(data_table_85237NED, mo):
    async def import_data_table_85237NED():
        result = await data_table_85237NED.app.embed()
        return result

    data_table_85237NED_result = await import_data_table_85237NED()
    mo.md(data_table_85237NED_result.defs["description"])
    return (data_table_85237NED_result,)


@app.cell
def _():
    import requests
    import json
    import pandas as pd
    import util
    return (pd,)


if __name__ == "__main__":
    app.run()
