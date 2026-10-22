#!/bin/bash
#SBATCH --account=f202315069pexf1a
#SBATCH --job-name=generate_colore_inputs
#SBATCH --time=00:02:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=1G
#SBATCH --partition=normal-arm
#SBATCH --output=generate_colore_inputs_slurm_%j.out

# Load modules
module load Anaconda3

# Activate the Python environment
eval "$(conda shell.bash hook)"
conda activate ../variance/envs/var_please

# Run the script
echo "Starting generate_colore_inputs..."
python generate_colore_inputs.py
echo "Finished generate_colore_inputs!"