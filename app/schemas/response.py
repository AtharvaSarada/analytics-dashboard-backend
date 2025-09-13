"""
Response schemas for consistent API responses.
"""

from typing import Any, Generic, TypeVar, Optional
from pydantic import BaseModel

DataType = TypeVar("DataType")


class ResponseModel(BaseModel, Generic[DataType]):
    """
    Generic response model for consistent API responses.
    """
    success: bool = True
    message: str
    data: Optional[DataType] = None
    error: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True
