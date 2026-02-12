#!/bin/bash
set -e

echo "=== Dev Tools Setup ==="

# Check for Homebrew (macOS package manager)
if ! command -v brew &> /dev/null; then
    echo "Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
else
    echo "Homebrew already installed."
fi

# List of tools to install
tools=(git node python3 docker jq wget)

for tool in "${tools[@]}"; do
    if command -v "$tool" &> /dev/null; then
        echo "$tool already installed: $($tool --version 2>&1 | head -1)"
    else
        echo "Installing $tool..."
        brew install "$tool"
    fi
done

echo ""
echo "=== Installed Versions ==="
git --version
node --version
python3 --version
docker --version 2>/dev/null || echo "docker not found"
jq --version 2>/dev/null || echo "jq not found"
wget --version 2>&1 | head -1 || echo "wget not found"

echo ""
echo "Setup complete!"
