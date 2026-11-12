# Imports
import os, sys
import time, psutil, resource
import numpy as np
import healpy as hp
import matplotlib.pyplot as plt
from astropy.io import fits
import pymaster as nmt

# Function to save a figure
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
    h, m, s = int(t // 3600), int((t % 3600) // 60), t % 60
    print(f"[MEM] [{h:02d}h{m:02d}m{s:05.2f}s] {label}:" + 
          f" current RSS = {current_mem:.2f}; peak RSS so far = {max_mem:.2f} GB", flush=True)

# Get input parameters
zmin = float(sys.argv[2])
zmax = float(sys.argv[3])
dir = f"{sys.argv[1]}_{zmin}-{zmax}"

# Define directories
input_dir = os.path.abspath("/projects/F202315069PEXF1/vitoria/results/" + dir)
plot_dir = os.path.join(input_dir, "plots")
catalog_path = os.path.join(input_dir, "colore_srcs_merged.fits")
os.makedirs(plot_dir, exist_ok=True)
print(f"Input directory: {input_dir}")
print(f"Plots directory: {plot_dir}")

# Open galaxy catalog and get data
with fits.open(catalog_path, memmap=True) as hdul:
    cat = hdul[1].data
    mask = (cat['Z_COSMO'] >= zmin) & (cat['Z_COSMO'] <= zmax)
    z = np.asarray(cat["Z_COSMO"], dtype=float)[mask]  # <-- not sure if i need z!
    positions = np.array([cat['RA'][mask], cat['DEC'][mask]])
print_state("Catalog read")

# Define NaMaster parameters
nside = 256
lmax = 2 * nside
weights = np.ones(len(positions[0]))

# Load visibility map if it exists, otherwise create it
if os.path.exists(os.path.join(input_dir, "visibility_map.fits")):
    vmap = hp.read_map(os.path.join(input_dir, "visibility_map.fits"))
else: 
    print("Creating full-sky visibility map...")
    vmap = np.ones(hp.nside2npix(nside), dtype=np.float64)
    vmap_path = os.path.join(input_dir, f"visibility_map.fits")
    hp.write_map(vmap_path, vmap, overwrite=True, dtype=np.float64)
    print(f"Saved visibility map to {vmap_path}")
print_state("Vismap created")

# Create bandpower array
print("Calculating Cls...")
bands = nmt.NmtBin.from_lmax_linear(lmax, nlb=1)  # <-- bands, nlb=1 means no binning 
ells = bands.get_effective_ells()  # <-- ls corresponding to the bands
f_cat = nmt.NmtFieldCatalogClustering(positions, weights, None, None, 
                                      mask=vmap, lmax=lmax, lonlat=True) 
mm_matrix = nmt.NmtWorkspace.from_fields(f_cat, f_cat, bands)  # <-- mode-coupling matrix
pseudo_cl = nmt.compute_coupled_cell(f_cat, f_cat)  # <-- pseudo Cls
cls = mm_matrix.decouple_cell(pseudo_cl)[0]
fname = os.path.join(input_dir, f"cls_namaster_{zmin}-{zmax}.txt")
np.savetxt(fname, np.column_stack((ells, cls)), header="ell Cl")
print_state("Cls done")

# Print general properties
print(f"Number of multipoles: {len(ells)}")
print(f"lmax: {lmax}")
print(f"C_0 (monopole): <not calculated>")
print(f"C_1 (dipole): <not calculated>")
print(f"Minimum C_l: {np.min(cls):.4e}")
print(f"Maximum C_l: {np.max(cls):.4e}")

# Plot angular power spectrum
plt.figure(figsize=(8, 5))
plt.plot(ells, cls, linewidth=1)
plt.xlabel(r"Multipole $\ell$")
plt.ylabel(r"$C_\ell$")
plt.title("Galaxy angular power spectrum (NaMaster)")
plt.yscale("log")
plt.grid(True, alpha=0.25)
save_figure(os.path.join(plot_dir, f"cls_namaster_{zmin}-{zmax}.png"))
print_state("Finished")
