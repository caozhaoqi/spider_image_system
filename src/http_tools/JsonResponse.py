import os
import sys
from typing import Any, Dict, Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class JsonResponse:
    """Standardized JSON response format with success and error states"""

    def __init__(self, data: Any = None, code: int = 0, msg: str = '') -> None:
        """
        Initialize JSON response
        
        Args:
            data: Response payload
            code: Response status code (0=success, -1=error)
            msg: Response message
        """
        self.data = data
        self.code = code 
        self.msg = msg

    @classmethod
    def success(cls, data: Any = None, code: int = 0, msg: str = 'success') -> 'JsonResponse':
        """Create success response"""
        return cls(data, code, msg)

    @classmethod 
    def error(cls, data: Any = None, code: int = -1, msg: str = 'error') -> 'JsonResponse':
        """Create error response"""
        return cls(data, code, msg)

    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary format"""
        return {
            'code': self.code,
            'msg': self.msg,
            'data': self.data
        }
