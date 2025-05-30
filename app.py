from flask import Flask, render_template, request, jsonify
import re

app = Flask(__name__)

# Definición de tokens para el análisis léxico
token_def = [
    ('NUMERO', r'\d+'),
    ('OPERADOR', r'[+\-*/=]'),
    ('IDENTIFICADOR', r'\b[a-dxX]\b'),
    ('PARENTESIS', r'[()]'),
    ('PUNTOYCOMA', r';'),
    ('ESPACIO', r'[ \t\n]+'),
    ('ERROR', r'.')
]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/lexico", methods=["POST"])
def lexico():
    code = request.json.get("code", "")
    tokens = []
    errores = []
    tabla = []
    
    lineas = code.split('\n')
    pos_actual = 0
    
    for num_linea, linea in enumerate(lineas, 1):
        linea = linea.strip()
        if not linea:
            continue
            
        # Verificar si esta línea es una cadena de a's y b's
        if all(c in 'ab;' for c in linea.replace(' ', '')):
            # Procesar como cadena de a's y b's
            if not linea.endswith(';'):
                errores.append({
                    "pos": pos_actual + len(linea),
                    "valor": "falta ;",
                    "linea": num_linea
                })
                tabla.append(f"Línea {num_linea}:")
                tabla.append("  Error: falta punto y coma al final")
            else:
                # Verificar que solo contenga 'a' y 'b' antes del punto y coma
                cadena = linea[:-1].strip()  # Quitar el punto y coma
                if all(c in 'ab' for c in cadena):
                    tabla.append(f"Línea {num_linea}:")
                    tabla.append(f"  CADENA: {cadena}")
                else:
                    tabla.append(f"Línea {num_linea}:")
                    tabla.append("  Error: caracteres no válidos en la cadena")
        else:
            # Procesar como código normal
            pos_linea = 0
            tokens_linea = []
            
            while pos_linea < len(linea):
                matched = False
                for tipo, patron in token_def:
                    regex = re.compile(patron)
                    match = regex.match(linea, pos_linea)
                    if match:
                        valor = match.group(0)
                        if tipo == 'ESPACIO':
                            pass  # ignorar espacios
                        elif tipo == 'ERROR':
                            # Verificar si es un símbolo no reconocido
                            if valor in '@&$':
                                tokens_linea.append(f"Error: símbolo no reconocido '{valor}'")
                            else:
                                tokens_linea.append(f"{tipo}: {valor}")
                        elif tipo == 'PUNTOYCOMA':
                            pass  # No mostrar el punto y coma
                        else:
                            tokens_linea.append(f"{tipo}: {valor}")
                        pos_linea += len(valor)
                        matched = True
                        break
                if not matched:
                    # Verificar si es un símbolo no reconocido
                    if linea[pos_linea] in '@&$':
                        tokens_linea.append(f"Error: símbolo no reconocido '{linea[pos_linea]}'")
                    else:
                        tokens_linea.append(f"Error: carácter no reconocido '{linea[pos_linea]}'")
                    pos_linea += 1
            
            # Si se encontraron tokens en la línea, agregarlos a la tabla
            if tokens_linea:
                tabla.append(f"Línea {num_linea}:")
                # Agregar cada token en una nueva línea con indentación
                for token in tokens_linea:
                    tabla.append(f"  {token}")
        
        pos_actual += len(linea) + 1

    if not tabla:
        tabla.append("No hay tokens para analizar")

    return jsonify(result="\n".join(tabla), errors=errores)

@app.route("/sintactico", methods=["POST"])
def sintactico():
    code = request.json.get("code", "").strip()
    mensajes = []
    errores = []

    try:
        # Dividir el código en líneas
        lineas = code.split('\n')
        
        for num_linea, linea in enumerate(lineas, 1):
            linea = linea.strip()
            if not linea:
                continue

            # Verificar si es una cadena de a's y b's
            if all(c in 'ab;' for c in linea.replace(' ', '')):
                mensajes.append(f"❌ Error en línea {num_linea}: Las cadenas 'ab' no son válidas")
                errores.append({
                    "pos": 0,
                    "valor": "X",
                    "linea": num_linea,
                    "length": len(linea)  # Agregar longitud total para subrayar toda la línea
                })
                continue
                
            # Validar que termine en punto y coma
            if not linea.endswith(';'):
                mensajes.append(f"❌ Error en línea {num_linea}: Falta punto y coma al final")
                errores.append({
                    "pos": len(linea),
                    "valor": ";",
                    "linea": num_linea,
                    "tipo": "semicolon"  # Identificar específicamente error de punto y coma
                })
                continue

            # Quitar el punto y coma para el análisis
            linea = linea[:-1].strip()

            # Dividir en partes por el operador de asignación
            if '=' not in linea:
                mensajes.append(f"❌ Error en línea {num_linea}: Falta el operador de asignación '='")
                # Encontrar la posición después del identificador
                match = re.match(r'^[a-dxX]', linea)
                if match:
                    pos = 1  # Después del identificador
                else:
                    pos = 0
                errores.append({
                    "pos": pos,
                    "valor": "=",
                    "linea": num_linea,
                    "tipo": "equals"  # Identificar específicamente error de igual
                })
                continue

            partes = linea.split('=', 1)
            identificador = partes[0].strip()
            expresion = partes[1].strip()

            # Validar identificador
            if not re.match(r'^[a-dxX]$', identificador):
                mensajes.append(f"❌ Error en línea {num_linea}: Identificador inválido '{identificador}'. Solo se permiten las letras a-d, x")
                errores.append({
                    "pos": linea.find(identificador),
                    "valor": "X",
                    "linea": num_linea
                })
                continue

            # Validar que la expresión no esté vacía
            if not expresion:
                mensajes.append(f"❌ Error en línea {num_linea}: Falta la expresión después del '='")
                errores.append({
                    "pos": linea.find('=') + 1,
                    "valor": "número",
                    "linea": num_linea
                })
                continue

            # Buscar el operador en la expresión
            operador_match = re.search(r'[+\-*/]', expresion)
            if not operador_match:
                mensajes.append(f"❌ Error en línea {num_linea}: Falta un operador (+, -, *, /) en la expresión")
                errores.append({
                    "pos": len(linea),
                    "valor": "operador",
                    "linea": num_linea
                })
                continue

            operador_pos = operador_match.start()
            operador = operador_match.group()

            # Dividir la expresión en dos números
            num1 = expresion[:operador_pos].strip()
            num2 = expresion[operador_pos + 1:].strip()

            # Validar el primer número
            if not num1:
                pos_error = linea.find('=') + 1
                mensajes.append(f"❌ Error en línea {num_linea}: Ingrese un número antes del operador")
                errores.append({
                    "pos": pos_error,
                    "valor": "número",
                    "linea": num_linea
                })
                continue
            elif not num1.isdigit():
                pos_error = linea.find(num1)
                mensajes.append(f"❌ Error en línea {num_linea}: '{num1}' no es un número válido")
                errores.append({
                    "pos": pos_error,
                    "valor": "X",
                    "linea": num_linea
                })
                continue

            # Validar el segundo número
            if not num2:
                pos_error = linea.find(operador) + 1
                mensajes.append(f"❌ Error en línea {num_linea}: Ingrese un número después del operador")
                errores.append({
                    "pos": pos_error,
                    "valor": "número",
                    "linea": num_linea
                })
                continue
            elif not num2.isdigit():
                pos_error = linea.find(num2)
                mensajes.append(f"❌ Error en línea {num_linea}: '{num2}' no es un número válido")
                errores.append({
                    "pos": pos_error,
                    "valor": "X",
                    "linea": num_linea
                })
                continue

            # Si llegamos aquí, la sintaxis es correcta
            mensajes.append(f"✅ Línea {num_linea}: Expresión válida")
        
        if not mensajes:
            return jsonify(result="❌ Error: No hay expresiones para analizar", errors=[])
            
    except Exception as e:
        return jsonify(result=f"❌ Error inesperado: {str(e)}", errors=[])

    return jsonify(result="\n".join(mensajes), errors=errores)

@app.route("/turing", methods=["POST"])
def turing_route():
    code = request.json.get("code", "").strip()
    mensaje, errores = analizar_binario(code)
    return jsonify(result=mensaje, errors=errores)

def analizar_binario(code):
    errores = []
    mensajes = []
    lines = code.splitlines()
    
    if not code.strip():
        return "❌ Error: El código está vacío", []
    
    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        if not line:
            continue
            
        # Verificar si termina en punto y coma
        if not line.endswith(';'):
            errores.append({
                "pos": len(line),
                "linea": line_num,
                "valor": "falta ;",
                "tipo": "semicolon"
            })
            mensajes.append(f"❌ Error en línea {line_num}: Falta punto y coma al final")
            mensajes.append(line)
            continue
            
        # Quitar el punto y coma para analizar la cadena
        cadena = line[:-1].strip()
        
        # Verificar si es una línea de código (contiene '=')
        if '=' in cadena:
            mensajes.append(f"❌ Error en línea {line_num}: Las expresiones aritméticas no son válidas")
            mensajes.append(cadena)
            errores.append({
                "pos": 0,
                "linea": line_num,
                "valor": "X",
                "length": len(cadena)
            })
            continue
        
        # Verificar que la cadena sea válida (solo 'ab' repetidos)
        if len(cadena) % 2 != 0:  # La longitud debe ser par
            mensajes.append(f"❌ Error en línea {line_num}: cadena inválida")
            mensajes.append(cadena)
            errores.append({
                "pos": len(cadena) - 1,
                "linea": line_num,
                "valor": "X",
                "length": 1
            })
            continue
            
        es_valida = True
        pos_error = 0
        for i in range(0, len(cadena), 2):
            if cadena[i:i+2] != 'ab':
                es_valida = False
                pos_error = i
                break
                
        if not es_valida:
            mensajes.append(f"❌ Error en línea {line_num}: Estructura inválida")
            mensajes.append(cadena)
            errores.append({
                "pos": pos_error,
                "linea": line_num,
                "valor": "X",
                "length": 2
            })
        else:
            mensajes.append(f"✅ Línea {line_num}: Cadena válida: {cadena}")
    
    if not mensajes:
        return "❌ Error: No hay cadenas para analizar", []
    
    return "\n".join(mensajes), errores

if __name__ == "__main__":
    app.run(debug=True)











