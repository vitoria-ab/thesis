# Imports
import healpy as hp
import numpy as np
from astropy.config.paths import get_cache_dir_path

# Check that we changed the cache directory correctly
cache_dir = get_cache_dir_path()
print(f"Astropy cache directory: {cache_dir}")

# Download pixel weights and pixel window functions
nsides = [32, 64, 128, 256, 512, 1024]
for nside in nsides:
    print(f"For nside ={nside}:", end=" ")
    print(f"Downloading healpy weights...", end=" ")
    dummy_map = np.zeros(hp.nside2npix(nside), dtype=np.float64)
    hp.map2alm(dummy_map, lmax=0, pol=False, use_pixel_weights=True)

    print(f"Downloading pixel window function...")
    hp.pixwin(nside, lmax=3 * nside - 1)

print("\nAll healpy files downloaded successfully!")
