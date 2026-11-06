#!/bin/bash
#SBATCH --account=f202315069pexf1a
#SBATCH --job-name=script9_download_healpy_weights
#SBATCH --time=00:20:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --partition=dev-arm
#SBATCH --output=script9_download_healpy_weights_%j.out

module load Anaconda3
module load GSL
module load FFTW

eval "$(conda shell.bash hook)"
conda activate /projects/F202315069PEXF1/vitoria/envs/env_thesis

# Set persistent Astropy cache directory
export XDG_CACHE_HOME="$HOME/.cache"
mkdir -p "${XDG_CACHE_HOME}/astropy"

# Download nside pixel weights for Healpy
echo "=== Downloading Healpy files for heracles ==="
python script9_download_healpy_weights.py
echo "=== Finished! ==="

