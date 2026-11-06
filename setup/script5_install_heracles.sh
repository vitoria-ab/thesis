#!/bin/bash
#SBATCH --account=f202315069pexf1a
#SBATCH --partition=dev-arm
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=00:12:00
#SBATCH --output=script5_install_heracles_%j.out

# Import necessary modules
set -e
module purge
module load Anaconda3
module load GCC
module load GSL
module load FFTW

eval "$(conda shell.bash hook)"
conda activate /projects/F202315069PEXF1/vitoria/envs/env_thesis

# Downgrade scipy
echo "===== Downgrading SciPy ====="
python -m pip install scipy==1.16.3

# Install Heracles
echo "===== Installing Heracles ====="
python -m pip install heracles

# Verify installation
echo "===== Verifying Heracles ====="
python - <<'PY'
import heracles
print("Heracles:", heracles.__file__)
print("Heracles imported successfully.")
PY
echo "===== Finished successfully ====="