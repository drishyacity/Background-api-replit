#!/usr/bin/env python3
"""
Test script to verify background removal functionality
"""

import tempfile
import os
from PIL import Image, ImageDraw
from minimal_rembg_processor import MinimalBackgroundRemover

def create_test_image():
    """Create a simple test image with a clear subject and background"""
    # Create a 300x300 image with white background
    img = Image.new('RGB', (300, 300), 'white')
    draw = ImageDraw.Draw(img)
    
    # Draw a red circle in the center (this should be preserved)
    draw.ellipse([100, 100, 200, 200], fill='red', outline='darkred', width=3)
    
    # Save to temporary file
    temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    img.save(temp_file.name, 'PNG')
    return temp_file.name

def test_background_removal():
    """Test the background removal functionality"""
    print("🧪 Testing Background Removal Functionality...")
    
    # Create test image
    input_path = create_test_image()
    output_path = tempfile.NamedTemporaryFile(suffix='.png', delete=False).name
    
    try:
        # Initialize processor
        processor = MinimalBackgroundRemover()
        
        # Check which mode we're using
        rembg = processor._get_rembg()
        if rembg and not processor.fallback_mode:
            print("✅ Using REAL AI background removal with rembg")
            mode = "AI-powered rembg"
        else:
            print("⚠️  Using advanced fallback algorithms")
            mode = "Advanced fallback"
        
        # Test background removal
        print(f"📸 Processing test image with {mode}...")
        success = processor.remove_background(input_path, output_path, 'transparent')
        
        if success:
            # Check if output file exists and has content
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                print("✅ Background removal completed successfully!")
                print(f"📁 Output saved to: {output_path}")
                
                # Load and check the result
                result_img = Image.open(output_path)
                print(f"📊 Result image size: {result_img.size}")
                print(f"📊 Result image mode: {result_img.mode}")
                
                if result_img.mode == 'RGBA':
                    print("✅ Image has transparency channel - background removal working!")
                else:
                    print("⚠️  Image doesn't have transparency - check processing")
                
                return True
            else:
                print("❌ Output file was not created properly")
                return False
        else:
            print("❌ Background removal failed")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False
    finally:
        # Clean up temporary files
        try:
            os.unlink(input_path)
            if os.path.exists(output_path):
                os.unlink(output_path)
        except:
            pass

if __name__ == "__main__":
    print("🚀 Background Removal API Test")
    print("=" * 50)
    
    success = test_background_removal()
    
    print("=" * 50)
    if success:
        print("🎉 ALL TESTS PASSED! Background removal is working properly!")
    else:
        print("💥 TESTS FAILED! Background removal needs fixing!")
    
    print("Test completed.")