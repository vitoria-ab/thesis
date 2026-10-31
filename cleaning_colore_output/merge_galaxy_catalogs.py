# Imports
import sys
from pathlib import Path
from astropy.io import fits
import warnings
import os
from astropy.units import UnitsWarning

# Ignore unit warnings raised by astropy
warnings.filterwarnings("ignore", category=UnitsWarning)

# Define directories
input_dir = Path("/projects/F202315069PEXF1/vitoria/running_colore/" + sys.argv[1])
output_file = input_dir / "colore_srcs_merged.fits"
temp_file = input_dir / "colore_srcs_merged.tmp"

# Find all source catalogs
files = sorted(input_dir.glob("colore_srcs_*.fits"))
files = [f for f in files if f != output_file and f != temp_file]
print(f"Found {len(files)} catalogs.", flush=True)

# Check catalogue structure and count total rows
# Get header (from the first file)
with fits.open(files[0]) as hdul:
    primary_header = hdul[0].header.copy()
    table_header = hdul[1].header.copy()
    reference = hdul[1].columns
    row_size = table_header["NAXIS1"]

# Checking total number of rows
total_rows = 0
for f in files:
    print(f"Checking {f.name}", flush=True)
    with fits.open(f) as hdul:
        current = hdul[1].columns
        header = hdul[1].header
        total_rows += header["NAXIS2"]
print(f"Total number of galaxies: {total_rows:,}", flush=True)

# Prepare output header
table_header["NAXIS2"] = total_rows
for header in (primary_header, table_header):
    header.pop("CHECKSUM", None)
    header.pop("DATASUM", None)

# Copy each catalogue one at a time
try:
    with open(temp_file, "wb") as output:
        # Write header
        output.write(primary_header.tostring(endcard=True, padding=True).encode("ascii"))
        output.write(table_header.tostring(endcard=True, padding=True).encode("ascii"))

        for f in files:
            # Write data into the final output
            print(f"Merging {f.name}", flush=True)
            with fits.open(f,memmap=False) as hdul:  data = hdul[1].data.tobytes()
            output.write(data)

            # Make sure that the data is deleted before continuing
            del data
            output.flush()
            os.fsync(output.fileno())
            os.posix_fadvise(output.fileno(), 0, output.tell(), os.POSIX_FADV_DONTNEED)

        # Pad FITS data to a multiple of 2880 bytes
        padding = (-output.tell()) % 2880
        output.write(b"\0" * padding)
        output.flush()
        os.fsync(output.fileno())
        os.posix_fadvise(output.fileno(), 0, output.tell(), os.POSIX_FADV_DONTNEED)
    
    # Replace final output only after successful completion
    os.replace(temp_file, output_file)

# Delete temporary file
finally:
    if temp_file.exists():  temp_file.unlink()
print(f"\nMerged {len(files)} catalogs.", flush=True)
print(f"Total number of galaxies: {total_rows:,}", flush=True)
print(f"Saved to: {output_file}", flush=True)
