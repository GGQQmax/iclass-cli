#!/usr/bin/env bash
# setup.sh — Setup script for iClass CLI project with user input

set -e  # stop on error

echo "🚀 Cloning iClass CLI repository..."
git clone https://github.com/GGQQmax/iclass-cli.git
cd iclass-cli

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
echo "    python mainUI.py"
echo ""
echo "🎉 Done!"

python mainUI.py
