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

# Ask if user wants to build and install the binary
echo "🔨 Building and installing iClass CLI..."
read -p "Would you like to build and install iClass CLI as a standalone binary? (y/n) " -n 1 -r INSTALL_BINARY
echo ""

if [[ $INSTALL_BINARY =~ ^[Yy]$ ]]; then
    echo "📦 Installing PyInstaller..."
    pip install pyinstaller
    
    echo "🔨 Building executable with PyInstaller..."
    pyinstaller main.py --onefile --name iclassCLI --add-data '.env:.' --distpath ./dist
    
    if [ -f "dist/iclassCLI" ]; then
        echo "✅ Build successful!"
        
        # Create ~/.local/bin if it doesn't exist
        mkdir -p ~/.local/bin
        
        echo "📁 Installing binary to ~/.local/bin/iclassCLI..."
        cp dist/iclassCLI ~/.local/bin/iclassCLI
        chmod +x ~/.local/bin/iclassCLI
        
        echo "✅ Binary installed successfully!"
        
        # Check if ~/.local/bin is in PATH
        if [[ ":$PATH:" == *":$HOME/.local/bin:"* ]]; then
            echo "✅ ~/.local/bin is already in your PATH"
        else
            echo "⚠️  ~/.local/bin is not in your PATH"
            read -p "Would you like to add ~/.local/bin to your PATH? (y/n) " -n 1 -r ADD_TO_PATH
            echo ""
            
            if [[ $ADD_TO_PATH =~ ^[Yy]$ ]]; then
                # Detect shell and patch accordingly
                SHELL_RC=""
                
                # Check for bash
                if [ -f "$HOME/.bashrc" ]; then
                    if ! grep -q 'export PATH="$HOME/.local/bin:$PATH"' "$HOME/.bashrc"; then
                        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
                        echo "✅ Updated ~/.bashrc"
                        SHELL_RC="$HOME/.bashrc"
                    fi
                fi
                
                # Check for zsh
                if [ -f "$HOME/.zshrc" ]; then
                    if ! grep -q 'export PATH="$HOME/.local/bin:$PATH"' "$HOME/.zshrc"; then
                        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.zshrc"
                        echo "✅ Updated ~/.zshrc"
                        SHELL_RC="$HOME/.zshrc"
                    fi
                fi
                
                if [ -n "$SHELL_RC" ]; then
                    echo "🔄 Reloading shell configuration..."
                    source "$SHELL_RC"
                    echo "✅ PATH reloaded successfully!"
                fi
            fi
        fi
        
        echo ""
        echo "🎉 You can now use 'iclassCLI' from anywhere in your terminal!"
    else
        echo "❌ Build failed. Binary not found in dist/"
    fi
else
    echo "⏭️  Skipping binary installation."
fi

echo ""
echo "🏁 Setup complete. To start using iClass CLI:"
echo ""
if [ -f ~/.local/bin/iclassCLI ]; then
    echo "    iclassCLI"
else
    echo "    source venv/bin/activate"
    echo "    python main.py"
fi
echo ""
echo "🎉 Done!"

