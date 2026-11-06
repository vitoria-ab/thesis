# Imports
import os
import sys
from astropy.io import fits
import numpy as np
import healpy as hp
import matplotlib.pyplot as plt
import time,psutil,resource

# Function to save figure
def save_figure(path):
    plt.tight_layout()
    plt.savefig(path, dpi=160, bbox_inches="tight")
    plt.close()
    print(f"Saved {path}")

# Function to print current state
START_TIME = time.time()
def print_state(label):
    current_mem = psutil.Process().memory_info().rss / 1e9
    max_mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e6
    t = time.time() - START_TIME
    h,m,s = int(t // 3600), int((t%3600) // 60), t % 60
    print(f'[MEM] [{h:02d}h{m:02d}m{s:05.2f}s] {label}: current RSS = {current_mem:.2f}; peak RSS so far = {max_mem:.2f} GB', flush=True)
    return

# Create directories
output_dir = sys.argv[1]
input_dir = os.path.abspath("/projects/F202315069PEXF1/vitoria/running_colore/" + output_dir)
plot_dir = os.path.join(output_dir, "plots")
zmin = float(sys.argv[2]);  zmax = float(sys.argv[3])
catalog_path = os.path.join(input_dir, "colore_srcs_merged.fits")
os.makedirs(plot_dir, exist_ok=True)
print(f"Input/output directory: {input_dir}")
print(f"Saving plots to: {plot_dir}")

# Open galaxy catalog and get data
with fits.open(catalog_path, memmap=True) as hdul:
    cat = hdul[1].data
    z = np.asarray(cat["Z_COSMO"], dtype=float)
    ra = np.asarray(cat["RA"], dtype=float)
    dec = np.asarray(cat["DEC"], dtype=float)
print_state("Catalog read")

# Extract the galaxies corresponding to this redshift slice
mask = (z>=zmin) & (z<=zmax)
ra=ra[mask];  dec=dec[mask]

# Calculate galaxy density contrast
nside = 128;  npix = hp.nside2npix(nside)
ipix = hp.ang2pix(nside, ra, dec, lonlat=True)
ncount = np.bincount(ipix, minlength=npix)
delta = ncount / np.mean(ncount) - 1

# Calculate angular power spectrum
l_max = 180  # <-- 2*nside as recommended for anafast
cls = hp.anafast(delta, lmax=l_max)
ells = np.arange(len(cls))
fname = os.path.join(output_dir, f"galaxy_cls_anafast_{zmin}-{zmax}.txt")
np.savetxt(fname, np.column_stack((ells, cls)), header="ell Cl")
print_state("Cl done")

# Print general properties
print(f"Number of multipoles: {len(ells)}")
print(f"l_max: {l_max}")
print(f"C_0 (monopole): {cls[0]:.4e}")
print(f"C_1 (dipole): {cls[1]:.4e}")
print(f"Minimum C_l (excluding monopole): {np.min(cls[1:]):.4e}")
print(f"Maximum C_l (excluding monopole): {np.max(cls[1:]):.4e}")

# Plot angular power spectrum
plt.figure(figsize=(8, 5))
plt.plot(ells[1:], cls[1:], linewidth=1)
plt.xlabel(r"Multipole $\ell$")
plt.ylabel(r"$C_\ell$")
plt.title("Galaxy angular power spectrum")
plt.yscale("log")
plt.grid(True, alpha=0.25)
save_figure(os.path.join(plot_dir, f"galaxy_cls_anafast_{zmin}-{zmax}.png"))
plt.show()
