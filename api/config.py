"""
Distributed Agentic Reasoning Framework (DARF)

FastAPI Configuration
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List
import json


@dataclass(slots=True)
class APIConfig:
    """
    Global API configuration.
    """

    title: str = "Distributed Agentic Reasoning Framework"

    description: str = (
        "DARF REST API"
    )

    version: str = "1.0"

    host: str = "127.0.0.1"

    port: int = 8000

    debug: bool = True

    reload: bool = True

    docs_url: str = "/docs"

    redoc_url: str = "/redoc"

    openapi_url: str = "/openapi.json"

    cors_origins: List[str] = field(
        default_factory=lambda: [
            "*",
        ]
    )

    cors_methods: List[str] = field(
        default_factory=lambda: [
            "*",
        ]
    )

    cors_headers: List[str] = field(
        default_factory=lambda: [
            "*",
        ]
    )

    metadata: dict = field(
        default_factory=dict,
    )

    # ========================================================
    # Helpers
    # ========================================================

    def endpoint(self) -> str:

        return (
            f"http://{self.host}:{self.port}"
        )

    def docs(self) -> str:

        return (
            self.endpoint()
            + self.docs_url
        )

    def openapi(self) -> str:

        return (
            self.endpoint()
            + self.openapi_url
        )

    # ========================================================
    # Serialization
    # ========================================================

    def to_dict(self):

        return {

            "title": self.title,

            "description": self.description,

            "version": self.version,

            "host": self.host,

            "port": self.port,

            "debug": self.debug,

            "reload": self.reload,

            "docs_url": self.docs_url,

            "redoc_url": self.redoc_url,

            "openapi_url": self.openapi_url,

            "cors_origins": self.cors_origins,

            "cors_methods": self.cors_methods,

            "cors_headers": self.cors_headers,

            "metadata": self.metadata,

        }

    def to_json(self):

        return json.dumps(

            self.to_dict(),

            indent=4,

            sort_keys=True,

        )

    # ========================================================
    # Representation
    # ========================================================

    def __str__(self):

        return (
            f"APIConfig("
            f"{self.host}:{self.port})"
        )

    def __repr__(self):

        return (
            f"<APIConfig "
            f"host='{self.host}' "
            f"port={self.port}>"
        )