"""Exception handlers for the REST API.

The app raises custom domain exceptions from the service layer; these handlers
convert them into the JSON responses expected by the frontend.
"""

from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.core.exceptions import AppException


async def handle_app_exception(_: Request, exc: AppException) -> JSONResponse:
	"""Serialize a custom application exception into a JSON error response."""
	return JSONResponse(
		status_code=exc.status_code,
		content={"detail": exc.detail},
	)


async def handle_http_exception(_: Request, exc: HTTPException) -> JSONResponse:
	"""Preserve existing FastAPI HTTP exceptions as JSON error responses."""
	return JSONResponse(
		status_code=exc.status_code,
		content={"detail": exc.detail},
	)


async def handle_validation_exception(
	_: Request,
	exc: RequestValidationError,
) -> JSONResponse:
	"""Return validation errors in the same detail shape the frontend already expects."""
	return JSONResponse(
		status_code=422,
		content={"detail": exc.errors()},
	)


async def handle_unexpected_exception(_: Request, exc: Exception) -> JSONResponse:
	"""Provide a safe fallback for uncaught exceptions without leaking internals."""
	return JSONResponse(
		status_code=500,
		content={"detail": "Internal server error"},
	)


def add_error_handlers(app: FastAPI) -> None:
	"""Register the application-level exception handlers."""
	app.add_exception_handler(AppException, handle_app_exception)
	app.add_exception_handler(HTTPException, handle_http_exception)
	app.add_exception_handler(RequestValidationError, handle_validation_exception)
	app.add_exception_handler(Exception, handle_unexpected_exception)
