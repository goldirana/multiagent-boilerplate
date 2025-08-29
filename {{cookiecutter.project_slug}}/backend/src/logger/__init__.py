import logging
import os
import re
from pathlib import Path
from logging.handlers import RotatingFileHandler
from backend.src.constants import CONFIG_FILE_PATH

import yaml
from box import ConfigBox

# import watchtower  # AWS CloudWatch logging
def read_yaml(file_path: str):
    try:
        with open(file_path, 'r') as file:
            params = yaml.safe_load(file)
        return ConfigBox(params)
    except FileNotFoundError:
        raise FileNotFoundError(f"YAML file not found at {file_path}")

def create_log_dir(base_dir): 
    os.makedirs(base_dir, exist_ok=True)

class CustomLogger:
    """Custom logger with additional logging methods and colored output support."""
    
    def __init__(self, name, log_file, log_level, log_format, third_party_level, get_aws_watchtower=True):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level)
        
        # Store original log levels for restoration if needed
        self.original_levels = {}
        
        # Set third party loggers
        for lib in ["openai", "urllib3", "langchain", "pymongo", "httpcore", "mongoengine"]:
            lib_logger = logging.getLogger(lib)
            self.original_levels[lib] = lib_logger.level
            lib_logger.setLevel(third_party_level)

        # Create formatter
        self.formatter = logging.Formatter(log_format)
        
        # Stream handler (colored output)
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(self.formatter)
        
        # File handler (no ANSI colors)
        file_handler = RotatingFileHandler(log_file, maxBytes=10_000_000, backupCount=5)
        file_handler.setFormatter(self.formatter)
        
        # No ANSI handler for clean file logging
        class NoAnsiFileHandler(RotatingFileHandler):
            def emit(self, record):
                record.msg = re.sub(r"\033\[[0-9;]*m", "", str(record.msg))
                super().emit(record)
        
        no_ansi_handler = NoAnsiFileHandler(log_file, maxBytes=10_000_000, backupCount=5)
        no_ansi_handler.setFormatter(self.formatter)
        
        # Configure basic logging
        logging.basicConfig(
            level=log_level,
            format=log_format,
            handlers=[stream_handler, file_handler, no_ansi_handler]
        )
        
        # Add AWS CloudWatch if enabled
        if get_aws_watchtower:
            try:
                cloudwatch_handler = watchtower.CloudWatchLogHandler(log_group="/ecs/xxx")
                cloudwatch_handler.setFormatter(self.formatter)
                self.logger.addHandler(cloudwatch_handler)
            except Exception as e:
                self.logger.error("Failed to add AWS cloudwatch handler: %s", e)
    
    def _log_with_color(self, level, msg, color_code=None, *args, **kwargs):
        """Internal method to log with optional color coding."""
        if color_code:
            colored_msg = f"\033[{color_code}m{msg}\033[0m"
            self.logger.log(level, colored_msg, *args, **kwargs)
        else:
            self.logger.log(level, msg, *args, **kwargs)
    
    # Standard logging methods
    def debug(self, msg, *args, **kwargs):
        self._log_with_color(logging.DEBUG, msg, "1;36", *args, **kwargs)  # Cyan
    
    def info(self, msg, *args, **kwargs):
        self._log_with_color(logging.INFO, msg, "1;37", *args, **kwargs)  # White
    
    def warning(self, msg, *args, **kwargs):
        self._log_with_color(logging.WARNING, msg, "1;33", *args, **kwargs)  # Yellow
    
    def error(self, msg, *args, **kwargs):
        self._log_with_color(logging.ERROR, msg, "1;31", *args, **kwargs)  # Red
    
    def critical(self, msg, *args, **kwargs):
        self._log_with_color(logging.CRITICAL, msg, "1;35;41", *args, **kwargs)  # Purple on red background
    
    # Custom logging methods
    def ok(self, msg, *args, **kwargs):
        """Log a success/OK message"""
        self._log_with_color(logging.INFO, f"✅ {msg}", "1;32", *args, **kwargs)  # Green
    
    def success(self, msg, *args, **kwargs):
        """Log a success message"""
        self._log_with_color(logging.INFO, f"🎉 SUCCESS: {msg}", "1;32", *args, **kwargs)  # Green
    
    def fail(self, msg, *args, **kwargs):
        """Log a failure message"""
        self._log_with_color(logging.ERROR, f"❌ FAIL: {msg}", "1;31", *args, **kwargs)  # Red
    
    def note(self, msg, *args, **kwargs):
        """Log an important note"""
        self._log_with_color(logging.INFO, f"📝 NOTE: {msg}", "1;34", *args, **kwargs)  # Blue
    
    def important(self, msg, *args, **kwargs):
        """Log an important message"""
        self._log_with_color(logging.WARNING, f"⚠️  IMPORTANT: {msg}", "1;33", *args, **kwargs)  # Yellow
    
    def step(self, msg, *args, **kwargs):
        """Log a process step"""
        self._log_with_color(logging.INFO, f"➡️  STEP: {msg}", "1;36", *args, **kwargs)  # Cyan
    
    def completed(self, msg, *args, **kwargs):
        """Log completion of a task"""
        self._log_with_color(logging.INFO, f"✔️  COMPLETED: {msg}", "1;32", *args, **kwargs)  # Green
    
    def started(self, msg, *args, **kwargs):
        """Log start of a task"""
        self._log_with_color(logging.INFO, f"🚀 STARTED: {msg}", "1;35", *args, **kwargs)  # Purple
    
    def progress(self, msg, *args, **kwargs):
        """Log progress update"""
        self._log_with_color(logging.INFO, f"📊 PROGRESS: {msg}", "1;33", *args, **kwargs)  # Yellow
    
    def data(self, msg, *args, **kwargs):
        """Log data-related information"""
        self._log_with_color(logging.DEBUG, f"📊 DATA: {msg}", "1;36", *args, **kwargs)  # Cyan
    
    # Method to add custom log level dynamically
    def add_custom_level(self, level_name, level_num, color_code=None):
        """Dynamically add a custom log level"""
        if not hasattr(logging, level_name.upper()):
            logging.addLevelName(level_num, level_name.upper())
        
        def custom_log_method(msg, *args, **kwargs):
            self._log_with_color(level_num, msg, color_code, *args, **kwargs)
        
        setattr(self, level_name.lower(), custom_log_method)
    
    # Pass through other logging methods
    def __getattr__(self, name):
        """Pass through any other methods to the underlying logger"""
        return getattr(self.logger, name)

def get_logger(name, log_file, log_level, log_format, third_party_level, get_aws_watchtower=True):
    """
    Configure and return a custom logger with enhanced logging methods.
    """
    return CustomLogger(name, log_file, log_level, log_format, third_party_level, get_aws_watchtower)

def setup_logging(get_aws_watchtower=True):
    params = read_yaml(CONFIG_FILE_PATH)
    
    logging_params = params.LOGGING
    base_dir = logging_params.BASE_DIR
    log_file = logging_params.LOG_FILE
    log_level = logging_params.LOG_LEVEL
    log_format = logging_params.LOG_FORMAT
    third_party_level = logging_params.THIRD_PARTY_LOGGER_LEVEL
    get_aws_watchtower = logging_params.GET_AWS_WATCHTOWER

    create_log_dir(base_dir)
    logger = get_logger(__name__, os.path.join(base_dir, log_file), log_level, log_format, third_party_level, get_aws_watchtower=get_aws_watchtower)
    return logger

# Initialize the logger
logger = setup_logging()

if __name__ == "__main__":
    # Test all the custom logging methods
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
    
    # Custom methods
    logger.ok("Everything is working fine")
    logger.success("Operation completed successfully")
    logger.fail("Operation failed")
    logger.note("Please remember to save your work")
    logger.important("This is an important notification")
    logger.step("Starting phase 2 of the process")
    logger.completed("Data processing completed")
    logger.started("New analysis started")
    logger.progress("Processing 75% complete")
    logger.data("Received 150 records for processing")
    
    # You can also add custom levels dynamically
    logger.add_custom_level("SECURITY", 25, "1;35")  # Purple
    logger.security("Security alert detected")