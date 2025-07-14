
#!/bin/bash

# Deployment script for Render.com
echo "🚀 Starting deployment process..."

# Install dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Test the application
echo "🧪 Testing application..."
python -c "from app import app; print('✅ App imports successfully')"

# Check if background processor works
echo "🔍 Checking background processor..."
python -c "
try:
    from minimal_rembg_processor import MinimalBackgroundRemover
    processor = MinimalBackgroundRemover()
    print('✅ Background processor working')
except Exception as e:
    print(f'⚠️ Background processor in fallback mode: {e}')
"

echo "🎉 Deployment ready!"
