import requests
import json
import pandas as pd


# From Dutch to English translations for vehicle data
translations = {
    "Totaal": "Total",
    "Benzine/benzine hybride/ethanol": "Petrol / Petrol Hybrids / Ethanol",
    "Diesel/diesel hybrides":"Diesel / Diesel Hybrids",
    "Full elektrisch/waterstof": "Battery Electric / Hydrogen",
    "LPG/ LPG hybrides": "LPG / LPG Hybrids",
    "CNG/CNG hybrides/LNG": "CNG / CNG Hybrids / LNG",
    "Overig": "Other",
    "LeeftijdVoertuig": "Vehicle Age",
    "BrandstofsoortVoertuig": "Fuel Type",
    "GemiddeldJaarkilometrage_2": "Average Annual Mileage",
    "KilometersNederlandsePersonenautoS_1": "Vehicle Kilometers in NL",
    "NederlandsePersonenautoSInGebruik_3": "Vehicles in Use in NL",
    "Perioden": "Period"
}

def translate(src):
    return translations.get(src, src)


def get_cbs_url(u):
    df = pd.read_json(u)
    expanded_df = df
    expanded_df = expanded_df.join(pd.DataFrame(expanded_df.pop("value").values.tolist()))
    # Remove the "odata.metadata" column:
    if "odata.metadata" in expanded_df.columns:
        expanded_df = expanded_df.drop(columns=["odata.metadata"])
    return expanded_df
