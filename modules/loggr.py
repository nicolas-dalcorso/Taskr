"""
Implements a simple, stand-alone logging module.


"""

from enum import Enum;
import os;
from logging import getLogger, StreamHandler, Formatter, DEBUG, INFO, WARNING, ERROR, CRITICAL;

class LogLevel(Enum):
    DEBUG = DEBUG;
    INFO = INFO;
    WARNING = WARNING;
    ERROR = ERROR;
    CRITICAL = CRITICAL;
    
class LogStatus(Enum):
    LOG_STATUS__SUCCESS             = 0;
    LOG_STATUS__ERR_FILE_NOT_FOUND  = 1;
    LOG_STATUS__ERR_CANNOT_WRITE    = 2;
    LOG_STATUS__ERR_UNKNOWN         = 3;
    
class Loggr:
    """General class for the logger. Implements a simple logging system based on a logfile.
    """
    def __init__(self, log_file, log_level=LogLevel.DEBUG, formatter_string='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%m-%d-%Y %I:%M:%S %p'):
        #   Set the logfile
        #   Check if the logfile exists
        if(not os.path.exists(log_file)):
            try:
                with open(log_file, 'w') as f:
                    f.write('');
            except:
                return LogStatus.LOG_STATUS__ERR_FILE_NOT_FOUND;
        
        self.log_file = open(log_file, "a+");
        
        #   Set the log level
        self.log_level = log_level;
        
        #   Set the logger
        self.logger = getLogger(__name__);
        self.logger.setLevel(self.log_level.value);
        
        #   Set the handler
        self.handler = StreamHandler(self.log_file);
        self.handler.setLevel(self.log_level.value);
        
        #   Set the formatter
        self.formatter = Formatter(formatter_string, datefmt);
        self.handler.setFormatter(self.formatter);
        
        #   Add the handler to the logger
        self.logger.addHandler(self.handler);
        
        self.log('Logging session started.', LogLevel.INFO);
        
        
        
    def log(self, message, level=LogLevel.INFO):
        if level.value >= self.log_level.value:
            self.logger.log(level.value, message);
            return LogStatus.LOG_STATUS__SUCCESS;
        else:
            return LogStatus.LOG_STATUS__ERR_UNKNOWN;
        
    def debug(self, message):
        return self.log(message, LogLevel.DEBUG);
    
    def info(self, message):
        return self.log(message, LogLevel.INFO);
    
    def warning(self, message):
        return self.log(message, LogLevel.WARNING);
    
    def error(self, message):
        return self.log(message, LogLevel.ERROR);
    
    def critical(self, message):
        return self.log(message, LogLevel.CRITICAL);
    
    def set_log_level(self, log_level):
        self.log_level = log_level;
        self.logger.setLevel(self.log_level.value);
        self.handler.setLevel(self.log_level.value);
        
    def get_log_level(self):
        return self.log_level;
    
    def set_log_file(self, log_file):
        self.log_file = log_file;
        
    def get_log_file(self):
        return self.log_file;
    
    def close(self):
        self.log('Logging session closed.', LogLevel.INFO);
        self.logger.removeHandler(self.handler);
        self.handler.close();
        
    def __del__(self):
        self.close();