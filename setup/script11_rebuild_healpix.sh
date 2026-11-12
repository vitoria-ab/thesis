#!/bin/bash
#SBATCH --account=f202315069pexf1a
#SBATCH --job-name=script11_rebuild_healpix
#SBATCH --partition=dev-arm
#SBATCH --time=00:05:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --mem=6G
#SBATCH --cpus-per-task=1
#SBATCH --output=script11_rebuild_healpix_%j.out

# Load necessary modules
set -euo pipefail
echo "===== Loading modules ====="
module purge
module load GCC
module load OpenMPI
module load GSL
module load FFTW
module load FFTW.MPI
module load CFITSIO
module load libconfig

# Define HEALPix paths
HEALPIX_DIR="/home/vitoria.ab/packages/CoLoRe/Healpix_3.83"
SOURCE="${HEALPIX_DIR}/src/C/subs/chealpix.c"
LIB="${HEALPIX_DIR}/lib/libchealpix.a"
HEADER="${HEALPIX_DIR}/include/chealpix.h"
CC=$(which gcc)
AR=$(which ar)

# Check if the HEALPix library and header exist
echo "===== Checking files ====="
if [[ ! -f "$SOURCE" || ! -f "$LIB" || ! -f "$HEADER" ]]; then
    echo "ERROR: Required HEALPix files not found."
    exit 1
fi
echo "Source: $SOURCE"
echo "Compiler: $CC"

# Preserve original library if not already backed up
BACKUP="${LIB}.original"
if [[ ! -f "$BACKUP" ]]; then
    cp "$LIB" "$BACKUP"
    echo "Original library backed up."
else
    echo "Original backup already exists."
fi

# Temporary build directory
TEMP_DIR=$(mktemp -d "${HEALPIX_DIR}/tmp_rebuild.XXXXXX")
trap 'rm -rf "$TEMP_DIR"' EXIT

# Compile HEALPix with -fPIC
echo "===== Compiling HEALPix with -fPIC ====="
"$CC" -fPIC -O2 -I"${HEALPIX_DIR}/include" -I"${HEALPIX_DIR}/src/C/subs" \
    -c "$SOURCE" -o "$TEMP_DIR/chealpix.s.o"

echo "===== Creating static library ====="
"$AR" rcs "$TEMP_DIR/libchealpix.a" "$TEMP_DIR/chealpix.s.o"

echo "===== Checking symbols ====="
nm -g --defined-only "$TEMP_DIR/libchealpix.a" | grep ring2nest

# Test linking with a shared library
echo "===== Testing shared-library linking ====="
"$CC" -shared -o "$TEMP_DIR/test.so" \
    -Wl,-z,defs \
    -Wl,--whole-archive "$TEMP_DIR/libchealpix.a" \
    -Wl,--no-whole-archive -lm
echo "Shared-library test passed."

echo "===== Replacing HEALPix library ====="
cp "$TEMP_DIR/libchealpix.a" "${LIB}.new"
mv "${LIB}.new" "$LIB"

echo "===== Finished ====="
echo "New library installed: $LIB"
echo "Original library preserved: $BACKUP"
