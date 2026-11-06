#!/bin/bash
#SBATCH --job-name=script7_create_kernel
#SBATCH --account=f202315069pexf1a
#SBATCH --partition=dev-arm
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=01:00:00
#SBATCH --output=script7_create_kernel_%j.out

# Activate environment
module load Anaconda3
eval "$(conda shell.bash hook)"
export CONDA_PKGS_DIRS=/projects/F202315069PEXF1/vitoria/conda_pkgs
conda activate /projects/F202315069PEXF1/vitoria/envs/env_thesis

# Install ipykernel and register
python -m pip install ipykernel
python -m ipykernel install --user --name=env_thesis --display-name="Python (env_thesis)"
echo "===== Kernel successfully registered! ====="