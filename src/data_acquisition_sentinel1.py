import os
import json
from shapely.geometry import shape
import asf_search as asf

def download_sentinel1(
        aoi_geojson_path: str,
        output_directory: str,
        start_date: str,
        end_date: str,
        orbit_direction: str = "ASC",
        max_results: int = 5):
    """
    Safe Sentinel-1 downloader.

    Parameters:
        aoi_geojson_path : Path to AOI GeoJSON file
        output_directory : Directory to download products
        start_date       : Start date (YYYY-MM-DD)
        end_date         : End date (YYYY-MM-DD)
        orbit_direction  : "ASC" or "DESC"
        max_results      : Maximum number of products
    """

    # 1. Load AOI GeoJSON → WKT
    with open(aoi_geojson_path, 'r') as f:
        geojson_data = json.load(f)

    if geojson_data.get('type') == 'FeatureCollection':
        geometry_dict = geojson_data['features'][0]['geometry']
    else:
        geometry_dict = geojson_data['geometry']

    geometry_wkt = shape(geometry_dict).wkt
    print(f"[INFO] Loaded AOI: {aoi_geojson_path}")

    # 2. Authenticate using environment variables (SAFE)
    username = os.getenv("ASF_USERNAME")
    password = os.getenv("ASF_PASSWORD")

    if not username or not password:
        raise ValueError("Environment variables ASF_USERNAME and ASF_PASSWORD not set.")

    session = asf.ASFSession().auth_with_creds(username, password)
    print("[INFO] Authentication successful")

    # 3. Orbit filter
    flight_dir = (asf.FLIGHT_DIRECTION.ASCENDING
                  if orbit_direction.upper() == "ASC"
                  else asf.FLIGHT_DIRECTION.DESCENDING)

    # 4. Search Sentinel-1 products
    results = asf.search(
        platform=asf.PLATFORM.SENTINEL1,
        processingLevel=asf.PRODUCT_TYPE.GRD_HD,
        start=start_date,
        end=end_date,
        intersectsWith=geometry_wkt,
        beamMode=asf.BEAMMODE.IW,
        flightDirection=flight_dir,
        maxResults=max_results
    )

    print(f"[INFO] Found {len(results)} products ({orbit_direction.upper()})")

    # 5. Download results
    os.makedirs(output_directory, exist_ok=True)

    for product in results:
        try:
            product.download(path=output_directory, session=session)
            print(f"[OK] Downloaded: {product.properties['fileName']}")
        except Exception as e:
            print(f"[ERROR] Failed: {product.properties['fileName']} | {e}")

    print(f"[DONE] All downloads saved at: {output_directory}")


# --------- USAGE EXAMPLE (Remove or modify as needed) ---------

if __name__ == "__main__":
    """
    Before running this script, set environment variables:
        export ASF_USERNAME="your_username"
        export ASF_PASSWORD="your_password"
    """

    download_sentinel1(
        aoi_geojson_path="path/to/your/aoi.geojson",
        output_directory="path/to/download/folder",
        start_date="2025-10-01",
        end_date="2025-10-31",
        orbit_direction="ASC",
        max_results=5
    )
