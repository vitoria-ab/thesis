#!/bin/bash
#SBATCH --account=f202315069pexf1a
#SBATCH --job-name=galaxy_cls_theory
#SBATCH --time=00:10:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --partition=normal-arm
#SBATCH --output=galaxy_cls_theory_%j.out

# Load modules and activate conda environment
module load Anaconda3
module load GSL
module load FFTW
eval "$(conda shell.bash hook)"
conda activate /projects/F202315069PEXF1/vitoria/envs/env_thesis

# Run file
echo "Computing Cls with theoretical model ($2-$3) from $1..."
python galaxy_cls_theory.py $1 $2 $3
echo "Finished!"