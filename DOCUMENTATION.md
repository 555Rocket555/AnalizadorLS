# Documentación Técnica - Analizador Léxico-Sintáctico

## Resumen Ejecutivo

El proyecto "Analizador Léxico-Sintáctico" es una aplicación web educativa que implementa un analizador de código fuente básico, enfocado en demostrar los procesos de tokenización léxica y construcción de árboles sintácticos. El objetivo principal es proporcionar una herramienta interactiva para el aprendizaje de conceptos fundamentales en el diseño de compiladores, permitiendo a los usuarios ingresar bloques de código y visualizar su descomposición en tokens y estructura sintáctica.

## Stack Tecnológico

### Frontend

- **HTML5**: Estructura semántica de la interfaz de usuario
- **CSS3**: Estilos responsivos con fuentes personalizadas (Inter y JetBrains Mono)
- **JavaScript (Vanilla)**: Lógica del lado cliente para manejo de eventos, comunicación AJAX y manipulación del DOM

### Backend

- **Python 3.14**: Lenguaje de programación principal
- **Flask 3.1.3**: Framework web ligero para desarrollo de APIs REST
- **flask-cors 6.0.2**: Extensión para manejo de Cross-Origin Resource Sharing (CORS)

### APIs Externas

- **Google Fonts API**: Para carga de fuentes tipográficas (Inter y JetBrains Mono)

## Arquitectura y Patrones

La aplicación sigue una arquitectura cliente-servidor con separación clara de responsabilidades:

### Arquitectura General

- **Frontend (Cliente)**: Maneja la interfaz de usuario, captura de entrada del usuario y presentación de resultados
- **Backend (Servidor)**: Procesa la lógica de negocio, realiza el análisis léxico y expone APIs REST

### Análisis Léxico

El analizador léxico utiliza expresiones regulares para tokenizar el código fuente de entrada, siguiendo la metodología específica dictada en clase. El proceso sigue estos pasos:

1. **Definición de Patrones Específicos de Clase**: Se definen conjuntos restringidos de palabras reservadas, operadores y caracteres especiales según los requisitos del profesor
   - **Palabras Reservadas**: `define`, `int`, `void`, `printf`, `main`, `while`, `if`, `else`, `for`, `return`, `float`, `double`
   - **Operadores**: `<=`, `>=`, `==`, `!=`, `&&`, `||`, `+`, `-`, `*`, `/`, `=`, `<`, `>`
   - **Caracteres Especiales**: `"`, `#`, `(`, `)`, `{`, `}`, `;`, `,`, `%`

2. **Tokenización**: Utiliza un patrón regex complejo que prioriza operadores de múltiples caracteres sobre individuales
3. **Clasificación**: Cada lexema se clasifica en categorías específicas del curso (palabras reservadas, identificadores, literales numéricos, operadores, caracteres especiales, espacios en blanco)
4. **Generación de Tokens**: Se crea una lista de objetos JSON con lexema y tipo para cada token identificado

### Generación de Tokens

Los tokens se generan mediante la función `analizar_codigo()` que:

- Aplica el patrón regex global al texto completo
- Itera sobre cada coincidencia
- Clasifica cada lexema según las reglas específicas de la asignatura
- Genera tipos de token siguiendo la nomenclatura dictada: "Salto de línea", "Tabulador", "Espacio vacío", "Integer", "Float", "Palabra Reservada", "Variable", "Cadena", "Operador", "Caracter Especial", "Desconocido"
- Retorna una lista estructurada de tokens en formato JSON

### Dibujo del Árbol Sintáctico

La visualización del árbol sintáctico ahora se genera dinámicamente desde el AST construido por el parser del backend. El proceso actual contempla:

- Generación de AST en el backend a partir de los tokens
- Renderizado jerárquico en el frontend mediante tarjetas anidadas
- Presentación de tipo de nodo y etiqueta para cada elemento del árbol
- Indicadores de error sintáctico cuando el parser no puede resolver la entrada

## Instalación y Configuración

### Configuración del Entorno Virtual

1. Crear entorno virtual:

   ```bash
   python -m venv env
   ```

2. Activar entorno virtual:
   ```bash
   source env/bin/activate  # Linux/Mac
   # o
   env\Scripts\activate     # Windows
   ```

### Instalación de Dependencias

Crear archivo `requirements.txt` con el siguiente contenido:

```
flask==3.1.3
flask-cors==6.0.2
```

Instalar dependencias:

```bash
pip install -r requirements.txt
```

### Configuración de Variables de Entorno

No se requieren variables de entorno específicas. Flask utiliza configuración por defecto.

### Configuración CORS

La extensión `flask-cors` está configurada globalmente en `app.py`:

```python
from flask_cors import CORS
CORS(app)  # Permite conexiones desde el frontend local
```

### Ejecución de la Aplicación

1. Navegar al directorio backend:

   ```bash
   cd backend
   ```

2. Ejecutar el servidor Flask:

   ```bash
   python app.py
   ```

3. Abrir `frontend/index.html` en un navegador web

## Estructura del Proyecto

```
AnalizadorLS/
├── main.py                 # Script CLI para análisis léxico interactivo
├── requirements.txt        # Dependencias del proyecto (pip)
├── README.md               # Documentación general del proyecto
├── DOCUMENTATION.md        # Este archivo - documentación técnica
├── backend/
│   ├── app.py              # Servidor Flask con endpoints API REST
│   ├── lexer.py            # Módulo centralizado de análisis léxico (clases Lexer y LexerConfig)
│   ├── env/                # Entorno virtual Python
│   │   ├── bin/            # Ejecutables (python, pip, activate, etc.)
│   │   ├── lib/            # Paquetes instalados
│   │   └── pyvenv.cfg      # Configuración del entorno virtual
├── frontend/
│   ├── index.html          # Interfaz principal de usuario
│   ├── css/
│   │   └── style.css       # Estilos CSS y temas de colores
│   └── js/
│       └── app.js          # Lógica JavaScript, manejo de eventos y AJAX
└── .gitignore             # Archivos a ignorar en control de versiones
```

**Cambios Recientes**:

- ✅ `backend/lexer.py`: Archivo nuevo con módulo de análisis léxico centralizado
- ✅ `requirements.txt`: Nuevo archivo para gestión de dependencias
- ✅ `main.py`: Refactorizado para usar módulo lexer.py
- ✅ `backend/app.py`: Refactorizado para eliminar duplicación

## Flujo de Datos (Data Flow)

El flujo de datos sigue un patrón request-response síncrono:

1. **Entrada del Usuario**: El usuario ingresa código fuente en el textarea del panel de entrada
2. **Activación del Análisis**: Click en el botón "Analizar" dispara el evento `analizarTodo()`
3. **Solicitud HTTP**: JavaScript realiza una petición POST a `http://127.0.0.1:5000/api/analizar`
4. **Payload**: Envío de datos JSON con el campo `codigo` conteniendo el texto fuente
5. **Procesamiento Backend**: Flask recibe la solicitud y ejecuta `analizar_codigo(codigo)`
6. **Análisis Léxico**: Aplicación de expresiones regulares para tokenización
7. **Respuesta JSON**: Retorno de array de objetos token con campos `lexema` y `tipo`
8. **Actualización Frontend**: Reemplazo del contenido del panel de tokens
9. **Renderizado**: Iteración sobre tokens y creación de elementos DOM para cada uno
10. **Actualización de Progreso**: Cálculo y visualización del porcentaje de procesamiento completado

## Estado Actual

La aplicación se encuentra en estado funcional para análisis léxico y sintáctico. El frontend presenta una interfaz renovada con la paleta de colores del proyecto, el backend procesa correctamente la tokenización de código fuente, y ahora también genera un AST que se renderiza como árbol sintáctico dinámico. La comunicación API funciona correctamente con manejo de CORS.

## Problemas Identificados, Tareas Pendientes y Priorización

### Prioridad CRÍTICA (Bloqueadores funcionales)

- **Parser Sintáctico Implementado**: El parser ahora genera un AST básico para el subconjunto de sintaxis definido en clase.
- **Árbol Sintáctico Dinámico**: El árbol se dibuja directamente desde el AST devuelto por el backend, actualizando la implementación anterior basada en demo estática.

### Prioridad ALTA (Funcionalidades principales)

- **Parser Sintáctico Completo**: Implementar parser recursivo descendente o LL(1) con gramática definida acorde a los requisitos del profesor
- **Validación de Entrada**: Implementar validación de código en el frontend antes de enviar al backend
- **Manejo de Errores Robusto**: Captura y presentación clara de errores sintácticos y léxicos durante el análisis
- **Linaje y Posición de Errores**: Mostrar número de línea y columna para cada token y error identificado

### Prioridad MEDIA (Mejoras de usabilidad)

- **Indicadores de Carga**: Mejorar la experiencia de usuario con spinners y mensajes de estado durante análisis
- **Funcionalidad de Guardado**: Permitir exportar análisis en formato JSON o XML
- **Historial de Análisis**: Guardar últimos análisis realizados en sesión
- **Copiar Información**: Mejora en funcionalidad de copy-paste de tokens

### Prioridad BAJA (Mejoras futuras)

- **Soporte Multiidioma**: Internacionalización de la interfaz
- **Tests Unitarios**: Cobertura de tests para lexer y parser
- **Documentación Mejorada**: Agregar comentarios en código y documentación API
- **Actualización a Frameworks Modernos**: Migración a React/Vue solo si se mantiene escalabilidad

## Deuda Técnica

### Código - ✅ RESUELTO

- **Ausencia de Comments y Docstrings**: ✅ **RESUELTO** - Todas las funciones, clases y módulos tienen docstrings exhaustivos en formato Google-style. Ver `backend/lexer.py` como referencia.
- **Sin Tipado Estricto**: ✅ **RESUELTO** - Implementados type hints completos en todas las funciones usando Python 3.10+ (Union `|`). Ver anotaciones en `backend/lexer.py` y `backend/app.py`.
- **Regex Complejo**: ✅ **RESUELTO** - Patrón regex refactorizado en componentes lógicos con comentarios explicativos en clase `LexerConfig.PATRON_REGEX` dentro de `backend/lexer.py`.
- **Duplicación de Lógica**: ✅ **RESUELTO** - Lógica de análisis léxico centralizada en módulo `backend/lexer.py` (clases `Lexer` y `LexerConfig`) reutilizado por `main.py` y `backend/app.py`.

**Cambios Implementados**:

- Creación de módulo `backend/lexer.py` con clases bien documentadas
- Refactorización de `backend/app.py` eliminando duplicación
- Refactorización de `main.py` para usar módulo centralizado
- Adición de archivo `requirements.txt` para dependencias

### Arquitectura

- **Sin Capa de Validación**: Falta validator layer entre frontend y backend
- **Estado Global en Frontend**: Variables globales `tokensGlobal` y `currentIndex` en JavaScript
- **Acoplamiento Frontend-Backend**: Frontend hardcodeado a `http://127.0.0.1:5000`
- **Sin Manejo de Excepciones**: ⚠️ **PARCIALMENTE RESUELTO** - Backend ahora retorna errores estructurados en `api_analizar()`, pero falta validación más robusta

### Infraestructura

- **Sin Configuración de Entorno**: No hay archivo `.env` ni manejo de variables de entorno
- **Sin Logging**: Ausencia de sistema de logging para debugging
- **Sin Tests**: Cobertura de tests nula para funcionalidades críticas
- **Sin CI/CD**: No hay pipelines de integración continua o deployment automático

### Documentación

- **Comentarios en Código**: ✅ **RESUELTO** - Docstrings completos en `backend/lexer.py`
- **Falta Ejemplos de Uso**: Ejemplos agregados en docstrings de módulos
- **API No Documentada**: Docstrings en endpoints, pero sin especificación formal OpenAPI/Swagger

## Upgrades y Customs Recomendados (Post-MVP)

- **Migración a Framework Moderno**: Considerar React/Vue para el frontend solo después de estabilizar funcionalidad central
- **Base de Datos**: Integrar SQLite para almacenamiento de análisis históricos (no crítico para MVP)
- **API REST Expandida**: Nuevos endpoints para análisis incremental y caché
- **Dockerización**: Facilitar deployment en diferentes entornos
- **CI/CD**: GitHub Actions para testing automático
- **Documentación API**: Swagger/OpenAPI para endpoints
- **Accesibilidad**: Cumplimiento de WCAG 2.1 AA</content>

<parameter name="filePath">/home/dunn/Workspace/Proyectos/AnalizadorLS/DOCUMENTATION.md
