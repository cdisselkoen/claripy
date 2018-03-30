import json

import pysmt
from pysmt.shortcuts import Symbol, get_env
from pysmt.smtlib.parser import SmtLibParser, PysmtSyntaxError


def make_pysmt_const_from_type(val, type):
    return getattr(pysmt.shortcuts, str(type))(val)


class SMTParser(object):
    def __init__(self, tokens):
        self.p = SmtLibParser()
        self.tokens = tokens

    def expect(self, *allowed):
        t = self.tokens.consume()
        if t not in allowed:
            raise PysmtSyntaxError("Invalid token, expected any of {}, got '{}'".format(allowed, t))
        return t

    def expect_assignment_tuple(self):
        self.expect('(')
        self.expect('define-fun')
        vname = self.p.parse_atom(self.tokens, 'define-fun')
        self.expect('(')
        self.expect(')')
        t = self.p.parse_type(self.tokens, 'define-fun')
        value_token = self.p.parse_atom(self.tokens, 'define-fun')
        val_repr = self.p.atom(value_token, get_env().formula_manager)
        self.expect(')')

        return Symbol(vname, t), getattr(pysmt.shortcuts, t.name)(val_repr.constant_value())

    def consume_assignment_list(self):
        self.expect('(')
        self.expect('model')
        """Parses a list of expressions from the tokens"""

        assignments = []
        while True:
            next_token = self.tokens.consume()
            self.tokens.add_extra_token(next_token)  # push it back
            if next_token == ')':
                break

            assignments.append(self.expect_assignment_tuple())

        self.expect(')')

        return assignments