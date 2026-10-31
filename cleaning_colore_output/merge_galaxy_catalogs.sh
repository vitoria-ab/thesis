#!/bin/bash
#SBATCH --account=f202315069pexf1a
#SBATCH --job-name=merge_galaxy_catalogs
#SBATCH --time=00:10:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --partition=normal-arm
#SBATCH --output=merge_galaxy_catalogs_%j.out

module load Anaconda3
eval "$(conda shell.bash hook)"
conda activate /projects/F202315069PEXF1/vitoria/envs/env_thesis

echo "Merging results from $1..."
python merge_galaxy_catalogs.py $1
echo "Finished!"