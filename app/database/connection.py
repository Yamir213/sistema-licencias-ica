# ============================================
# CAMBIADO A SQLITE - VERSIÓN DE DESARROLLO
# ============================================

from .sqlite_connection import engine, SessionLocal, Base, get_db

# Re-exportar todo para que el resto del proyecto funcione igual
__all__ = ["engine", "SessionLocal", "Base", "get_db"]

print("✅ Usando SQLite - Modo desarrollo")