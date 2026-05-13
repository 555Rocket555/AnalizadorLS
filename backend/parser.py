from typing import Any, Dict, List


class ParserError(Exception):
    def __init__(self, message, lexema=None):
        self.message = f"{message} (Token: '{lexema}')" if lexema else message
        super().__init__(self.message)


class Parser:
    TYPE_SPECIFIERS = {"int", "void", "float", "double", "char", "boolean", "string"}

    def __init__(self, tokens: List[Dict[str, Any]]) -> None:
        self.tokens = [
            t
            for t in tokens
            if t["tipo"] not in {"Espacio vacío", "Salto de línea", "Tabulador"}
        ]
        self.current = 0
        self.nodes = []
        self.edges = []
        self.id_counter = 1
        self.errors = []  # NUEVO: Lista para almacenar múltiples errores

    def _new_node(self, label: str, type_name: str) -> int:
        nid = self.id_counter
        self.id_counter += 1
        self.nodes.append({"id": nid, "label": label, "type": type_name})
        return nid

    def _add_edge(self, from_id: int, to_id: int):
        self.edges.append({"from": from_id, "to": to_id})

    # ==========================================
    # LÓGICA PRINCIPAL CON MODO PÁNICO
    # ==========================================
    def parse(self) -> Dict[str, Any]:
        root_id = self._new_node("Inicio", "Program")
        prev_leaves = [root_id]

        while not self._is_at_end():
            try:
                stmt_root, stmt_leaves = self._declaration()
                for leaf in prev_leaves:
                    self._add_edge(leaf, stmt_root)
                prev_leaves = stmt_leaves
            except ParserError as e:
                # MODO PÁNICO: Atrapamos el error, lo guardamos y sincronizamos
                self.errors.append(e.message)
                self._synchronize()

        return {"nodes": self.nodes, "edges": self.edges, "errors": self.errors}

    def _synchronize(self):
        """Avanza los tokens hasta encontrar un punto seguro para reanudar el análisis"""
        self._advance()
        while not self._is_at_end():
            # Si acabamos de pasar un punto y coma, estamos a salvo
            if self._previous()["lexema"] == ";":
                return
            # Si el siguiente token es el inicio de una nueva declaración, estamos a salvo
            peek_lexema = self._peek()["lexema"]
            if peek_lexema in [
                "int",
                "float",
                "char",
                "boolean",
                "string",
                "void",
                "if",
                "while",
                "return",
                "printf",
            ]:
                return
            self._advance()

    # ==========================================
    # RESTO DE LA GRAMÁTICA (Intacta)
    # ==========================================
    def _declaration(self):
        if self._match_lexema("#"):
            self._consume_lexema("define", "Se esperaba 'define'")
            name = self._consume_name("Se esperaba identificador")
            value = self._advance()
            def_id = self._new_node("#define", "Preprocessor")
            name_id = self._new_node(name["lexema"], "Variable")
            val_id = self._new_node(value["lexema"], "Literal")
            self._add_edge(def_id, name_id)
            self._add_edge(def_id, val_id)
            return def_id, [name_id, val_id]

        if self._check_lexema_in(self.TYPE_SPECIFIERS):
            return self._parse_declaration()
        return self._statement()

    def _parse_declaration(self):
        type_token = self._advance()
        type_id = self._new_node(type_token["lexema"], "Type")
        name = self._consume_name("Se esperaba identificador")
        name_id = self._new_node(name["lexema"], "Variable")

        if self._match_lexema("("):
            self._add_edge(type_id, name_id)
            if not self._check_lexema(")"):
                while True:
                    p_type = self._advance()
                    p_name = self._consume_name(
                        "Se esperaba identificador de parámetro"
                    )
                    param_id = self._new_node(
                        f"{p_type['lexema']} {p_name['lexema']}", "Parameter"
                    )
                    self._add_edge(name_id, param_id)
                    if not self._match_lexema(","):
                        break
            self._consume_lexema(")", "Se esperaba )")
            block_root, block_leaves = self._compound_statement()
            self._add_edge(name_id, block_root)
            return type_id, block_leaves

        leaves = []
        while True:
            if self._match_lexema("="):
                eq_id = self._new_node("=", "Assign")
                val_root, val_leaves = self._expression()
                self._add_edge(type_id, eq_id)
                self._add_edge(eq_id, name_id)
                self._add_edge(eq_id, val_root)
                leaves.extend([name_id] + val_leaves)
            else:
                self._add_edge(type_id, name_id)
                leaves.append(name_id)

            if self._match_lexema(","):
                name = self._consume_name("Se esperaba identificador")
                name_id = self._new_node(name["lexema"], "Variable")
            else:
                break

        self._consume_lexema(";", "Falta ;")
        semi_id = self._new_node(";", "Punctuation")
        for leaf in leaves:
            self._add_edge(leaf, semi_id)
        return type_id, [semi_id]

    def _statement(self):
        if self._match_lexema("if"):
            return self._if_statement()
        if self._match_lexema("while"):
            return self._while_statement()
        if self._match_lexema("return"):
            return self._return_statement()
        if self._match_lexema("printf"):
            return self._printf_call()
        if self._check_lexema("{"):
            return self._compound_statement()
        return self._expression_statement()

    def _while_statement(self):
        while_id = self._new_node("while", "Keyword")
        cond_root, cond_leaves = self._expression()
        self._add_edge(while_id, cond_root)

        self._consume_lexema("do", "Falta do en el while")
        do_id = self._new_node("do", "Keyword")
        for leaf in cond_leaves:
            self._add_edge(leaf, do_id)

        body_root, body_leaves = self._statement()
        self._add_edge(do_id, body_root)
        return while_id, body_leaves

    def _if_statement(self):
        if_id = self._new_node("if", "Keyword")
        cond_root, cond_leaves = self._expression()
        self._add_edge(if_id, cond_root)

        self._consume_lexema("then", "Falta then")
        then_id = self._new_node("then", "Keyword")
        for leaf in cond_leaves:
            self._add_edge(leaf, then_id)

        then_root, then_leaves = self._statement()
        self._add_edge(then_id, then_root)

        if self._match_lexema("else"):
            else_id = self._new_node("else", "Keyword")
            for leaf in cond_leaves:
                self._add_edge(leaf, else_id)
            else_root, else_leaves = self._statement()
            self._add_edge(else_id, else_root)
            return if_id, then_leaves + else_leaves

        return if_id, then_leaves

    def _return_statement(self):
        ret_id = self._new_node("return", "Keyword")
        val_root, val_leaves = self._expression()
        self._add_edge(ret_id, val_root)
        self._consume_lexema(";", "Falta ;")
        semi_id = self._new_node(";", "Punctuation")
        for leaf in val_leaves:
            self._add_edge(leaf, semi_id)
        return ret_id, [semi_id]

    def _printf_call(self):
        print_id = self._new_node("printf", "Call")
        self._consume_lexema("(", "Falta (")
        val_root, val_leaves = self._expression()
        self._add_edge(print_id, val_root)
        self._consume_lexema(")", "Falta )")
        self._consume_lexema(";", "Falta ;")
        semi_id = self._new_node(";", "Punctuation")
        for leaf in val_leaves:
            self._add_edge(leaf, semi_id)
        return print_id, [semi_id]

    def _expression_statement(self):
        expr_root, expr_leaves = self._expression()
        self._consume_lexema(";", "Falta ;")
        semi_id = self._new_node(";", "Punctuation")
        for leaf in expr_leaves:
            self._add_edge(leaf, semi_id)
        return expr_root, [semi_id]

    def _expression(self):
        return self._assignment()

    def _assignment(self):
        left_root, left_leaves = self._logical_or()
        if self._match_lexema("="):
            op = self._previous()
            eq_id = self._new_node(op["lexema"], "Assign")
            right_root, right_leaves = self._assignment()
            self._add_edge(eq_id, left_root)
            self._add_edge(eq_id, right_root)
            return eq_id, left_leaves + right_leaves
        return left_root, left_leaves

    def _logical_or(self):
        left_root, left_leaves = self._logical_and()
        while self._match_lexema("||"):
            op_id = self._new_node("||", "Logical")
            right_root, right_leaves = self._logical_and()
            self._add_edge(op_id, left_root)
            self._add_edge(op_id, right_root)
            left_root, left_leaves = op_id, left_leaves + right_leaves
        return left_root, left_leaves

    def _logical_and(self):
        left_root, left_leaves = self._equality()
        while self._match_lexema("&&"):
            op_id = self._new_node("&&", "Logical")
            right_root, right_leaves = self._equality()
            self._add_edge(op_id, left_root)
            self._add_edge(op_id, right_root)
            left_root, left_leaves = op_id, left_leaves + right_leaves
        return left_root, left_leaves

    def _equality(self):
        left_root, left_leaves = self._comparison()
        while self._match_lexema("==", "!="):
            op = self._previous()
            op_id = self._new_node(op["lexema"], "Binary")
            right_root, right_leaves = self._comparison()
            self._add_edge(op_id, left_root)
            self._add_edge(op_id, right_root)
            left_root, left_leaves = op_id, left_leaves + right_leaves
        return left_root, left_leaves

    def _comparison(self):
        left_root, left_leaves = self._term()
        while self._match_lexema("<", ">", "<=", ">="):
            op = self._previous()
            op_id = self._new_node(op["lexema"], "Binary")
            right_root, right_leaves = self._term()
            self._add_edge(op_id, left_root)
            self._add_edge(op_id, right_root)
            left_root, left_leaves = op_id, left_leaves + right_leaves
        return left_root, left_leaves

    def _term(self):
        left_root, left_leaves = self._factor()
        while self._match_lexema("+", "-"):
            op = self._previous()
            op_id = self._new_node(op["lexema"], "Binary")
            right_root, right_leaves = self._factor()
            self._add_edge(op_id, left_root)
            self._add_edge(op_id, right_root)
            left_root, left_leaves = op_id, left_leaves + right_leaves
        return left_root, left_leaves

    def _factor(self):
        left_root, left_leaves = self._unary()
        while self._match_lexema("*", "/", "%"):
            op = self._previous()
            op_id = self._new_node(op["lexema"], "Binary")
            right_root, right_leaves = self._unary()
            self._add_edge(op_id, left_root)
            self._add_edge(op_id, right_root)
            left_root, left_leaves = op_id, left_leaves + right_leaves
        return left_root, left_leaves

    def _unary(self):
        if self._match_lexema("!", "++", "--", "-"):
            op = self._previous()
            op_id = self._new_node(op["lexema"], "Unary")
            right_root, right_leaves = self._unary()
            self._add_edge(op_id, right_root)
            return op_id, right_leaves
        return self._primary()

    def _primary(self):
        if (
            self._match_type("Integer")
            or self._match_type("Float")
            or self._match_type("Cadena")
            or self._match_type("Variable")
        ):
            nid = self._new_node(self._previous()["lexema"], "Literal")
            return nid, [nid]
        if self._match_lexema("("):
            expr_root, expr_leaves = self._expression()
            self._consume_lexema(")", "Falta )")
            return expr_root, expr_leaves
        raise ParserError("Token inesperado", self._peek()["lexema"])

    def _compound_statement(self):
        self._consume_lexema("{", "Falta {")
        block_id = self._new_node("{}", "Block")
        prev_leaves = [block_id]
        while not self._is_at_end() and not self._check_lexema("}"):
            try:
                stmt_root, stmt_leaves = self._declaration()
                for leaf in prev_leaves:
                    self._add_edge(leaf, stmt_root)
                prev_leaves = stmt_leaves
            except ParserError as e:
                # MODO PÁNICO (DENTRO DE BLOQUES)
                self.errors.append(e.message)
                self._synchronize()
        self._consume_lexema("}", "Falta }")
        return block_id, prev_leaves

    # --- Utilidades Base ---
    def _is_at_end(self):
        return self.current >= len(self.tokens)

    def _peek(self):
        return self.tokens[self.current]

    def _previous(self):
        return self.tokens[self.current - 1]

    def _advance(self):
        if not self._is_at_end():
            self.current += 1
        return self._previous()

    def _check_lexema_in(self, s):
        return not self._is_at_end() and self._peek()["lexema"] in s

    def _match_lexema(self, *lexemas):
        for l in lexemas:
            if not self._is_at_end() and self._peek()["lexema"] == l:
                self._advance()
                return True
        return False

    def _match_type(self, t):
        if not self._is_at_end() and self._peek()["tipo"] == t:
            self._advance()
            return True
        return False

    def _consume_lexema(self, l, msg):
        if not self._is_at_end() and self._peek()["lexema"] == l:
            return self._advance()
        raise ParserError(msg, self._peek()["lexema"])

    def _consume_name(self, msg):
        if not self._is_at_end() and self._peek()["tipo"] in [
            "Variable",
            "Palabra Reservada",
        ]:
            return self._advance()
        raise ParserError(msg, self._peek()["lexema"])

    def _check_lexema(self, l):
        return not self._is_at_end() and self._peek()["lexema"] == l
