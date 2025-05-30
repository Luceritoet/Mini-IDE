"""
Módulo para el análisis léxico del Mini IDE.
"""

import re
from typing import List, Tuple, Dict

class Token:
    def __init__(self, tipo: str, valor: str, posicion: int):
        self.tipo = tipo
        self.valor = valor
        self.posicion = posicion

    def __str__(self):
        return f"{self.tipo}: {self.valor}"

class AnalizadorLexico:
    def __init__(self):
        self.token_def = [
            ('NUMERO', r'\d+'),
            ('OPERADOR', r'[+\-*/=]'),
            ('IDENTIFICADOR', r'\b[a-dxX]\b'),
            ('PARENTESIS', r'[()]'),
            ('ESPACIO', r'[ \t\n]+'),
            ('ERROR', r'.')
        ]
        # Precompilar las expresiones regulares para mejor rendimiento
        self.tokens_regex = [(tipo, re.compile(patron)) for tipo, patron in self.token_def]

    def analizar(self, codigo: str) -> Tuple[List[str], List[Dict]]:
        """
        Analiza el código fuente y retorna los tokens encontrados.
        
        Args:
            codigo: String con el código a analizar
            
        Returns:
            Tuple con lista de tokens y lista de errores
        """
        tokens = []
        errores = []
        pos = 0

        while pos < len(codigo):
            matched = False
            
            for tipo, regex in self.tokens_regex:
                match = regex.match(codigo, pos)
                if match:
                    valor = match.group(0)
                    if tipo == 'ESPACIO':
                        pass  # Ignorar espacios
                    elif tipo == 'ERROR':
                        errores.append({"pos": pos, "valor": valor})
                        tokens.append(f"❌ Error: carácter inesperado '{valor}' en posición {pos}")
                    else:
                        tokens.append(Token(tipo, valor, pos))
                    pos += len(valor)
                    matched = True
                    break
                    
            if not matched:
                errores.append({"pos": pos, "valor": codigo[pos]})
                tokens.append(f"❌ Error desconocido en posición {pos}")
                pos += 1

        return [str(token) if isinstance(token, Token) else token for token in tokens], errores





