import re
from typing import Dict, List


class LexerConfig:
    PALABRAS_RESERVADAS = {
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
        "do",
        "then",
        "char",
        "boolean",
        "string",
    }

    # Definición de tokens con nombre para usar grupos de captura
    # 1. Comentarios
    # 2. Strings
    # 3. Floats
    # 4. Operadores de 2 caracteres primero por precedencia
    TOKENS_SPEC = [
        ("COMENTARIO", r"//.*|/\*[\s\S]*?\*/"),
        ("CADENA", r'"[^"\\\n]*(?:\\.[^"\\\n]*)*"'),
        ("FLOAT", r"\d+\.\d+(?!\.)"),
        ("INTEGER", r"\d+(?!\.)"),
        ("OPERADOR", r"\+\+|--|<=|>=|==|!=|&&|\|\||[+\-*/=<>!%]"),
        ("ESPECIAL", r"[()\[\]{};,%#]"),
        ("ID", r"[a-zA-Z_][a-zA-Z_0-9]*"),
        ("TABULADOR", r"\t"),  # <-- NUEVA REGLA SOLO PARA TABS
        ("ESPACIO", r" +"),
        ("SALTO", r"\n"),
    ]

    PATRON_GLOBAL = "|".join(f"(?P<{name}>{ptrn})" for name, ptrn in TOKENS_SPEC)


class Lexer:
    def __init__(self):
        self.regex = re.compile(LexerConfig.PATRON_GLOBAL)

    def analizar(self, codigo: str) -> List[Dict[str, str]]:
        tokens = []
        # Usamos finditer para tener más control sobre la posición de los errores
        for mo in self.regex.finditer(codigo):
            tipo = mo.lastgroup
            lexema = mo.group(tipo)

            if tipo == "ESPACIO":
                tokens.append({"lexema": lexema, "tipo": "Espacio vacío"})
            elif tipo == "SALTO":
                tokens.append({"lexema": r"\n", "tipo": "Salto de línea"})
            elif tipo == "TABULADOR":  # <-- AÑADIR ESTA VALIDACIÓN
                tokens.append({"lexema": r"\t", "tipo": "Tabulador"})
            elif tipo == "COMENTARIO":
                continue  # Ignoramos comentarios para el AST
            elif tipo == "FLOAT":
                tokens.append({"lexema": lexema, "tipo": "Float"})
            elif tipo == "INTEGER":
                tokens.append({"lexema": lexema, "tipo": "Integer"})
            elif tipo == "ID":
                t = (
                    "Palabra Reservada"
                    if lexema in LexerConfig.PALABRAS_RESERVADAS
                    else "Variable"
                )
                tokens.append({"lexema": lexema, "tipo": t})
            elif tipo == "CADENA":
                tokens.append({"lexema": lexema, "tipo": "Cadena"})
            elif tipo == "OPERADOR":
                tokens.append({"lexema": lexema, "tipo": "Operador"})
            elif tipo == "ESPECIAL":
                tokens.append({"lexema": lexema, "tipo": "Caracter Especial"})
            else:
                tokens.append({"lexema": lexema, "tipo": "Desconocido"})

        return tokens
