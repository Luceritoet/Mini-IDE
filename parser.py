"""
Módulo para el análisis sintáctico del Mini IDE.
"""

import re
from typing import Tuple, List, Dict

class AnalizadorSintactico:
    def __init__(self):
        self.identificadores_validos = set('abcdxX')
        self.operadores_validos = set('+-*/=')

    def analizar(self, codigo: str) -> Tuple[str, List[Dict]]:
        """
        Analiza la sintaxis del código fuente.
        
        Args:
            codigo: String con el código a analizar
            
        Returns:
            Tuple con mensaje de resultado y lista de errores
        """
        codigo = codigo.replace("\n", "").replace(" ", "")
        errores = []

        try:
            # Validar estructura básica
            if not codigo:
                return "❌ El código está vacío", [{"pos": 0, "valor": ""}]

            # Validar operador de asignación
            if "=" not in codigo:
                return "❌ Falta el operador de asignación '='", [{"pos": 0, "valor": codigo}]

            # Separar lado izquierdo y derecho
            izquierda, derecha = codigo.split('=', 1)
            
            # Validar identificador
            if not izquierda or len(izquierda) != 1 or izquierda not in self.identificadores_validos:
                return "❌ Identificador inválido (debe ser a, b, c, d, x o X)", [{"pos": 0, "valor": izquierda}]

            # Validar expresión derecha
            if not derecha:
                return "❌ Falta la expresión después del '='", [{"pos": len(izquierda) + 1, "valor": ""}]

            # Validar expresión aritmética
            resultado = self._validar_expresion(derecha, len(izquierda) + 1)
            if resultado[0].startswith("❌"):
                return resultado

            return "✅ Estructura sintáctica válida", []

        except Exception as e:
            return f"❌ Error inesperado: {str(e)}", [{"pos": 0, "valor": codigo}]

    def _validar_expresion(self, expr: str, offset: int) -> Tuple[str, List[Dict]]:
        """
        Valida una expresión aritmética.
        
        Args:
            expr: Expresión a validar
            offset: Posición inicial para reportar errores
            
        Returns:
            Tuple con mensaje de resultado y lista de errores
        """
        tokens = []
        current_num = ""
        
        for i, c in enumerate(expr):
            if c.isdigit():
                current_num += c
            else:
                if current_num:
                    tokens.append(("NUM", current_num))
                    current_num = ""
                
                if c in self.operadores_validos:
                    tokens.append(("OP", c))
                else:
                    return f"❌ Carácter inválido '{c}' en la expresión", [{"pos": offset + i, "valor": c}]
        
        if current_num:
            tokens.append(("NUM", current_num))

        # Validar estructura de tokens
        for i in range(len(tokens)):
            if i % 2 == 0 and tokens[i][0] != "NUM":
                return "❌ Se esperaba un número", [{"pos": offset, "valor": expr}]
            elif i % 2 == 1 and tokens[i][0] != "OP":
                return "❌ Se esperaba un operador", [{"pos": offset, "valor": expr}]

        return "✅ Expresión válida", []







