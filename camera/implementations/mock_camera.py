"""
Mock camera implementation for development and testing.
"""
import numpy as np
import cv2
import logging
import time
import os
import math
from ..base import AbstractCamera

logger = logging.getLogger(__name__)

class MockCamera(AbstractCamera):
    """Mock camera for development and testing."""
    
    def __init__(self, capture_dir=None):
        super().__init__()
        self.webcam = None
        self._init_webcam()
        # Add camera settings attributes needed by web app
        self.exposure_us = 100000  # Default exposure time in microseconds
        self.gain = 1.0  # Default gain value
        self.use_digital_gain = False  # Whether to use digital gain
        self.digital_gain = 1.0  # Digital gain value
        self.save_raw = False  # Whether to save raw images
        self.recording = False  # Whether currently recording
        self.capture_status = "Ready"  # Current capture status
        self.capture_dir = capture_dir if capture_dir else "captures"  # Directory for saved images
        self.skip_frames = 0  # Performance setting
        self.exposure_mode = "manual"  # Exposure mode
        logger.info("Mock camera initialized")
    
    def _init_webcam(self):
        """Try to initialize webcam if available."""
        try:
            self.webcam = cv2.VideoCapture(0)
            if self.webcam.isOpened():
                logger.info("Mock camera: Using webcam for preview")
            else:
                self.webcam = None
                logger.warning("Mock camera: Webcam not available, using random data")
        except Exception as e:
            logger.warning(f"Mock camera: Could not initialize webcam: {e}")
            self.webcam = None
    
    def initialize(self):
        """Initialize the mock camera."""
        logger.info("Mock camera: initialize()")
        try:
            # Create capture directory if it doesn't exist
            os.makedirs(self.capture_dir, exist_ok=True)
            self.status = "Mock camera ready"
            logger.info("Mock camera initialized successfully")
        except Exception as e:
            self.status = f"Mock camera error: {str(e)}"
            logger.error(f"Failed to initialize mock camera: {e}")
            raise
    
    def create_preview_configuration(self, main=None):
        return {"type": "preview", "main": main}
    
    def create_still_configuration(self, main=None, raw=None):
        return {"type": "still", "main": main, "raw": raw}
    
    def create_video_configuration(self, main=None):
        return {"type": "video", "main": main}
    
    def configure(self, config):
        logger.debug(f"Mock camera: configure({config})")
    
    def start(self):
        logger.debug("Mock camera: start()")
        self.started = True
    
    def stop(self):
        logger.debug("Mock camera: stop()")
        self.started = False
    
    def capture_array(self, name="main"):
        """Return webcam frame or dummy data."""
        if self.webcam and self.webcam.isOpened():
            ret, frame = self.webcam.read()
            if ret:
                frame = cv2.resize(frame, (1440, 810))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                return frame
        
        # Fallback to dummy image
        return np.random.randint(0, 255, (810, 1440, 3), dtype=np.uint8)
    
    def capture_file(self, filename, name=None):
        """Create dummy image file."""
        logger.debug(f"Mock camera: capture_file({filename}, {name})")
        dummy_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        cv2.imwrite(filename, dummy_image)
    
    def set_controls(self, controls):
        logger.debug(f"Mock camera: set_controls({controls})")
    
    def start_recording(self, encoder, filename):
        logger.debug(f"Mock camera: start_recording({encoder}, {filename})")
        self.recording = True
    
    def stop_recording(self):
        logger.debug("Mock camera: stop_recording()")
        self.recording = False
    
    def cleanup(self):
        logger.debug("Mock camera: cleanup()")
        if self.webcam:
            self.webcam.release()
            self.webcam = None
    
    def us_to_shutter_string(self, us):
        """Convert microseconds to a human-readable shutter speed string."""
        if us >= 1000000:  # 1 second or longer
            return f"{us/1000000:.1f}s"
        else:
            return f"1/{int(1000000/us)}"
    
    def gain_to_iso(self, gain):
        """Convert gain value to ISO equivalent."""
        return int(gain * 100)
    
    def iso_to_gain(self, iso):
        """Convert ISO value to gain."""
        return iso / 100.0
    
    def slider_to_us(self, slider_value):
        """Convert slider value to microseconds."""
        min_us = 100
        max_us = 200_000_000
        log_range = math.log(max_us / min_us)
        return int(min_us * math.exp(slider_value * log_range / 1000))
    
    def get_exposure_seconds(self):
        """Get the current exposure time in seconds."""
        return self.exposure_us / 1000000.0
    
    def get_exposure_us(self):
        """Get the current exposure time in microseconds."""
        return self.exposure_us
    
    def set_exposure_us(self, us):
        """Set the exposure time in microseconds."""
        self.exposure_us = us
    
    def get_frame(self):
        """Get a frame as JPEG data."""
        try:
            frame = self.capture_array()
            if frame is not None:
                # Apply digital gain if enabled
                if self.use_digital_gain and self.digital_gain > 1.0:
                    frame = cv2.multiply(frame, self.digital_gain)
                
                # Convert to JPEG
                _, jpeg = cv2.imencode('.jpg', frame)
                return jpeg.tobytes()
        except Exception as e:
            logger.error(f"Error getting frame: {e}")
        return None
    
    def capture_still(self):
        """Capture a still image."""
        try:
            self.capture_status = "Capturing..."
            frame = self.capture_array()
            
            # Apply digital gain if enabled
            if self.use_digital_gain and self.digital_gain > 1.0:
                frame = cv2.multiply(frame, self.digital_gain)
            
            # Save the image
            filename = f"{self.capture_dir}/capture_{int(time.time())}.jpg"
            cv2.imwrite(filename, frame)
            
            self.capture_status = "Capture complete"
            return True
        except Exception as e:
            self.capture_status = f"Capture failed: {str(e)}"
            logger.error(f"Error capturing still: {e}")
            return False

# Mock encoder class
class MockH264Encoder:
    def __init__(self, bitrate=None):
        self.bitrate = bitrate
        logger.info(f"Mock H264Encoder initialized with bitrate={bitrate}")