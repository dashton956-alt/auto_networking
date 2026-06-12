"""Platform-wide exception hierarchy."""


class ANIFError(Exception):
    """Base exception for all ANIF platform errors."""


class IntentValidationError(ANIFError):
    """Raised when an intent fails schema or constraint validation."""


class PolicyEvaluationError(ANIFError):
    """Raised when policy evaluation encounters an unrecoverable error."""


class RiskScoringError(ANIFError):
    """Raised when risk scoring cannot produce a deterministic result."""


class AuditWriteError(ANIFError):
    """Raised when an audit record cannot be written. Halts the pipeline."""


class GovernanceError(ANIFError):
    """Raised when governance gate encounters an invalid state."""


class SoTAdapterError(ANIFError):
    """Raised when the source-of-truth adapter cannot reach its backend."""
