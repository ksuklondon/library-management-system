"""
Moduł inicjalizujący pakiet models w auth-service.

Umożliwia wygodny import modeli, np.:
    from app.models import User
"""

from .user import User

# __all__ określa, które symbole będą eksportowane przy "from ... import *".
__all__ = ["User"]

