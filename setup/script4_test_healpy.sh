#!/bin/bash
#SBATCH --job-name=script4_test_healpy
#SBATCH --partition=normal-arm
#SBATCH --account=f202315069pexf1a
#SBATCH --time=00:05:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --output=script4_test_healpy_%j.out

module load Anaconda3

eval "$(conda shell.bash hook)"
conda activate /projects/F202315069PEXF1/vitoria/envs/env_thesis

echo "===== Checking healpy ====="
python - <<'PY'
import healpy as hp
print("healpy version:", hp.__version__)
print("healpy imported successfully.")
PY