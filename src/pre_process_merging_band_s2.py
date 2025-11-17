import rasterio
import numpy as np
import os
from glob import glob
import matplotlib.pyplot as plt
from rasterio.crs import CRS


# -------------------------------------------------------
# CONFIGURATION  (replace these with your own folders)
# -------------------------------------------------------
input_folder = r"path/to/sentinel2/post_event_folder"
output_folder = r"path/to/output_folder"

# Bands to extract
bands = ["B04", "B03", "B02", "B08"]  # Red, Green, Blue, NIR

# Base output filename
base_output_file = os.path.join(output_folder, "S2_merged_RGBNIR.tif")


# -------------------------------------------------------
# CRS (example: UTM zone 41N, EPSG:32641)
# Change to your required CRS
# -------------------------------------------------------
sentinel_crs = CRS.from_proj4("+proj=utm +zone=41 +datum=WGS84 +units=m +no_defs")


# -------------------------------------------------------
# CREATE OUTPUT DIRECTORY
# -------------------------------------------------------
os.makedirs(output_folder, exist_ok=True)


# -------------------------------------------------------
# SAFE FILE VERSIONING
# -------------------------------------------------------
counter = 1
output_file = base_output_file

while os.path.exists(output_file):
    output_file = os.path.join(output_folder, f"S2_merged_RGBNIR_v{counter}.tif")
    counter += 1


# -------------------------------------------------------
# FIND BAND FILES (.tif or .jp2)
# -------------------------------------------------------
band_files = {}

for band in bands:
    tiff_search = os.path.join(input_folder, "**", f"*{band}*.tif")
    jp2_search = os.path.join(input_folder, "**", f"*{band}*.jp2")

    files = glob(tiff_search, recursive=True)
    if not files:
        files = glob(jp2_search, recursive=True)

    if not files:
        raise FileNotFoundError(f"Band {band} not found in: {input_folder}")

    band_files[band] = files[0]

print("\n[INFO] Band files located:")
for b, path in band_files.items():
    print(f"  {b}: {path}")


# -------------------------------------------------------
# READ BANDS + CHECK ALIGNMENT
# -------------------------------------------------------
arrays = []
ref_meta = None

for i, band in enumerate(bands):
    with rasterio.open(band_files[band]) as src:
        data = src.read(1)

        if i == 0:
            ref_meta = src.meta.copy()
            ref_meta.update(
                count=len(bands),
                dtype=rasterio.uint16,
                crs=sentinel_crs
            )
        else:
            if src.width != ref_meta["width"] or src.height != ref_meta["height"]:
                raise ValueError(f"[ERROR] Shape mismatch for band {band}")
            if src.transform != ref_meta["transform"]:
                raise ValueError(f"[ERROR] Transform mismatch for band {band}")

        arrays.append(data)

stacked = np.stack(arrays, axis=0)


# -------------------------------------------------------
# SAVE MERGED GEOTIFF
# -------------------------------------------------------
with rasterio.open(output_file, "w", **ref_meta) as dst:
    dst.write(stacked)

print(f"\n✔ Saved georeferenced RGB+NIR mosaic:\n  {output_file}")


# -------------------------------------------------------
# DISPLAY RGB PREVIEW
# -------------------------------------------------------
rgb = stacked[:3]
rgb = np.clip(rgb, 0, 10000)
rgb = ((rgb / 10000) * 255).astype(np.uint8)

plt.figure(figsize=(10, 10))
plt.imshow(np.transpose(rgb, (1, 2, 0)))
plt.axis("off")
plt.title("Sentinel-2 RGB Preview")
plt.show()
