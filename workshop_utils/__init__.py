"""Workshop helper utilities.

Importing from the package root keeps notebook cells short::

    from workshop_utils import get_chat_client
"""

from .clients import SUPPORTED_PROVIDERS, current_provider, get_chat_client

__all__ = ["get_chat_client", "current_provider", "SUPPORTED_PROVIDERS"]
