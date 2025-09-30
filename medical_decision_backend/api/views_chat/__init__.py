# PUBLIC_INTERFACE
def __getattr__(name):
    """
    This package-level __getattr__ re-exports view callables from the sibling module
    `api.views_chat` (file: views_chat.py). This allows imports like:
        from api.views_chat import chat, recommend, upload_report, get_recommendation
    to work even though there is also a package directory named `views_chat/`.
    """
    # Lazy import to avoid Django app registry issues at import time
    from .. import views_chat as _views_chat_module
    # expose expected view functions if present
    exports = {
        "chat": getattr(_views_chat_module, "chat", None),
        "recommend": getattr(_views_chat_module, "recommend", None),
        "upload_report": getattr(_views_chat_module, "upload_report", None),
        "get_recommendation": getattr(_views_chat_module, "get_recommendation", None),
    }
    if name in exports and exports[name] is not None:
        return exports[name]
    raise AttributeError(f"module 'api.views_chat' has no attribute '{name}'")

# Explicit __all__ for static analyzers and star-import safety
__all__ = ["chat", "recommend", "upload_report", "get_recommendation"]
