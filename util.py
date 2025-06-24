import requests
import json
import pandas as pd


# From Dutch to English translations for vehicle data
translations = {
    # Common terms
    "Totaal": "Total",
    "Overig": "Other",
    "Perioden": "Period",
    "Definitief": "Final",
    
    # 85405NED - Vehicle kilometers dataset
    "Benzine/benzine hybride/ethanol": "Petrol / Petrol Hybrids / Ethanol",
    "Diesel/diesel hybrides":"Diesel / Diesel Hybrids",
    "Full elektrisch/waterstof": "Battery Electric / Hydrogen",
    "LPG/ LPG hybrides": "LPG / LPG Hybrids",
    "CNG/CNG hybrides/LNG": "CNG / CNG Hybrids / LNG",
    "LeeftijdVoertuig": "Vehicle Age",
    "BrandstofsoortVoertuig": "Fuel Type",
    "GemiddeldJaarkilometrage_2": "Average Annual Mileage",
    "KilometersNederlandsePersonenautoS_1": "Vehicle Kilometers in NL",
    "NederlandsePersonenautoSInGebruik_3": "Vehicles in Use in NL",
    
    # 85237NED - Active passenger cars dataset
    "Bouwjaar": "Construction Year",
    "TotaalNederland": "Total Netherlands",
    
    # Construction year categories
    "Tot 1910": "Up to 1910",
    "1910 tot 1920": "1910 to 1920",
    "1920 tot 1930": "1920 to 1930",
    "1930 tot 1940": "1930 to 1940",
    "1940 tot 1950": "1940 to 1950",
    "1950 tot 1960": "1950 to 1960",
    "1960 tot 1970": "1960 to 1970",
    "1970 tot 1980": "1970 to 1980",
    "1980 tot 1990": "1980 to 1990",
    "1990 tot 2000": "1990 to 2000",
    "2000 tot 2010": "2000 to 2010",
    "2010 tot 2020": "2010 to 2020",
    "Vanaf 2020": "From 2020 onwards",
    "Totaal alle bouwjaren": "Total all construction years",
    "Groepen van bouwjaren": "Groups of construction years",
    "Afzonderlijke bouwjaren naar klasse": "Individual construction years by class",
    
    # Fuel types
    "Benzine": "Gasoline",
    "Diesel": "Diesel",
    "LPG": "LPG",
    "Elektriciteit": "Electricity",
    "CNG": "CNG",
    "OverigOnbekend": "Other/Unknown",
    
    # Age groups (coded versions)
    "18Tot20Jaar": "18 to 20 years",
    "20Tot25Jaar": "20 to 25 years",
    "25Tot30Jaar": "25 to 30 years",
    "30Tot40Jaar": "30 to 40 years",
    "40Tot50Jaar": "40 to 50 years",
    "50Tot60Jaar": "50 to 60 years",
    "60Tot65Jaar": "60 to 65 years",
    "65JaarEnOuder": "65 years and older",
    
    # Age groups (text versions from DataProperties)
    "18 tot 20 jaar": "18 to 20 years",
    "20 tot 25 jaar": "20 to 25 years", 
    "25 tot 30 jaar": "25 to 30 years",
    "30 tot 40 jaar": "30 to 40 years",
    "40 tot 50 jaar": "40 to 50 years",
    "50 tot 60 jaar": "50 to 60 years",
    "60 tot 65 jaar": "60 to 65 years",
    "65 jaar en ouder": "65 years and older",
    
    # Vehicle colors
    "Beige": "Beige",
    "Blauw": "Blue",
    "Bruin": "Brown",
    "Creme": "Cream",
    "Geel": "Yellow",
    "Grijs": "Gray",
    "Groen": "Green",
    "Oranje": "Orange",
    "Paars": "Purple",
    "Rood": "Red",
    "Roze": "Pink",
    "Wit": "White",
    "Zwart": "Black",
    "OverigeKleuren": "Other Colors",
    
    # Topic categories
    "Personenauto's per provincie": "Passenger cars per province",
    "Brandstofsoort van personenauto's": "Fuel type of passenger cars",
    "Eigendom personenauto's": "Ownership of passenger cars",
    "Op naam particulieren, naar leeftijd": "Owned by individuals, by age",
    "Klasse van leeggewicht": "Empty weight class",
    "Meest voorkomende kleuren": "Most common colors",
    
    # Units
    "aantal": "number",
    
    # Dutch provinces
    "Groningen": "Groningen",
    "Fryslân": "Friesland", 
    "Drenthe": "Drenthe",
    "Overijssel": "Overijssel",
    "Flevoland": "Flevoland",
    "Gelderland": "Gelderland",
    "Utrecht": "Utrecht",
    "Noord-Holland": "North Holland",
    "Zuid-Holland": "South Holland",
    "Zeeland": "Zeeland",
    "Noord-Brabant": "North Brabant",
    "Limburg": "Limburg",
    
    # Additional fuel type variants
    "Overig/Onbekend": "Other/Unknown",
    
    # Additional color variants
    "Overige kleuren": "Other colors",
    
    # Ownership types
    "Op naam bedrijf": "Registered to company",
    "Particulieren totaal": "Private individuals total",
    
    # Construction year groupings
    "Bouwjaren tot 1910": "Construction years up to 1910",
    "Bouwjaren 1910 tot 1920": "Construction years 1910 to 1920",
    "Bouwjaren 1920 tot 1930": "Construction years 1920 to 1930",
    "Bouwjaren 1930 tot 1940": "Construction years 1930 to 1940",
    "Bouwjaren 1940 tot 1950": "Construction years 1940 to 1950",
    "Bouwjaren 1950 tot 1960": "Construction years 1950 to 1960",
    "Bouwjaren 1960 tot 1970": "Construction years 1960 to 1970",
    "Bouwjaren 1970 tot 1980": "Construction years 1970 to 1980",
    "Bouwjaren 1980 tot 1990": "Construction years 1980 to 1990",
    "Bouwjaren 1990 tot 2000": "Construction years 1990 to 2000",
    "Bouwjaren 2000 tot 2010": "Construction years 2000 to 2010",
    "Bouwjaren 2010 tot 2020": "Construction years 2010 to 2020",
    "Bouwjaren vanaf 2020": "Construction years from 2020 onwards",
    
    # Weight ranges
    "0-450 kg": "0-450 kg",
    "451-550 kg": "451-550 kg",
    "551-650 kg": "551-650 kg",
    "651-750 kg": "651-750 kg",
    "751-850 kg": "751-850 kg",
    "851-950 kg": "851-950 kg",
    "951-1050 kg": "951-1050 kg",
    "1051-1150 kg": "1051-1150 kg",
    "1151-1250 kg": "1151-1250 kg",
    "1251-1350 kg": "1251-1350 kg",
    "1351-1450 kg": "1351-1450 kg",
    "1451-1550 kg": "1451-1550 kg",
    "1551-1650 kg": "1551-1650 kg",
    "1651-1750 kg": "1651-1750 kg",
    "1751-1850 kg": "1751-1850 kg",
    "1851-1950 kg": "1851-1950 kg",
    "1951-2050 kg": "1951-2050 kg",
    "2051-2150 kg": "2051-2150 kg",
    "2151-2250 kg": "2151-2250 kg",
    "2251-2350 kg": "2251-2350 kg",
    "2351-2450 kg": "2351-2450 kg",
    "2451 kg en meer": "2451 kg and above"
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
