from datetime import datetime
import requests
import pandas as pd
import geopandas as gpd
from shapely.geometry import shape
import os
import json


# ------------------------------------------------------------
# Step 0: Configuration (replace with your own folders)
# ------------------------------------------------------------

pre_output_dir = r"path/to/pre_output"
post_output_dir = r"path/to/post_output"
roi_file = r"path/to/roi_file.geojson"

# Create output folders
os.makedirs(pre_output_dir, exist_ok=True)
os.makedirs(post_output_dir, exist_ok=True)

# Choose collection
DATA_COLLECTION = "SENTINEL-2"

# Date ranges (YYYY-MM-DD)
PRE_START  = "2025-10-08"
PRE_END    = "2025-10-10"
POST_START = "2025-10-11"
POST_END   = "2025-10-13"


# ------------------------------------------------------------
# Step 1: Load AOI and convert to WKT
# ------------------------------------------------------------
with open(roi_file) as f:
    roi_geojson = json.load(f)

geom = shape(roi_geojson["features"][0]["geometry"])
roi_wkt = geom.wkt
print(f"[INFO] ROI loaded")


# ------------------------------------------------------------
# Step 2: Load credentials from environment variables
# ------------------------------------------------------------
CDSE_USERNAME = os.getenv("CDSE_USERNAME")
CDSE_PASSWORD = os.getenv("CDSE_PASSWORD")

if not CDSE_USERNAME or not CDSE_PASSWORD:
    raise ValueError("Environment variables CDSE_USERNAME and CDSE_PASSWORD must be set.")


# ------------------------------------------------------------
# Step 3: Keycloak Authentication
# ------------------------------------------------------------
def get_keycloak_token(username: str, password: str) -> str:
    data = {
        "client_id": "cdse-public",
        "username": username,
        "password": password,
        "grant_type": "password",
    }

    r = requests.post(
        "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token",
        data=data
    )
    r.raise_for_status()

    return r.json()["access_token"]


# ------------------------------------------------------------
# Step 4: Sentinel-2 download function
# ------------------------------------------------------------
def download_s2(start_date, end_date, save_folder):

    start_iso = pd.to_datetime(start_date).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    end_iso   = pd.to_datetime(end_date).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    # CDSE OData query
    query_url = (
        f"https://catalogue.dataspace.copernicus.eu/odata/v1/Products"
        f"?$filter=Collection/Name eq '{DATA_COLLECTION}' "
        f"and OData.CSC.Intersects(area=geography'SRID=4326;{roi_wkt}') "
        f"and ContentDate/Start ge {start_iso} "
        f"and ContentDate/Start lt {end_iso} "
        f"&$count=True&$top=1000"
    )

    token = get_keycloak_token(CDSE_USERNAME, CDSE_PASSWORD)
    session = requests.Session()
    session.headers.update({"Authorization": f"Bearer {token}"})

    resp = session.get(query_url)
    resp.raise_for_status()
    data = resp.json()

    if "value" not in data or len(data["value"]) == 0:
        print(f"[INFO] No products found between {start_date} and {end_date}.")
        return

    df = pd.DataFrame(data["value"])
    df["geometry"] = df["GeoFootprint"].apply(shape)
    gdf = gpd.GeoDataFrame(df, geometry="geometry")

    gdf["identifier"] = gdf["Name"].str.split(".").str[0]
    print(f"[INFO] Found {len(gdf)} products ({start_date} → {end_date})")

    # Download loop
    for _, row in gdf.iterrows():
        try:
            product_id = row["Id"]
            identifier = row["identifier"]

            # Step 1: Get redirect
            url = f"https://catalogue.dataspace.copernicus.eu/odata/v1/Products({product_id})/$value"
            response = session.get(url, allow_redirects=False)

            # Follow redirects
            while response.status_code in (301, 302, 303, 307):
                url = response.headers["Location"]
                response = session.get(url, allow_redirects=False)

            # Final download
            file_resp = session.get(url, allow_redirects=True)
            save_path = os.path.join(save_folder, f"{identifier}.zip")

            with open(save_path, "wb") as f:
                f.write(file_resp.content)

            print(f"[OK] Downloaded {identifier}")

        except Exception as e:
            print(f"[ERROR] Failed downloading {row['Name']}: {e}")


# ------------------------------------------------------------
# Step 5: Run downloads
# ------------------------------------------------------------
print("\n=== Downloading Pre-Event Sentinel-2 ===")
download_s2(PRE_START, PRE_END, pre_output_dir)

print("\n=== Downloading Post-Event Sentinel-2 ===")
download_s2(POST_START, POST_END, post_output_dir)

print("\n✔ Completed Sentinel-2 pre/post downloads.")
