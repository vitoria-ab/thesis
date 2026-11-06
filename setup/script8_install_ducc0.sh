#!/bin/bash
#SBATCH --account=f202315069pexf1a
#SBATCH --job-name=script8_install_ducc0
#SBATCH --time=00:10:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --partition=dev-arm
#SBATCH --output=script8_install_ducc0_%j.out

set -e

# Load modules
module purge
module load Anaconda3
module load GCC
module load GSL
module load FFTW

# Activate environment
eval "$(conda shell.bash hook)"
conda activate /projects/F202315069PEXF1/vitoria/envs/env_thesis

# Install ducc0
echo "===== Installing ducc0 ====="
python -m pip install ducc0

# Verify
echo "===== Verifying installation ====="
python - <<'PY'
import ducc0
import heracles.ducc
print("ducc0:", ducc0.__file__)
print("Heracles DUCC module imported successfully.")
PY
echo "===== Finished successfully ====="
