"""
API REST para Analizador Léxico-Sintáctico

Proporciona endpoints para análisis léxico de código fuente mediante HTTP.
Utiliza el módulo lexer para la tokenización.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from lexer import Lexer
from parser import Parser, ParserError

app = Flask(__name__)
CORS(app)  # Permite conexión CORS con frontend local

# Instancia global del lexer
lexer = Lexer()


@app.route("/api/analizar", methods=["POST"])
def api_analizar():
    """
    Endpoint POST para análisis léxico.

    Recibe código fuente en formato JSON y retorna tokens clasificados.

    Request JSON:
        {
            "codigo": str - Código fuente a analizar
        }

    Response JSON (200 OK):
        {
            "tokens": List[Dict] - Lista de tokens con 'lexema' y 'tipo'
        }

    Returns:
        Response JSON con tokens o error si request es inválido.
    """
    try:
        data = request.get_json()
        if data is None:
            return jsonify({"error": "Solicitud JSON inválida"}), 400

        codigo = data.get("codigo", "")
        tokens = lexer.analizar(codigo)
        try:
            tree = Parser(tokens).parse()
            return jsonify({"tokens": tokens, "tree": tree}), 200
        except ParserError as parser_error:
            return jsonify(
                {"tokens": tokens, "tree": None, "parserError": str(parser_error)}
            ), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
