# Explicit static imports to avoid dynamic attribute lookups and recursive imports.
# Re-export view callables from the sibling module file 'api/views_chat.py'.

# PUBLIC_INTERFACE
from ..views_chat import chat  # noqa: F401

# PUBLIC_INTERFACE
from ..views_chat import recommend  # noqa: F401

# PUBLIC_INTERFACE
from ..views_chat import upload_report  # noqa: F401

# PUBLIC_INTERFACE
from ..views_chat import get_recommendation  # noqa: F401

# Explicit __all__ for static analyzers and star-import safety
__all__ = ["chat", "recommend", "upload_report", "get_recommendation"]
