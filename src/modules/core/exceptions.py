class AppException(Exception):
    """Base exception class"""
    pass

class AuthError(AppException):
    """Authentication related errors"""
    
class DataError(AppException):
    """Data loading errors"""
    
class SessionError(AppException):
    """Session management errors"""