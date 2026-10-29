#!/bin/bash
#SBATCH --account=f202315069pexf1a
#SBATCH --partition=dev-arm
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=00:10:00
#SBATCH --output=script3_check_packages_%j.out

# Initialize conda environment
set -e
module purge
module load Anaconda3
module load GCC
module load GSL
module load FFTW
eval "$(conda shell.bash hook)"
conda activate /projects/F202315069PEXF1/vitoria/envs/env_thesis

# Install libconf
echo "===== Installing libconf ====="
python -m pip install libconf

# Check if necessary packages are working correctly
echo "===== Verifying required packages ====="
python - <<'PY'
import libconf
import numpy
import scipy
import astropy
import healpy
import pyccl

print("libconf:", libconf.__file__)
print("NumPy:", numpy.__version__)
print("SciPy:", scipy.__version__)
print("Astropy:", astropy.__version__)
print("healpy:", healpy.__version__)
print("PyCCL:", pyccl.__file__)
print("All package checks passed.")
PY

echo "===== Finished successfully ====="
