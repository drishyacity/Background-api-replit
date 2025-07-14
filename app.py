import os
import logging
import re
import sys
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
from werkzeug.middleware.proxy_fix import ProxyFix
import tempfile
import uuid

# Configure logging first
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Import with compatibility handling
try:
    from minimal_rembg_processor import MinimalBackgroundRemover
    BACKGROUND_PROCESSOR_AVAILABLE = True
    logger.info("Background processor imported successfully")
except ImportError as e:
    logger.warning(f"Background processor import failed: {e}")
    BACKGROUND_PROCESSOR_AVAILABLE = False
    MinimalBackgroundRemover = None
except Exception as e:
    logger.error(f"Unexpected error importing background processor: {e}")
    BACKGROUND_PROCESSOR_AVAILABLE = False
    MinimalBackgroundRemover = None

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default_secret_key_for_dev")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Enable CORS
CORS(app, origins="*", methods=["GET", "POST", "OPTIONS"])

# Configuration
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
UPLOAD_FOLDER = tempfile.gettempdir()

app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize background remover (lazy loading)
bg_remover = None

# Utility functions
def validate_image(file):
    """Validate uploaded image file"""
    if not file or file.filename == '':
        return False
    
    filename = file.filename.lower()
    return any(filename.endswith('.' + ext) for ext in ALLOWED_EXTENSIONS)

def validate_hex_color(hex_color):
    """Validate hex color format"""
    if not hex_color:
        return False
    
    # Remove # if present
    color = hex_color.lstrip('#')
    
    # Check if it's a valid hex color (6 digits)
    if len(color) != 6:
        return False
    
    try:
        int(color, 16)
        return True
    except ValueError:
        return False

def get_file_extension(filename):
    """Get file extension from filename"""
    if not filename:
        return ''
    return filename.rsplit('.', 1)[1].lower() if '.' in filename else ''

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring with compatibility info"""
    try:
        # Check system compatibility including scientific libraries
        compatibility_status = {
            'background_processor': BACKGROUND_PROCESSOR_AVAILABLE,
            'python_version': sys.version,
            'flask_available': True,
            'pil_available': True,  # We know PIL is available if we got this far
            'numpy_available': 'numpy' in sys.modules,
            'scipy_available': 'scipy' in sys.modules,
            'opencv_available': 'cv2' in sys.modules,
            'skimage_available': 'skimage' in sys.modules
        }
        
        # Try to check if background remover can initialize
        processor_status = 'available'
        try:
            if BACKGROUND_PROCESSOR_AVAILABLE:
                test_processor = MinimalBackgroundRemover()
                if test_processor.fallback_mode:
                    processor_status = 'fallback_mode'
                else:
                    processor_status = 'full_functionality'
            else:
                processor_status = 'unavailable'
        except Exception as e:
            processor_status = f'error: {str(e)}'
        
        return jsonify({
            'status': 'healthy',
            'service': 'background-removal-api',
            'version': '1.0.1',
            'processor_status': processor_status,
            'compatibility': compatibility_status,
            'deployment_ready': True,
            'port': os.environ.get('PORT', '5000'),
            'host': '0.0.0.0'
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@app.route('/remove-background', methods=['POST'])
def remove_background():
    """
    Remove background from uploaded image with custom background options
    
    Form data:
    - image: Image file (required)
    - background_type: 'transparent', 'solid', or 'image' (default: 'transparent')
    - background_color: Hex color for solid background (required if background_type='solid')
    - background_image: Background image file (required if background_type='image')
    """
    try:
        # Check if image file is present
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        image_file = request.files['image']
        if image_file.filename == '':
            return jsonify({'error': 'No image file selected'}), 400
        
        # Validate image file
        if not validate_image(image_file):
            return jsonify({'error': 'Invalid image file. Supported formats: PNG, JPG, JPEG, WebP'}), 400
        
        # Get background options
        background_type = request.form.get('background_type', 'transparent')
        background_color = request.form.get('background_color', '')
        background_image = request.files.get('background_image')
        
        # Validate background type
        if background_type not in ['transparent', 'solid', 'image']:
            return jsonify({'error': 'Invalid background_type. Must be: transparent, solid, or image'}), 400
        
        # Validate solid color background
        if background_type == 'solid':
            if not background_color:
                return jsonify({'error': 'background_color is required for solid background'}), 400
            if not validate_hex_color(background_color):
                return jsonify({'error': 'Invalid hex color format. Use format: #RRGGBB'}), 400
        
        # Validate image background
        if background_type == 'image':
            if not background_image or background_image.filename == '':
                return jsonify({'error': 'background_image is required for image background'}), 400
            if not validate_image(background_image):
                return jsonify({'error': 'Invalid background image file. Supported formats: PNG, JPG, JPEG, WebP'}), 400
        
        # Generate unique filename
        unique_id = str(uuid.uuid4())
        original_ext = get_file_extension(image_file.filename)
        temp_input_path = os.path.join(UPLOAD_FOLDER, f"{unique_id}_input.{original_ext}")
        temp_output_path = os.path.join(UPLOAD_FOLDER, f"{unique_id}_output.png")
        
        # Save uploaded image
        image_file.save(temp_input_path)
        logger.info(f"Saved input image: {temp_input_path}")
        
        # Save background image if provided
        bg_image_path = None
        if background_type == 'image' and background_image:
            bg_ext = get_file_extension(background_image.filename)
            bg_image_path = os.path.join(UPLOAD_FOLDER, f"{unique_id}_bg.{bg_ext}")
            background_image.save(bg_image_path)
            logger.info(f"Saved background image: {bg_image_path}")
        
        # Initialize background remover if not already done
        global bg_remover
        if bg_remover is None:
            if not BACKGROUND_PROCESSOR_AVAILABLE or MinimalBackgroundRemover is None:
                return jsonify({'error': 'Background processing not available. Please check installation.'}), 500
            
            logger.info("Initializing background remover...")
            try:
                bg_remover = MinimalBackgroundRemover()
                logger.info("Background remover initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize background remover: {e}")
                return jsonify({'error': f'Background processor initialization failed: {str(e)}'}), 500
        
        # Process image with background remover
        logger.info(f"Processing image with background_type: {background_type}")
        success = bg_remover.remove_background(
            input_path=temp_input_path,
            output_path=temp_output_path,
            background_type=background_type,
            background_color=background_color,
            background_image_path=bg_image_path
        )
        
        if not success:
            return jsonify({'error': 'Failed to process image'}), 500
        
        # Return processed image
        logger.info(f"Successfully processed image: {temp_output_path}")
        
        def cleanup_files():
            """Clean up temporary files after sending response"""
            try:
                if os.path.exists(temp_input_path):
                    os.remove(temp_input_path)
                if os.path.exists(temp_output_path):
                    os.remove(temp_output_path)
                if bg_image_path and os.path.exists(bg_image_path):
                    os.remove(bg_image_path)
                logger.info("Temporary files cleaned up")
            except Exception as e:
                logger.error(f"Error cleaning up files: {str(e)}")
        
        # Return processed image and schedule cleanup
        try:
            return send_file(
                temp_output_path,
                mimetype='image/png',
                as_attachment=True,
                download_name=f"processed_{unique_id}.png"
            )
        finally:
            # Schedule cleanup after sending file
            import threading
            cleanup_thread = threading.Thread(target=cleanup_files)
            cleanup_thread.daemon = True
            cleanup_thread.start()
        
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/', methods=['GET'])
def index():
    """API information endpoint with compatibility status"""
    processor_info = 'AI-powered' if BACKGROUND_PROCESSOR_AVAILABLE else 'Basic processing'
    
    return jsonify({
        'service': 'Background Removal API',
        'version': '1.0.1',
        'processor_type': processor_info,
        'endpoints': {
            'health': '/health',
            'remove_background': '/remove-background'
        },
        'supported_formats': list(ALLOWED_EXTENSIONS),
        'max_file_size': f"{MAX_FILE_SIZE // (1024*1024)}MB",
        'background_options': ['transparent', 'solid', 'image'],
        'compatibility': {
            'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            'deployment_ready': True
        }
    })

@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file size limit exceeded"""
    return jsonify({
        'error': f'File size exceeds maximum limit of {MAX_FILE_SIZE // (1024*1024)}MB'
    }), 413

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV', 'development') != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
