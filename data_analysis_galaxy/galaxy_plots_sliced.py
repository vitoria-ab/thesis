# Imports
import sys
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import healpy as hp
from astropy.io import fits

# Function to save figure
def save_figure(path):
    plt.tight_layout()
    plt.savefig(path, dpi=160, bbox_inches="tight")
    plt.close()
    print(f"Saved {path}")

# Create directories
input_dir = os.path.abspath("/projects/F202315069PEXF1/vitoria/results/" + sys.argv[1])
zmin = float(sys.argv[2]);  zmax = float(sys.argv[3])
catalog_path = os.path.join(input_dir, "colore_srcs_merged.fits")
plot_dir = os.path.join(input_dir, "plots")
os.makedirs(plot_dir, exist_ok=True)
print(f"Input/output directory: {input_dir}")
print(f"Saving plots to: {plot_dir}")

# Open galaxy catalog and get data
with fits.open(catalog_path, memmap=True) as hdul:
    cat = hdul[1].data
    z = np.asarray(cat["Z_COSMO"], dtype=float)
    ra = np.asarray(cat["RA"], dtype=float)
    dec = np.asarray(cat["DEC"], dtype=float)

# Plot histogram of galaxies per redshift
ngal = np.sum((z>=zmin) & (z<=zmax))
plt.figure(figsize=(7, 5))
plt.hist(z, bins=50, histtype="step", linewidth=1.5, label="z distribution")
plt.axvline(zmin, color="r", linestyle="--", label=f"z slice {zmin:.2f}-{zmax:.2f}")
plt.axvline(zmax, color="r", linestyle="--")
plt.text(0.03, 0.05, f"$N_{{gal}} = {ngal:,}$", 
         transform=plt.gca().transAxes, ha="left", va="bottom", 
         bbox=dict(boxstyle="round", facecolor="white", alpha=0.8))
plt.xlabel(f"Z_COSMO (catalog redshift)")
plt.ylabel("Number of galaxies")
plt.title("CoLoRe galaxy redshift distribution")
plt.grid(True, alpha=0.25)
plt.legend()
save_figure(os.path.join(plot_dir, f"redshift_{zmin}-{zmax}.png"))

# Extract the galaxies corresponding to this redshift slice
mask = (z>=zmin) & (z<=zmax)
ra=ra[mask];  dec=dec[mask]

# Plot galaxy density
nside = 128;  npix = hp.nside2npix(nside)
ipix = hp.ang2pix(nside, ra, dec, lonlat=True)
ncount = np.bincount(ipix, minlength=npix)
hp.mollview(ncount, title="Galaxy density map", unit="Number of galaxies")
save_figure(os.path.join(plot_dir, f"density_{zmin}-{zmax}.png"))

# Plot galaxy overdensity
nmean = np.mean(ncount)
delta = ncount / nmean - 1
hp.mollview(delta, title=r"Galaxy density contrast ($\delta$)")
save_figure(os.path.join(plot_dir, f"overdensity_{zmin}-{zmax}.png"))

