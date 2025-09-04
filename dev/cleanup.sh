#!/bin/bash

# Change to project root directory (one level up from dev/)
cd "$(dirname "$0")/.."

echo "🧹 Cleaning up old venv and switching to conda..."

# Remove old venv if it exists
if [ -d "venv" ]; then
    echo "Removing old venv directory..."
    rm -rf venv
    echo "✅ Old venv removed"
fi

# Show conda environment info
echo ""
echo "🐍 Conda environment will be created at:"
echo "   /mnt/nvme0n1p8/conda-envs/lbm-arena"
echo ""
echo "💾 Disk space on big partition:"
df -h /mnt/nvme0n1p8 | grep -v Filesystem

echo ""
echo "🚀 Run ./dev.sh to create conda environment and start the project"
