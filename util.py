import requests
import json
import pandas as pd
from cache_manager import CBSCacheManager


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
    "2451 kg en meer": "2451 kg and above",
    
    # 85236NED - Motor vehicles by type and region dataset
    "Regio's": "Regions",
    "Period": "Period",
    "Totaal wegvoertuigen": "Total Road Vehicles",
    "Totaal bedrijfsvoertuigen": "Total Commercial Vehicles",
    "Totaal bedrijfsmotorvoertuigen": "Total Commercial Motor Vehicles",
    "Totaal aanhangwagens en opleggers": "Total Trailers and Semi-trailers",
    "Motorfiets": "Motorcycle",
    "Alle voertuigen met bromfietskenteken": "All Moped-licensed Vehicles"
}

def translate(src):
    return translations.get(src, src)


# Initialize global cache manager
_cache_manager = CBSCacheManager()


def get_cbs_url(u, force_refresh=False, use_cache=True):
    """
    Fetch CBS OData URL with intelligent caching.
    
    Args:
        u: CBS OData URL to fetch
        force_refresh: If True, bypass cache and fetch fresh data
        use_cache: If False, disable caching entirely (for debugging)
    
    Returns:
        pandas.DataFrame: Processed CBS data
    """
    if use_cache:
        # Try to get data from cache first
        cached_df = _cache_manager.get_cached_data(u, force_refresh=force_refresh)
        if cached_df is not None:
            print(f"Loaded from cache: {u}")
            return cached_df
        
        print(f"Cache miss, fetching from API: {u}")
    
    # Fetch from API
    try:
        df = pd.read_json(u)
        expanded_df = df
        expanded_df = expanded_df.join(pd.DataFrame(expanded_df.pop("value").values.tolist()))
        
        # Remove the "odata.metadata" column:
        if "odata.metadata" in expanded_df.columns:
            expanded_df = expanded_df.drop(columns=["odata.metadata"])
        
        # Save to cache if caching is enabled
        if use_cache:
            _cache_manager.save_data_to_cache(u, expanded_df)
        
        return expanded_df
        
    except Exception as e:
        print(f"Error fetching data from {u}: {e}")
        # Try to return stale cached data as fallback
        if use_cache:
            cached_df = _cache_manager.get_cached_data(u, force_refresh=False)
            if cached_df is not None:
                print(f"Using stale cached data as fallback: {u}")
                return cached_df
        raise


def invalidate_cache(url=None):
    """
    Invalidate cache for specific dataset or all cached data.
    
    Args:
        url: CBS dataset URL to invalidate, or None to invalidate all
    """
    _cache_manager.invalidate_cache(url)


def get_cache_stats():
    """Get cache statistics."""
    return _cache_manager.get_cache_stats()


def cleanup_fragmented_cache(dataset_id=None):
    """
    Clean up fragmented cache files from paginated requests.
    
    Args:
        dataset_id: Optional dataset ID to clean, or None to clean all
    
    Returns:
        Number of files cleaned up
    """
    return _cache_manager.cleanup_fragmented_cache(dataset_id)


def get_cbs_url_paginated(base_url, page_size=5000, use_cache=True, force_refresh=False):
    """
    Fetch complete CBS dataset using pagination with intelligent aggregate caching.
    
    Args:
        base_url: Base CBS OData URL without pagination parameters
        page_size: Records per page (default 5000)
        use_cache: Whether to use caching (default True)
        force_refresh: Force refresh even if cached (default False)
    
    Returns:
        Complete pandas.DataFrame with all records
    """
    if use_cache:
        # Check if we have a complete cached dataset
        # For paginated requests, we use the base URL for cache lookup
        cached_df = _cache_manager.get_cached_data(base_url, force_refresh=force_refresh)
        if cached_df is not None:
            print(f"Loaded complete dataset from cache: {base_url}")
            return cached_df
        
        print(f"Cache miss, fetching complete paginated dataset: {base_url}")

    # Fetch data using pagination
    skip = 0
    all_data = []
    
    while True:
        paged_url = f"{base_url}?$top={page_size}&$skip={skip}"
        try:
            # For individual pages, disable caching to avoid fragment storage
            page_df = get_cbs_url(paged_url, use_cache=False, force_refresh=True)
            if page_df.empty or len(page_df) == 0:
                break  # No more data
            
            all_data.append(page_df)
            skip += page_size
            print(f"Fetched {len(page_df)} records (total so far: {skip})")
            
            # If we got fewer records than page_size, we've reached the end
            if len(page_df) < page_size:
                break
                
        except Exception as e:
            print(f"Error fetching page at skip={skip}: {e}")
            break
    
    if all_data:
        # Combine all pages into a single DataFrame
        import pandas as pd
        complete_df = pd.concat(all_data, ignore_index=True)
        print(f"Total records fetched: {len(complete_df)}")
        
        # Save complete dataset to cache using clean key
        if use_cache:
            _cache_manager.save_aggregated_data_to_cache(base_url, complete_df)
        
        return complete_df
    else:
        # Fallback to empty DataFrame
        import pandas as pd
        return pd.DataFrame()
