"""Tests para los validadores."""

import unittest
from invisible_friend.models import Persona
from invisible_friend.validators import ParejaValidator
from invisible_friend.exceptions import ValidationError


class TestParejaValidator(unittest.TestCase):
    """Tests para ParejaValidator."""
    
    def setUp(self) -> None:
        """Configuración previa a cada test."""
        self.restricciones = [
            ["Alice", "Bob"],
            ["Charlie", "Diana"],
        ]
        self.validator = ParejaValidator(self.restricciones)
        
        self.alice = Persona("Alice", "alice@example.com")
        self.bob = Persona("Bob", "bob@example.com")
        self.charlie = Persona("Charlie", "charlie@example.com")
        self.diana = Persona("Diana", "diana@example.com")
    
    def test_pareja_valida_permitida(self) -> None:
        """Test que verifica que parejas permitidas son válidas."""
        self.assertTrue(self.validator.es_pareja_valida(self.alice, self.charlie))
        self.assertTrue(self.validator.es_pareja_valida(self.bob, self.diana))
    
    def test_pareja_invalida_prohibida(self) -> None:
        """Test que verifica que parejas prohibidas son inválidas."""
        self.assertFalse(self.validator.es_pareja_valida(self.alice, self.bob))
        self.assertFalse(self.validator.es_pareja_valida(self.bob, self.alice))
        self.assertFalse(self.validator.es_pareja_valida(self.alice, self.alice))
    
    def test_pareja_misma_persona(self) -> None:
        """Test que verifica que una persona no puede ser su propio amigo invisible."""
        self.assertFalse(self.validator.es_pareja_valida(self.alice, self.alice))
    
    def test_validar_ciclo_valido(self) -> None:
        """Test que verifica validación de ciclo válido."""
        # Ciclo válido: Alice → Charlie → Bob → Diana → Alice
        ciclo = [self.alice, self.charlie, self.bob, self.diana]
        self.assertTrue(self.validator.validar_ciclo(ciclo))
    
    def test_validar_ciclo_invalido(self) -> None:
        """Test que verifica validación de ciclo inválido."""
        # Ciclo inválido: Alice → Bob (prohibido)
        ciclo = [self.alice, self.bob, self.charlie, self.diana]
        self.assertFalse(self.validator.validar_ciclo(ciclo))
    
    def test_agregar_restriccion(self) -> None:
        """Test para agregar restricción."""
        self.validator.agregar_restriccion("Alice", "Charlie")
        self.assertFalse(self.validator.es_pareja_valida(self.alice, self.charlie))
    
    def test_remover_restriccion(self) -> None:
        """Test para remover restricción."""
        self.validator.remover_restriccion("Alice", "Bob")
        self.assertTrue(self.validator.es_pareja_valida(self.alice, self.bob))


class TestPersonaModel(unittest.TestCase):
    """Tests para el modelo Persona."""
    
    def test_persona_valida(self) -> None:
        """Test que verifica creación de persona válida."""
        persona = Persona("Juan", "juan@example.com")
        self.assertEqual(persona.nombre, "Juan")
        self.assertEqual(persona.email, "juan@example.com")
    
    def test_persona_sin_email(self) -> None:
        """Test que verifica que el email es obligatorio."""
        with self.assertRaises(ValidationError):
            Persona("Juan", "")

    def test_persona_nombre_vacio(self) -> None:
        """Test que verifica validación de nombre vacío."""
        with self.assertRaises(ValidationError):
            Persona("", "juan@example.com")
    
    def test_persona_email_invalido(self) -> None:
        """Test que verifica validación de email inválido."""
        with self.assertRaises(ValidationError):
            Persona("Juan", "email_invalido")
    
    def test_persona_hash(self) -> None:
        """Test que verifica que personas se pueden usar en sets."""
        p1 = Persona("Juan", "juan@example.com")
        p2 = Persona("Juan", "otro@example.com")
        
        personas_set = {p1, p2}
        self.assertEqual(len(personas_set), 1)  # Mismo nombre = mismo hash


if __name__ == "__main__":
    unittest.main()
