import logging
from datetime import datetime
import os
import traceback
from functools import wraps

class LogHandler(logging.Handler):
    """Custom handler to prevent exc_info overwrite"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.history = []

    def emit(self, record):
        if hasattr(record, 'exc_info') and record.exc_info:
            self.history.append(record.exc_info)
        try:
            msg = self.format(record)
            self.stream.write(msg + self.terminator)
            self.flush()
        finally:
            if self.history:
                record.exc_info = self.history.pop()

class LoggerSetup:
    @staticmethod
    def setup():
        # Create logs directory if it doesn't exist
        log_dir = 'logs'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Ana logger ayarları
        main_logger = logging.getLogger('PrezzoBot')
        main_logger.setLevel(logging.DEBUG)  # En detaylı log seviyesi
        
        # Genel loglar için handler
        general_handler = logging.FileHandler(f'{log_dir}/bot_{timestamp}.log')
        general_handler.setLevel(logging.INFO)
        
        # Hata logları için özel handler
        error_handler = LogHandler(filename=f'{log_dir}/errors_{timestamp}.log')
        error_handler.setLevel(logging.ERROR)
        error_handler.addFilter(lambda record: record.levelno >= logging.ERROR)
        
        # Debug logları için handler
        debug_handler = logging.FileHandler(f'{log_dir}/debug_{timestamp}.log')
        debug_handler.setLevel(logging.DEBUG)
        
        # Konsol çıktısı için handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Format tanımlamaları
        debug_format = logging.Formatter(
            '%(asctime)s:%(levelname)s:[%(module)s:%(funcName)s:%(lineno)d] - %(message)s'
        )
        error_format = logging.Formatter(
            '%(asctime)s:%(levelname)s:[%(module)s:%(funcName)s:%(lineno)d]\n'
            'Message: %(message)s\n'
            'Exception: %(exc_info)s\n'
            'Details: %(details)s\n'
            'Stack: %(stack)s\n'
        )
        general_format = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s')
        
        # Format atamaları
        debug_handler.setFormatter(debug_format)
        error_handler.setFormatter(error_format)
        general_handler.setFormatter(general_format)
        console_handler.setFormatter(general_format)
        
        # Handler'ları logger'a ekle
        main_logger.addHandler(general_handler)
        main_logger.addHandler(error_handler)
        main_logger.addHandler(debug_handler)
        main_logger.addHandler(console_handler)
        
        return main_logger

def log_step(step_name):
    """Decorator for logging survey steps"""
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            logger = logging.getLogger('PrezzoBot')
            try:
                logger.info(f"Starting step: {step_name}")
                logger.debug(f"Step details - Function: {func.__name__}, Args: {args}, Kwargs: {kwargs}")
                result = func(self, *args, **kwargs)
                logger.info(f"Successfully completed step: {step_name}")
                return result
            except Exception as e:
                error_details = {
                    'step': step_name,
                    'function': func.__name__,
                    'error_type': type(e).__name__,
                    'error_msg': str(e),
                    'stack_trace': traceback.format_exc()
                }
                logger.error(
                    f"Error in step '{step_name}'",
                    extra={
                        'details': error_details,
                        'stack_info': traceback.format_exc()
                    }
                )
                raise
        return wrapper
    return decorator

def log_error(logger, message, exc_info=None, details=None, stack=None):
    """Error logları için yardımcı fonksiyon"""
    try:
        extra = {
            'details': details if details else {},
            'stack': stack if stack else '',
        }
        logger.error(message, exc_info=exc_info if exc_info else True, extra=extra)
    except Exception as e:
        print(f"Logging error: {e}")

# Export the necessary functions and classes
__all__ = ['LoggerSetup', 'log_step', 'log_error']
