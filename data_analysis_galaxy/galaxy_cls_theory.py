# Imports
print("Importing", flush=True)
import os, sys
import numpy as np
import camb
import matplotlib.pyplot as plt
from astropy.io import fits
from scipy.special import erf

# Function to save a figure
def save_figure(path):
    plt.tight_layout()
    plt.savefig(path, dpi=160, bbox_inches="tight")
    plt.close()
    print(f"Saved {path}")

# Get input parameters
print("Defining folders", flush=True)
zmin = float(sys.argv[2])
zmax = float(sys.argv[3])
dir = f"{sys.argv[1]}_{zmin}-{zmax}"

# Define directories (bias is not necessary, can be just a number)
input_dir = os.path.join("/projects/F202315069PEXF1/vitoria/results", dir)
plot_dir = os.path.join(input_dir, "plots")
catalog_path = os.path.join(input_dir, "colore_srcs_merged.fits")
dndz_path = os.path.join(input_dir, "dndz.txt")
print(f"Input directory: {input_dir}")

# Read dndz
# NOTES: (a) 50 points is enough; (b) dndz norm is useless
#print("Getting dndz", flush=True)
dndz_data = np.loadtxt(dndz_path)
zs,dndz = dndz_data[:,0], dndz_data[:,1]
mask = (zs>=zmin) & (zs<=zmax)
zs,dndz = zs[mask], dndz[mask]
print(f"Number of redshift samples: {len(zs)}")

# Create dnd
print("Creating dndz",flush=True) 
amp=22.357;  alpha=1.044;  z0=0.568;  beta=1.742;  smooth=0.002 
zs = np.linspace(zmin-0.02,zmax+0.02,2000) 
def f(zlim):  return erf( (zs-zlim) / (np.sqrt(2)*smooth) )
window = 0.5 * (f(zmin) - f(zmax))
dndz = window * amp * (zs/z0)**alpha * np.exp(-(zs/z0)**beta) * 3600 

# Calculate expected number of galaxies and shot noise
print("Calculating expected shot noise", flush=True)
norm = np.trapezoid(dndz,zs)
Ngal_expected = norm * 4*np.pi * (180/np.pi)**2
cl_shot = 1 / (norm * (180/np.pi)**2)
print(f"Integrated dndz: {norm:.4f} galaxies/deg2")
print(f"Expected full-sky number of galaxies: {Ngal_expected:.0f}")
print(f"Expected shot noise: {cl_shot:.4e}")

# Check actual number of galaxies in the catalogue
print("Opening catalog", flush=True)
with fits.open(catalog_path, memmap=True) as hdul:
    cat = hdul[1].data
    Ngal = np.count_nonzero((cat["Z_COSMO"]>=zmin) & (cat["Z_COSMO"]<=zmax))
print(f"Actual number of galaxies: {Ngal}")
print(f"Catalogue shot noise: {4*np.pi/Ngal:.4e}")

# Define NaMaster parameters
nside = 128
lmax = 2 * nside

# Define cosmology to use and grid of ks to generate
csm = {
    'omega_M': 0.31,       # Total matter density parameter today, Ω_m
    'omega_B': 0.05,       # Baryon density parameter today, Ω_b
    'omega_L': 0.69,       # Dark energy density parameter, Ω_Λ (we're considering a flat Universe)
    'h': 0.6774,           # Reduced Hubble constant: h = H0 / (100 km s^-1 Mpc^-1)
    'w': -1.0,             # Dark energy equation-of-state parameter, w = p / (ρ c²); -1 for ΛCDM
    'ns': 0.967,           # Scalar spectral index of primordial perturbations
    'sigma_8': np.nan,     # RMS matter density fluctuation in spheres of radius 8 h^-1 Mpc
    'As': 2.142e-9         # Amplitude of primordial scalar perturbations at the pivot scale
}

# Set cosmology in CAMB
print("Setting cosmology",flush=True)
pars = camb.CAMBparams()
pars.set_cosmology(H0=100*csm["h"], ombh2=csm["omega_B"]*csm["h"]**2, 
                   omch2=(csm["omega_M"]-csm["omega_B"])*csm["h"]**2,
                   omk=0.0, mnu=0.0)
pars.InitPower.set_params(As=csm["As"], ns=csm["ns"],r=0.)

# Define source terms
pars.WantCls = True
pars.Want_CMB, pars.Want_CMB_lensing, pars.DoLensing                                                    = False, False, False
pars.SourceTerms.counts_velocity, pars.SourceTerms.counts_radial, pars.SourceTerms.counts_timedelay     = False, False, False
pars.SourceTerms.counts_ISW, pars.SourceTerms.counts_potential, pars.SourceTerms.counts_evolve          = False, False, False
pars.SourceTerms.line_phot_dipole, pars.SourceTerms.line_phot_quadrupole, pars.SourceTerms.line_basic   = False, False, False
pars.SourceTerms.line_distortions, pars.SourceTerms.line_extra, pars.SourceTerms.line_reionization      = False, False, False
pars.SourceTerms.use_21cm_mK                                                                            = False      
pars.SourceTerms.counts_density, pars.SourceTerms.counts_redshift, pars.SourceTerms.counts_lensing      = True, False, False

# Define galaxy source window
print("Define source window",flush=True)
source = camb.sources.SplinedSourceWindow(bias=1.0, dlog10Ndm=0.0)
source.source_type = "counts"
source.set_table(zs, dndz)
pars.SourceWindows = [source]

print("Calculating Cls", flush=True)
pars.set_for_lmax(lmax, lens_potential_accuracy=1)
pars.NonLinear = camb.model.NonLinear_none  # <-- repeat after set_for_lmax or gives an error!!
results = camb.get_results(pars)
cls_dict = results.get_source_cls_dict(raw_cl=True, lmax=lmax)

# Selecting Cls
cls_camb = cls_dict["W1xW1"][2:lmax+1]
ells_camb = np.arange(2, lmax+1)
print("CAMB calculation finished!",flush=True)
camb_file = os.path.join(input_dir, f"cls_theory_{zmin}-{zmax}.txt")
np.savetxt(camb_file, np.column_stack((ells_camb, cls_camb)), header="ell Cl")
print(f"Saved theoretical Cls to {camb_file}")

# Print general properties
print(f"Number of multipoles: {len(ells_camb)}")
print(f"lmax: {lmax}")
print(f"C_0 (monopole): <not calculated>")
print(f"C_1 (dipole): <not calculated>")
print(f"Minimum C_l: {np.min(cls_camb):.4e}")
print(f"Maximum C_l: {np.max(cls_camb):.4e}")

# Plot angular power spectrum
plt.figure(figsize=(8, 5))
plt.plot(ells_camb, cls_camb, linewidth=1)
plt.xlabel(r"Multipole $\ell$")
plt.ylabel(r"$C_\ell$")
plt.title("Galaxy angular power spectrum (theory)")
plt.yscale("log")
plt.grid(True, alpha=0.25)
save_figure(os.path.join(plot_dir, f"cls_theory_{zmin}-{zmax}.png"))
