"""Módulo de parser sintáctico para el Analizador Léxico-Sintáctico.

Construye un árbol de sintaxis abstracta (AST) a partir de la lista de tokens
producida por el lexer. Está diseñado para un subconjunto de la sintaxis C-like
utilizada en clase.
"""

from typing import Any, Dict, List


class ParserError(Exception):
    """Excepción lanzada cuando el parser encuentra una entrada inválida."""


class Parser:
    """Parser recursivo descendente para un subconjunto de la sintaxis de C."""

    TYPE_SPECIFIERS = {"int", "void", "float", "double"}

    def __init__(self, tokens: List[Dict[str, Any]]) -> None:
        self.tokens = [
            t
            for t in tokens
            if t["tipo"] not in {"Espacio vacío", "Salto de línea", "Tabulador"}
        ]
        self.current = 0

    def parse(self) -> Dict[str, Any]:
        """Parsea todos los tokens y retorna un AST raíz."""
        children = []
        while not self._is_at_end():
            children.append(self._declaration())
        return {"type": "Program", "label": "Programa", "children": children}

    def _declaration(self) -> Dict[str, Any]:
        if self._check_lexema_in(self.TYPE_SPECIFIERS):
            return self._parse_declaration()
        return self._statement()

    def _parse_declaration(self) -> Dict[str, Any]:
        type_token = self._advance()
        name = self._consume_name("Se esperaba un identificador después del tipo.")

        if self._match_lexema("("):
            params = self._parse_parameter_list()
            self._consume_lexema(
                ")", "Se esperaba ')' después de la lista de parámetros."
            )
            body = self._compound_statement()
            label = f"{type_token['lexema']} {name['lexema']}()"
            children = []
            if params:
                children.append(
                    {"type": "ParameterList", "label": "Parámetros", "children": params}
                )
            children.append(body)
            return {"type": "FunctionDeclaration", "label": label, "children": children}

        if self._match_lexema("="):
            initializer = self._expression()
            self._consume_lexema(
                ";", "Se esperaba ';' al final de la declaración de variable."
            )
            return {
                "type": "VariableDeclaration",
                "label": f"{type_token['lexema']} {name['lexema']}",
                "children": [initializer],
            }

        self._consume_lexema(
            ";", "Se esperaba ';' al final de la declaración de variable."
        )
        return {
            "type": "VariableDeclaration",
            "label": f"{type_token['lexema']} {name['lexema']}",
            "children": [],
        }

    def _parse_parameter_list(self) -> List[Dict[str, Any]]:
        parameters = []
        if self._check_lexema(")"):
            return parameters

        while True:
            type_token = self._consume_type_specifier(
                "Se esperaba un tipo en la lista de parámetros."
            )
            name = self._consume_name("Se esperaba un identificador de parámetro.")
            parameters.append(
                {
                    "type": "Parameter",
                    "label": f"{type_token['lexema']} {name['lexema']}",
                    "children": [],
                }
            )
            if not self._match_lexema(","):
                break
        return parameters

    def _statement(self) -> Dict[str, Any]:
        if self._match_lexema("if"):
            return self._if_statement()
        if self._match_lexema("while"):
            return self._while_statement()
        if self._match_lexema("for"):
            return self._for_statement()
        if self._match_lexema("return"):
            return self._return_statement()
        if self._check_lexema("{"):
            return self._compound_statement()
        return self._expression_statement()

    def _if_statement(self) -> Dict[str, Any]:
        self._consume_lexema("(", "Se esperaba '(' después de 'if'.")
        condition = self._expression()
        self._consume_lexema(")", "Se esperaba ')' después de la condición.")
        then_branch = self._statement()
        else_branch = None
        if self._match_lexema("else"):
            else_branch = self._statement()
        children = [
            {"type": "Condition", "label": "Condición", "children": [condition]},
            {"type": "Then", "label": "Then", "children": [then_branch]},
        ]
        if else_branch:
            children.append(
                {"type": "Else", "label": "Else", "children": [else_branch]}
            )
        return {"type": "IfStatement", "label": "If", "children": children}

    def _while_statement(self) -> Dict[str, Any]:
        self._consume_lexema("(", "Se esperaba '(' después de 'while'.")
        condition = self._expression()
        self._consume_lexema(")", "Se esperaba ')' después de la condición.")
        body = self._statement()
        return {
            "type": "WhileStatement",
            "label": "While",
            "children": [
                {"type": "Condition", "label": "Condición", "children": [condition]},
                body,
            ],
        }

    def _for_statement(self) -> Dict[str, Any]:
        self._consume_lexema("(", "Se esperaba '(' después de 'for'.")
        initializer = None
        if not self._check_lexema(";"):
            initializer = self._expression_statement(allow_missing_semicolon=True)
        self._consume_lexema(
            ";", "Se esperaba ';' después de la inicialización del for."
        )
        condition = None
        if not self._check_lexema(";"):
            condition = self._expression()
        self._consume_lexema(";", "Se esperaba ';' después de la condición del for.")
        increment = None
        if not self._check_lexema(")"):
            increment = self._expression()
        self._consume_lexema(")", "Se esperaba ')' después de la cláusula for.")
        body = self._statement()
        children = []
        if initializer:
            children.append(
                {"type": "Initializer", "label": "Init", "children": [initializer]}
            )
        if condition:
            children.append(
                {"type": "Condition", "label": "Condición", "children": [condition]}
            )
        if increment:
            children.append(
                {"type": "Increment", "label": "Incremento", "children": [increment]}
            )
        children.append(body)
        return {"type": "ForStatement", "label": "For", "children": children}

    def _return_statement(self) -> Dict[str, Any]:
        expr = None
        if not self._check_lexema(";"):
            expr = self._expression()
        self._consume_lexema(";", "Se esperaba ';' después de 'return'.")
        children = (
            [{"type": "ReturnValue", "label": "Valor", "children": [expr]}]
            if expr
            else []
        )
        return {"type": "ReturnStatement", "label": "Return", "children": children}

    def _compound_statement(self) -> Dict[str, Any]:
        self._consume_lexema("{", "Se esperaba '{' para iniciar un bloque.")
        statements = []
        while not self._check_lexema("}") and not self._is_at_end():
            statements.append(self._declaration())
        self._consume_lexema("}", "Se esperaba '}' al final del bloque.")
        return {"type": "Block", "label": "Bloque", "children": statements}

    def _expression_statement(
        self, allow_missing_semicolon: bool = False
    ) -> Dict[str, Any]:
        if self._check_lexema(";"):
            self._consume_lexema(";", "Se esperaba ';'.")
            return {"type": "EmptyStatement", "label": ";", "children": []}
        expr = self._expression()
        if not allow_missing_semicolon:
            self._consume_lexema(";", "Se esperaba ';' al final de la expresión.")
        return {"type": "ExpressionStatement", "label": "Expr", "children": [expr]}

    def _expression(self) -> Dict[str, Any]:
        return self._assignment()

    def _assignment(self) -> Dict[str, Any]:
        expr = self._logical_or()
        if self._match_lexema("="):
            equals = self._previous()
            value = self._assignment()
            if expr["type"] != "Identifier":
                raise ParserError(
                    "La asignación debe tener un identificador en el lado izquierdo."
                )
            return {
                "type": "Assignment",
                "label": equals["lexema"],
                "children": [expr, value],
            }
        return expr

    def _logical_or(self) -> Dict[str, Any]:
        expr = self._logical_and()
        while self._match_lexema("||"):
            operator = self._previous()
            right = self._logical_and()
            expr = {
                "type": "LogicalExpression",
                "label": operator["lexema"],
                "children": [expr, right],
            }
        return expr

    def _logical_and(self) -> Dict[str, Any]:
        expr = self._equality()
        while self._match_lexema("&&"):
            operator = self._previous()
            right = self._equality()
            expr = {
                "type": "LogicalExpression",
                "label": operator["lexema"],
                "children": [expr, right],
            }
        return expr

    def _equality(self) -> Dict[str, Any]:
        expr = self._comparison()
        while self._match_lexema("==", "!="):
            operator = self._previous()
            right = self._comparison()
            expr = {
                "type": "BinaryExpression",
                "label": operator["lexema"],
                "children": [expr, right],
            }
        return expr

    def _comparison(self) -> Dict[str, Any]:
        expr = self._term()
        while self._match_lexema("<", ">", "<=", ">="):
            operator = self._previous()
            right = self._term()
            expr = {
                "type": "BinaryExpression",
                "label": operator["lexema"],
                "children": [expr, right],
            }
        return expr

    def _term(self) -> Dict[str, Any]:
        expr = self._factor()
        while self._match_lexema("+", "-"):
            operator = self._previous()
            right = self._factor()
            expr = {
                "type": "BinaryExpression",
                "label": operator["lexema"],
                "children": [expr, right],
            }
        return expr

    def _factor(self) -> Dict[str, Any]:
        expr = self._unary()
        while self._match_lexema("*", "/"):
            operator = self._previous()
            right = self._unary()
            expr = {
                "type": "BinaryExpression",
                "label": operator["lexema"],
                "children": [expr, right],
            }
        return expr

    def _unary(self) -> Dict[str, Any]:
        if self._match_lexema("-", "!"):
            operator = self._previous()
            right = self._unary()
            return {
                "type": "UnaryExpression",
                "label": operator["lexema"],
                "children": [right],
            }
        return self._primary()

    def _primary(self) -> Dict[str, Any]:
        if self._match_type("Integer"):
            return {
                "type": "Literal",
                "label": self._previous()["lexema"],
                "children": [],
            }
        if self._match_type("Float"):
            return {
                "type": "Literal",
                "label": self._previous()["lexema"],
                "children": [],
            }
        if self._match_type("Cadena"):
            return {
                "type": "Literal",
                "label": self._previous()["lexema"],
                "children": [],
            }
        if self._match_type("Variable"):
            return {
                "type": "Identifier",
                "label": self._previous()["lexema"],
                "children": [],
            }
        if self._match_lexema("("):
            expr = self._expression()
            self._consume_lexema(")", "Se esperaba ')' después de la expresión.")
            return {"type": "Grouping", "label": "()", "children": [expr]}
        raise ParserError(f"Token inesperado: {self._peek()['lexema']}")

    def _match_lexema(self, *lexemas: str) -> bool:
        if self._check_lexema_any(lexemas):
            self._advance()
            return True
        return False

    def _check_lexema(self, lexema: str) -> bool:
        if self._is_at_end():
            return False
        return self._peek()["lexema"] == lexema

    def _check_lexema_any(self, lexemas: List[str]) -> bool:
        if self._is_at_end():
            return False
        return self._peek()["lexema"] in lexemas

    def _check_lexema_in(self, lexemas: set) -> bool:
        if self._is_at_end():
            return False
        return self._peek()["lexema"] in lexemas

    def _match_type(self, tipo: str) -> bool:
        if self._is_at_end():
            return False
        if self._peek()["tipo"] == tipo:
            self._advance()
            return True
        return False

    def _consume(self, tipo: str, mensaje: str) -> Dict[str, Any]:
        if self._match_type(tipo):
            return self._previous()
        raise ParserError(mensaje)

    def _consume_name(self, mensaje: str) -> Dict[str, Any]:
        if self._check_type("Variable") or (
            self._check_lexema("main") and self._peek()["tipo"] == "Palabra Reservada"
        ):
            return self._advance()
        raise ParserError(mensaje)

    def _consume_type_specifier(self, mensaje: str) -> Dict[str, Any]:
        if self._check_type_specifier():
            return self._advance()
        raise ParserError(mensaje)

    def _consume_lexema(self, lexema: str, mensaje: str) -> Dict[str, Any]:
        if self._check_lexema(lexema):
            return self._advance()
        raise ParserError(mensaje)

    def _check_type_specifier(self) -> bool:
        return (
            self._check_type("Palabra Reservada")
            and self._peek()["lexema"] in self.TYPE_SPECIFIERS
        )

    def _check_type(self, tipo: str) -> bool:
        if self._is_at_end():
            return False
        return self._peek()["tipo"] == tipo

    def _peek(self) -> Dict[str, Any]:
        return self.tokens[self.current]

    def _previous(self) -> Dict[str, Any]:
        return self.tokens[self.current - 1]

    def _advance(self) -> Dict[str, Any]:
        if not self._is_at_end():
            self.current += 1
        return self.tokens[self.current - 1]

    def _is_at_end(self) -> bool:
        return self.current >= len(self.tokens)
