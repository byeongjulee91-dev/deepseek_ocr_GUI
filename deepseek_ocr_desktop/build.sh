#!/bin/bash
# Build script for DeepSeek-OCR Desktop (Linux/Mac)
# Creates a standalone executable using PyInstaller

set -e  # Exit on error

echo "========================================="
echo "DeepSeek-OCR Desktop - Build Script"
echo "========================================="
echo ""

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv not found! Please install uv first:"
    echo "curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Warning: Virtual environment not detected."
    echo "It's recommended to build in a virtual environment."
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if PyInstaller is installed
if ! python3 -c "import PyInstaller" 2>/dev/null; then
    echo "❌ PyInstaller not found!"
    echo "Installing PyInstaller with uv..."
    uv pip install pyinstaller>=6.0.0
fi

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build dist
echo "✅ Clean complete"
echo ""

# Run PyInstaller
echo "📦 Building with PyInstaller..."
echo "This may take several minutes..."
echo ""

pyinstaller deepseek_ocr.spec --clean

# Check if build was successful
if [ -d "dist/DeepSeek-OCR" ]; then
    echo ""
    echo "========================================="
    echo "✅ Build successful!"
    echo "========================================="
    echo ""
    echo "Executable location: dist/DeepSeek-OCR/"
    echo "Main executable: dist/DeepSeek-OCR/DeepSeek-OCR"
    echo ""
    echo "📊 Build size:"
    du -sh dist/DeepSeek-OCR
    echo ""
    echo "📝 Note: Model files (~5-10GB) will be downloaded on first run"
    echo "         to ~/.cache/huggingface/"
    echo ""
    echo "To run the application:"
    echo "  cd dist/DeepSeek-OCR"
    echo "  ./DeepSeek-OCR"
    echo ""
    echo "To create a distributable archive:"
    echo "  cd dist"
    echo "  tar -czf DeepSeek-OCR-linux.tar.gz DeepSeek-OCR/"
    echo ""
else
    echo ""
    echo "========================================="
    echo "❌ Build failed!"
    echo "========================================="
    echo "Check the error messages above."
    exit 1
fi
