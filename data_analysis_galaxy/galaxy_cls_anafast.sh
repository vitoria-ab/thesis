#!/bin/bash
#SBATCH --account=f202315069pexf1a
#SBATCH --job-name=galaxy_cls_anafast
#SBATCH --time=00:05:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=12G
#SBATCH --partition=normal-arm
#SBATCH --output=galaxy_cls_anafast_%j.out

module load Anaconda3
module load GSL
module load FFTW
eval "$(conda shell.bash hook)"
conda activate /projects/F202315069PEXF1/vitoria/envs/env_thesis

echo "Computing Cls with anafast ($2-$3) from $1..."
python galaxy_cls_anafast.py $1 $2 $3
echo "Finished!"