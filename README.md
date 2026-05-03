# Analizador Léxico-Sintáctico

Una aplicación web interactiva para el análisis léxico y sintáctico de código fuente, desarrollada como proyecto de **Compiladores e Intérpretes**. Implementa la metodología y diccionario de tokens específicos definidos en clase.

## Características

- **Análisis Léxico Conforme a Clase**: Tokenización en tiempo real siguiendo el diccionario de palabras reservadas, operadores y caracteres especiales definido por el profesor.
- **Interfaz Web Moderna**: Editor de código con numeración de líneas, sincronización en tiempo real y navegación intuitiva.
- **API REST Backend**: Servicio Flask que procesa solicitudes de análisis y retorna tokens con formato específico de clase.
- **Visualización de Tokens**: Presentación estructurada de tokens con tipos según nomenclatura de clase (`Palabra Reservada`, `Variable`, `Operador`, etc.).
- **Árbol Sintáctico**: Visualización dinámica del árbol de análisis sintáctico basada en el AST generado por el backend.

## Stack Tecnológico

- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Backend**: Python 3.14, Flask 3.1.3
- **Dependencias**: flask-cors 6.0.2 para manejo de CORS
- **Entorno**: Virtualenv para aislamiento de dependencias

## Instalación

### Prerrequisitos

- Python 3.14 o superior
- Navegador web moderno

### Pasos de Instalación

1. **Clonar el repositorio**:

   ```bash
   git clone https://github.com/tu-usuario/analizador-ls.git
   cd analizador-ls
   ```

2. **Crear entorno virtual**:

   ```bash
   python -m venv env
   source env/bin/activate  # En Windows: env\Scripts\activate
   ```

3. **Instalar dependencias**:

   ```bash
   pip install flask flask-cors
   ```

4. **Ejecutar la aplicación**:

   ```bash
   # Desde el directorio backend
   cd backend
   python app.py
   ```

5. **Acceder al frontend**:
   Abrir `frontend/index.html` en el navegador web.

## Uso

1. **Ingresar código**: Escribir o pegar código fuente en el panel "Flujo de entrada"
2. **Analizar**: Hacer clic en el botón "Analizar" (▶) para procesar el código
3. **Revisar Tokens**: La salida muestra cada token en formato `<'lexema', TIPO>` según nomenclatura de clase
4. **Explorar Árbol**: Visualizar la estructura sintáctica en el panel "Árbol sintáctico" con renderizado dinámico desde el AST.

### Tokens Soportados

**Palabras Reservadas**: `define`, `int`, `void`, `printf`, `main`, `while`, `if`, `else`, `for`, `return`, `float`, `double`  
**Operadores**: `<=`, `>=`, `==`, `!=`, `&&`, `||`, `+`, `-`, `*`, `/`, `=`, `<`, `>`  
**Caracteres Especiales**: `"`, `#`, `(`, `)`, `{`, `}`, `;`, `,`, `%`

## Notas Importantes

- ⚠️ **Diccionario de Tokens**: El conjunto de palabras reservadas y operadores está restringido según los requisitos de la asignatura. No añadir elementos sin consultar al profesor.
- 🔄 **Trabajo en Progreso**: El análisis sintáctico y generación del árbol están en desarrollo.
- 📚 **Referencia de Clase**: Este proyecto implementa específicamente la metodología dictada en clase de Compiladores e Intérpretes.

## Estado del Proyecto

| Componente        | Estado       | Completitud |
| ----------------- | ------------ | ----------- |
| Análisis Léxico   | ✅ Funcional | 100%        |
| Tokenización      | ✅ Funcional | 100%        |
| Parser Sintáctico | ✅ Funcional | 80%         |
| Árbol Sintáctico  | ✅ Funcional | 80%         |
| API REST          | ✅ Funcional | 100%        |
| Frontend UI       | ✅ Funcional | 90%         |

## Contribución

Este es un proyecto educativo de la asignatura **Compiladores e Intérpretes**. Las contribuciones deben alinearse con los objetivos de la asignatura y ser aprobadas por el profesor.

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## Proyecto Académico

Este proyecto fue desarrollado como parte de la asignatura **Compiladores e Intérpretes** de la carrera de Ingeniería Informática. Implementa los conceptos teóricos de análisis léxico, tokens y análisis sintáctico según la metodología de clase.</content>
<parameter name="filePath">/home/dunn/Workspace/Proyectos/AnalizadorLS/README.md
