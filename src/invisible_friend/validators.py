"""Validadores para parejas y restricciones."""

from typing import List, Set, Tuple
from invisible_friend.models import Persona
from invisible_friend.exceptions import ValidationError


class ParejaValidator:
    """Valida si dos personas pueden ser asignadas como amigos invisibles."""
    
    def __init__(self, restricciones: List[List[str]]) -> None:
        """
        Inicializa el validador.
        
        Args:
            restricciones: Lista de pares de nombres que no pueden ser asignados juntos
        """
        # Convertir a frozensets para búsqueda bidireccional eficiente
        self.restricciones: Set[frozenset] = {
            frozenset(par) for par in restricciones
        }
    
    def es_pareja_valida(self, persona1: Persona, persona2: Persona) -> bool:
        """
        Verifica si dos personas pueden ser asignadas juntas.
        
        Args:
            persona1: Primera persona
            persona2: Segunda persona
            
        Returns:
            True si la pareja es válida, False en caso contrario
        """
        if persona1 == persona2:
            return False
        
        pareja = frozenset([persona1.nombre, persona2.nombre])
        return pareja not in self.restricciones
    
    def validar_ciclo(self, personas_ordenadas: List[Persona]) -> bool:
        """
        Valida que un ciclo completo sea válido.
        
        Args:
            personas_ordenadas: Lista de personas en orden de asignación cíclica
            
        Returns:
            True si todas las asignaciones son válidas
        """
        if not personas_ordenadas:
            raise ValidationError("Lista de personas vacía")
        
        for i, persona in enumerate(personas_ordenadas):
            siguiente = personas_ordenadas[(i + 1) % len(personas_ordenadas)]
            if not self.es_pareja_valida(persona, siguiente):
                return False
        
        return True
    
    def agregar_restriccion(self, persona1: str, persona2: str) -> None:
        """Añade una nueva restricción."""
        self.restricciones.add(frozenset([persona1, persona2]))
    
    def remover_restriccion(self, persona1: str, persona2: str) -> None:
        """Remueve una restricción existente."""
        self.restricciones.discard(frozenset([persona1, persona2]))
    
    def obtener_restricciones(self) -> List[Tuple[str, str]]:
        """Retorna todas las restricciones como tuplas."""
        return [tuple(sorted(par)) for par in self.restricciones]
