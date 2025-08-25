import marimo

__generated_with = "0.14.17"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _(mo):
    mo.md(r"""# Scotland:  Personal Transport - Roads""")
    return


@app.cell
def _(mo):
    # Render an image from a local file
    mo.image(src="images/gb-sct-personal-transport-roads.png", 
             alt="Scotland: Personal Transport - Roads", 
             width=800,
             style={"margin": "0 auto"},
             caption="Flow of data for Scotland's Personal Transport - Roads module")
    return


@app.cell
def _(mo):
    parameters = [
        "stock_buses_diesel",
        "stock_personal_vehicles_diesel",
        "stock_freight_heavy_trucks_diesel",
        "stock_freight_light_trucks_diesel",
        "stock_personal_vehicles_petrol",
        "stock_motorcycles_petrol",
        "stock_freight_light_trucks_petrol",
        "energy_intensity_buses_diesel",
        "energy_intensity_personal_vehicles_diesel",
        "energy_intensity_freight_heavy_trucks_diesel",
        "energy_intensity_freight_light_trucks_diesel",
        "energy_intensity_personal_vehicles_petrol",
        "energy_intensity_motorcycles_petrol",
        "energy_intensity_freight_light_trucks_petrol",
        "emission_factor_diesel_kwh_to_co2e",
        "emission_factor_petrol_kwh_to_co2e"    
    ]

    md = "This notebook calculates the following parameters:\n\n"
    for p in parameters:
        md += f"- `{p}`\n"
    mo.md(md)
    return


@app.cell
def _(mo):
    mo.md(
        r"""
    ---

    # User input
    """
    )
    return


@app.cell
def _(args, mo):
    local_authorities = [
        "Aberdeen City",
        "Aberdeenshire",
        "Angus",
        "Argyll and Bute",
        "City of Edinburgh",
        "Clackmannanshire",
        "Dumfries and Galloway",
        "Dundee City",
        "East Ayrshire",
        "East Dunbartonshire",
        "East Lothian",
        "East Renfrewshire",
        "Falkirk",
        "Fife",
        "Glasgow City",
        "Highland",
        "Inverclyde",
        "Midlothian",
        "Moray",
        "Na h-Eileanan Siar",
        "North Ayrshire",
        "North Lanarkshire",
        "Orkney Islands",
        "Perth and Kinross",
        "Renfrewshire",
        "Scottish Borders",
        "Shetland Islands",
        "South Ayrshire",
        "South Lanarkshire",
        "Stirling",
        "West Dunbartonshire",
        "West Lothian",
        "Scotland total"
    ]

    # With search functionality
    local_authority_dropdown = mo.ui.dropdown(
        options=local_authorities,
        value=args.city,
        label="Choose local authority",
        searchable=True,
    )

    local_authority_dropdown
    return (local_authority_dropdown,)


@app.cell
def _(args, mo):
    year_dropdown = mo.ui.dropdown(
        options=["2023", "2022", "2021", "2020", "2019"],
        value=args.year,
        label="Choose year",
    )
    year_dropdown
    return (year_dropdown,)


@app.cell
def _(mo):
    mo.md(
        r"""
    ---

    # 1. Record the fuel consumption per vehicle type and per road type from the sub-national road transport consumption data. 

    "Buses, diesel cars, HGV and diesel LGV
    are all classed as diesel-consuming vehicles, while petrol
    cars, motorcycles and petrol LGV are classed as petrol-
    consuming vehicles" (Subnational Consumption Statistics
    Methodology and guidance booklet, 2024, p. 38).

    Repeat this process for each local authority and for each
    year back to 2005.

    **Source**: 
    https://assets.publishing.service.gov.uk/media/685a855272588f418862071f/subnational-road-transport-fuel-consumption-tables-2005-2023.xlsx
    """
    )
    return


@app.cell
def _(
    local_authority_dropdown,
    subnational_road_transport_fuel_consumption_dataframe,
):

    def get_subnational_road_transport_fuel_consumption_ktoe(local_authority):
        df = subnational_road_transport_fuel_consumption_dataframe 
        # Filter the DataFrame for the specified local authority and region
        df = df.loc[(df["Region"] == "Scotland") & (df["Local Authority [Note 4]"] == local_authority)]
        # Drop unnecessary columns
        df = df.drop(columns=["Local Authority Code", "Region", "Local Authority [Note 4]"])
        # Transpose the DataFrame to have fuel types as rows
        df = df.T
        # Rename column to local authority name
        df.columns = ["Fuel Consumption (kTOE)"]
        return df

    subnational_road_transport_fuel_consumption_ktoe = get_subnational_road_transport_fuel_consumption_ktoe(local_authority_dropdown.value)

    subnational_road_transport_fuel_consumption_ktoe

    #mo.plain(subnational_road_transport_fuel_consumption_ktoe)
    return (subnational_road_transport_fuel_consumption_ktoe,)


@app.cell
def _(mo):
    mo.md(
        r"""
    ---

    # 2. Convert kTOE to kWh

    Using an energy conversion factor of 1 tonne oil equivalent (toe) = 11,630 kWh

    **Source**: Page 48, [2012 Guidelines to Defra / DECC's GHG Conversion Factors for Company Reporting](https://assets.publishing.service.gov.uk/media/5a79beaae5274a684690bcb2/pb13773-ghg-conversion-factors-2012.pdf)
    """
    )
    return


@app.cell
def _(subnational_road_transport_fuel_consumption_ktoe):

    subnational_road_transport_fuel_consumption_kwh = subnational_road_transport_fuel_consumption_ktoe.copy()
    subnational_road_transport_fuel_consumption_kwh *= 11630*1000
    subnational_road_transport_fuel_consumption_kwh.columns = ["Fuel Consumption (kWh)"]
    subnational_road_transport_fuel_consumption_kwh
    return (subnational_road_transport_fuel_consumption_kwh,)


@app.cell
def _(mo):
    mo.md(
        r"""
    ---

    # 3. Get Emission Conversion Factors for Petrol and Diesel


    Multiply the converted sub-national road transport
    consumption data by the diesel or petrol emissions
    factor for the corresponding year based on the vehicle
    type's fuel classification. We use the average biofuel
    blend as per Note 6 of the which states, "the bioenergy
    totals estimate the consumption in each local authority
    of bioethanol and biodiesel that is blended into petrol
    and diesel respectively. This biofuel is included in the
    overall petroleum consumption totals." This is different
    than in the Sub-national total final energy consumption
    where Note 4 states, "The biofuels, bioethanol and
    biodiesel (blended into petrol and diesel respectively)
    are not included under road transport petroleum
    consumption, but reported separately under
    "Bioenergy and waste: Road Transport "

    Due to the lack of biofuels, 100% mineral blends should
    be used for the inventory years 2009-2005.

    Note that sub-national data published in 2023 for the
    year 2021 should be multiplied by the emission factors
    published in 2023 which will correspond to data
    collected in 2021 based on the time lag of reporting.

    To stay consistent with the LA GHG, that uses gross
    energy consumption values for calculations, and the
    PBCCDR we have pulled the gross emissions factors for
    our calculations.


    **Source**: [UK Greenhouse gas reporting: conversion factors](https://www.gov.uk/government/collections/government-conversion-factors-for-company-reporting)
    """
    )
    return


@app.cell
def _(conversion_factors, mo, pd):

    petrol_emission_factor_kwh = conversion_factors.loc[(conversion_factors["Level 3"] == "Petrol (average biofuel blend)") & (conversion_factors["UOM"] == "kWh (Net CV)"), "GHG Conversion Factor 2025"].values[0]
    diesel_emission_factor_kwh = conversion_factors.loc[(conversion_factors["Level 3"] == "Diesel (average biofuel blend)") & (conversion_factors["UOM"] == "kWh (Net CV)"), "GHG Conversion Factor 2025"].values[0]

    mo.md(f"""
    - Petrol: `{petrol_emission_factor_kwh} kgCO2/kWh`
    - Diesel: `{diesel_emission_factor_kwh} kgCO2/kWh`
    """)
    #petrol_emission_factor_kwh
    pd.DataFrame({
        "Fuel Type": [ "Petrol", "Diesel" ],
        "Emission Factor (kgCO2e/kWh)": [
            petrol_emission_factor_kwh,
            diesel_emission_factor_kwh
        ]
    })

    return diesel_emission_factor_kwh, petrol_emission_factor_kwh


@app.cell
def _(mo):
    mo.md(
        r"""
    ---

    # 4. Aggregate Emissions (per road and vehicle type)

    Calculated as:

    `emissions (kgCO2e) = fuel consumption (kWh) * fuel emission factor (kgCO2e/kWh)`
    """
    )
    return


@app.cell
def _(
    diesel_emission_factor_kwh,
    petrol_emission_factor_kwh,
    subnational_road_transport_fuel_consumption_kwh,
):

    def calculate_emissions_per_vehicle_type():
        # Create copy of dataframe
        subnational_road_transport_emissions = subnational_road_transport_fuel_consumption_kwh.copy()
        subnational_road_transport_emissions.columns = ["Emissions (kgCO2e)"]

        vehicel_types = ['Buses - \nMotorways', 'Buses - \nA roads', 'Buses - \nMinor roads',
               'Buses total', 'Diesel cars - \nMotorways', 'Diesel cars - \nA roads',
               'Diesel cars - \nMinor roads', 'Diesel cars total',
               'Petrol cars - \nMotorways', 'Petrol cars - \nA roads',
               'Petrol cars - \nMinor roads', 'Petrol cars total',
               'Motorcycles - \nMotorways', 'Motorcycles - \nA roads',
               'Motorcycles - \nMinor roads', 'Motorcycles total',
               'Diesel HGV - Motorways', 'Diesel HGV - A roads',
               'Diesel HGV - Minor roads', 'Diesel HGV total',
               'Natural Gas HGV - Motorways', 'Natural Gas HGV - A roads',
               'Natural Gas HGV - Minor roads', 'Natural Gas HGV total',
               'Diesel LGV - \nMotorways', 'Diesel LGV - \nA roads',
               'Diesel LGV - \nMinor roads', 'Diesel LGV total',
               'Petrol LGV - \nMotorways', 'Petrol LGV - \nA roads',
               'Petrol LGV - \nMinor roads', 'Petrol LGV total',
               'LPG LGV - \nMotorways', 'LPG LGV - \nA roads',
               'LPG LGV - \nMinor roads', 'LPG LGV total']

        for vehicle_type in vehicel_types:
            if "diesel" in vehicle_type.lower() or "buses" in vehicle_type.lower():
                factor = diesel_emission_factor_kwh
            else:
                factor = petrol_emission_factor_kwh
            subnational_road_transport_emissions.loc[vehicle_type, "Emissions (kgCO2e)"] = subnational_road_transport_fuel_consumption_kwh.loc[vehicle_type, "Fuel Consumption (kWh)"] * factor

        return subnational_road_transport_emissions

    subnational_road_transport_emissions = calculate_emissions_per_vehicle_type()
    subnational_road_transport_emissions

    return (subnational_road_transport_emissions,)


@app.cell
def _(mo):
    mo.md(
        r"""
    ---

    # 5. Calculate Operations (per road and vehicle type)

    ## 5a. Get Operations Conversion Factors

    ClimateView's operations units are used to translate emissions data into activity data.
    To calculate operations units, divide the emissions by their passenger vehicle, delivery
    vehicle or business travel - land conversion factor to convert from kgCO2e to vehicle
    kilometres or passenger kilometres.

    **Source**: [UK Greenhouse gas reporting: conversion factors](https://www.gov.uk/government/collections/government-conversion-factors-for-company-reporting)
    """
    )
    return


@app.cell
def _(conversion_factors, pd):
    average_local_bus_factor = conversion_factors.loc[
        (conversion_factors["Level 3"] == "Average local bus") & 
        (conversion_factors["UOM"] == "passenger.km") & 
        (conversion_factors["GHG/Unit"] == "kg CO2e"), "GHG Conversion Factor 2025"].values[0]
    average_car_diesel_factor = conversion_factors.loc[
        (conversion_factors["Level 3"] == "Average car") & 
        (conversion_factors["Column Text"] == "Diesel") & 
        (conversion_factors["GHG/Unit"] == "kg CO2e"), "GHG Conversion Factor 2025"].values[0]
    average_car_petrol_factor = conversion_factors.loc[
        (conversion_factors["Level 3"] == "Average car") &
        (conversion_factors["Column Text"] == "Petrol") &
        (conversion_factors["GHG/Unit"] == "kg CO2e"), "GHG Conversion Factor 2025"].values[0]
    hgv_diesel_factor = conversion_factors.loc[
        (conversion_factors["Level 2"] == "HGV (all diesel)") & 
        (conversion_factors["Level 3"] == "All HGVs") & 
        (conversion_factors["Column Text"] == "Average laden") & 
        (conversion_factors["UOM"] == "tonne.km") & 
        (conversion_factors["GHG/Unit"] == "kg CO2e"), "GHG Conversion Factor 2025"].values[0]
    average_vans_diesel_factor = conversion_factors.loc[
        (conversion_factors["Level 2"] == "Vans") & 
        (conversion_factors["Level 3"] == "Average (up to 3.5 tonnes)") & 
        (conversion_factors["Column Text"] == "Diesel") & 
        (conversion_factors["UOM"] == "km") & 
        (conversion_factors["GHG/Unit"] == "kg CO2e"), "GHG Conversion Factor 2025"].values[0]
    average_vans_petrol_factor = conversion_factors.loc[
        (conversion_factors["Level 2"] == "Vans") & 
        (conversion_factors["Level 3"] == "Average (up to 3.5 tonnes)") & 
        (conversion_factors["Column Text"] == "Petrol") & 
        (conversion_factors["UOM"] == "km") & 
        (conversion_factors["GHG/Unit"] == "kg CO2e"), "GHG Conversion Factor 2025"].values[0]
    average_motorbike_factor = conversion_factors.loc[
        (conversion_factors["Level 2"] == "Motorbike") & 
        (conversion_factors["Level 3"] == "Average") & 
        (conversion_factors["GHG/Unit"] == "kg CO2e"), "GHG Conversion Factor 2025"].values[0]


    pd.DataFrame({
        "Vehicle Type": [
            "Average local bus",
            "Cars (by size) - Average car - Diesel",
            "Average car - Petrol",
            "HGV (all diesel) - All HGV - Average laden",
            "Average van - Diesel",
            "Average van - Petrol",
            "Average motorbike"
        ],
        "Conversion Factor": [
            average_local_bus_factor,
            average_car_diesel_factor,
            average_car_petrol_factor,
            hgv_diesel_factor,
            average_vans_diesel_factor,
            average_vans_petrol_factor,
            average_motorbike_factor
        ],
        "Units": [
            "kgCO2e/passenger.km",
            "kgCO2e/vehicle.km",
            "kgCO2e/vehicle.km",
            "kgCO2e/tonne.km",
            "kgCO2e/km",
            "kgCO2e/km",
            "kgCO2e/km"
        ]
    })
    #petrol_emission_factor_kwh
    return (
        average_car_diesel_factor,
        average_car_petrol_factor,
        average_local_bus_factor,
        average_motorbike_factor,
        average_vans_diesel_factor,
        average_vans_petrol_factor,
        hgv_diesel_factor,
    )


@app.cell
def _(mo):
    mo.md(r"""## 5b. Calculate Operations (per road and vehicle type)""")
    return


@app.cell
def _(
    average_car_diesel_factor,
    average_car_petrol_factor,
    average_local_bus_factor,
    average_motorbike_factor,
    average_vans_diesel_factor,
    average_vans_petrol_factor,
    hgv_diesel_factor,
    subnational_road_transport_emissions,
):

    def calculate_operations_per_vehicle_type():
        # Create copy of dataframe
        subnational_road_transport_operations = subnational_road_transport_emissions.copy()
        subnational_road_transport_operations.columns = ["Operations (km)"]

        vehicel_types = ['Buses - \nMotorways', 'Buses - \nA roads', 'Buses - \nMinor roads',
               'Buses total', 'Diesel cars - \nMotorways', 'Diesel cars - \nA roads',
               'Diesel cars - \nMinor roads', 'Diesel cars total',
               'Petrol cars - \nMotorways', 'Petrol cars - \nA roads',
               'Petrol cars - \nMinor roads', 'Petrol cars total',
               'Motorcycles - \nMotorways', 'Motorcycles - \nA roads',
               'Motorcycles - \nMinor roads', 'Motorcycles total',
               'Diesel HGV - Motorways', 'Diesel HGV - A roads',
               'Diesel HGV - Minor roads', 'Diesel HGV total',
               'Natural Gas HGV - Motorways', 'Natural Gas HGV - A roads',
               'Natural Gas HGV - Minor roads', 'Natural Gas HGV total',
               'Diesel LGV - \nMotorways', 'Diesel LGV - \nA roads',
               'Diesel LGV - \nMinor roads', 'Diesel LGV total',
               'Petrol LGV - \nMotorways', 'Petrol LGV - \nA roads',
               'Petrol LGV - \nMinor roads', 'Petrol LGV total',
               'LPG LGV - \nMotorways', 'LPG LGV - \nA roads',
               'LPG LGV - \nMinor roads', 'LPG LGV total']

        for vehicle_type in vehicel_types:
            if vehicle_type.startswith("Buses"):
                factor = average_local_bus_factor
            elif vehicle_type.startswith("Diesel cars"):
                factor = average_car_diesel_factor
            elif vehicle_type.startswith("Petrol cars"):
                factor = average_car_petrol_factor
            elif vehicle_type.startswith("Motorcycles"):
                factor = average_motorbike_factor
            elif vehicle_type.startswith("Diesel HGV"):
                factor = hgv_diesel_factor
            elif vehicle_type.startswith("Diesel LGV"):
                factor = average_vans_diesel_factor
            elif vehicle_type.startswith("Petrol LGV"):
                factor = average_vans_petrol_factor
            subnational_road_transport_operations.loc[vehicle_type, "Operations (km)"] = subnational_road_transport_emissions.loc[vehicle_type, "Emissions (kgCO2e)"] / factor

        return subnational_road_transport_operations

    subnational_road_transport_operations = calculate_operations_per_vehicle_type()
    subnational_road_transport_operations

    return (subnational_road_transport_operations,)


@app.cell
def _(mo):
    mo.md(
        r"""
    ---

    # 6. Calculate Energy Intensity (per road and vehicle type)

    To generate energy intensity, we divide the kWh values from step
    2 by the activity data from step 5.
    """
    )
    return


@app.cell
def _(
    subnational_road_transport_fuel_consumption_kwh,
    subnational_road_transport_operations,
):
    subnational_road_transport_energy_intensity = subnational_road_transport_operations.copy()
    subnational_road_transport_energy_intensity.columns = ["Energy Intensity (kWh/km)"]
    subnational_road_transport_energy_intensity["Energy Intensity (kWh/km)"] /= subnational_road_transport_fuel_consumption_kwh["Fuel Consumption (kWh)"]
    subnational_road_transport_energy_intensity
    return (subnational_road_transport_energy_intensity,)


@app.cell
def _(mo):
    mo.md(
        r"""
    ---

    ---

    # Internal
    """
    )
    return


@app.cell
def _(BytesIO, mo, pd, requests, year_dropdown):

    def get_subnational_road_transport_fuel_consumption_dataframe(year):
        url = "https://assets.publishing.service.gov.uk/media/685a855272588f418862071f/subnational-road-transport-fuel-consumption-tables-2005-2023.xlsx"
        r = requests.get(url)
        df = pd.read_excel(BytesIO(r.content), sheet_name=year, skiprows=3)
        return df

    subnational_road_transport_fuel_consumption_dataframe = get_subnational_road_transport_fuel_consumption_dataframe(year_dropdown.value)

    mo.md("## Fetch: UK road transport energy consumption at regional and local authority level, 2005 to 2023")

    return (subnational_road_transport_fuel_consumption_dataframe,)


@app.cell
def _(BytesIO, mo, pd, requests):

    def get_conversion_factors_2025():
        url = "https://assets.publishing.service.gov.uk/media/6846b6ea57f3515d9611f0dd/ghg-conversion-factors-2025-flat-format.xlsx"
        r = requests.get(url)
        df = pd.read_excel(BytesIO(r.content), sheet_name="Factors by Category", skiprows=5)
        return df 

    conversion_factors = get_conversion_factors_2025()
    mo.md("## Fetch: Greenhouse gas reporting: conversion factors 2025")

    return (conversion_factors,)


@app.cell
def _(
    diesel_emission_factor_kwh,
    json,
    local_authority_dropdown,
    mo,
    petrol_emission_factor_kwh,
    subnational_road_transport_energy_intensity,
    subnational_road_transport_operations,
    year_dropdown,
):
    def get_operations(fuel_type):
        return subnational_road_transport_operations.loc[fuel_type, "Operations (km)"]

    def get_energy_intensity(fuel_type):
        return subnational_road_transport_energy_intensity.loc[fuel_type, "Energy Intensity (kWh/km)"]

    parameter_data = {
        "year": year_dropdown.value,
        "local_authority": local_authority_dropdown.value,
        "values": {
            "stock_buses_diesel": get_operations("Buses total"),
            "stock_personal_vehicles_diesel": get_operations("Diesel cars total"),
            "stock_freight_heavy_trucks_diesel": get_operations("Diesel HGV total"),
            "stock_freight_light_trucks_diesel": get_operations("Diesel LGV total"),
            "stock_personal_vehicles_petrol": get_operations("Petrol cars total"),
            "stock_motorcycles_petrol": get_operations("Motorcycles total"),
            "stock_freight_light_trucks_petrol": get_operations("Petrol LGV total"),
            "energy_intensity_buses_diesel": get_energy_intensity("Buses total"),
            "energy_intensity_personal_vehicles_diesel": get_energy_intensity("Diesel cars total"),
            "energy_intensity_freight_heavy_trucks_diesel": get_energy_intensity("Diesel HGV total"),
            "energy_intensity_freight_light_trucks_diesel": get_energy_intensity("Diesel LGV total"),
            "energy_intensity_personal_vehicles_petrol": get_energy_intensity("Petrol cars total"),
            "energy_intensity_motorcycles_petrol": get_energy_intensity("Motorcycles total"),
            "energy_intensity_freight_light_trucks_petrol": get_energy_intensity("Petrol LGV total"),
            "emission_factor_diesel_kwh_to_co2e": diesel_emission_factor_kwh,
            "emission_factor_petrol_kwh_to_co2e": petrol_emission_factor_kwh    
        }
    }

    print(json.dumps(parameter_data, indent=2))
    mo.md("## Output to console")
    return


@app.cell
def _():
    import requests
    import json
    import pandas as pd
    import pyarrow
    from io import BytesIO
    return BytesIO, json, pd, requests


@app.cell
def _():
    # Set up argument parser for running from command line
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", default="2023")
    parser.add_argument("--city", default="Scotland total")
    args, _ = parser.parse_known_args()
    return (args,)


if __name__ == "__main__":
    app.run()
