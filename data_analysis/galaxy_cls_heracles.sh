#!/bin/bash
#SBATCH --account=f202315069pexf1a
#SBATCH --job-name=galaxy_cls_heracles
#SBATCH --time=00:20:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=12G
#SBATCH --partition=normal-arm
#SBATCH --output=galaxy_cls_heracles_%j.out

# Load modules and activate conda environment
module load Anaconda3
module load GSL
module load FFTW
eval "$(conda shell.bash hook)"
conda activate /projects/F202315069PEXF1/vitoria/envs/env_thesis

# Cache has the pixel weight maps
export XDG_CACHE_HOME="$HOME/.cache"
mkdir -p "${XDG_CACHE_HOME}/astropy"

# Run file
echo "Computing Cls with Heracles ($2-$3) from $1..."
python galaxy_cls_heracles.py $1 $2 $3
echo "Finished!"