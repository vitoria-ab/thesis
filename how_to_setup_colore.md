# README — Building and Running CoLoRe on the Cluster

## 1. Paths and dependencies

CoLoRe is installed at:

```bash
/home/vitoria.ab/packages/CoLoRe
```

The HEALPix installation used by CoLoRe is:

```bash
/home/vitoria.ab/packages/CoLoRe/Healpix_3.83
```

Dependencies used for the successful build:
- GCC
- OpenMPI
- GSL
- FFTW
- FFTW.MPI
- CFITSIO
- libconfig
- HEALPix (`libchealpix.a`)

## 2. Load the required modules

Before compiling or running CoLoRe, load the required modules:

```bash
module load GCC
module load OpenMPI
module load GSL
module load FFTW
module load FFTW.MPI
module load CFITSIO
module load libconfig
```

Check the loaded modules with:

```bash
module list
```

For reproducibility, use the same module versions as the successful build whenever possible.

## 3. Rebuild HEALPix with `-fPIC` (one-time fix)

The original CoLoRe build failed during linking with errors such as:

```text
relocation R_X86_64_32 cannot be used against local symbol; recompile with -fPIC
```

The problem was that the static HEALPix library, `libchealpix.a`, had been compiled without `-fPIC`. CoLoRe links against the installed copy in `Healpix_3.83/lib/`, so rebuilding the library alone was not sufficient: the rebuilt copy also had to be installed there.

### Step 3.1 — Go to the HEALPix directory

```bash
cd /home/vitoria.ab/packages/CoLoRe/Healpix_3.83
```

### Step 3.2 — Clean the old build

```bash
make -C src/C/subs clean
```

### Step 3.3 — Compile the static library with `-fPIC`

Use `FLAGS`, not `CFLAGS`, because this HEALPix Makefile uses the variable `FLAGS`.

```bash
make -C src/C/subs static PIC=-fPIC FLAGS="-O2 -Wall -fPIC -DENABLE_FITSIO -I/eb/x86_64/software/CFITSIO/4.6.4-GCCcore-15.2.0/include"
```

The compilation command should include both:

```text
-fPIC
-I/eb/x86_64/software/CFITSIO/4.6.4-GCCcore-15.2.0/include
```

A successful build should finish without errors and create:

```text
src/C/subs/libchealpix.a
```

### Step 3.4 — Copy the rebuilt library to the installed location

**This step is essential.** CoLoRe links against the library in `Healpix_3.83/lib/`, not directly against the copy in `src/C/subs/`.

```bash
cp src/C/subs/libchealpix.a lib/libchealpix.a
```

## 4. Compile CoLoRe

Go to the CoLoRe directory:

```bash
cd /home/vitoria.ab/packages/CoLoRe
```

Compile:

```bash
make
```

If the build succeeds, the executable should be available at:

```text
/home/vitoria.ab/packages/CoLoRe/CoLoRe
```

You do not normally need to repeat the HEALPix rebuild every time you use CoLoRe. Repeat it if you rebuild HEALPix or encounter the same linker error again.

## 5. Running CoLoRe

Whenever you open a new session or submit a new SLURM job, load the required modules before running CoLoRe.

For example, a SLURM script can include:

```bash
module load GCC
module load OpenMPI
module load GSL
module load FFTW
module load FFTW.MPI
module load CFITSIO
module load libconfig

cd /home/vitoria.ab/packages/CoLoRe

./CoLoRe your_config.cfg
```

Replace `your_config.cfg` with the path to your actual configuration file. Keep any additional environment variables required by your setup, including library paths, in the SLURM script.

## 6. Troubleshooting

### `mpicc: Command not found`

The MPI compiler is not available in the current environment.

```bash
module load OpenMPI
which mpicc
```

If `which mpicc` returns a path, try compiling again.

### `fitsio.h: No such file or directory`

The CFITSIO header path is missing from the compilation flags. Check that the header exists:

```bash
ls /eb/x86_64/software/CFITSIO/4.6.4-GCCcore-15.2.0/include/fitsio.h
```

The HEALPix compilation command must include the corresponding `-I` path.

### `relocation ... recompile with -fPIC`

Rebuild the HEALPix static library using the commands in Section 3, and make sure to copy the new archive into `Healpix_3.83/lib/libchealpix.a`.

### CoLoRe cannot find a shared library when running

Check that the required modules are loaded and that the runtime library paths are correctly configured. A successful compilation does not guarantee that every runtime dependency will be available.

## 7. Important notes

- The HEALPix rebuild and library copy are build-time steps, not steps to repeat for every simulation.
- Load the required modules in every new terminal session or SLURM job.
- Use the same compiler and MPI toolchain used for the successful build.
- The Makefile currently uses `/home/damonge/include` and `/home/damonge/lib` for GSL. These are paths belonging to another user; if they become unavailable, update the CoLoRe Makefile to use the appropriate GSL paths from your environment.
- Test a small simulation before launching a large production run.
