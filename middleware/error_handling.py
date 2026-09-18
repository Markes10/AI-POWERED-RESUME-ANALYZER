"""
Error handling middleware and custom exceptions
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
import traceback

try:
    from jose.exceptions import ExpiredSignatureError as JoseExpiredSignatureError
    from jose.exceptions import JWTError as JoseJWTError
    TokenExpiredError = JoseExpiredSignatureError
    TokenInvalidError = JoseJWTError
except Exception:
    try:
        from jwt.exceptions import ExpiredSignatureError as PyJWTExpiredSignatureError
        from jwt.exceptions import InvalidTokenError as PyJWTInvalidTokenError
        TokenExpiredError = PyJWTExpiredSignatureError
        TokenInvalidError = PyJWTInvalidTokenError
    except Exception:
        TokenExpiredError = None
        TokenInvalidError = None


class AuthError(Exception):
    def __init__(self, message: str):
        self.message = message


class PermissionError(Exception):
    def __init__(self, message: str):
        self.message = message


class NotFoundError(Exception):
    def __init__(self, message: str):
        self.message = message


class ValidationError(Exception):
    def __init__(self, message: str):
        self.message = message


async def error_handler(request: Request, call_next):
    try:
        return await call_next(request)
    except AuthError as e:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": str(e.message)},
        )
    except PermissionError as e:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": str(e.message)},
        )
    except NotFoundError as e:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(e.message)},
        )
    except ValidationError as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": str(e.message)},
        )
    except RequestValidationError as e:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": str(e)},
        )
    except TokenExpiredError:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Token has expired"},
        )
    except TokenInvalidError:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Invalid token"},
        )
    except SQLAlchemyError:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Database error occurred"},
        )
    except Exception:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "An unexpected error occurred"},
        )
