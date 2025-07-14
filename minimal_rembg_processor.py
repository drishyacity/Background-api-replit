import os
import logging
import sys
import tempfile
import io

# Import PIL with compatibility handling
try:
    from PIL import Image, ImageFilter, ImageEnhance
    PIL_AVAILABLE = True
except ImportError as e:
    logging.error(f"PIL import failed: {e}")
    PIL_AVAILABLE = False
    Image = None

# Try to import numpy with fallback
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    logging.warning("NumPy not available, using fallback processing")
    NUMPY_AVAILABLE = False
    np = None

# Try to import scipy with fallback
try:
    import scipy
    from scipy import ndimage
    SCIPY_AVAILABLE = True
except ImportError:
    logging.warning("SciPy not available, using basic processing")
    SCIPY_AVAILABLE = False
    scipy = None

# Try to import scikit-image with fallback
try:
    from skimage import filters, segmentation, morphology
    SKIMAGE_AVAILABLE = True
except ImportError:
    logging.warning("Scikit-image not available, using PIL-only processing")
    SKIMAGE_AVAILABLE = False

# Try to import OpenCV with fallback
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    logging.warning("OpenCV not available, using PIL-only processing")
    CV2_AVAILABLE = False
    cv2 = None

logger = logging.getLogger(__name__)

class MinimalBackgroundRemover:
    """Minimal background remover using rembg with fallback"""
    
    def __init__(self):
        """Initialize the background remover"""
        if not PIL_AVAILABLE:
            raise ImportError("PIL (Pillow) is required but not available")
        
        self.rembg = None
        self.fallback_mode = False
        logger.info("MinimalBackgroundRemover initialized with compatibility checks")
    
    def _get_rembg(self):
        """Lazy load rembg with fallback handling"""
        if self.rembg is None:
            try:
                import rembg
                from rembg import bg
                self.rembg = rembg
                self.bg_func = bg
                self.fallback_mode = False
                logger.info("Rembg loaded successfully with real AI background removal")
            except Exception as e:
                logger.warning(f"Failed to load rembg: {e}. Using advanced fallback mode.")
                # Set to False to indicate rembg is not available
                self.rembg = False
                self.fallback_mode = True
        return self.rembg
    
    def _simple_background_removal(self, image):
        """Advanced background removal using scientific algorithms for actual background removal"""
        if not PIL_AVAILABLE:
            raise ImportError("PIL not available for fallback processing")
        
        try:
            # Convert to RGBA if not already
            if image.mode != 'RGBA':
                image = image.convert('RGBA')
            
            # Try actual background removal with available libraries
            if CV2_AVAILABLE and NUMPY_AVAILABLE:
                logger.info("Using OpenCV background removal")
                return self._opencv_background_removal(image)
            elif SKIMAGE_AVAILABLE and NUMPY_AVAILABLE:
                logger.info("Using scikit-image background removal")
                return self._skimage_background_removal(image)
            elif SCIPY_AVAILABLE and NUMPY_AVAILABLE:
                logger.info("Using SciPy background removal")
                return self._scipy_background_removal(image)
            else:
                logger.info("Using advanced PIL background removal")
                return self._advanced_pil_background_removal(image)
            
        except Exception as e:
            logger.error(f"Background removal failed: {e}")
            # Return original image if all processing fails
            return image.convert('RGBA')
    
    def _scipy_background_removal(self, image):
        """Background removal using SciPy algorithms"""
        try:
            from scipy import ndimage
            from scipy.ndimage import label, binary_fill_holes
            
            img_array = np.array(image)
            img_rgb = img_array[:, :, :3]
            
            # Convert to grayscale
            img_gray = np.mean(img_rgb, axis=2)
            
            # Apply Gaussian filter
            img_smooth = ndimage.gaussian_filter(img_gray, sigma=2.0)
            
            # Threshold to create binary image
            threshold = np.mean(img_smooth) + np.std(img_smooth) * 0.5
            binary = img_smooth > threshold
            
            # Fill holes and remove small objects
            binary_filled = binary_fill_holes(binary)
            
            # Label connected components
            labeled, num_features = label(binary_filled)
            
            # Find the largest component (likely the main subject)
            if num_features > 0:
                component_sizes = [(labeled == i).sum() for i in range(1, num_features + 1)]
                largest_component = np.argmax(component_sizes) + 1
                mask = (labeled == largest_component).astype(np.uint8)
            else:
                # Fallback: use thresholded image
                mask = binary_filled.astype(np.uint8)
            
            # Apply morphological operations
            mask = ndimage.binary_opening(mask, iterations=2)
            mask = ndimage.binary_closing(mask, iterations=3)
            
            # Apply mask to create transparent background
            result_array = img_array.copy()
            result_array[:, :, 3] = mask * 255  # Set alpha channel
            
            result = Image.fromarray(result_array, 'RGBA')
            logger.info("Applied SciPy background removal")
            return result
        except Exception as e:
            logger.warning(f"SciPy background removal failed: {e}, falling back")
            return self._advanced_pil_background_removal(image)
    
    def _skimage_background_removal(self, image):
        """Background removal using scikit-image segmentation"""
        try:
            from skimage import segmentation, filters, morphology, measure
            
            img_array = np.array(image)
            img_rgb = img_array[:, :, :3]  # Remove alpha channel for processing
            
            # Apply Gaussian filter to reduce noise
            img_smooth = filters.gaussian(img_rgb, sigma=1.0, channel_axis=2)
            
            # Use watershed segmentation to separate foreground and background
            # Convert to grayscale for segmentation
            img_gray = np.mean(img_smooth, axis=2)
            
            # Find local maxima (foreground seeds)
            local_maxima = morphology.local_maxima(img_gray)
            markers = measure.label(local_maxima)
            
            # Apply watershed
            segments = segmentation.watershed(-img_gray, markers)
            
            # Create mask for largest segment (likely foreground)
            unique, counts = np.unique(segments, return_counts=True)
            largest_segment = unique[np.argmax(counts[1:])+1]  # Skip background (0)
            
            # Create binary mask
            mask = (segments == largest_segment).astype(np.uint8)
            
            # Apply morphological operations to clean up mask
            mask = morphology.binary_closing(mask, morphology.disk(5))
            mask = morphology.binary_fill_holes(mask)
            
            # Apply mask to create transparent background
            result_array = img_array.copy()
            result_array[:, :, 3] = mask * 255  # Set alpha channel
            
            result = Image.fromarray(result_array, 'RGBA')
            logger.info("Applied scikit-image watershed background removal")
            return result
        except Exception as e:
            logger.warning(f"Scikit-image background removal failed: {e}, falling back")
            return self._scipy_background_removal(image)
    
    def _opencv_background_removal(self, image):
        """Actual background removal using OpenCV algorithms"""
        try:
            # Convert PIL to OpenCV format
            img_array = np.array(image)
            img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGBA2BGR)
            
            # Create mask using GrabCut algorithm for background removal
            mask = np.zeros(img_bgr.shape[:2], np.uint8)
            bgd_model = np.zeros((1, 65), np.float64)
            fgd_model = np.zeros((1, 65), np.float64)
            
            # Define rectangle around the main subject (center 80% of image)
            height, width = img_bgr.shape[:2]
            rect = (int(width*0.1), int(height*0.1), int(width*0.8), int(height*0.8))
            
            # Apply GrabCut
            cv2.grabCut(img_bgr, mask, rect, bgd_model, fgd_model, 5, cv2.GC_INIT_WITH_RECT)
            
            # Create final mask
            mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
            
            # Apply mask to create transparent background
            result_array = img_array.copy()
            result_array[:, :, 3] = mask2 * 255  # Set alpha channel
            
            result = Image.fromarray(result_array, 'RGBA')
            logger.info("Applied OpenCV GrabCut background removal")
            return result
        except Exception as e:
            logger.warning(f"OpenCV background removal failed: {e}, falling back")
            return self._advanced_pil_background_removal(image)
    
    def _advanced_pil_background_removal(self, image):
        """Advanced background removal using only PIL with color-based segmentation"""
        try:
            if not NUMPY_AVAILABLE:
                return self._basic_pil_background_removal(image)
            
            # Convert PIL to numpy for advanced processing
            img_array = np.array(image)
            img_rgb = img_array[:, :, :3]
            
            # Color-based background removal
            # Calculate color statistics
            height, width = img_rgb.shape[:2]
            
            # Sample border pixels to identify background color
            border_pixels = np.concatenate([
                img_rgb[0, :],      # top border
                img_rgb[-1, :],     # bottom border
                img_rgb[:, 0],      # left border
                img_rgb[:, -1]      # right border
            ])
            
            # Find dominant background color
            bg_color = np.mean(border_pixels, axis=0)
            
            # Calculate color distance from background
            color_diff = np.sqrt(np.sum((img_rgb - bg_color) ** 2, axis=2))
            
            # Create mask based on color difference
            threshold = np.mean(color_diff) + np.std(color_diff) * 0.5
            mask = color_diff > threshold
            
            # Clean up mask with morphological operations
            from scipy.ndimage import binary_opening, binary_closing
            if SCIPY_AVAILABLE:
                mask = binary_opening(mask, iterations=1)
                mask = binary_closing(mask, iterations=2)
            
            # Apply mask to create transparent background
            result_array = img_array.copy()
            result_array[:, :, 3] = mask.astype(np.uint8) * 255
            
            result = Image.fromarray(result_array, 'RGBA')
            logger.info("Applied advanced PIL color-based background removal")
            return result
            
        except Exception as e:
            logger.warning(f"Advanced PIL background removal failed: {e}, using basic fallback")
            return self._basic_pil_background_removal(image)
    
    def _basic_pil_background_removal(self, image):
        """Basic background removal using PIL edge detection"""
        try:
            # Convert to grayscale for edge detection
            gray = image.convert('L')
            
            # Apply edge detection
            edges = gray.filter(ImageFilter.FIND_EDGES)
            
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(edges)
            enhanced_edges = enhancer.enhance(2.0)
            
            # Create mask from edges
            threshold = 30
            mask = enhanced_edges.point(lambda x: 255 if x > threshold else 0, mode='L')
            
            # Apply morphological operations using PIL
            mask = mask.filter(ImageFilter.MaxFilter(size=3))  # Dilation
            mask = mask.filter(ImageFilter.MinFilter(size=3))  # Erosion
            
            # Apply mask to original image
            result = image.copy()
            result.putalpha(mask)
            
            logger.info("Applied basic PIL edge-based background removal")
            return result
            
        except Exception as e:
            logger.error(f"Basic PIL background removal failed: {e}")
            return image
    
    def remove_background(self, input_path, output_path, background_type='transparent', 
                         background_color=None, background_image_path=None):
        """
        Remove background from image using rembg
        """
        try:
            # Load and process the input image
            logger.info(f"Loading input image: {input_path}")
            
            # Get rembg and remove background - using simple approach
            rembg = self._get_rembg()
            
            if rembg and rembg != False and not self.fallback_mode:
                try:
                    logger.info("Removing background with rembg...")
                    with open(input_path, 'rb') as input_file:
                        input_data = input_file.read()
                    
                    # Use the simple remove function without session
                    output_data = rembg.remove(input_data)
                    
                    # Convert to PIL Image
                    subject_image = Image.open(io.BytesIO(output_data)).convert('RGBA')
                    logger.info(f"Background removed with rembg. Image size: {subject_image.size}")
                except Exception as e:
                    logger.warning(f"Rembg processing failed: {e}. Switching to fallback mode.")
                    self.fallback_mode = True
                    # Fall through to fallback processing
                    
            if self.fallback_mode or not rembg or rembg == False:
                # Fallback: use simple processing or just convert to RGBA
                logger.warning("Using fallback background processing")
                original_image = Image.open(input_path)
                subject_image = self._simple_background_removal(original_image)
                logger.info(f"Fallback processing completed. Size: {subject_image.size}")
            
            # Apply background based on type
            if background_type == 'transparent':
                result_image = subject_image
                logger.info("Using transparent background")
                
            elif background_type == 'solid':
                result_image = self._apply_solid_background(subject_image, background_color)
                logger.info(f"Applied solid background: {background_color}")
                
            elif background_type == 'image':
                result_image = self._apply_image_background(subject_image, background_image_path)
                logger.info("Applied image background")
            
            # Save result
            result_image.save(output_path, 'PNG')
            logger.info(f"Result saved to: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error removing background: {str(e)}")
            return False
    
    def _apply_solid_background(self, subject_image, hex_color):
        """Apply solid color background"""
        try:
            # Convert hex to RGB
            hex_color = hex_color.lstrip('#')
            rgb_color = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            
            # Create background
            background = Image.new('RGBA', subject_image.size, rgb_color + (255,))
            
            # Composite images
            result = Image.alpha_composite(background, subject_image)
            return result.convert('RGB')
        except Exception as e:
            logger.error(f"Error applying solid background: {e}")
            return subject_image.convert('RGB')
    
    def _apply_image_background(self, subject_image, bg_image_path):
        """Apply image background"""
        try:
            # Load background image
            bg_image = Image.open(bg_image_path).convert('RGBA')
            
            # Resize background to match subject
            bg_image = bg_image.resize(subject_image.size, Image.Resampling.LANCZOS)
            
            # Composite images
            result = Image.alpha_composite(bg_image, subject_image)
            return result.convert('RGB')
        except Exception as e:
            logger.error(f"Error applying image background: {e}")
            return subject_image.convert('RGB')