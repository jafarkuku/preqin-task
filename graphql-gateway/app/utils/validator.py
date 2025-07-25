"""
Type-safe generic response validation helpers for GraphQL Gateway.
"""

import logging
from typing import Optional, TypeVar, Union, overload

logger = logging.getLogger(__name__)

T = TypeVar('T')


@overload
def safe_response(
    result: Union[T, BaseException, None],
    service_name: str,
    default: T
) -> T: ...


@overload
def safe_response(
    result: Union[T, BaseException, None],
    service_name: str,
    default: None = None
) -> Optional[T]: ...


def safe_response(
    result: Union[T, BaseException, None],
    service_name: str,
    default: Optional[T] = None
) -> Union[T, Optional[T]]:
    """
    Safely handle any service response with proper typing.

    Args:
        result: Service response (could be data, exception, or None)
        service_name: Service name for logging
        default: Default value to return on error

    Returns:
        Valid response or default value with proper typing
    """
    if isinstance(result, BaseException):
        logger.error("%s service error: %s", service_name, result)
        return default
    elif result is None:
        logger.warning("No %s response received", service_name)
        return default
    else:
        return result
