# Imports
import os
import sys
import time
import psutil
import resource
import numpy as np
import healpy as hp
import matplotlib.pyplot as plt
import heracles
import heracles.ducc

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

# Heracles parameters
nside = 128
lmax = 180  # <-- conservative estimate of 1.5 x nside

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

# Load galaxy catalog using Heracles
print("Loading galaxy catalog...")
valm = heracles.read_vmap(vmap_path, transform=True, lmax=lmax)
catalog = heracles.FitsCatalog(catalog_path, columns=["RA", "DEC", "Z_COSMO"], ext=1)
catalog.visibility = valm
print(f"Catalog sky fraction: {catalog.fsky:.6f}")
catalog = catalog[f"(Z_COSMO >= {zmin}) & (Z_COSMO <= {zmax})"]
print_state("Catalog done")

# Define discrete mapper
print("Setting up DiscreteMapper...")
mapper = heracles.ducc.DiscreteMapper(lmax)
fields = {"POS": heracles.Positions(mapper,"RA","DEC",mask="VIS")}
catalogs = {0: catalog}

# Calculate spherical harmonic coefficients
print("Calculating spherical harmonic coefficients...")
data = heracles.map_catalogs(fields, catalogs, parallel=False)
print_state("Coefs done")

# Calculate Cls
print("\nCalculating Cls...")
spectra = heracles.angular_power_spectra(data, debias=False)
cls = spectra["POS", "POS", 0, 0]
ells = np.arange(lmax + 1)
fname = os.path.join(input_dir, f"cls_heracles_{zmin}-{zmax}.txt")
np.savetxt(fname, np.column_stack((ells, cls)), header="ell Cl")
print_state("Cls done")

# Print general properties
print(f"Number of multipoles: {len(ells)}")
print(f"lmax: {lmax}")
print(f"C_0 (monopole): {cls[0]:.4e}")
print(f"C_1 (dipole): {cls[1]:.4e}")
print(f"Minimum C_l (excluding monopole): {np.min(cls[1:]):.4e}")
print(f"Maximum C_l (excluding monopole): {np.max(cls[1:]):.4e}")

# Plot angular power spectrum
plt.figure(figsize=(8, 5))
plt.plot(ells[1:], cls[1:], linewidth=1)
plt.xlabel(r"Multipole $\ell$")
plt.ylabel(r"$C_\ell$")
plt.title("Galaxy angular power spectrum (Heracles DiscreteMapper)")
plt.yscale("log")
plt.grid(True, alpha=0.25)
save_figure(os.path.join(plot_dir, f"cls_heracles_{zmin}-{zmax}.png"))
print_state("Finished")
