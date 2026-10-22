# ---------- Initial imports ----------
import os
import time, psutil, resource
import argparse
import numpy as np
import pysm3
import healpy as hp



# ---------- Initial setup ----------
# Set the path to the local PySM data directory
os.environ.setdefault("PYSM_LOCAL_DATA", "/home/roger02/ScienceCodes/pysm_data")

# Define function to print current state
START_TIME = time.time()
def print_state(label):
    ''' Print the current and peak memory usage along with the elapsed time. '''

    current_mem = psutil.Process().memory_info().rss / 1e9
    max_mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e6
    time = time.time() - START_TIME
    h,m,s = int(time // 3600), int((time%3600) // 60), time % 60
    print(f'[MEM] [{h:02d}h{m:02d}m{s:05.2f}s] {label}: current RSS = {current_mem:.2f}; peak RSS so far = {max_mem:.2f} GB', flush=True)
    return

# Parse arguments from command line
parser = argparse.ArgumentParser()
parser.add_argument('--seed', type=int, required=True)       # random seed
parser.add_argument('--lower-z', type=float, required=True)  # lower redshift limit
parser.add_argument('--upper-z', type=float, required=True)  # higher redshift limit
args = parser.parse_args()
print_state("Start")


# IN HERE WE NEED TO FIRST:
# 1. GENERATE Pk FROM CAMB WITH A GIVEN COSMOLOGY
# 2. GENERATE THE HI MAP FROM COLORE WITH A GIVEN Pk (FROM CAMB)



# ---------- Generate synthetic maps for each redshift ----------
# Load table of (probably randomly generated?) frequencies
nu_interval = np.loadtxt(f'./colore_run_seed_{args.seed}/nuTable.txt')  # <-- alter this later!
nu_mean = np.round(np.mean(nu_interval, axis=1), 4)
print_state('Loaded nuTable.txt')

# Function to create maps, generate astrophysical foregrounds (with PySM), and add CoLoRe (done elsewhere)
def get_maps(nu, nside, coord):
    ''' Get the PySM foreground sky map at a given frequency and Nside,
    and retrieves the CoLoRe HI maps; combines them in the final result (in mK). '''

    # Initial quantities
    sky = pysm3.Sky(nside=nside, preset_strings=["f1","s1","d1","a1","c1"])  # <-- emission models included
    npix = hp.nside2npix(nside)
    if coord in ["C","E"]:  rotator = hp.Rotator(coord=['G',coord])

    # Generate emission maps using PySM3 + CoLoRe + CMB for each frequency
    T = np.zeros((len(nu), npix), dtype=np.float32)
    for i,freq in enumerate(nu):
        fore = (sky.get_emission(freq*pysm3.u.MHz).value[0] + 2.73e6) / 1e3  # <-- convert from uK to mK
        if coord in ["C","E"]:  fore = rotator.rotate_map_pixel(fore)
        fname = f'./colore_seed_{args.seed}_imap_s1_nu{i:03}.fits'
        HImap = hp.ud_grade(hp.read_map(fname), nside_out = nside)  # <-- if nside is always the same, remove the ud_grade step!
        T[i] = fore + HImap
    return T

# Create maps
nside = 512
Ts = get_maps(nu_mean, nside, "G")
print_state("PySM maps generated")
# NECESSARY TO ADD A STEP IN HERE BEAMING THE COMPLETE MAP WITH THE MEERKAT BEAM  XX



# ---------- Perform PCA cleaning and average over the redshift shell considered ----------
# Function to do PCA cleaning
def PCA_cleaning(M, Nfg, remove_mean=True, return_eigen=False):
    ''' Perform PCA cleaning on the input map M, removing Nfg dominant modes;
    returns either the cleaned matrix or the eigenvalues (if return_eigen=True). '''

    # Calculate the covariance matrix
    if remove_mean:  
        M = M - np.mean(M, axis=1, keepdims=True)
        C = np.cov(M)
    else: 
        C = (M @ M.T) / M.shape[1]

    # Get the eigenvalues and eigenvectors
    eigenval,V = np.linalg.eigh(C)
    idx = np.argsort(eigenval)[::-1]
    eigenval = eigenval[idx]
    V = V[:,idx]
    
    # Return the eigenvalues and eigenvectors (probably to be used for plotting or debugging)
    if return_eigen:
        eignumb = np.arange(1,len(eigenval) + 1)
        return eignumb, eigenval, V

    # Project out the Nfg dominant modes and return the cleaned matrix
    V = V[:,:Nfg]
    M -= V @ (V.T @ M)  # <-- more memory-efficient
    return M

# Perform PCA cleaning
Nfg = 4
Ts = PCA_cleaning(Ts, Nfg)

# Average over the redshift shell
redshift_mean = 1420.0 / nu_mean - 1
start = np.abs(redshift_mean - args.lower_z).argmin()
stop = np.abs(redshift_mean - args.upper_z).argmin()
Ts = np.mean(Ts[start:stop + 1], axis=0)
print_state("PCA cleaned")

# Calculate the galactic coordinates for the healpy maps
theta, phi = hp.pix2ang(nside, np.arange(hp.nside2npix(nside)))
ra = np.degrees(phi)
dec = 90.0 - np.degrees(theta)
# A PARTIR DAQUI É CALCULAR O ANGULAR POWER SPECTRUM QUE QUEREMOS (INCLUÍNDO MAIS O EFEITO DA JANELA? PROBABLY)










