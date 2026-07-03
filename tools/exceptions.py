"""
Distributed Agentic Reasoning Framework (DARF)

Tool Exceptions
"""

class ToolError(Exception):
    """Base tool exception."""


class ToolExecutionError(ToolError):
    """Raised when tool execution fails."""


class ToolNotFoundError(ToolError):
    """Raised when a tool cannot be found."""


class ToolDisabledError(ToolError):
    """Raised when a disabled tool is executed."""


class ToolRegistrationError(ToolError):
    """Raised when tool registration fails."""


class ToolTimeoutError(ToolError):
    """Raised when a tool exceeds its timeout."""


class ToolValidationError(ToolError):
    """Raised when tool input validation fails."""