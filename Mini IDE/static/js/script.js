// Variables globales
let editor;

// Reloj en header
function actualizarReloj() {
    const reloj = document.getElementById("clock");
    const ahora = new Date();
    let h = ahora.getHours().toString().padStart(2,'0');
    let m = ahora.getMinutes().toString().padStart(2,'0');
    let s = ahora.getSeconds().toString().padStart(2,'0');
    reloj.textContent = `Hora: ${h}:${m}:${s}`;
}

// Función para alternar modo oscuro
function toggleDarkMode() {
    document.body.classList.toggle('dark');
}

// Función para validar el código en tiempo real
function validarCodigo(editor) {
    const code = editor.getValue();
    const lines = code.split('\n');
    
    // Limpiar marcadores anteriores
    editor.clearGutter('error-gutter');
    editor.getAllMarks().forEach(mark => mark.clear());

    lines.forEach((line, index) => {
        // Validar punto y coma al final de cada línea no vacía
        if (line.trim() && !line.trim().endsWith(';')) {
            const marker = document.createElement('div');
            marker.className = 'error-marker';
            marker.innerHTML = '❌';
            marker.title = 'Falta punto y coma al final de la línea';
            editor.setGutterMarker(index, 'error-gutter', marker);
            
            // Marcar la línea con error
            editor.markText(
                {line: index, ch: 0},
                {line: index, ch: line.length},
                {className: 'error-line'}
            );
        }

        // Validar caracteres no permitidos
        const invalidChars = line.match(/[^a-dxX0-9+\-*/=() ;]/g);
        if (invalidChars) {
            const marker = document.createElement('div');
            marker.className = 'error-marker';
            marker.innerHTML = '❌';
            marker.title = `Caracteres no permitidos: ${invalidChars.join(', ')}`;
            editor.setGutterMarker(index, 'error-gutter', marker);
            
            // Marcar los caracteres inválidos
            let pos = 0;
            while (pos < line.length) {
                const char = line[pos];
                if (!/[a-dxX0-9+\-*/=() ;]/.test(char)) {
                    editor.markText(
                        {line: index, ch: pos},
                        {line: index, ch: pos + 1},
                        {className: 'error-char'}
                    );
                }
                pos++;
            }
        }
    });
}

// Inicialización cuando el documento está listo
document.addEventListener('DOMContentLoaded', function() {
    // Iniciar reloj
    setInterval(actualizarReloj, 1000);
    actualizarReloj();

    // Inicializar CodeMirror
    editor = CodeMirror.fromTextArea(document.getElementById('code'), {
        lineNumbers: true,
        mode: 'javascript',
        theme: 'default',
        styleActiveLine: true,
        matchBrackets: true,
        autofocus: true,
        gutters: ['CodeMirror-linenumbers', 'error-gutter'],
        extraKeys: {
            'Enter': function(cm) {
                cm.replaceSelection('\n');
                const pos = cm.getCursor();
                validarCodigo(cm);
            },
            'Semicolon': function(cm) {
                cm.replaceSelection(';');
                validarCodigo(cm);
            }
        }
    });

    // Validar código mientras se escribe
    editor.on('change', function() {
        validarCodigo(editor);
    });

    // Configurar botón de modo oscuro
    const btnDarkMode = document.getElementById('btnDarkMode');
    btnDarkMode.addEventListener('click', toggleDarkMode);

    // Configurar los botones de análisis
    document.getElementById('btnLexico').addEventListener('click', () => analizarLexico(editor));
    document.getElementById('btnSintactico').addEventListener('click', () => analizarSintactico(editor));
    document.getElementById('btnTuring').addEventListener('click', () => simularTuring(editor));
});

// Función para realizar el análisis léxico
async function analizarLexico(editor) {
    const code = editor.getValue();
    try {
        const response = await fetch('/lexico', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ code: code })
        });
        const data = await response.json();
        mostrarResultados(data.result, data.errors, editor);
    } catch (error) {
        console.error('Error:', error);
        mostrarResultados('Error al procesar la solicitud', [], editor);
    }
}

// Función para realizar el análisis sintáctico
async function analizarSintactico(editor) {
    const code = editor.getValue();
    try {
        const response = await fetch('/sintactico', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ code: code })
        });
        const data = await response.json();
        mostrarResultados(data.result, data.errors, editor);
    } catch (error) {
        console.error('Error:', error);
        mostrarResultados('Error al procesar la solicitud', [], editor);
    }
}

// Función para simular la máquina de Turing
async function simularTuring(editor) {
    const code = editor.getValue();
    try {
        const response = await fetch('/turing', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ code: code })
        });
        const data = await response.json();
        mostrarResultados(data.result, data.errors, editor);
    } catch (error) {
        console.error('Error:', error);
        mostrarResultados('Error al procesar la solicitud', [], editor);
    }
}

// Función para mostrar los resultados
function mostrarResultados(resultado, errores, editor) {
    const resultadosDiv = document.getElementById('resultado');
    resultadosDiv.innerHTML = '';

    // Crear elemento para mostrar el resultado
    const resultadoElement = document.createElement('div');
    resultadoElement.className = resultado.includes('❌') ? 'error' : 'success';
    resultadoElement.textContent = resultado;
    resultadosDiv.appendChild(resultadoElement);

    // Marcar errores en el editor
    editor.clearGutter('error-gutter');
    editor.getAllMarks().forEach(mark => mark.clear());

    if (errores && errores.length > 0) {
        errores.forEach(error => {
            const lineaIndex = (error.linea || 1) - 1;
            const marker = document.createElement('div');
            marker.className = 'error-marker';
            marker.innerHTML = '❌';
            
            if (error.valor === "falta ;") {
                // Error de punto y coma faltante
                marker.title = `Error en línea ${error.linea}: Falta punto y coma al final`;
                editor.setGutterMarker(lineaIndex, 'error-gutter', marker);
                
                const line = editor.getLine(lineaIndex);
                if (line) {
                    editor.markText(
                        {line: lineaIndex, ch: line.length},
                        {line: lineaIndex, ch: line.length},
                        {className: 'error-semicolon'}
                    );
                }
            } else {
                // Otros tipos de errores
                marker.title = `Error en línea ${error.linea}: ${error.valor}`;
                editor.setGutterMarker(lineaIndex, 'error-gutter', marker);

                // Si tenemos una posición específica en la línea
                if (error.pos !== undefined) {
                    const lineStart = editor.indexFromPos({line: lineaIndex, ch: 0});
                    const posInLine = error.pos - lineStart;
                    
                    editor.markText(
                        {line: lineaIndex, ch: posInLine},
                        {line: lineaIndex, ch: posInLine + 1},
                        {className: 'error-char'}
                    );
                } else {
                    // Si no hay posición específica, marcar toda la línea
                    const line = editor.getLine(lineaIndex);
                    if (line) {
                        editor.markText(
                            {line: lineaIndex, ch: 0},
                            {line: lineaIndex, ch: line.length},
                            {className: 'error-line'}
                        );
                    }
                }
            }
        });
    }
} 