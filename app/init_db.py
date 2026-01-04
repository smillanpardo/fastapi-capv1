"""
Script para inicializar/reiniciar la base de datos.
Crea todas las tablas definidas en los modelos.
"""
from db.database import engine, Base
from models.user import Usuario
from models.transaction import Transaction

def init_db():
    """Crea todas las tablas en la base de datos"""
    print("Creando tablas en la base de datos...")
    print(f"Modelos detectados: {len(Base.metadata.tables)} tablas")
    print(f"Tablas a crear: {list(Base.metadata.tables.keys())}")
    Base.metadata.create_all(bind=engine)
    print("✅ Tablas creadas exitosamente")

def drop_all_tables():
    """Elimina todas las tablas (usar solo en desarrollo)"""
    print("⚠️  Eliminando todas las tablas...")
    Base.metadata.drop_all(bind=engine)
    print("✅ Tablas eliminadas")

def reset_db():
    """Reinicia la base de datos (elimina y recrea todas las tablas)"""
    drop_all_tables()
    init_db()

if __name__ == "__main__":
    # Descomenta la función que necesites ejecutar:
    # init_db()  # Solo crear tablas nuevas
    reset_db()  # Eliminar y recrear todas las tablas (RECOMENDADO para agregar nuevos campos)
