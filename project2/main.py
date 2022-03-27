from typing import Callable

from termcolor import colored


class BNF_Symbol:

    def __init__(self, name, value, terminates=False):
        """
        Constructor for a BNF Symbol, containing symbol name, value, and terminal status.
        @param self:
        @param name:
        @param value:
        @param terminates:
        @return:
        """
        self.type = name
        self.value = value
        self.terminates = terminates

        if not self.terminates and type(self.value) != list:
            self.value = [self.value]

    def __repr__(self):
        """
        Helper function to display the symbol as a tree, recursively descending into each child
        to show the tree
        @return:
        """
        if self.terminates:
            return f"{self.type}: " + colored("\"" + self.value + "\"", 'green')
        else:
            header = '│ ' + self.type + ':'
            body = '\n'.join(map(repr, self.value))

            # if body.count('\n') == 0:
            #     return header + ' ' + body
            # else:
            return header + '\n' + '└───' + body.replace('\n', '\n' + '    ')

    def __iter__(self):
        """
        Describe iterable status based on terminal status
        @return:
        """
        return iter(()) if self.terminates else iter(self.value)


class BNF_Parser_Result(tuple):
    """
    Class to contain the (intermediate) results of a BNF Grammar parsing
    """
    def __repr__(self):
        return '''%s
        '''.replace('''
        ''', '\n') % self[0]


class _BNF_Parser:
    """
    BNF Grammar parser, storing references to the handler function, terminal state attribute,
    and the grammar type.
    """

    handler = None
    f = None
    terminates = False

    def __init__(self, f, terminates=False, handler=None) -> None:
        self.terminates = terminates
        self.f = f
        self.handler = handler

    def eval(self, handler):
        """
        Sets the computational handler for use when calculating the resultant expression
        """
        self.handler = handler

    def __call__(self, s):
        x = self.f(s)
        if x:
            matched, rest = x
            sym = BNF_Symbol(self.f.__name__, matched, self.terminates)

            # call the symbol handler if present
            if self.handler is not None:
                self.handler(sym)
            return BNF_Parser_Result((sym, rest))


def bnf_parser(f: Callable = None, terminates: bool = False, handler: Callable = None):
    """
    Helper function to wrap the class instantiation, so we can define terminals more cleanly
    """
    if f:
        return _BNF_Parser(f)
    else:
        def wrapper(function):
            return _BNF_Parser(function, terminates=terminates, handler=handler)

        return wrapper


def ordered_definition(*grammars):
    """
    Return a thunk parser that matches sequences of symbols
    """

    def parse(s):
        acc = []
        rest = s
        for sym in grammars:
            x = sym(rest)
            if not x:
                return False
            matched, rest = x
            acc.append(matched)
        return acc, rest

    return parse


def multiple_definitions(*bnf_symbols):
    """
    Return a thunk parser that matches alternatives
    """

    def parse(s):
        for sym in bnf_symbols:
            x = sym(s)
            if x:
                return x
        return False

    return parse


@bnf_parser(terminates=True)
def left_brace(s):
    """
    matches character that wraps <term> on the left
    """
    if s and s[0] == '{':
        return s[0], s[1:]


@bnf_parser(terminates=True)
def right_brace(s):
    """
    matches character that wraps <term> on the right
    """
    if s and s[0] == '}':
        return s[0], s[1:]


@bnf_parser(terminates=True)
def literal(s):
    """
    <literal>  ::=  0|1|2|3|4|5|6|7|8|9
    """
    if s and s[0] in ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9'):
        return s[0], s[1:]


@literal.eval
def handler_literal(sym):
    sym.result = int(sym.value)


@bnf_parser
def plus_or_minus(s):
    """
    matches + or - operator in a factor
    """
    if s and s[0] in ('+', '-'):
        return s[0], s[1:]


@bnf_parser
def times_or_divides(s):
    """
    matches * or / operator in an expression
    """
    if s and s[0] in ('*', '/'):
        return s[0], s[1:]


@bnf_parser
def term(s):
    """
    <term>  ::=  {  <expression>  }  |  <literal>
    """
    return multiple_definitions(ordered_definition(left_brace, expression, right_brace),
                                literal)(s)


@term.eval
def handler_term(sym):
    if len(sym.value) == 1:  # <literal>
        lit = sym.value[0]
        sym.result = lit.result
    else:  # { <expression> }
        left, expr, right = sym.value
        sym.result = expr.result


@bnf_parser
def factor(s):
    """
    <factor>  :==  <term> + <factor>  |  <term> - <factor>  |  <term>
    """
    return multiple_definitions(ordered_definition(term, plus_or_minus, factor),
                                term)(s)


@factor.eval
def handler_factor(sym):
    if len(sym.value) == 1:  # <term>
        ter = sym.value[0]
        sym.result = ter.result
    else:
        ter, op, fac = sym.value
        if op.value[0] == '-':  # <term> - <factor>
            sym.result = ter.result - fac.result
        else:  # <term> + <factor>
            sym.result = ter.result + fac.result


@bnf_parser
def expression(s):
    """
    <expression>  ::=  <factor>  * <expression>   |   <factor>  /  <expression>   |   <factor>
    """
    return multiple_definitions(ordered_definition(factor, times_or_divides, expression),
                                factor)(s)


@expression.eval
def eval_expression(sym):
    if len(sym.value) == 1:  # <factor>
        fac = sym.value[0]
        sym.result = fac.result
    else:
        fac, op, expr = sym.value
        if op.value[0] == '*':  # <factor> * <expression>
            sym.result = fac.result * expr.result
        else:  # <factor> / <expression>
            sym.result = fac.result / expr.result


def calc(s):
    return expression(s)[0].result


if __name__ == "__main__":
    expr = expression('{2*4}+5*6-7/{1+2}')

    print(expr)

    print(expr[0].result)
    # print(calc('4+5*6-7'))
    # print(calc('4+5'))
