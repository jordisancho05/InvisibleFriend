"""Script de pruebas y demostración de funcionalidades."""

from pathlib import Path
from invisible_friend.config import Config
from invisible_friend.models import Persona
from invisible_friend.validators import ParejaValidator
from invisible_friend.services.secret_santa import SecretSantaService
from invisible_friend.utils.logger import get_logger

logger = get_logger(__name__)


def demo_basico() -> None:
    """Demostración básica de funcionalidades."""
    print("\n" + "="*60)
    print("🎁 DEMOSTRACIÓN - INVISIBLE FRIEND")
    print("="*60 + "\n")
    
    # 1. Crear personas manualmente
    print("1️⃣  Creando personas...")
    personas = [
        Persona("Alice", "alice@example.com"),
        Persona("Bob", "bob@example.com"),
        Persona("Charlie", "charlie@example.com"),
        Persona("Diana", "diana@example.com"),
    ]
    print(f"   ✓ {len(personas)} personas creadas\n")
    
    # 2. Crear validador con restricciones
    print("2️⃣  Configurando restricciones...")
    restricciones = [["Alice", "Bob"]]
    validator = ParejaValidator(restricciones)
    print(f"   ✓ {len(restricciones)} restricción(es) configurada(s)\n")
    
    # 3. Validar parejas
    print("3️⃣  Validando parejas...")
    print(f"   Alice - Bob: {validator.es_pareja_valida(personas[0], personas[1])}")
    print(f"   Alice - Charlie: {validator.es_pareja_valida(personas[0], personas[2])}\n")
    
    # 4. Generar asignaciones
    print("4️⃣  Generando asignaciones...")
    service = SecretSantaService(validator, max_intentos=100)
    asignaciones = service.generar_asignaciones(personas)
    print(f"   ✓ Asignaciones generadas!\n")
    
    # 5. Mostrar asignaciones
    print("5️⃣  Mostrando asignaciones:")
    service.imprimir_asignaciones(asignaciones)
    print()


def demo_config() -> None:
    """Demostración cargando configuración desde YAML."""
    print("\n" + "="*60)
    print("⚙️  DEMOSTRACIÓN - CARGANDO CONFIGURACIÓN")
    print("="*60 + "\n")
    
    try:
        config = Config(Path("config/settings.yaml"))
        
        print(f"📋 Personas cargadas: {len(config.personas)}")
        for persona in config.personas[:3]:
            print(f"   - {persona.nombre} ({persona.email or 'sin email'})")
        
        print(f"\n🚫 Restricciones: {len(config.restricciones)}")
        for restriccion in config.restricciones[:2]:
            print(f"   - {restriccion[0]} ≠ {restriccion[1]}")
        
        print(f"\n⚡ Configuración SMTP:")
        print(f"   - Servidor: {config.smtp_server}")
        print(f"   - Puerto: {config.smtp_port}")
        print(f"   - Max intentos: {config.max_intentos}\n")
        
    except Exception as e:
        print(f"❌ Error cargando configuración: {e}\n")


def demo_errores() -> None:
    """Demostración de manejo de errores."""
    print("\n" + "="*60)
    print("🔴 DEMOSTRACIÓN - MANEJO DE ERRORES")
    print("="*60 + "\n")
    
    from invisible_friend.exceptions import ValidationError
    
    # Intentar crear persona con email inválido
    print("1️⃣  Intentando crear persona con email inválido...")
    try:
        Persona("Juan", "email_invalido")
    except ValidationError as e:
        print(f"   ✓ Error capturado: {e}\n")
    
    # Intentar asignar persona a sí misma
    print("2️⃣  Intentando asignar persona a sí misma...")
    try:
        Persona("Juan", "juan@example.com")
        from invisible_friend.models import Asignacion
        p = Persona("Juan", "juan@example.com")
        Asignacion(p, p)
    except ValidationError as e:
        print(f"   ✓ Error capturado: {e}\n")


if __name__ == "__main__":
    demo_basico()
    demo_config()
    demo_errores()
    
    print("✅ Demostraciones completadas!\n")
