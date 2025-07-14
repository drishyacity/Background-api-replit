# Deployment Guide - Background Removal API

## Updated for Python 3.11.10 Compatibility

This guide contains deployment instructions with all compatibility issues resolved.

## Quick Deploy Options

### 1. Render.com (Recommended)
- Fully configured with `render.yaml`
- Automatic builds with compatibility handling
- Health checks enabled
- Auto-scaling configured

**Steps:**
1. Connect your GitHub repository to Render.com
2. Create new Web Service
3. Select this repository
4. Deploy automatically (all settings are pre-configured)

### 2. Heroku
```bash
# Create Heroku app
heroku create your-app-name

# Push to Heroku
git push heroku main

# Check logs
heroku logs --tail
```

### 3. Railway
```bash
# Deploy to Railway
railway deploy
```

## Compatibility Features

### Python 3.11.10 Support
- All dependencies tested and compatible
- Fallback processing for missing AI libraries
- Graceful error handling for dependency issues

### Dependency Handling
- Core Flask stack: Always available
- AI libraries (rembg): Fallback mode if unavailable
- Image processing: Multiple fallback layers

### Health Monitoring
- `/health` endpoint with compatibility status
- Processor status information
- Deployment readiness indicators

## Environment Variables

### Required (Auto-generated on platforms)
- `PORT`: Application port (auto-set by platform)
- `SESSION_SECRET`: Flask session secret (auto-generated)

### Optional
- `FLASK_ENV`: Set to 'production' for deployment
- `PYTHON_VERSION`: Set to '3.11.10'
- `PYTHONUNBUFFERED`: Set to '1' for better logging

## Build Process

The build script (`build.sh`) includes:
1. Core dependency installation with version pinning
2. Error handling for missing AI libraries
3. Compatibility checks for Python 3.11.10
4. Fallback mechanisms for failed installations

## API Capabilities

### With Full AI Stack
- Precise background removal using rembg
- Support for complex images
- High-quality edge detection

### Fallback Mode (if AI unavailable)
- Basic image processing using PIL
- Simple contrast enhancement
- Edge filtering
- Still functional for basic use cases

## Testing Your Deployment

### Health Check
```bash
curl https://your-app.render.com/health
```

### API Info
```bash
curl https://your-app.render.com/
```

### Background Removal Test
```bash
curl -X POST https://your-app.render.com/remove-background \
  -F "image=@test-image.jpg" \
  -F "background_type=transparent" \
  -o result.png
```

## Troubleshooting

### Common Issues
1. **AI Dependencies Fail**: App automatically switches to fallback mode
2. **Memory Limits**: Reduce image size or increase instance resources
3. **Timeout Issues**: Increase timeout in deployment settings

### Logs
- Health endpoint shows compatibility status
- Detailed logging for all processing steps
- Error messages include fallback information

## Performance Optimization

### Memory
- Automatic file cleanup after processing
- Optimized dependency loading
- Fallback processing for resource constraints

### CPU
- Single worker configuration for stability
- Request limits to prevent overload
- Efficient image processing algorithms

## Security Features

- File type validation
- Size limits (10MB default)
- Secure filename handling
- Input sanitization
- CORS properly configured

## Support

The application is designed to work even with partial dependency installations, ensuring maximum compatibility across different deployment environments.