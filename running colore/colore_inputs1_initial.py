# ---------- Initial imports ----------
import numpy as np
import camb
import time,psutil,resource
from scipy.special import erf


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


# ---------- Generate Pk file with CAMB ----------
# Define cosmology to use and grid of ks to generate
cosm = {
    'omega_M': 0.31,       # Total matter density parameter today, Ω_m
    'omega_B': 0.05,       # Baryon density parameter today, Ω_b
    'omega_L': 1 - 0.31,   # Dark energy density parameter, Ω_Λ (we're considering a flat Universe)
    'h': 0.6774,           # Reduced Hubble constant: h = H0 / (100 km s^-1 Mpc^-1)
    'w': -1.0,             # Dark energy equation-of-state parameter, w = p / (ρ c²); -1 for ΛCDM
    'ns': 0.967,            # Scalar spectral index of primordial perturbations
    'sigma_8': np.nan,      # RMS matter density fluctuation in spheres of radius 8 h^-1 Mpc; calculated by CAMB
    'As': 2.142e-9          # Amplitude of primordial scalar perturbations at the pivot scale
}
Npoints = 500;  kmin = 1e-4;  kmax = 2.0

# Define function to call camb
def get_pk(cosm,z):
    """Calculate the linear matter power spectrum and growth rate with CAMB."""

    # Set cosmology
    pars = camb.CAMBparams()
    pars.set_cosmology(H0=100 * cosm["h"], ombh2=cosm["omega_B"] * cosm["h"]**2, 
                       omch2=(cosm["omega_M"] - cosm["omega_B"]) * cosm["h"]**2, 
                       omk=0.0, mnu=0.0)
    pars.set_dark_energy(w=cosm["w"])  # <-- it's LCDM for w=-1
    pars.InitPower.set_params(As=cosm["As"], ns=cosm["ns"], r=0)
    pars.set_matter_power(redshifts=[z], kmax=kmax, nonlinear=False)
    pars.NonLinear = camb.model.NonLinear_none

    # Calculate results
    results = camb.get_results(pars)
    k,_,pk = results.get_matter_power_spectrum(minkh=kmin, maxkh=kmax, npoints=Npoints)
    return k,pk[0]

# Calculate Pks and save
k, pk = get_pk(cosm, z=0.0)
np.savetxt("results/pk.txt", np.column_stack((k, pk)))
print_state("Pk done")



# ---------- Generate dndz, bias, Tz and nuTable files ----------
zmin=0;  zmax=0.6500;  Npoints=4096  # <-- auxiliary files need to span redshift 0 - zmax
z = np.linspace(zmin, zmax, Npoints)

# bias
bias = np.ones_like(z)
np.savetxt("results/bias.txt", np.column_stack((z, bias)))

# temperature 
T_HI = np.full_like(z, 0.05)  # <-- we are choosing a constant 0.05K for HI
np.savetxt("results/tz.txt", np.column_stack((z, T_HI)))

# table of wavelength shells
zmin_shell=0.60;  zmax_shell=zmax  # <-- nuTable and dndz can restrict redshift to zmin - zmax range
nu_HI=1420.405;  n_bins=50
nu_edges = np.linspace(nu_HI/(1+zmax_shell), nu_HI/(1+zmin_shell), n_bins+1)
nuTable = np.column_stack((nu_edges[:-1], nu_edges[1:]))
np.savetxt("results/nuTable.txt", nuTable, fmt="%.18e")

# dndz
amp=22.357;  alpha=1.044;  z0=0.568;  beta=1.742;  smooth=0.002
window = 0.5 * (erf((z-zmin_shell)/(np.sqrt(2)*smooth)) - erf((z-zmax_shell)/(np.sqrt(2)*smooth)))
dndz = window * amp * (z/z0)**alpha * np.exp(-(z/z0)**beta) * 3600
np.savetxt("results/dndz.txt", np.column_stack((z, dndz)))
print_state("CoLoRe files done")

