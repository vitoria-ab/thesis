#!/bin/bash
#SBATCH --account=f202315069pexf1a
#SBATCH --job-name=script12_install_namaster
#SBATCH --partition=dev-arm
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=6G
#SBATCH --time=00:30:00
#SBATCH --output=script12_install_namaster_%j.out

set -euo pipefail

# Load necessary modules and activate the conda environment
echo "===== Setting up environment ====="
module purge
module load Anaconda3
module load GCC
module load OpenMPI
module load GSL
module load FFTW
module load FFTW.MPI
module load CFITSIO
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate /projects/F202315069PEXF1/vitoria/envs/env_thesis

# Compiler and dependency paths
export GSL_DIR="/eb/aarch64/software/GSL/2.8-GCC-14.3.0"
export FFTW_DIR="/eb/aarch64/software/FFTW/3.3.10-llvm-compilers-21.1.8"
export CFITSIO_DIR="/eb/aarch64/software/CFITSIO/4.6.2-GCCcore-14.3.0"
export HEALPIX_DIR="/home/vitoria.ab/packages/CoLoRe/Healpix_3.83"
export CPPFLAGS="-I${GSL_DIR}/include -I${FFTW_DIR}/include -I${CFITSIO_DIR}/include -I${HEALPIX_DIR}/include"
export LDFLAGS="-L${GSL_DIR}/lib -L${FFTW_DIR}/lib -L${CFITSIO_DIR}/lib -L${HEALPIX_DIR}/lib"
export LIBS="-lcfitsio -lchealpix"
export LD_LIBRARY_PATH="${GSL_DIR}/lib:${FFTW_DIR}/lib:${CFITSIO_DIR}/lib:${HEALPIX_DIR}/lib:${LD_LIBRARY_PATH:-}"

# Make sure the existing Python dependencies are available
echo "===== Checking Python environment ====="
python -c "import numpy, scipy, astropy; print('NumPy:', numpy.__version__); print('SciPy:', scipy.__version__); print('Astropy:', astropy.__version__)"

# Check HEALPix library
echo "===== Checking HEALPix ====="
HEALPIX_LIB="${HEALPIX_DIR}/lib/libchealpix.a"
HEALPIX_HEADER="${HEALPIX_DIR}/include/chealpix.h"
if [[ ! -f "$HEALPIX_LIB" || ! -f "$HEALPIX_HEADER" ]]; then
    echo "ERROR: HEALPix library or header not found."
    exit 1
fi
echo "Library:"
file "$HEALPIX_LIB"

# Check for ring2nest symbol in the HEALPix library
echo "Checking ring2nest symbol..."
if ! nm -g --defined-only "$HEALPIX_LIB" | grep -qE '[[:space:]]ring2nest$'; then
    echo "ERROR: ring2nest was not found in libchealpix.a."
    echo "The existing HEALPix library cannot be used for this NaMaster build."
    exit 1
fi
if ! grep -q "ring2nest" "$HEALPIX_HEADER"; then
    echo "ERROR: ring2nest was not found in chealpix.h."
    exit 1
fi

# Check that HEALPix was compiled with -fPIC
echo "Checking position-independent code..."
TEMP_DIR=$(mktemp -d)
trap 'rm -rf "$TEMP_DIR"' EXIT
ar p "$HEALPIX_LIB" chealpix.s.o > "$TEMP_DIR/chealpix.s.o"
if readelf -r "$TEMP_DIR/chealpix.s.o" | grep -q "R_AARCH64_ADR_PREL_PG_HI21.*stderr"; then
    echo "ERROR: HEALPix object still contains a non-PIC stderr relocation."
    exit 1
fi
echo "HEALPix symbol, header and PIC checks passed."

# Build directory
BUILD_DIR="/home/vitoria.ab/packages/pymaster_build"
mkdir -p "$BUILD_DIR"
cd "$BUILD_DIR"

# Remove previous extracted source and build artefacts
echo "===== Removing previous source/build files ====="
rm -rf pymaster-3.0.1

# Download NaMaster source
echo "===== Downloading NaMaster ====="
if [[ ! -f pymaster-3.0.1.tar.gz ]]; then
    python -m pip download --no-deps --no-binary=:all: --no-build-isolation --no-cache-dir pymaster==3.0.1
else
    echo "Using existing source tarball."
fi

# Extract source
echo "===== Extracting fresh source ====="
tar -xzf pymaster-3.0.1.tar.gz
cd pymaster-3.0.1

# Configure HEALPix linking
echo "===== Linking existing HEALPix installation ====="
mkdir -p _deps/lib _deps/include
ln -sfn "$HEALPIX_LIB" _deps/lib/libchealpix.a
ln -sfn "$HEALPIX_HEADER" _deps/include/chealpix.h

# Check HEALPix symlinks
if [[ ! -f _deps/lib/libchealpix.a || ! -f _deps/include/chealpix.h ]]; then
    echo "ERROR: HEALPix symlinks were not created correctly."
    exit 1
fi
echo "Using HEALPix library: $(readlink -f _deps/lib/libchealpix.a)"
echo "Using HEALPix header: $(readlink -f _deps/include/chealpix.h)"

# Install NaMaster
echo "===== Installing NaMaster ====="
python -m pip install --no-build-isolation --no-deps --no-cache-dir --force-reinstall .

# Verify installation
echo "===== Verifying installation ====="
python -c "import pymaster; print('NaMaster version:', pymaster.__version__)"
echo "===== Installation completed ====="
