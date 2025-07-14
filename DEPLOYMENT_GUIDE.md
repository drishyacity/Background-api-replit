# Deployment Guide - Background Removal API

## Quick Deployment Commands

### Render.com
```bash
# Automatically uses render.yaml configuration
# Just connect your Git repository to Render
```

### Heroku
```bash
heroku create your-app-name
git push heroku main
```

### Railway
```bash
railway login
railway link
railway up
```

### Docker
```bash
# Build and run locally
docker build -t background-removal-api .
docker run -p 5000:5000 background-removal-api

# Or use docker-compose
docker-compose up
```

### Vercel (Serverless)
```bash
vercel --prod
```

## Production Dependencies

All deployment configurations use the verified dependencies from `requirements-production.txt`:

### Core Stack
- **Python**: 3.11.10
- **Flask**: 3.1.1 
- **Gunicorn**: 23.0.0

### AI & Image Processing
- **rembg**: 2.0.67 (AI background removal)
- **ONNX Runtime**: 1.19.2 (Neural network inference)
- **OpenCV**: 4.10.0.84 (Computer vision)
- **NumPy**: 2.2.6 (Numerical computing)
- **SciPy**: 1.14.1 (Scientific computing)
- **Pillow**: 11.3.0 (Image processing)

### Supporting Libraries
- **scikit-image**: 0.25.2 (Image segmentation)
- **numba**: 0.61.2 (JIT compilation)
- **jsonschema**: 4.24.0 (API validation)
- Plus 20+ additional verified dependencies

## Configuration Files

| Platform | Config File | Purpose |
|----------|-------------|---------|
| Render | `render.yaml` | Main production deployment |
| Heroku | `app.json`, `Procfile` | Heroku platform |
| Railway | `railway.json` | Railway deployment |
| Vercel | `vercel.json` | Serverless functions |
| Docker | `Dockerfile`, `docker-compose.yml` | Containerization |
| Generic | `deploy-config.yaml` | Universal config |

## Environment Variables

Required for all deployments:
```
FLASK_ENV=production
PYTHONUNBUFFERED=1
PYTHONDONTWRITEBYTECODE=1
WEB_CONCURRENCY=1
PORT=5000
```

## Health Check

All platforms monitor: `GET /health`

Expected response:
```json
{
  "status": "healthy",
  "processor_status": "full_functionality",
  "deployment_ready": true
}
```

## Resource Requirements

- **Memory**: 512MB minimum (recommended for AI processing)
- **Disk**: 512MB minimum 
- **CPU**: 0.1 cores minimum
- **Timeout**: 300 seconds (for large image processing)

## Build Process

1. Install Python 3.11.10
2. Upgrade pip, setuptools, wheel
3. Install from `requirements-production.txt`
4. Verify core dependencies
5. Start with Gunicorn WSGI server

## Troubleshooting

### Common Issues
- **Memory errors**: Increase memory limit to 1GB
- **Timeout errors**: Increase timeout to 300+ seconds
- **Build failures**: Check Python version is 3.11.10
- **Import errors**: Verify all dependencies in requirements-production.txt

### Debug Commands
```bash
# Test locally
python main.py

# Check dependencies
python -c "import rembg, cv2, numpy; print('OK')"

# Test API
curl http://localhost:5000/health
```