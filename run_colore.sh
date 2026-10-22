#!/bin/bash
#SBATCH --job-name=run_colore
#SBATCH --account=f202315069pexf1a
#SBATCH --partition=normal-arm
#SBATCH --nodes=16  # <-- XX
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --time=10:00:00  # <-- XX

module purge

module load GCC
module load OpenMPI
module load GSL
module load FFTW
module load FFTW.MPI
module load CFITSIO
module load libconfig

export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/home/OLD_USERNAME/ScienceCodes/CoLoRe/Healpix_3.83/lib  # <-- XX

cd /home/roger02/project/projects/variance/colore_run_seed_1000

srun --cpu-bind=none /home/roger02/ScienceCodes/CoLoRe/CoLoRe ./params.cfg