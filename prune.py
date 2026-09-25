"""Strip build-only and doc files from the pixi env so the runtime image stays small."""

import json
import os
import shutil
import subprocess
from pathlib import Path

PREFIX = Path(os.environ["PRUNE_PREFIX"])

# Compiler toolchain (only needed to build R/Python packages from source) and
# pandoc (only needed for RMarkdown / PDF export, and there is no LaTeX anyway).
# Runtime libs like libgcc, libstdcxx and libgfortran are deliberately kept.
PACKAGES = {
    "binutils_impl_linux-64",
    "binutils_linux-64",
    "gcc_impl_linux-64",
    "gcc_linux-64",
    "gfortran_impl_linux-64",
    "gxx_impl_linux-64",
    "gxx_linux-64",
    "kernel-headers_linux-64",
    "libgcc-devel_linux-64",
    "libstdcxx-devel_linux-64",
    "sysroot_linux-64",
    "pandoc",
}

# Whole directories nothing at runtime reads.
DIRS = [
    "include",
    "share/man",
    "share/info",
    "share/doc",
    "share/gtk-doc",
]

# Glob patterns: static libs, R vignettes/tests, Python test suites, bytecode.
GLOBS = [
    "**/*.a",
    "lib/R/library/*/doc",
    "lib/R/library/*/tests",
    "lib/python3.*/site-packages/**/tests",
    "**/__pycache__",
]

before = subprocess.run(["du", "-sm", PREFIX], capture_output=True, text=True).stdout.split()[0]

removed_pkgs = []
for meta in (PREFIX / "conda-meta").glob("*.json"):
    info = json.loads(meta.read_text())
    if info.get("name") not in PACKAGES:
        continue
    for rel in info.get("files", []):
        p = PREFIX / rel
        if p.is_symlink() or p.is_file():
            p.unlink()
    meta.unlink()
    removed_pkgs.append(info["name"])

for d in DIRS:
    shutil.rmtree(PREFIX / d, ignore_errors=True)

for pattern in GLOBS:
    for p in list(PREFIX.glob(pattern)):
        if p.is_dir() and not p.is_symlink():
            shutil.rmtree(p, ignore_errors=True)
        elif p.exists() or p.is_symlink():
            p.unlink()

for dirpath, dirnames, filenames in os.walk(PREFIX, topdown=False):
    if not dirnames and not filenames and Path(dirpath) != PREFIX:
        os.rmdir(dirpath)

after = subprocess.run(["du", "-sm", PREFIX], capture_output=True, text=True).stdout.split()[0]
missing = PACKAGES - set(removed_pkgs)
print(f"pruned {len(removed_pkgs)} packages; {before} MB -> {after} MB")
if missing:
    print(f"warning: not found in env: {sorted(missing)}")
