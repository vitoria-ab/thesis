"""Plot only CoLoRe inputs and outputs relevant to galaxy distribution and HI intensity mapping."""

# Imports
import sys
import os
import warnings
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

# Function to load data
def load_txt(path):
    ''' Function to guarantee size of the files. '''
    if not os.path.isfile(path):
        warnings.warn(f"Missing input file: {path}")
        return None
    data = np.loadtxt(path)
    if data.ndim == 1:
        data = data[None,:]
    if data.shape[1] < 2:
        warnings.warn(f"Expected at least two columns in {path}")
        return None
    return data

# Create directories
input_dir = os.path.abspath("/projects/F202315069PEXF1/vitoria/running_colore/" + sys.argv[1])
catalog_path = os.path.join(input_dir, "colore_srcs_merged.fits")
plot_dir = os.path.join(input_dir, "plots")
os.makedirs(plot_dir, exist_ok=True)
print(f"Input/output directory: {input_dir}")
print(f"Saving plots to: {plot_dir}")

# Open galaxy catalog
with fits.open(catalog_path, memmap=True) as hdul:

    # Get redshift column
    cat = hdul[1].data
    z = np.asarray(cat["Z_COSMO"], dtype=float)
    zmin = float(sys.argv[2]);  zmax = float(sys.argv[3])

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
    save_figure(os.path.join(plot_dir, f"output_galaxy_redshift_{zmin}-{zmax}.png"))

    # Extract the galaxies corresponding to this redshift slice
    mask = (cat["Z_COSMO"]>=zmin) & (cat["Z_COSMO"]<=zmax)
    ra = np.asarray(cat["RA"][mask], dtype=float)
    dec = np.asarray(cat["DEC"][mask], dtype=float)

    # Plot galaxy density
    nside = 128;  npix = hp.nside2npix(nside)
    ipix = hp.ang2pix(nside, ra, dec, lonlat=True)
    ncount = np.bincount(ipix, minlength=npix)
    hp.mollview(ncount, title="Galaxy density map", unit="Number of galaxies")
    save_figure(os.path.join(plot_dir, f"output_galaxy_density_{zmin}-{zmax}.png"))

    # Plot galaxy overdensity
    nmean = np.mean(ncount)
    delta = ncount / nmean - 1
    hp.mollview(delta, title=r"Galaxy density contrast ($\delta$)")
    save_figure(os.path.join(plot_dir, f"output_galaxy_overdensity_{zmin}-{zmax}.png"))

