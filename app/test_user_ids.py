"""
Script de prueba para verificar la generación de user_id automático
"""
from sqlalchemy.orm import Session
from db.database import SessionLocal
from crud.user import crear_usuario
from schemas.user import UsuarioCreate
from models.transaction import UserRole


def test_user_id_generation():
    """Prueba la generación automática de user_id"""
    db: Session = SessionLocal()
    
    try:
        print("🧪 Probando generación de user_id automático...\n")
        
        # Crear operadores
        print("1️⃣ Creando operadores...")
        operador1 = crear_usuario(db, UsuarioCreate(
            nombre="Juan Operador",
            email="juan@example.com",
            password="password123",
            role=UserRole.OPERADOR
        ))
        print(f"   ✅ Operador 1: {operador1.user_id} - {operador1.nombre}")
        
        operador2 = crear_usuario(db, UsuarioCreate(
            nombre="Maria Operadora",
            email="maria@example.com",
            password="password123",
            role=UserRole.OPERADOR
        ))
        print(f"   ✅ Operador 2: {operador2.user_id} - {operador2.nombre}")
        
        operador3 = crear_usuario(db, UsuarioCreate(
            nombre="Carlos Operador",
            email="carlos@example.com",
            password="password123",
            role=UserRole.OPERADOR
        ))
        print(f"   ✅ Operador 3: {operador3.user_id} - {operador3.nombre}")
        
        # Crear aprobadores
        print("\n2️⃣ Creando aprobadores...")
        aprobador1 = crear_usuario(db, UsuarioCreate(
            nombre="Ana Aprobadora",
            email="ana@example.com",
            password="password123",
            role=UserRole.APROBADOR
        ))
        print(f"   ✅ Aprobador 1: {aprobador1.user_id} - {aprobador1.nombre}")
        
        aprobador2 = crear_usuario(db, UsuarioCreate(
            nombre="Luis Aprobador",
            email="luis@example.com",
            password="password123",
            role=UserRole.APROBADOR
        ))
        print(f"   ✅ Aprobador 2: {aprobador2.user_id} - {aprobador2.nombre}")
        
        print("\n✅ ¡Prueba exitosa!")
        print("\n📋 Resumen:")
        print(f"   - Operadores: {operador1.user_id}, {operador2.user_id}, {operador3.user_id}")
        print(f"   - Aprobadores: {aprobador1.user_id}, {aprobador2.user_id}")
        
    except Exception as e:
        print(f"\n❌ Error durante la prueba: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    test_user_id_generation()
