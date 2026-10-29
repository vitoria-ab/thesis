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
    if not os.path.isfile(path):
        warnings.warn(f"Missing input file: {path}")
        return None
    data = np.loadtxt(path)
    if data.ndim == 1:
        data = data[None, :]
    if data.shape[1] < 2:
        warnings.warn(f"Expected at least two columns in {path}")
        return None
    return data

# Function to plot CoLoRe inputs
def plot_inputs(input_dir, plot_dir):
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

# Function to plot healpix map (not sure what this is)
def plot_healpix_map(path, title, output_path, unit=None):
    if not os.path.isfile(path):
        warnings.warn(f"Missing map: {path}")
        return
    sky_map = hp.read_map(path)
    hp.mollview(sky_map, title=title, unit=unit, cbar=True)
    save_figure(output_path)

def plot_galaxy_catalog(catalog_path, plot_dir):
    if not os.path.isfile(catalog_path):
        warnings.warn(f"Missing CoLoRe source catalogue: {catalog_path}")
        return

    with fits.open(catalog_path, memmap=True) as hdul:
        cat = hdul[1].data
        names = list(cat.dtype.names or [])
        lower_to_actual = {name.lower(): name for name in names}

        z_name = next((lower_to_actual[n] for n in ("z", "z_cosmo", "zcosmo", "z_obs", "z_rsd", "redshift") if n in lower_to_actual), None)
        if z_name is not None:
            z = np.asarray(cat[z_name], dtype=float)
            z = z[np.isfinite(z)]
            if z.size:
                plt.figure(figsize=(7, 5))
                plt.hist(z, bins=50, histtype="step", linewidth=1.5)
                plt.xlabel(f"{z_name} (catalogue redshift)")
                plt.ylabel("Number of galaxies")
                plt.title("CoLoRe galaxy redshift distribution")
                plt.grid(True, alpha=0.25)
                save_figure(os.path.join(plot_dir, "output_galaxy_redshift.png"))
        else:
            warnings.warn(f"No recognized redshift field in catalogue; available columns: {names}")

        ra_name = lower_to_actual.get("ra")
        dec_name = lower_to_actual.get("dec")
        if ra_name is None or dec_name is None:
            warnings.warn(f"Catalogue has no recognizable RA/DEC columns; available columns: {names}")
            return

        # Galaxy-count overdensity, following the CoLoRe example notebook
        nside = 32
        npix = hp.nside2npix(nside)
        ipix = hp.ang2pix(nside, cat[ra_name], cat[dec_name], lonlat=True)
        ncount = np.bincount(ipix, minlength=npix)
        nmean = np.mean(ncount)
        delta = ncount / nmean - 1

        hp.mollview(delta, title=r"$\delta$")
        save_figure(os.path.join(plot_dir, "output_galaxy_overdensity.png"))

# Function to plot HI maps
def plot_hi_maps(input_dir, plot_dir, prefix):
    nu_data = load_txt(os.path.join(input_dir, "nuTable.txt"))
    if nu_data is None:
        return
    for i, (nu_low, nu_high) in enumerate(nu_data[:, :2]):
        nu_mid = 0.5 * (nu_low + nu_high)
        filename = f"{prefix}_imap_s1_nu{i:03d}.fits"
        path = os.path.join(input_dir, filename)
        plot_healpix_map(path, f"CoLoRe HI intensity map (nu={nu_mid:.2f} MHz)", os.path.join(plot_dir, f"output_hi_imap_nu{i:03d}.png"), unit="mK")

# Create directories
input_dir = os.path.abspath(sys.argv[1])
plot_dir = os.path.join(input_dir, "plots")
prefix = "colore"
os.makedirs(plot_dir, exist_ok=True)
print(f"Input/output directory: {input_dir}")
print(f"Saving plots to: {plot_dir}")

# Plot results into directory
plot_inputs(input_dir, plot_dir)
plot_galaxy_catalog(os.path.join(input_dir, f"{prefix}_srcs_s1_0.fits"), plot_dir)
plot_hi_maps(input_dir, plot_dir, prefix)
print("Done. Review warnings above for missing files or catalogue fields.")

