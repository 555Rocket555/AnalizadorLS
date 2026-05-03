"""
##########################  CODIGO BASE ##########################

FUNCIONAMIENTO
1. El usuario puede escribir varias líneas (como código real)
2. Termina con Enter en una línea vacía
3. El programa analiza todo y muestra los tokens
"""

import re

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
}

OPERADORES = {
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

CARACTERES_ESPECIALES = {
    '"',
    "#",
    "(",
    ")",
    "{",
    "}",
    ";",
    ",",
    "%",
}

# Primero se intentan los operadores de 2 caracteres, luego los de 1.
PATRON = r"\n|\t| +|<=|>=|==|!=|&&|\|\||\d+|[a-zA-Z_][a-zA-Z_0-9]*|\".*?\"|."


def analizar(codigo):
    tokens = []
    coincidencias = re.findall(PATRON, codigo)

    for lexema in coincidencias:
        if lexema == "\n":
            tokens.append((r"\n", "Salto de línea"))
        elif lexema == "\t":
            tokens.append((r"\t", "Tabulador"))
        elif re.fullmatch(r" +", lexema):
            tokens.append((lexema, "Espacio vacío"))
        elif re.fullmatch(r"\d+", lexema):
            tokens.append((lexema, "Integer"))
        elif re.fullmatch(r"[a-zA-Z_][a-zA-Z_0-9]*", lexema):
            if lexema.lower() in PALABRAS_RESERVADAS:
                tokens.append((lexema, "Palabra Reservada"))
            else:
                tokens.append((lexema, "Variable"))
        elif re.fullmatch(r'".*?"', lexema):
            tokens.append((lexema, "Cadena"))
        elif lexema in OPERADORES:
            tokens.append((lexema, "Operador"))
        elif lexema in CARACTERES_ESPECIALES:
            tokens.append((lexema, "Caracter Especial"))
        else:
            tokens.append((lexema, "Desconocido"))

    return tokens


while True:
    print("\nIntroduce tu bloque (termina con una línea vacía):\n")

    lineas = []
    while True:
        linea = input()
        if linea == "":
            break
        lineas.append(linea)

    codigo = "\n".join(lineas)

    print("\n#Bloque:\n")
    print(codigo)

    resultado = analizar(codigo)

    print("\n#Tokens\n")
    for lexema, tipo in resultado:
        print(f"<'{lexema}', {tipo}>")

    print(f"\nTotal de tokens: {len(resultado)}")

    repetir = input("\n¿Quieres analizar otro bloque? (s/n): ").strip().lower()
    if repetir != "s":
        print("Programa finalizado.")
        break
