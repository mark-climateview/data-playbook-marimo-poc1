import pandas as pd
from pathlib import Path
from typing import Optional, List, Dict, Any
import requests
import time

try:
    import marimo as mo
    _MARIMO_AVAILABLE = True
except ImportError:
    _MARIMO_AVAILABLE = False


# Cloud detection - set to False when running locally
CLOUD = True

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
    "ID": "ID",
    "Regio's": "Regions",
    "Totaal wegvoertuigen": "Total Road Vehicles",
    "Personenauto": "Passenger Car",
    "Totaal bedrijfsvoertuigen": "Total Commercial Vehicles",
    "Totaal bedrijfsmotorvoertuigen": "Total Commercial Motor Vehicles",
    "Bestelauto": "Delivery Van",
    "Vrachtauto (excl. trekker voor oplegger)": "Truck (excl. tractor for semi-trailer)",
    "Trekker voor oplegger": "Tractor for semi-trailer",
    "Speciaal voertuig": "Special vehicle",
    "Bus": "Bus",
    "Totaal aanhangwagens en opleggers": "Total Trailers and Semi-trailers",
    "Aanhangwagen": "Trailer",
    "Oplegger": "Semi-trailer",
    "Motorfiets": "Motorcycle",
    "Alle voertuigen met bromfietskenteken": "All Moped-licensed Vehicles",
    "Snorfiets": "Light moped",
    "Bromfiets": "Moped",
    "Brommobiel": "Moped car",
    "Overige voertuigen met bromfietskenteken": "Other moped-licensed vehicles",
    "Landsdeel": "Region",
    "Provincie": "Province",
    "Coropgebied": "COROP area",
    "Gemeentecode": "Municipality code",
    "Naam": "Name",
    "Gemeente grootteklasse": "Municipality size class",
    "Stedelijkheid van gemeenten": "Urbanization of municipalities"
}


def translate(src):
    """Translate Dutch terms to English using the translations dictionary."""
    return translations.get(src, src)


def is_running_in_cloud() -> bool:
    """
    Detect if the notebook is running in Marimo Community Cloud (WASM) vs locally.
    
    Returns:
        bool: True if running in cloud/WASM environment, False if running locally
    """
    if not _MARIMO_AVAILABLE:
        return False
    
    try:
        # Get the notebook directory/location
        notebook_dir = mo.notebook_dir()
        
        # Convert to string to check if it's a URL
        notebook_dir_str = str(notebook_dir)
        
        # Cloud/WASM environments return URLs, local environments return filesystem paths
        return notebook_dir_str.startswith(('http://', 'https://'))
    except:
        return False


def get_execution_environment() -> Dict[str, Any]:
    """
    Get detailed information about the current execution environment.
    
    Returns:
        Dict with environment details including:
        - is_cloud: Whether running in cloud/WASM
        - is_local: Whether running locally
        - marimo_available: Whether marimo is available
        - notebook_dir: The notebook directory/URL
        - notebook_location: The notebook location (if available)
    """
    env_info = {
        'marimo_available': _MARIMO_AVAILABLE,
        'is_cloud': False,
        'is_local': True,
        'notebook_dir': None,
        'notebook_location': None
    }
    
    if _MARIMO_AVAILABLE:
        try:
            # Get notebook directory
            notebook_dir = mo.notebook_dir()
            env_info['notebook_dir'] = str(notebook_dir)
            
            # Try to get notebook location if available
            try:
                notebook_location = mo.notebook_location()
                env_info['notebook_location'] = str(notebook_location)
            except:
                env_info['notebook_location'] = env_info['notebook_dir']
            
            # Detect cloud vs local based on URL
            is_cloud = str(notebook_dir).startswith(('http://', 'https://'))
            env_info['is_cloud'] = is_cloud
            env_info['is_local'] = not is_cloud
            
        except Exception as e:
            env_info['error'] = str(e)
    
    return env_info


def get_environment_info() -> str:
    """
    Get a human-readable summary of the current execution environment.
    
    Returns:
        str: Formatted environment information
    """
    env = get_execution_environment()
    
    if not env['marimo_available']:
        return "Environment: Not running in Marimo"
    
    if env['is_cloud']:
        return f"Environment: Marimo Cloud/WASM (URL: {env['notebook_dir']})"
    else:
        return f"Environment: Marimo Local (Path: {env['notebook_dir']})"


def get_data_file_path(dataset_id: str, endpoint: str = "") -> Path:
    """
    Get the file path for a local data file using Marimo's notebook directory.
    
    This function uses mo.notebook_dir() to get the correct path that works
    both locally and on Marimo Community Cloud.
    
    Args:
        dataset_id: Dataset ID (e.g., "85236NED")
        endpoint: Optional endpoint name (e.g., "TypedDataSet", "Bouwjaar")
    
    Returns:
        Path: Path to the data file
    """
    # Use marimo notebook directory if available, otherwise fall back to current directory
    if _MARIMO_AVAILABLE:
        try:
            base_dir = mo.notebook_dir()
            # Debug info for cloud detection
            if str(base_dir).startswith(('http://', 'https://')):
                # Running in cloud/WASM environment
                pass  # Could add logging here if needed
        except:
            base_dir = Path.cwd()
    else:
        base_dir = Path.cwd()
    
    # Construct filename
    if endpoint:
        filename = f"{dataset_id}_{endpoint}.parquet"
    else:
        filename = f"{dataset_id}.parquet"
    
    return base_dir / "data" / filename


def get_local_data(dataset_id: str, endpoint: str = "") -> pd.DataFrame:
    """
    Load data from local data folder or GitHub Pages (when running in cloud).
    
    This is the recommended way to load CBS data that works both locally
    and on Marimo Community Cloud. When running locally, it loads from the
    local data/ folder. When running in the cloud, it loads from GitHub Pages.
    
    Args:
        dataset_id: Dataset ID (e.g., "85236NED")
        endpoint: Optional endpoint name (e.g., "TypedDataSet", "Bouwjaar")
                 If empty, loads the base dataset metadata
    
    Returns:
        pandas.DataFrame: The loaded data
    
    Raises:
        FileNotFoundError: If the data file doesn't exist
        Exception: If there's an error loading the data
    """
    # Check if we're running in the cloud
    if CLOUD:
        return get_cloud_data(dataset_id, endpoint)
    else:
        return get_local_data_file(dataset_id, endpoint)


def get_local_data_file(dataset_id: str, endpoint: str = "") -> pd.DataFrame:
    """
    Load data from local data folder (local execution only).
    
    Args:
        dataset_id: Dataset ID (e.g., "85236NED")
        endpoint: Optional endpoint name (e.g., "TypedDataSet", "Bouwjaar")
    
    Returns:
        pandas.DataFrame: The loaded data
    """
    data_file = get_data_file_path(dataset_id, endpoint)
    
    if not data_file.exists():
        raise FileNotFoundError(
            f"Data file not found: {data_file}\n"
            f"Please run 'uv run data_fetcher.py' to fetch the data first."
        )
    
    try:
        df = pd.read_parquet(data_file)
        print(f"Loaded from local data: {data_file.name} ({len(df)} records)")
        return df
    except Exception as e:
        raise Exception(f"Error loading data from {data_file}: {e}")


def get_cloud_data(dataset_id: str, endpoint: str = "", 
                   base_url: str = "https://mark-climateview.github.io/data-playbook-marimo-poc1/data/") -> pd.DataFrame:
    """
    Load data from GitHub Pages (cloud execution only).
    
    Args:
        dataset_id: Dataset ID (e.g., "85236NED")
        endpoint: Optional endpoint name (e.g., "TypedDataSet", "Bouwjaar")
        base_url: Base URL for the GitHub Pages data hosting
    
    Returns:
        pandas.DataFrame: The loaded data
    """
    # Construct filename
    if endpoint:
        filename = f"{dataset_id}_{endpoint}.parquet"
    else:
        filename = f"{dataset_id}.parquet"
    
    # Construct full URL
    data_url = f"{base_url}{filename}"
    
    try:
        print(f"Loading from GitHub Pages: {data_url}")
        df = pd.read_parquet(data_url)
        print(f"Loaded from cloud data: {filename} ({len(df)} records)")
        return df
    except Exception as e:
        raise Exception(f"Error loading data from {data_url}: {e}")


def list_available_data() -> List[Dict[str, Any]]:
    """
    List all available data files (local or cloud).
    
    Returns:
        List of available data files with their sizes and environment info
    """
    if CLOUD:
        return list_cloud_data()
    else:
        return list_local_data()


def list_local_data() -> List[Dict[str, Any]]:
    """
    List all available data files in the local data folder.
    
    Returns:
        List of available data files with their sizes and environment info
    """
    # Use marimo notebook directory if available
    if _MARIMO_AVAILABLE:
        try:
            base_dir = mo.notebook_dir()
        except:
            base_dir = Path.cwd()
    else:
        base_dir = Path.cwd()
    
    data_dir = base_dir / "data"
    
    if not data_dir.exists():
        return []
    
    files = []
    for parquet_file in data_dir.glob("*.parquet"):
        size_mb = parquet_file.stat().st_size / (1024 * 1024)
        files.append({
            "filename": parquet_file.name,
            "size_mb": round(size_mb, 2),
            "path": str(parquet_file),
            "environment": get_environment_info()
        })
    
    return sorted(files, key=lambda x: x["filename"])


def list_cloud_data(base_url: str = "https://mark-climateview.github.io/data-playbook-marimo-poc1/data/") -> List[Dict[str, Any]]:
    """
    List available data files from GitHub Pages (cloud execution only).
    
    Note: This function attempts to check common dataset files since we can't
    easily list directory contents from GitHub Pages.
    
    Args:
        base_url: Base URL for the GitHub Pages data hosting
    
    Returns:
        List of available data files with environment info
    """
    # Common datasets to check
    common_datasets = [
        "85236NED",
        "85237NED", 
        "85405NED"
    ]
    
    # Common endpoints to check
    common_endpoints = ["", "DataProperties", "Perioden", "TypedDataSet", "Bouwjaar"]
    
    files = []
    for dataset in common_datasets:
        for endpoint in common_endpoints:
            if endpoint:
                filename = f"{dataset}_{endpoint}.parquet"
            else:
                filename = f"{dataset}.parquet"
            
            data_url = f"{base_url}{filename}"
            
            # Try to check if file exists (quick HEAD request)
            try:
                response = requests.head(data_url, timeout=5)
                if response.status_code == 200:
                    content_length = response.headers.get('Content-Length', '0')
                    size_mb = int(content_length) / (1024 * 1024) if content_length.isdigit() else 0
                    files.append({
                        "filename": filename,
                        "size_mb": round(size_mb, 2),
                        "path": data_url,
                        "environment": get_environment_info()
                    })
            except:
                # File doesn't exist or network error, skip
                pass
    
    return sorted(files, key=lambda x: x["filename"])


def get_cbs_url(url: str, force_refresh: bool = False) -> pd.DataFrame:
    """
    Fetch data from CBS API URL and return as DataFrame.
    
    Args:
        url: CBS OData API URL
        force_refresh: Whether to ignore cache (not used in this simple implementation)
    
    Returns:
        pandas.DataFrame: The fetched data
    """
    try:
        print(f"Fetching: {url}")
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        
        data = response.json()
        if 'value' in data:
            return pd.DataFrame(data['value'])
        else:
            return pd.DataFrame(data)
            
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return pd.DataFrame()


def get_cbs_url_paginated(url: str, force_refresh: bool = False, max_pages: int = 100, page_size: int = 5000) -> pd.DataFrame:
    """
    Fetch paginated data from CBS API URL and return as DataFrame.
    
    Args:
        url: CBS OData API URL
        force_refresh: Whether to ignore cache (not used in this simple implementation)
        max_pages: Maximum number of pages to fetch
        page_size: Number of records per page (max 10000, recommended 5000)
    
    Returns:
        pandas.DataFrame: The combined paginated data
    """
    all_data = []
    page_count = 0
    skip = 0
    
    try:
        while page_count < max_pages:
            # Add OData pagination parameters
            separator = '&' if '?' in url else '?'
            current_url = f"{url}{separator}$skip={skip}&$top={page_size}"
            
            print(f"Fetching page {page_count + 1}: {current_url}")
            response = requests.get(current_url, timeout=60)
            response.raise_for_status()
            
            data = response.json()
            
            if 'value' in data and data['value']:
                page_data = data['value']
                all_data.extend(page_data)
                page_count += 1
                skip += len(page_data)
                
                # If we got fewer records than requested, we've reached the end
                if len(page_data) < page_size:
                    break
                
                # Small delay between requests
                time.sleep(0.5)
            else:
                break
        
        if all_data:
            print(f"Fetched {len(all_data)} total records across {page_count} pages")
            return pd.DataFrame(all_data)
        else:
            print("No data found")
            return pd.DataFrame()
            
    except Exception as e:
        print(f"Error fetching paginated data from {url}: {e}")
        if all_data:
            print(f"Returning partial data: {len(all_data)} records")
            return pd.DataFrame(all_data)
        return pd.DataFrame()


def get_cache_stats() -> Dict[str, Any]:
    """
    Get cache statistics (simplified for compatibility).
    
    Returns:
        Dict with basic cache info
    """
    data_dir = Path.cwd() / "data"
    if data_dir.exists():
        files = list(data_dir.glob("*.parquet"))
        total_size = sum(f.stat().st_size for f in files) / (1024 * 1024)
        return {
            "cache_dir": str(data_dir),
            "total_size_mb": round(total_size, 2),
            "file_count": len(files)
        }
    else:
        return {
            "cache_dir": str(data_dir),
            "total_size_mb": 0,
            "file_count": 0
        }


def check_data_availability(dataset_id: str, endpoints: Optional[List[str]] = None) -> Dict[str, Dict[str, Any]]:
    """
    Check which data files are available for a dataset (local or cloud).
    
    Args:
        dataset_id: Dataset ID to check
        endpoints: List of endpoints to check, or None to check common ones
    
    Returns:
        Dict with availability status for each endpoint and environment info
    """
    if endpoints is None:
        # Common endpoints to check
        endpoints = ["", "DataProperties", "Perioden", "TypedDataSet"]
    
    if CLOUD:
        return check_cloud_data_availability(dataset_id, endpoints)
    else:
        return check_local_data_availability(dataset_id, endpoints)


def check_local_data_availability(dataset_id: str, endpoints: List[str]) -> Dict[str, Dict[str, Any]]:
    """
    Check which local data files are available for a dataset.
    
    Args:
        dataset_id: Dataset ID to check
        endpoints: List of endpoints to check
    
    Returns:
        Dict with availability status for each endpoint and environment info
    """
    results = {}
    env_info = get_execution_environment()
    
    for endpoint in endpoints:
        data_file = get_data_file_path(dataset_id, endpoint)
        results[endpoint if endpoint else "metadata"] = {
            "available": data_file.exists(),
            "path": str(data_file),
            "size_mb": round(data_file.stat().st_size / (1024 * 1024), 2) if data_file.exists() else 0,
            "environment": env_info
        }
    
    return results


def check_cloud_data_availability(dataset_id: str, endpoints: List[str], 
                                  base_url: str = "https://mark-climateview.github.io/data-playbook-marimo-poc1/data/") -> Dict[str, Dict[str, Any]]:
    """
    Check which cloud data files are available for a dataset.
    
    Args:
        dataset_id: Dataset ID to check
        endpoints: List of endpoints to check
        base_url: Base URL for the GitHub Pages data hosting
    
    Returns:
        Dict with availability status for each endpoint and environment info
    """
    results = {}
    env_info = get_execution_environment()
    
    for endpoint in endpoints:
        if endpoint:
            filename = f"{dataset_id}_{endpoint}.parquet"
        else:
            filename = f"{dataset_id}.parquet"
        
        data_url = f"{base_url}{filename}"
        
        # Try to check if file exists (quick HEAD request)
        try:
            response = requests.head(data_url, timeout=5)
            available = response.status_code == 200
            content_length = response.headers.get('Content-Length', '0')
            size_mb = int(content_length) / (1024 * 1024) if content_length.isdigit() else 0
        except:
            available = False
            size_mb = 0
        
        results[endpoint if endpoint else "metadata"] = {
            "available": available,
            "path": data_url,
            "size_mb": round(size_mb, 2),
            "environment": env_info
        }
    
    return results