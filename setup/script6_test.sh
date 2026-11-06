#!/bin/bash
#SBATCH --job-name=test
#SBATCH --partition=dev-arm
#SBATCH --account=f202315069pexf1a
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=00:05:00
#SBATCH --output=test_%j.out

set -e

module purge
module load Anaconda3
module load GCC
module load GSL
module load FFTW

eval "$(conda shell.bash hook)"
conda activate /projects/F202315069PEXF1/vitoria/envs/env_thesis

echo "===== Checking package compatibility ====="

python - <<'PY'
import numpy
import scipy
import astropy
import healpy
import pyccl
import heracles

print("NumPy:", numpy.__version__)
print("SciPy:", scipy.__version__)
print("Astropy:", astropy.__version__)
print("healpy:", healpy.__version__)
print("PyCCL:", pyccl.__file__)
print("Heracles:", heracles.__file__)

print("\nAll package imports successful!")
PY

echo "===== Finished successfully ====="