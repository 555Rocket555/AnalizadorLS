"""
Módulo de Análisis Léxico

Este módulo implementa un analizador léxico para código fuente simple, siguiendo
la metodología de la asignatura Compiladores e Intérpretes.

Proporciona la clase Lexer para tokenizar código fuente según un conjunto
específico de palabras reservadas, operadores y caracteres especiales definidos
por el profesor.

Ejemplo de uso:
    lexer = Lexer()
    tokens = lexer.analizar("int main() { return 0; }")
    for token in tokens:
        print(f"<'{token['lexema']}', {token['tipo']}>")
"""

import re
from typing import Dict, List


class LexerConfig:
    """Configuración centralizada del analizador léxico."""

    # Palabras reservadas según metodología de clase
    PALABRAS_RESERVADAS: set = {
        "define",
        "int",
        "void",
        "printf",
        "main",
        "while",
        "if",
        "else",
        "for",
        "return",
        "float",
        "double",
    }

    # Operadores de dos caracteres y de un carácter
    OPERADORES: set = {
        "<=",
        ">=",
        "==",
        "!=",
        "&&",
        "||",
        "+",
        "-",
        "*",
        "/",
        "=",
        "<",
        ">",
    }

    # Caracteres especiales válidos
    CARACTERES_ESPECIALES: set = {'"', "#", "(", ")", "{", "}", ";", ",", "%"}

    # Patrón regex compilado para tokenización
    # Los operadores de 2 caracteres se colocan primero para tener precedencia
    PATRON_REGEX: str = (
        r"\n|\t| +|<=|>=|==|!=|&&|\|\|"  # Saltos, tabulaciones, espacios y operadores de 2 chars
        r"|\d+\.\d+|\.\d+|\d+\."  # Números flotantes (todas las variantes)
        r"|\d+"  # Números enteros
        r"|[a-zA-Z_][a-zA-Z_0-9]*"  # Identificadores y palabras reservadas
        r'|".*?"'  # Cadenas de texto
        r"|."  # Cualquier otro carácter
    )


class Lexer:
    """
    Analizador léxico para código fuente.

    Realiza la tokenización de código fuente en lexemas clasificados según
    tipos específicos de la asignatura.

    Attributes:
        config (LexerConfig): Configuración del lexer (palabras reservadas, operadores, etc.)
    """

    def __init__(self, config: LexerConfig | None = None) -> None:
        """
        Inicializa el analizador léxico.

        Args:
            config (LexerConfig | None): Configuración del lexer. Si es None, usa LexerConfig por defecto.
        """
        self.config = config or LexerConfig()
        self._patron_compilado = re.compile(self.config.PATRON_REGEX)

    def analizar(self, codigo: str) -> List[Dict[str, str]]:
        """
        Analiza código fuente y retorna lista de tokens.

        Realiza análisis léxico del código fuente proporcionado, identificando
        y clasificando cada lexema según su tipo (palabra reservada, operador,
        identificador, literal, etc.).

        Args:
            codigo (str): Código fuente a analizar

        Returns:
            List[Dict[str, str]]: Lista de diccionarios con claves 'lexema' y 'tipo'.
                Cada diccionario representa un token identificado.
                Ejemplo: {"lexema": "int", "tipo": "Palabra Reservada"}

        Tipos de token generados:
            - "Salto de línea": Caracteres de nueva línea
            - "Tabulador": Caracteres de tabulación
            - "Espacio vacío": Secuencias de espacios
            - "Integer": Números sin punto decimal
            - "Float": Números con punto decimal
            - "Palabra Reservada": Identificadores que coinciden con palabras reservadas
            - "Variable": Identificadores que no son palabras reservadas
            - "Cadena": Texto entre comillas dobles
            - "Operador": Símbolos de operación matemática o lógica
            - "Caracter Especial": Caracteres de puntuación y delimitadores
            - "Desconocido": Caracteres no reconocidos
        """
        tokens: List[Dict[str, str]] = []
        coincidencias = self._patron_compilado.findall(codigo)

        for lexema in coincidencias:
            token = self._clasificar_lexema(lexema)
            tokens.append(token)

        return tokens

    def _clasificar_lexema(self, lexema: str) -> Dict[str, str]:
        """
        Clasifica un lexema individual en su tipo correspondiente.

        Args:
            lexema (str): Lexema a clasificar

        Returns:
            Dict[str, str]: Diccionario con 'lexema' y 'tipo'
        """
        # Caracteres especiales de whitespace
        if lexema == "\n":
            return {"lexema": r"\n", "tipo": "Salto de línea"}
        elif lexema == "\t":
            return {"lexema": r"\t", "tipo": "Tabulador"}
        elif re.fullmatch(r" +", lexema):
            return {"lexema": lexema, "tipo": "Espacio vacío"}

        # Números (flotantes primero, luego enteros)
        elif re.fullmatch(r"\d+\.\d+|\.\d+|\d+\.", lexema):
            return {"lexema": lexema, "tipo": "Float"}
        elif re.fullmatch(r"\d+", lexema):
            return {"lexema": lexema, "tipo": "Integer"}

        # Identificadores y palabras reservadas
        elif re.fullmatch(r"[a-zA-Z_][a-zA-Z_0-9]*", lexema):
            tipo = (
                "Palabra Reservada"
                if lexema.lower() in self.config.PALABRAS_RESERVADAS
                else "Variable"
            )
            return {"lexema": lexema, "tipo": tipo}

        # Cadenas de texto
        elif re.fullmatch(r'".*?"', lexema):
            return {"lexema": lexema, "tipo": "Cadena"}

        # Operadores
        elif lexema in self.config.OPERADORES:
            return {"lexema": lexema, "tipo": "Operador"}

        # Caracteres especiales
        elif lexema in self.config.CARACTERES_ESPECIALES:
            return {"lexema": lexema, "tipo": "Caracter Especial"}

        # Token desconocido
        else:
            return {"lexema": lexema, "tipo": "Desconocido"}
