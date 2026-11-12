#!/bin/bash
#SBATCH --account=f202315069pexf1a
#SBATCH --job-name=colore_inputs
#SBATCH --time=00:30:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=10G
#SBATCH --partition=normal-arm
#SBATCH --output=colore_inputs_%j.out

# Load modules and conda environment
module load Anaconda3
module load GSL
module load FFTW
eval "$(conda shell.bash hook)"
conda activate /projects/F202315069PEXF1/vitoria/envs/env_thesis

# Run the specified python script
echo "Generating CoLoRe inputs for $1\_$2-$3..."
python colore_inputs.py $1 $2 $3
echo "Finished!"