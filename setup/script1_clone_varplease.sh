#!/bin/bash
#SBATCH --account=f202315069pexf1a
#SBATCH --partition=dev-arm
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=01:00:00
#SBATCH --output=script1_clone_varplease_%j.out

# Load the Anaconda module
module load Anaconda3
# Initialize Conda for Bash
eval "$(conda shell.bash hook)"
# Change cache directory to project folder (instead of personal folder)
export CONDA_PKGS_DIRS=/projects/F202315069PEXF1/vitoria/conda_pkgs
# Activate environment
conda activate ../../variance/envs/var_please

# Inspect the environment
echo "===== Environment path ====="
echo "$CONDA_PREFIX"
echo "===== Python executable ====="
which python
echo "===== Python version ====="
python --version
echo "===== Installed packages ====="
conda list

# Export the environment specification
echo "===== Exporting environment specification ====="
conda env export > var_please_environment.yml

# Create an independent copy of the environment
echo "===== Cloning environment ====="
conda create --prefix ../../vitoria/envs/env_thesis --clone "$CONDA_PREFIX"
echo "===== Finished ====="