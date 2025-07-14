#!/bin/bash
# Build script for Render deployment - Python 3.11.10 Compatible

echo "Starting build process for Python 3.11.10..."

# Upgrade pip and setuptools
pip install --upgrade pip setuptools wheel

# Install core dependencies first with compatibility checks
echo "Installing core Flask dependencies..."
pip install flask==3.1.1 flask-cors==6.0.1 gunicorn==23.0.0 werkzeug==3.1.3

# Install image processing libraries with compatible versions
echo "Installing image processing libraries with compatible versions..."
pip install pillow==11.3.0 numpy==2.2.6

# Install scientific libraries with version compatibility
echo "Installing scientific libraries..."
pip install scipy==1.14.1 || echo "Warning: scipy installation failed - using PIL-only fallback"
pip install scikit-image==0.24.0 || echo "Warning: scikit-image installation failed - using basic processing"
pip install opencv-python-headless==4.10.0.84 || echo "Warning: opencv installation failed - using PIL-only processing"

# Try to install rembg with error handling
echo "Installing background removal libraries..."
pip install --no-deps rembg==2.0.67 || echo "Warning: rembg installation failed, using fallback mode"

# Try to install AI libraries with error handling
echo "Installing AI libraries..."
pip install onnxruntime==1.19.2 || echo "Warning: onnxruntime installation failed - using fallback mode"

# Install additional utilities with fallback
pip install jsonschema tqdm coloredlogs pooch || echo "Warning: some utilities failed to install - continuing with core functionality"

echo "Build completed with compatibility checks!"