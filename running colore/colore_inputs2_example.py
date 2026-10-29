# ---------- Initial imports ----------
import os
import numpy as np
import time,psutil,resource
import pyccl as ccl
from scipy.integrate import simpson
import libconf
dir = "results_example"
os.makedirs(dir, exist_ok=True)


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
csm = {
    'omega_M': 0.3,       # Total matter density parameter today, Ω_m
    'omega_B': 0.3,       # Baryon density parameter today, Ω_b
    'omega_L': 0.7,       # Dark energy density parameter, Ω_Λ (we're considering a flat Universe)
    'h': 0.7,             # Reduced Hubble constant: h = H0 / (100 km s^-1 Mpc^-1)
    'w': -1.0,            # Dark energy equation-of-state parameter, w = p / (ρ c²); -1 for ΛCDM
    'ns': 0.96,           # Scalar spectral index of primordial perturbations
    'sigma_8': 0.8,       # RMS matter density fluctuation in spheres of radius 8 h^-1 Mpc; calculated by CAMB
}
Npoints_pk = 1024;  kmin = 1e-4;  kmax = 100
a = 1.  # <-- scale factor, equivalent to z=0

# Set cosmology
cosmo = ccl.Cosmology(Omega_c=csm['omega_M']-csm['omega_B'],
                      Omega_b=csm['omega_B'], h=csm['h'],
                      sigma8=csm['sigma_8'], n_s=csm['ns'],
                      transfer_function='eisenstein_hu')
k = np.geomspace(kmin, kmax, Npoints_pk)
pk = ccl.linear_matter_power(cosmo, k*cosmo['h'],a)*cosmo['h']**3
np.savetxt(f"{dir}/pk.txt", np.transpose([k, pk]))
print_state("Pk done")



# ---------- Generate dndz, bias, Tz and nuTable files ----------
zmin=0;  zmax=0.2;  Npoints=1024
zs = np.linspace(zmin, zmax, Npoints)

# dndz
ngals = 1E5
ndens = ngals / (4*np.pi*(180/np.pi)**2)
nz = zs**2*np.exp(-(zs/0.03)**1.5)
nz *= ndens / simpson(nz, x=zs)
np.savetxt(f'{dir}/dndz.txt', np.transpose([zs, nz]))

# bias
bz = (1+zs)
np.savetxt(f'{dir}/bias.txt', np.transpose([zs, bz]))

# temperature
tz = 0.05 * np.ones_like(zs)
np.savetxt(f'{dir}/tz.txt', np.transpose([zs, tz]))

# table of wavelength shells
zmin_shell=0.04;  zmax_shell=0.14
nu_HI=1420.;  n_bins=5
nu_edges = np.linspace(nu_HI/(1+zmax_shell), nu_HI/(1+zmin_shell), n_bins+1)
nuTable = np.transpose([nu_edges[:-1], nu_edges[1:]])
np.savetxt(f"{dir}/nuTable.txt", nuTable, fmt="%.18e")
print_state("CoLoRe files done")


# ---------- Generate CoLoRe config file ----------
zmin=0.0001;  zmax=0.15;  n_grid=256;  n_side=64
config = {}
config['global'] = {'prefix_out': f'{dir}/colore',
                    'output_format': 'FITS',
                    'output_density': True,
                    'pk_filename': f'{dir}/pk.txt',
                    'z_min': zmin,
                    'z_max': zmax,
                    'seed': 1000,
                    'write_pred': False,
                    'just_write_pred': False}
config['field_par'] = {'r_smooth': 1.,
                       'smooth_potential': True,
                       'n_grid': n_grid,
                       'dens_type': 1,
                       'lpt_buffer_fraction': 0.6,
                       'lpt_interp_type': 1,
                       'lpt_vels': 0,
                       'output_lpt': 0}
config['cosmo_par'] = csm
# Note: if you need more than one sample of galaxies/intensity maps/custom tracers etc.
# just add `srcs2` `imap2` etc.
config['srcs1'] = {'nz_filename': f'{dir}/dndz.txt',
                   'bias_filename': f'{dir}/bias.txt',
                   'include_lensing': True,
                   'store_skewers': True}
config['imap1'] = {'tbak_filename': f'{dir}/tz.txt',
                   'bias_filename': f'{dir}/bias.txt',
                   'freq_list': f'{dir}/nuTable.txt',
                   'freq_rest': 1420.0,
                   'nside': n_side}
with open(f'{dir}/params.cfg', 'w') as configfile:
    libconf.dump(config, configfile)
