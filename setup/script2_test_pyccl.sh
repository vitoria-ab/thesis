#!/bin/bash
#SBATCH --account=f202315069pexf1a
#SBATCH --partition=normal-arm
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=00:02:00
#SBATCH --output=script2_test_pyccl_%j.out

# Load conda environment
set -e
module load Anaconda3
module load GSL
module load FFTW
eval "$(conda shell.bash hook)"
conda activate /projects/F202315069PEXF1/vitoria/envs/env_thesis

# Checking pyCCL version
echo "===== Checking PyCCL ====="
python - <<'PY'
import pyccl as ccl

print("PyCCL version:", getattr(ccl, "__version__", "unknown"))
print("PyCCL location:", ccl.__file__)
print("Cosmology signature:", __import__("inspect").signature(ccl.Cosmology))

cosmo = ccl.Cosmology(
    Omega_c=0.25,
    Omega_b=0.05,
    h=0.7,
    n_s=0.96,
    sigma8=0.8
)

pk = ccl.linear_matter_power(cosmo, 0.1, 1.0)
print("Linear matter power P(k=0.1, z=0):", pk)

assert pk > 0, "Power spectrum must be positive"
print("PyCCL test passed.")
PY