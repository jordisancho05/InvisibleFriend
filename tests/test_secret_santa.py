"""Tests para el servicio de Secret Santa."""

import unittest
from unittest.mock import MagicMock
from invisible_friend.models import Persona
from invisible_friend.validators import ParejaValidator
from invisible_friend.services.secret_santa import SecretSantaService
from invisible_friend.exceptions import AssignmentError


class TestSecretSantaService(unittest.TestCase):
    """Tests para SecretSantaService."""
    
    def setUp(self) -> None:
        """Configuración previa a cada test."""
        self.restricciones = [["Alice", "Bob"]]
        self.validator = ParejaValidator(self.restricciones)
        self.service = SecretSantaService(self.validator, max_intentos=100)
        
        self.personas = [
            Persona("Alice", "alice@example.com"),
            Persona("Bob", "bob@example.com"),
            Persona("Charlie", "charlie@example.com"),
            Persona("Diana", "diana@example.com"),
        ]
    
    def test_generar_asignaciones_validas(self) -> None:
        """Test que verifica que se generan asignaciones válidas."""
        asignaciones = self.service.generar_asignaciones(self.personas)
        
        # Debe haber una asignación por persona
        self.assertEqual(len(asignaciones), len(self.personas))
        
        # Cada persona debe estar asignada a alguien
        for persona, asignado in asignaciones.items():
            self.assertIsNotNone(asignado)
            self.assertNotEqual(persona, asignado)
    
    def test_generar_asignaciones_forma_ciclo(self) -> None:
        """Test que verifica que las asignaciones forman un ciclo."""
        asignaciones = self.service.generar_asignaciones(self.personas)
        
        # Verificar que cada persona está exactamente una vez
        personas_asignadas = set()
        for persona, asignado in asignaciones.items():
            personas_asignadas.add(persona)
            personas_asignadas.add(asignado)
        
        self.assertEqual(len(personas_asignadas), len(self.personas))
    
    def test_generar_asignaciones_pocas_personas(self) -> None:
        """Test que verifica error con pocas personas."""
        with self.assertRaises(AssignmentError):
            self.service.generar_asignaciones([self.personas[0]])
    
    def test_obtener_asignaciones_formateadas(self) -> None:
        """Test para conversión a formato nombre -> nombre."""
        asignaciones = self.service.generar_asignaciones(self.personas)
        formateadas = self.service.obtener_asignaciones_formateadas(asignaciones)
        
        # Debe ser un diccionario de strings
        for de, para in formateadas.items():
            self.assertIsInstance(de, str)
            self.assertIsInstance(para, str)
    
    def test_imprimir_asignaciones(self, capsys=None) -> None:
        """Test para impresión de asignaciones."""
        asignaciones = self.service.generar_asignaciones(self.personas)
        
        # Solo verificar que no lance excepción
        self.service.imprimir_asignaciones(asignaciones)


if __name__ == "__main__":
    unittest.main()
