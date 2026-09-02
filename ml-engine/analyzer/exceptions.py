"""Custom exceptions for the analysis pipeline."""

from __future__ import annotations


class AnalysisError(Exception):
    """Base class for analysis failures."""

    code: str = "analysis_error"

    def __init__(self, message: str, *, code: str | None = None):
        super().__init__(message)
        if code:
            self.code = code


class ValidationError(AnalysisError):
    """Video failed pre-analysis quality checks."""

    code = "validation_failed"


class ProcessingError(AnalysisError):
    """Unexpected failure during processing."""

    code = "processing_failed"
