#!/usr/bin/env bash
set -euo pipefail

VERSION="$1"

echo "=== Publishing samcov ${VERSION} ==="

# ── PyPI (Forgejo) ──
echo "→ Uploading to PyPI registry..."
uvx -q twine upload --non-interactive dist/*

# ── Conda (Forgejo) ──
echo "→ Building conda package..."
export SAMCOV_VERSION="${VERSION}"
rm -rf output
RATTLER_BUILD="$(command -v rattler-build || true)"
if [ -z "${RATTLER_BUILD}" ]; then
    RATTLER_BUILD="/usr/local/bin/rattler-build"
fi
"${RATTLER_BUILD}" build --recipe conda/recipe.yaml --no-test

CONDA_FILE=$(find output -name "*.conda" | head -n1)
if [ -z "${CONDA_FILE}" ]; then
    echo "ERROR: No .conda artifact found" >&2
    exit 1
fi

echo "→ Uploading ${CONDA_FILE} to Forgejo conda registry..."
curl -fsS \
    --user "ydeng:${PACKAGE_UPLOAD_TOKEN}" \
    --upload-file "${CONDA_FILE}" \
    "https://git.reslate.solutions/api/packages/ydeng/conda/main/$(basename "${CONDA_FILE}")" || {
    echo "WARNING: conda upload failed (token may be missing in local runs)" >&2
}

echo "=== Done ==="
