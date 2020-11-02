import re
from lark import Lark
from lark import InlineTransformer
from typing import NamedTuple

class Symbol(NamedTuple):
    value: str

grammar = Lark(r"""
    ?start : expr+
    ?expr  : atom
           | lista
           | quoted 
    quoted : "'" expr
    lista   : "(" expr+ ")"
    ?atom  : STRING -> string
           | SYMBOL -> symbol
           | NUMBER -> number
           | BOOLEAN -> boolean
           | NAME -> name
           | CHAR -> char
    CHAR   : /\#\\\w+/
    STRING : /"[^"\\]*"/
    SYMBOL: /[-+=\/*!@$^&~<>?]+/
    NUMBER : /-?\d+(\.\d+)?/
    BOOLEAN: /\#t|\#nil/
    NAME   : /[a-zA-Z][-?\w]*/
    %ignore /\s+/
    %ignore /;[^\n]*/
""")

class LispyTransformer(InlineTransformer):
    CHARS = {
        "altmode": "\x1b",
        "backnext": "\x1f",
        "backspace": "\b",
        "call": "SUB",
        "linefeed": "\n",
        "page": "\f",
        "return": "\r",
        "rubout": "\xc7",
        "space": " ",
        "tab": "\t",
    }

    def char(self, token):
        token = token.split('#\\')[-1]
        return token if token.lower() not in self.CHARS else self.CHARS[token.lower()]    

    def string(self, token):
        return eval(token)

    def symbol(self, token):
        return Symbol(token)

    def number(self, token):
        return float(token)
    
    def boolean(self, token):
        return True if token.value == "#t" else False

    def name(self, token):
        return Symbol(token)
        
    def lista(self, *args):
        return list(args)

    def quoted(self, token):
        return [Symbol('quote'), token]

    def start(self, *args):
        array = list(args)
        array.insert(0, Symbol('begin'))
        return array

