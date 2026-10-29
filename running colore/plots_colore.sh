#!/bin/bash
#SBATCH --account=f202315069pexf1a
#SBATCH --job-name=plots_colore
#SBATCH --time=00:10:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=1G
#SBATCH --partition=normal-arm
#SBATCH --output=plots_colore_%j.out

module load Anaconda3
module load GSL
module load FFTW
eval "$(conda shell.bash hook)"
conda activate /projects/F202315069PEXF1/vitoria/envs/env_thesis

echo "Plotting results from $1..."
python plots_colore.py $1
echo "Finished!"