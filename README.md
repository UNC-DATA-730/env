# DATA 730 course environment image

Prebuilt Docker image with Python, R, JupyterLab and every package the course
uses. Assignment repos point their `.devcontainer/devcontainer.json` at it:

```json
"image": "ghcr.io/unc-data-730/env:latest"
```

so a student's codespace only has to download the image instead of compiling
Python and downloading ~2000 conda packages on every launch.

`pixi.toml` and `pixi.lock` here are copies of the ones in
[lecture-notebooks](https://github.com/UNC-DATA-730/lecture-notebooks), which is
the source of truth for the package list.

## Updating the image

1. Edit `pixi.toml` (or copy a newer one from lecture-notebooks).
2. Run `pixi lock` to refresh `pixi.lock`.
3. Commit and push to `main`. The **Build and publish image** Action rebuilds and
   pushes `:latest` plus a `:YYYY-MM-DD` tag. Takes roughly 10-15 minutes.

New codespaces pick up `:latest` automatically. Existing codespaces keep their
old image until rebuilt (Codespaces: ... -> Rebuild Container). To freeze an
assignment on a known-good build, use its date tag instead of `:latest`.

## One-time setup after the first build

The package must be **public** or student forks cannot pull it. In the
organization's **Packages** page, open `env` -> **Package settings** ->
**Change visibility** -> Public. This only needs doing once.

## Local test

```bash
docker build --platform linux/amd64 -t data730-env .
docker run --rm --platform linux/amd64 data730-env jupyter kernelspec list
```
