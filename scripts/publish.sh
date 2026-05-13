#!/usr/bin/env bash
set -euo pipefail

VERSION="$1"

echo "=== Publishing samcov ${VERSION} ==="

# ── PyPI (Forgejo internal registry) ──
echo "→ Uploading to Forgejo PyPI registry..."
FORGEJO_PYPI_URL="https://git.reslate.solutions/api/packages/ydeng/pypi/"
uvx -q twine upload \
    --repository-url "${FORGEJO_PYPI_URL}" \
    --username "ydeng" \
    --password "${PACKAGE_UPLOAD_TOKEN}" \
    --non-interactive \
    dist/*

# ── Conda (Forgejo) ──
echo "→ Building conda package..."
export SAMCOV_VERSION="${VERSION}"
rm -rf output
RATTLER_BUILD="$(command -v rattler-build || true)"
if [ -z "${RATTLER_BUILD}" ]; then
    RATTLER_BUILD="/usr/local/bin/rattler-build"
fi
"${RATTLER_BUILD}" build --recipe conda/recipe.yaml --no-test --package-format tar-bz2

CONDA_FILE=$(find output -name "*.tar.bz2" | head -n1)
if [ -z "${CONDA_FILE}" ]; then
    echo "ERROR: No .tar.bz2 artifact found" >&2
    exit 1
fi

echo "→ Uploading ${CONDA_FILE} to Forgejo conda registry..."
curl -fsS \
    --user "ydeng:${PACKAGE_UPLOAD_TOKEN}" \
    --upload-file "${CONDA_FILE}" \
    "https://git.reslate.solutions/api/packages/ydeng/conda/$(basename "${CONDA_FILE}")" || {
    echo "WARNING: conda upload failed (token may be missing in local runs)" >&2
}

echo "=== Done ==="
