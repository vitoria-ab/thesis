"""Plot only CoLoRe inputs and outputs relevant to galaxy distribution and HI intensity mapping."""

# Imports
import sys
import os
import glob
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


def plot_inputs(input_dir, plot_dir):
    ''' Plot inputs for CoLoRe and save them to a directory. '''
    # P(k): input used to generate the cosmological density field.
    data = load_txt(os.path.join(input_dir, "pk.txt"))
    if data is not None:
        k, pk = data[:, 0], data[:, 1]
        good = np.isfinite(k) & np.isfinite(pk) & (k > 0) & (pk > 0)
        plt.figure(figsize=(7, 5))
        plt.loglog(k[good], pk[good])
        plt.xlabel(r"$k\ [h\,\mathrm{Mpc}^{-1}]$")
        plt.ylabel(r"$P(k)\ [(\mathrm{Mpc}/h)^3]$")
        plt.title("Input linear matter power spectrum")
        plt.grid(True, which="both", alpha=0.25)
        save_figure(os.path.join(plot_dir, "input_pk.png"))

    # Galaxy redshift distribution and bias.
    nz_data = load_txt(os.path.join(input_dir, "dndz.txt"))
    bias_data = load_txt(os.path.join(input_dir, "bias.txt"))
    if nz_data is not None:
        fig, ax1 = plt.subplots(figsize=(7, 5))
        ax1.plot(nz_data[:, 0], nz_data[:, 1], label=r"$dN/(dz\,d\Omega)$")
        ax1.set_xlabel("Redshift z")
        ax1.set_ylabel(r"$dN/(dz\,d\Omega)\ [\mathrm{deg}^{-2}]$")
        ax1.grid(True, alpha=0.25)
        if bias_data is not None:
            ax2 = ax1.twinx()
            ax2.plot(bias_data[:, 0], bias_data[:, 1], "--", label="Bias b(z)")
            ax2.set_ylabel("Bias b(z)")
            lines1, labels1 = ax1.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax1.legend(lines1 + lines2, labels1 + labels2, loc="best")
        else:
            ax1.legend()
        ax1.set_title("Input galaxy redshift distribution and bias")
        save_figure(os.path.join(plot_dir, "input_dndz_bias.png"))

    # HI brightness temperature.
    tz_data = load_txt(os.path.join(input_dir, "tz.txt"))
    if tz_data is not None:
        plt.figure(figsize=(7, 5))
        plt.plot(tz_data[:, 0], tz_data[:, 1])
        plt.xlabel("Redshift z")
        plt.ylabel(r"$T_{\rm HI}$ [mK]")
        plt.title("Input HI brightness temperature")
        plt.grid(True, alpha=0.25)
        save_figure(os.path.join(plot_dir, "input_temperature.png"))

    # Frequency bins used for the HI maps.
    nu_data = load_txt(os.path.join(input_dir, "nuTable.txt"))
    if nu_data is not None:
        plt.figure(figsize=(7, 4.5))
        for i, (nu_low, nu_high) in enumerate(nu_data[:, :2]):
            plt.plot([nu_low, nu_high], [i, i], linewidth=5, solid_capstyle="butt")
            plt.text((nu_low + nu_high) / 2, i + 0.12, f"{nu_low:.1f}–{nu_high:.1f} MHz", ha="center", fontsize=8)
        plt.xlabel("Frequency [MHz]")
        plt.ylabel("Frequency-bin index")
        plt.yticks(range(len(nu_data)), [str(i) for i in range(len(nu_data))])
        plt.title("Input HI frequency bins")
        plt.grid(True, axis="x", alpha=0.25)
        save_figure(os.path.join(plot_dir, "input_frequency_bins.png"))


def plot_galaxies(input_dir, plot_dir):
    ''' Plot several plots related to the galaxy catalog and save them to a directory. '''

    catalog_path = os.path.join(input_dir, "colore_srcs_merged.fits")
    with fits.open(catalog_path, memmap=True) as hdul:
        # Get redshift column
        cat = hdul[1].data
        z = np.asarray(cat["Z_COSMO"], dtype=float)

        # Plot histogram of galaxies per redshift
        plt.figure(figsize=(7, 5))
        plt.hist(z, bins=50, histtype="step", linewidth=1.5)
        plt.xlabel(f"Z_COSMO (catalog redshift)")
        plt.ylabel("Number of galaxies")
        plt.title("CoLoRe galaxy redshift distribution")
        plt.grid(True, alpha=0.25)
        save_figure(os.path.join(plot_dir, "output_galaxy_redshift.png"))

        # Galaxy-count overdensity, following the CoLoRe example notebook
        nside = 32
        npix = hp.nside2npix(nside)
        ipix = hp.ang2pix(nside, cat["RA"], cat["DEC"], lonlat=True)
        ncount = np.bincount(ipix, minlength=npix)
        nmean = np.mean(ncount)
        delta = ncount / nmean - 1
        hp.mollview(delta, title=r"$\delta$")
        save_figure(os.path.join(plot_dir, "output_galaxy_overdensity.png"))


def plot_HI(input_dir, plot_dir):
    ''' Plot each HI map and save to a directory. '''
    # Get all files of HI imaging
    pattern = os.path.join(input_dir, f"colore_imap_s1_nu*.fits")
    files = sorted(glob.glob(pattern))

    # Sort through the files and plot each
    for path in files:
        filename = os.path.basename(path)
        i = int(filename.split("_nu")[-1].replace(".fits", ""))
        sky_map = hp.read_map(path)
        title = f"CoLoRe HI intensity map (bin {i})"
        hp.mollview(sky_map, title=title, unit="mK", cbar=True)
        save_figure(os.path.join(plot_dir, f"output_hi_imap_nu{i:03d}.png"))

# Create directories
input_dir = os.path.abspath("/projects/F202315069PEXF1/vitoria/running_colore/" + sys.argv[1])
plot_dir = os.path.join(input_dir, "plots")
os.makedirs(plot_dir, exist_ok=True)
print(f"Input/output directory: {input_dir}")
print(f"Saving plots to: {plot_dir}")

# Plot results into directory
plot_inputs(input_dir, plot_dir)
plot_galaxies(input_dir, plot_dir)
plot_HI(input_dir, plot_dir)
print("Finished!")

