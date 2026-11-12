# Initial imports
from scipy.special import erf
import os,sys
import numpy as np
import camb
from camb.sources import SplinedSourceWindow
import time,psutil,resource
import matplotlib.pyplot as plt

# Function to save a figure
def save_figure(path):
    plt.tight_layout()
    plt.savefig(path, dpi=160, bbox_inches="tight")
    plt.close()
    print(f"Saved {path}")

# Define function to print current state
START_TIME = time.time()
def print_state(label):
    ''' Print the current and peak memory usage along with the elapsed time. '''

    current_mem = psutil.Process().memory_info().rss / 1e9
    max_mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e6
    t = time.time() - START_TIME
    h,m,s = int(t // 3600), int((t%3600) // 60), t % 60
    print(f'[MEM] [{h:02d}h{m:02d}m{s:05.2f}s] {label}: current RSS = {current_mem:.2f}; peak RSS so far = {max_mem:.2f} GB', flush=True)
    return
print_state("Start")

# Define directories
output_dir = sys.argv[1]
input_dir = os.path.abspath("/projects/F202315069PEXF1/vitoria/running_colore/" + output_dir)
plot_dir = os.path.join(output_dir,"plots")
zmin = float(sys.argv[2]);  zmax = float(sys.argv[3])
os.makedirs(plot_dir, exist_ok=True)
print(f"Input directory: {input_dir}")
print(f"Output directory: {output_dir}")

# Define parameters
lmax = 180
zmin_aux=0;  zmax_aux=1.;  Npoints=1024  # range of auxiliary files
zmin_catalog=0.5;  zmax_catalog=0.85     # range of galaxy distribution

# Define inputs for CAMB for galaxy clustering
zs, bias = np.loadtxt(os.path.join(input_dir, "bias.txt"), unpack=True)
_, dndz = np.loadtxt(os.path.join(input_dir, "dndz.txt"), unpack=True)
#zs = np.linspace(zmin_aux, zmax_aux, Npoints)
#bias = np.ones_like(zs)
#amp=22.357;  alpha=1.044;  z0=0.568;  beta=1.742;  smooth=0.002
#def f(zlim):  return erf((zs-zlim) / (np.sqrt(2)*smooth))
#window = 0.5 * (f(zmin_catalog) - f(zmax_catalog))
mask = (zs>=zmin)&(zs<=zmax)
zs_help = np.copy(zs)
zs = zs[mask];  dndz = dndz[mask];  bias = bias[mask]

# Define cosmology to use and grid of ks to generate
csm = {
    'omega_M': 0.31, 
    'omega_B': 0.05, 
    'omega_L': 0.69,
    'h': 0.6774, 
    'w': -1.0,  
    'ns': 0.967, 
    'sigma_8': np.nan, 
    'As': 2.142e-9 
}

# Set cosmology in CAMB
pars = camb.CAMBparams()
pars.set_cosmology(H0=100*csm["h"], ombh2=csm["omega_B"]*csm["h"]**2, 
                   omch2=(csm["omega_M"]-csm["omega_B"])*csm["h"]**2,
                   omk=0.0, mnu=0.0)
pars.set_dark_energy(w=csm["w"])
pars.InitPower.set_params(As=csm["As"], ns=csm["ns"], r=0)
pars.set_for_lmax(lmax, lens_potential_accuracy=1)
pars.NonLinear = camb.model.NonLinear_none

# Disable all unnecessary calculations to save memory and time
pars.Want_CMB, pars.Want_CMB_lensing, pars.DoLensing = False,False,False
pars.SourceTerms.counts_velocity, pars.SourceTerms.counts_radial, pars.SourceTerms.counts_timedelay  = False,False,False
pars.SourceTerms.counts_ISW, pars.SourceTerms.counts_potential, pars.SourceTerms.counts_evolve = False,False,False
pars.SourceTerms.line_phot_dipole, pars.SourceTerms.line_phot_quadrupole, pars.SourceTerms.line_basic = False,False,False
pars.SourceTerms.line_distortions, pars.SourceTerms.line_extra, pars.SourceTerms.line_reionization = False,False,False
pars.SourceTerms.use_21cm_mK = False      
pars.SourceTerms.counts_density = True
pars.SourceTerms.counts_redshift, pars.SourceTerms.counts_lensing = False,False
pars.Want_cl_2D_array = True

# Set up source window for galaxy clustering
pars.SourceWindows = [SplinedSourceWindow(z=zs, W=dndz, bias_z=bias)]
map_ = 'W1xW1'
results = camb.get_results(pars)
cls = results.get_source_cls_dict(raw_cl=True)[map_][2:lmax+1]
ells = np.arange(2, lmax+1)

# Save the theoretical Cls to a text file
fname = os.path.join(output_dir, f"galaxy_cls_theory_{zmin}-{zmax}.txt")
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
plt.title("Galaxy angular power spectrum (theory)")
plt.yscale("log")
plt.grid(True, alpha=0.25)
save_figure(os.path.join(plot_dir, f"galaxy_cls_theory_{zmin}-{zmax}.png"))
print_state("Finished")
