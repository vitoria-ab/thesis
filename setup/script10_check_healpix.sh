#!/bin/bash
#SBATCH --account=f202315069pexf1a
#SBATCH --job-name=script10_check_healpix
#SBATCH --partition=dev-arm
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --time=00:05:00
#SBATCH --output=script10_check_healpix_%j.out

# Load modules
module purge
module load GCC
module load OpenMPI
module load GSL
module load FFTW
module load FFTW.MPI
module load CFITSIO
module load libconfig
module load Anaconda3

# Activate environment
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate /projects/F202315069PEXF1/vitoria/envs/env_thesis

# Define correct paths
HEALPIX_DIR="/home/vitoria.ab/packages/CoLoRe/Healpix_3.83"
BUILD_DIR="/home/vitoria.ab/packages/pymaster_build/pymaster-3.0.1"

# Get debug information
echo "===== Compiler ====="
which gcc
which mpicc

echo "===== Environment variables ====="
echo "CPPFLAGS=$CPPFLAGS"
echo "LDFLAGS=$LDFLAGS"
echo "LIBS=$LIBS"

echo "===== HEALPix library ====="
ls -lh "$HEALPIX_DIR/lib/libchealpix.a"
file "$HEALPIX_DIR/lib/libchealpix.a"

echo "===== HEALPix symbols ====="
nm -A -g --defined-only "$HEALPIX_DIR/lib/libchealpix.a" | grep ring2nest || true

echo "===== HEALPix header ====="
grep -n -B 3 -A 3 ring2nest "$HEALPIX_DIR/include/chealpix.h" || true

echo "===== NaMaster config.log ====="
find "$BUILD_DIR" -name config.log -print

echo "===== ring2nest linker diagnostics ====="
find "$BUILD_DIR" -name config.log -exec grep -n -B 10 -A 20 ring2nest {} \; || true
echo "===== Finished ====="
