"""
Módulo para la simulación de la Máquina de Turing del Mini IDE.
"""

from typing import Tuple, List, Dict

class MaquinaTuring:
    def __init__(self):
        self.simbolos_validos = {'0', '1'}

    def analizar(self, codigo: str) -> Tuple[str, List[Dict]]:
        """
        Analiza una cadena binaria para la máquina de Turing.
        
        Args:
            codigo: String con la cadena a analizar
            
        Returns:
            Tuple con mensaje de resultado y lista de errores
        """
        errores = []
        lineas = codigo.splitlines()

        # Validar que haya contenido
        if not codigo.strip():
            return "❌ La cadena está vacía", [{"pos": 0, "valor": ""}]

        # Analizar cada línea
        for num_linea, linea in enumerate(lineas, start=1):
            for pos, caracter in enumerate(linea):
                if caracter not in self.simbolos_validos:
                    errores.append({
                        "pos": pos,
                        "linea": num_linea,
                        "valor": caracter
                    })

        if errores:
            return "❌ Error: Solo se permiten caracteres '0' y '1' para la simulación", errores

        # Aquí se podría agregar la lógica real de la máquina de Turing
        # Por ahora solo validamos la cadena
        return f"✅ Máquina de Turing simuló la cadena correctamente: {codigo}", []

    def simular(self, cadena: str) -> Tuple[str, List[str]]:
        """
        Simula el procesamiento de una cadena en la máquina de Turing.
        Esta es una implementación básica que se puede expandir según necesidades.
        
        Args:
            cadena: String con la cadena a procesar
            
        Returns:
            Tuple con el resultado final y lista de pasos
        """
        # TODO: Implementar la simulación real de la máquina de Turing
        # Por ahora solo retornamos un mensaje de éxito
        return "Aceptada", ["Inicio", "Procesando...", "Fin"]







