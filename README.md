# Background Removal API

A production-ready Flask API for AI-powered background removal with multiple output options.

## 🚀 Features

- **AI Background Removal**: Powered by rembg for precise subject extraction
- **Multiple Output Options**: 
  - Transparent backgrounds (PNG)
  - Solid color backgrounds
  - Custom image backgrounds
- **REST API**: Simple HTTP endpoints for easy integration
- **Production Ready**: Optimized for cloud deployment


## 📋 API Endpoints

### Health Check
```
GET /health
```

### Background Removal
```
POST /remove-background
Content-Type: multipart/form-data

Parameters:
- image (required): Image file to process
- background_type: 'transparent', 'solid', or 'image' (default: transparent)
- background_color: Hex color for solid backgrounds (e.g., #FF0000)
- background_image: Background image file for image backgrounds
```

## 🚀 Deployment

### Render.com (One-Click Deploy)

1. Fork this repository
2. Connect to Render.com
3. Create new Web Service from your repo
4. Deploy automatically with included `render.yaml`

### Manual Deployment

**Build Command:**
```bash
./build.sh
```

**Start Command:**
```bash
gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 300 --preload app:app
```

## 🛠️ Local Development

```bash
# Install dependencies (handled by package manager)
python main.py
```

Test the API:
```bash
curl http://localhost:5000/health
curl -X POST http://localhost:5000/remove-background \
  -F "image=@your-image.jpg" \
  -F "background_type=transparent" \
  -o result.png
```

## 📁 Project Structure

```
├── app.py                    # Main Flask application
├── main.py                   # Entry point
├── minimal_rembg_processor.py # Background removal engine

├── build.sh                  # Deployment build script
├── render.yaml               # Render.com configuration
├── Procfile                  # Process specification
└── requirements.txt          # Dependencies
```

## ⚙️ Configuration

- **Max File Size**: 10MB
- **Supported Formats**: PNG, JPG, JPEG, WebP
- **Memory**: 1GB+ recommended
- **Timeout**: 300 seconds for processing

## 🔧 Technical Stack

- **Framework**: Flask 3.1.1
- **AI Engine**: rembg 2.0.59
- **Image Processing**: Pillow, OpenCV, scikit-image
- **Server**: Gunicorn with optimized workers
- **Python**: 3.11.10