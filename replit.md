# Background Removal API - System Documentation

## Overview

This is a Flask-based web API that provides background removal functionality for images. The service offers multiple background replacement options including transparent backgrounds, solid colors, and custom background images. The application is designed as a stateless REST API with comprehensive error handling and deployment-ready configuration.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Framework**: Flask with Python 3.11+
- **API Style**: RESTful HTTP endpoints with CORS enabled
- **Web Server**: Gunicorn for production deployment
- **File Handling**: Temporary file storage using Python's `tempfile` module
- **Image Processing**: PIL (Pillow) for image manipulation with custom background removal algorithms
- **Database**: PostgreSQL support configured (via psycopg2-binary) though not actively used in current implementation

### Key Design Decisions
- **Stateless Design**: No persistent storage - files are processed and cleaned up immediately to avoid storage overhead
- **In-Memory Processing**: Uses temporary files for processing to eliminate persistent storage requirements
- **Multiple Processing Implementations**: Includes both alternative (PIL-based) and improved background removal implementations
- **Cloud-Ready**: Pre-configured for Render.com deployment with zero configuration required

## Key Components

### Core Application Files
- `app.py`: Main Flask application with route definitions, CORS configuration, and request handling
- `main.py`: Application entry point that configures host, port, and debug settings
- `minimal_rembg_processor.py`: Production background removal engine with rembg AI integration and multiple fallback algorithms
- `requirements.txt`: Exact dependency versions for reproducible deployments
- `build.sh`: Production build script with dependency verification
- `render.yaml`: Zero-configuration deployment for Render.com
- `Procfile`: Process configuration for various hosting platforms

### Main Classes
- **MinimalBackgroundRemover**: Production-ready background removal processor with:
  - Primary: rembg neural network-based AI removal
  - Fallback 1: SciPy-based segmentation and morphological operations
  - Fallback 2: OpenCV GrabCut algorithm for object extraction
  - Fallback 3: scikit-image watershed segmentation
  - Final fallback: PIL-based edge detection and filtering

### API Endpoints
- `/health`: Health check endpoint with detailed compatibility status
- `/remove-background`: POST endpoint for background removal with options:
  - `background_type`: transparent, solid, or image
  - `background_color`: hex color for solid backgrounds
  - `background_image`: custom background image file
  - Supports PNG, JPG, JPEG, WebP formats up to 10MB

### Key Features
- Multiple background replacement options (transparent, solid color, image replacement)
- File validation (type, size, format checking)
- Secure filename handling with sanitization
- Comprehensive logging and error handling
- Image size optimization for performance

## Data Flow

1. **Image Upload**: Client uploads image via HTTP POST request
2. **Validation**: File undergoes validation for type, size, and format compliance
3. **Processing**: Image is processed through background removal algorithms:
   - Load and optionally resize image for performance
   - Apply advanced edge detection and color analysis
   - Generate subject mask and apply background replacement
4. **Response**: Processed image is returned to client
5. **Cleanup**: Temporary files are automatically cleaned up

## External Dependencies

### Core Dependencies (Current Production Configuration)
- **Flask 3.1.1**: Web framework for API endpoints
- **Flask-CORS 6.0.1**: Cross-origin request handling
- **Gunicorn 23.0.0**: Production WSGI server
- **Werkzeug 3.1.3**: Security utilities and file handling

### Image Processing Stack (Full AI-powered)
- **Pillow 11.3.0**: Core image processing and manipulation
- **NumPy 2.2.6**: Numerical operations for image arrays
- **ONNX Runtime 1.19.2**: Neural network inference engine
- **OpenCV 4.10.0.84**: Computer vision algorithms (headless)
- **rembg 2.0.67**: AI-powered background removal with neural networks
- **SciPy 1.14.1**: Advanced scientific computing for image processing
- **scikit-image**: Image segmentation and morphological operations

### Supporting Libraries
- **Requests 2.32.4**: HTTP client for external API calls
- **tqdm 4.67.1**: Progress bars for processing operations
- **jsonschema**: API response validation
- **pymatting**: Advanced alpha matting algorithms
- **numba**: JIT compilation for performance optimization

## Deployment Strategy

### Render.com Deployment (Zero Configuration)
The application includes complete deployment automation:

- **render.yaml**: Full Render.com service configuration with auto-detection
- **runtime.txt**: Python 3.11 version specification
- **requirements.txt**: Exact package versions for reproducible builds
- **DEPLOYMENT_READY.md**: Complete deployment guide with step-by-step instructions

### Build Process
- Automatic Python environment detection
- Dependency installation from pinned versions
- Health check configuration for monitoring
- Scaling and resource allocation settings

### Production Configuration
- **Environment Variables**: Configurable session secrets and port settings
- **Proxy Support**: ProxyFix middleware for proper header handling behind load balancers
- **CORS**: Configured for cross-origin requests from any domain
- **File Size Limits**: 10MB maximum file size with proper validation
- **Logging**: Comprehensive debug logging for troubleshooting

The application is designed to be deployment-ready with minimal configuration, making it suitable for cloud platforms like Render.com, Heroku, or similar PaaS providers.

## Recent Changes: Latest modifications with dates

### July 14, 2025: REAL Background Removal Fixed - AI Models Working ✅
- Successfully installed REAL AI background removal: rembg==2.0.67 with onnxruntime==1.19.2
- Fixed actual background removal functionality - now removes backgrounds properly instead of just filtering
- Implemented REAL AI-powered background removal using rembg neural networks
- Added advanced fallback algorithms: OpenCV GrabCut, Scikit-image watershed, SciPy segmentation
- Created comprehensive background removal test suite with real functionality verification
- Fixed multi-tier processing: AI rembg → OpenCV GrabCut → Scikit-image → SciPy → basic PIL
- Successfully installed core Flask dependencies: Flask 3.1.1, Flask-CORS 6.0.1, Gunicorn 23.0.0, Pillow 11.3.0, NumPy 2.2.6, Werkzeug 3.1.3
- Fixed SciPy compatibility issues with proper version pinning (scipy==1.14.1)
- Added scikit-image support with fallback handling (scikit-image==0.24.0) 
- Integrated OpenCV-headless for advanced image processing (opencv-python-headless==4.10.0.84)
- Enhanced build.sh with scientific library installation and error handling
- Updated render.yaml with optimized settings and proper Python version specification
- Added comprehensive compatibility checking for all scientific libraries in health endpoint
- Enhanced minimal_rembg_processor.py with REAL background removal algorithms instead of just filters
- Created robust error handling that gracefully degrades functionality when dependencies are missing
- Updated DEPLOYMENT.md with complete scientific library compatibility information
- Application now supports 5 different REAL background removal modes depending on available libraries
- All compatibility issues resolved AND background removal actually works now - production ready

### July 13, 2025: Background removal API successfully running on port 5000 with rembg integration
- Modified app.py to use rembg instead of manual background removal implementation
- Created MinimalBackgroundRemover with lazy initialization to avoid startup delays
- Dependencies installed: Flask, Flask-CORS, Pillow, NumPy, rembg, onnxruntime, and supporting libraries
- Health check endpoint confirmed working at /health ✅
- API ready for background removal requests at /remove-background ✅
- Supports transparent, solid color, and image backgrounds ✅

### Previous Updates:
- API tested with user's image - processing works but takes time due to model initialization
- Project cleaned up and optimized for deployment ✅
- Removed unnecessary files and consolidated utility functions into app.py
- Updated render.yaml with proper build and start commands for Render.com deployment
- Created build.sh script with version-pinned dependencies for compatibility
- Added Procfile for deployment flexibility
- Updated README.md with deployment instructions