# syntax=docker/dockerfile:1

# Stage 1: solve and install the pixi environment. Nothing from this stage
# except the finished env directory reaches the final image.
FROM ghcr.io/prefix-dev/pixi:0.81.0 AS build

WORKDIR /opt/data730
COPY pixi.toml pixi.lock ./
RUN --mount=type=cache,target=/root/.cache/rattler \
    pixi install --locked -e default

ENV PATH=/opt/data730/.pixi/envs/default/bin:$PATH

# Kernelspecs go under the env prefix so they travel with it.
RUN python -m ipykernel install --sys-prefix --name python3 --display-name "Python 3 (pixi)" \
 && R -e 'IRkernel::installspec(sys_prefix = TRUE, displayname = "R (pixi)")'

# Strip the compiler toolchain, pandoc, docs, tests and other build-only files.
COPY prune.py /tmp/prune.py
RUN PRUNE_PREFIX=/opt/data730/.pixi/envs/default python /tmp/prune.py

# Stage 2: runtime image. Devcontainer base gives us git, sudo and the vscode
# user that Codespaces expects.
FROM mcr.microsoft.com/devcontainers/base:ubuntu-24.04

LABEL org.opencontainers.image.source=https://github.com/UNC-DATA-730/env \
      org.opencontainers.image.description="DATA 730 course environment: Python, R, JupyterLab and course packages"

# Same absolute path as the build stage: conda envs are not relocatable.
COPY --from=build --chown=vscode:vscode /opt/data730/.pixi/envs/default /opt/data730/.pixi/envs/default

# The env's bin dir on PATH is what lets GitHub's "Open in JupyterLab" find jupyter.
ENV PATH=/opt/data730/.pixi/envs/default/bin:$PATH
