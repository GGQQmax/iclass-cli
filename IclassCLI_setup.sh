#!/usr/bin/env bash
# setup.sh — Setup script for iClass CLI project with user input

set -e  # stop on error

echo "🚀 Cloning iClass CLI repository..."
git clone https://github.com/GGQQmax/iclass-cli.git
cd iclass-cli

echo "🐍 Checking if Python virtual environment module is available..."
if ! python3 -m ensurepip --version &>/dev/null; then
    echo "⚠️  Python virtual environment module is not available. Installing it now..."
    if [ -f /etc/redhat-release ]; then
        # For Red Hat-based distros (e.g., CentOS, Fedora)
        sudo dnf install -y python3-virtualenv
    elif [ -f /etc/debian_version ]; then
        # For Debian-based distros (e.g., Ubuntu)
        sudo apt update && sudo apt install -y python3-venv
    elif [ -f /etc/arch-release ]; then
        # For Arch-based distros
        sudo pacman -S --noconfirm python-virtualenv
    else
        echo "❌ Unsupported Linux distribution. Please install Python virtual environment manually."
        exit 1
    fi
else
    echo "✅ Python virtual environment module is already available."
fi

echo "🐍 Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Ask for credentials
echo ""
echo "🔐 Setting up environment credentials..."
read -p "Enter your Student ID: " STUDENTID
read -s -p "Enter your SSO Password: " PASSWORD
echo ""
echo "✅ Credentials received."

# Write to .env
cat > .env <<EOF
USERNAMEID="${STUDENTID}"
PASSWORD="${PASSWORD}"
EOF

echo "✅ .env file created successfully!"
echo ""
echo "🏁 Setup complete. To start using iClass CLI:"
echo ""
echo "    source venv/bin/activate"
echo "    python main.py"
echo ""
echo "🎉 Done!"

python main.py
