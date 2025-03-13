from dataclasses import dataclass

@dataclass
class Config:
    EXCEL_FILE: str = 'veriler-1.xlsx'
    URL: str = 'https://www.prezzovoice.co.uk'
    MAX_RETRIES: int = 1
    RETRY_DELAY: int = 5  # Increased from 5
    IMPLICIT_WAIT: int = 2  # Reduced from 3
    PAGE_LOAD_TIMEOUT: int = 15  # Reduced from 20
    
    # Proxy configuration
    USE_PROXY: bool = False
    PROXY_LIST: list = None

    # Error handling configuration
    RESTART_ON_ERROR: bool = False  # Hata durumunda başa dönmeyi kontrol eder
    CONTINUE_FROM_ERROR: bool = True  # Hata alınan yerden devam etmeyi sağlar
    ERROR_SCREENSHOT: bool = True  # Hata durumunda ekran görüntüsü alma
    MAX_ATTEMPTS: int = 2  # Added for stuck detection
    MAX_CONSECUTIVE_ERRORS: int = 3  # Added for error handling
    BROWSER_CHECK_INTERVAL: int = 5  # Added for browser status check

    # Performance configuration - optimized timings
    MIN_WAIT: float = 0.05  # Reduced from 0.1
    MAX_WAIT: float = 0.2  # Reduced from 0.3
    TYPE_PAUSE: float = 0.01  # Reduced from 0.02
    PAGE_WAIT: float = 0.3  # Changed from 1 to 0.3
    
    # Browser configuration
    HEADLESS: bool = False  # Headless mode
    DISABLE_IMAGES: bool = True  # Disable image loading
    DISABLE_ANIMATIONS: bool = True  # Disable animations

    # Browser View Configuration
    WINDOW_WIDTH: int = 1920
    WINDOW_HEIGHT: int = 1080
    VIEWPORT_WIDTH: int = 1366
    VIEWPORT_HEIGHT: int = 768
    USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    
    # Resource Loading Configuration
    BLOCK_RESOURCES: bool = True  # Block unnecessary resources
    LOAD_IMAGES: bool = True  # Load images
    LOAD_CSS: bool = True  # Load CSS
    LOAD_JS: bool = True  # Load JavaScript
    BLOCK_MEDIA: bool = True  # Block media (audio/video)
    BLOCK_FONTS: bool = True  # Block custom fonts
    
    # Page Render Configuration
    FORCE_DARK_MODE: bool = False
    FORCE_COLORS: bool = True
    HIGH_CONTRAST: bool = False
    REDUCED_MOTION: bool = True

    def __post_init__(self):
        if self.PROXY_LIST is None:
            self.PROXY_LIST = [
                'http://proxy1:8080',
                'http://proxy2:8080'
            ]

    def get_prefs(self) -> dict:
        """Browser preferences for resource loading"""
        return {
            'profile.default_content_setting_values': {
                'images': 1 if self.LOAD_IMAGES else 2,
                'javascript': 1 if self.LOAD_JS else 2,
                'stylesheet': 1 if self.LOAD_CSS else 2,
                'media_stream': 2 if self.BLOCK_MEDIA else 1,
                'plugins': 2,
                'popups': 2,
                'geolocation': 2,
                'notifications': 2,
                'auto_select_certificate': 2,
                'fullscreen': 2,
                'mouselock': 2,
                'mixed_script': 2,
                'media_stream_mic': 2,
                'media_stream_camera': 2,
                'protocol_handlers': 2,
                'ppapi_broker': 2,
                'automatic_downloads': 2,
                'midi_sysex': 2,
                'push_messaging': 2,
                'ssl_cert_decisions': 2,
                'metro_switch_to_desktop': 2,
                'protected_media_identifier': 2,
                'app_banner': 2,
                'site_engagement': 2,
                'durable_storage': 2
            }
        }

# Create default configuration instance
config = Config()

# Make sure to export the config instance
__all__ = ['Config', 'config']
