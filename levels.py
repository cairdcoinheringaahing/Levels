import argparse
import functools
import itertools
import math
import random
import re
import sys

if __name__ == '__main__':
    allinput = list(map(eval, sys.stdin.readlines()))
    sys.stdin.seek(0)

code_page = r'''
→←↓↑↖↗↘↙⇑£␊⇓↕↔∕∖
↥↧≤≥¦§°±Þþß⍶⍷⍸⍹✸
 !"#$%&'()*+,-./
0123456789:;<=>?
@ABCDEFGHIJKLMNO
PQRSTUVWXYZ[\]^_
`abcdefghijklmno
pqrstuvwxyz{|}~¡
×ĀĄĈĐĖĚĜĤĪĴĶĹŁŇŌ
ŒØŘŠŤŬŮŴÝŶŽ‼⁇⁈⁉‽
÷āąĉđėěĝĥīĵķĺłňō
œøřšťŭůŵýŷž¿©®ªº
⁰¹²³⁴⁵⁶⁷⁸⁹‘’‚‛‹›
₀₁₂₃₄₅₆₇₈₉“”„‟«»
αβγδεζηθικλμνξοπ
ρςστυφχψωΔΘΛΞΣΨΩ
'''

code_page = code_page.replace('\n', '').replace('␊', '\n')
cp = list(code_page)

def numfunc(real, comp):
    def inner(x, y = None):
        if isinstance(x, complex):
            if y is not None:
                return comp(x, y)
            return comp(x)
        
        if y is not None:
            return real(x, y)
        return real(x)
    return inner

constants = [

    math.pi,
    math.e,
    (1 + math.sqrt(5)) / 2,
    100,
    128,
    256,
    0.5,
    '"',
    "'",
    code_page,
    'AEIOUaeiou',
    'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz',
    '0123456789',

]

math_funcs1 = {
    
     0: lambda x: x // 2,
     1: lambda x: x  / 2,
     2: lambda x: x  * 2,
     3: lambda x: x ** 2,
    
     4: lambda x: 1 / x,
     5: abs,
     6: int,

     7: math.cos,
     8: math.sin,
     9: math.tan,
    10: math.acos,
    11: math.asin,
    12: math.atan,

    13: math.cosh,
    14: math.sinh,
    15: math.tanh,
    16: math.acosh,
    17: math.asinh,
    18: math.atanh,

    19: math.exp,
    20: math.log,
    21: math.log2,
    22: math.log10,
    23: math.degrees,
    24: math.radians,

    25: numfunc(math.floor, lambda x: x.real),
    26: numfunc(math.ceil,  lambda x: x.imag),
    27: round,
    28: lambda x: complex(*x[:2]),
    29: numfunc(lambda x: (x > 0) - (x < 0), lambda x: x.real - x.imag * 1j)

}

math_funcs2 = {

     0: math.gcd,
     1: math.atan2,
     2: math.hypot,
     3: math.log,
     4: round,
     5: lambda x, y: x*y // math.gcd(x, y),
     6: complex,
     7: lambda x, y: math.factorial(x) / (math.factorial(x - y) * math.factorial(y)),
     8: lambda x, y: math.factorial(x) /  math.factorial(x - y),

}

string_funcs = {

     0: str.upper,
     1: str.lower,
     2: str.title,
     3: str.splitlines,
     4: str.strip,
     5: str.swapcase,

}

commands = {

    '✸' :(0, lambda code: None, 'Create an entry point'),
    '#' :(0, lambda code: None, 'Conditionally exit'),
    '.' :(0, lambda code: None, 'Do nothing'),
    '@' :(0, lambda code: None, 'Exit'),
    '"' :(0, lambda code: None, 'Delimit a string'),
    "'" :(0, lambda code: None, 'Delimit a char array'),
    '\n':(0, lambda code: None, 'Separate lines'),

    '→': (0,
          lambda code: code.set_delta((1, 0, 0)),
          'Set direction to east',
    ),

    '←': (0,
          lambda code: code.set_delta((-1, 0, 0)),
          'Set direction to west',
    ),

    '↓': (0,
          lambda code: code.set_delta((0, 1, 0)),
          'Set direction to south',
    ),

    '↑': (0,
          lambda code: code.set_delta((0, -1, 0)),
          'Set direction to north',
    ),

    '↖': (0,
          lambda code: code.set_delta((-1, -1, 0)),
          'Set direction to north-west',
    ),

    '↗': (0,
          lambda code: code.set_delta((1, -1, 0)),
          'Set direction to north-east',
    ),

    '↘': (0,
          lambda code: code.set_delta((1, 1, 0)),
          'Set direction to south-east',
    ),

    '↙': (0,
          lambda code: code.set_delta((-1, 1, 0)),
          'Set direction to south-west',
    ),

    '⇑': (0,
          lambda code: code.set_delta((0, 0, -1)),
          'Set direction to up',
    ),

    '£': (2,
          lambda code, x, y: string_funcs[x](y),
          'String functions',
    ),

    '⇓': (0,
          lambda code: code.set_delta((0, 0, 1)),
          'Set direction to down',
    ),

    '↕': (0,
          lambda code: code.mirror('↕'),
          'Reflect IPs travelling north/south',
    ),

    '↔': (0,
          lambda code: code.mirror('↔'),
          'Reflect IPs travelling east/west',
    ),

    '∕': (0,
          lambda code: code.mirror('∕'),
          'Mirror the IP at right angles',
    ),

    '∖': (0,
          lambda code: code.mirror('∖'),
          'Mirror the IP at right angles',
    ),

    '↥': (1,
          lambda code, x: code.set_delta((0, 0, -bool(x))),
          'Conditionally travel up',
    ),

    '↧': (1,
          lambda code, x: code.set_delta((0, 0, bool(x))),
          'Conditionally travel down',
    ),

    '≤': (2,
          lambda code, x, y: x <= y,
          'x ≤ y',
    ),

    '≥': (2,
          lambda code, x, y: x >= y,
          'x ≥ y',
    ),

    '¦': (2,
          lambda code, x, y: abs(x - y),
          '|x - y|',
    ),

    '§': (0,
          lambda code: code.stack.sort(),
          'stack',
          'Sort the stack',
    ),

    '°': (0,
          lambda code: code.set_delta((random.randint(-code.size, code.size),
                                       random.randint(-code.size, code.size),
                                       random.randint(-code.size, code.size))),
          'Travel in a random direction',
    ),

    '±': (2,
          lambda code, x, y: (x+y, x-y),
          'splat',
          'Push x+y and x-y',
    ),

    'Þ': (1,
          lambda code, x: list(filter(None, x)),
          'Remove falsy values from x',
    ),

    'þ': (1,
          lambda code, x: list(filter(operator.not_, x)),
          'Remove truthy values from x',
    ),

    'ß': (0,
          lambda code: code.go_to((random.randint(-code.size, code.size),
                                   random.randint(-code.size, code.size),
                                   random.randint(-code.size, code.size))),
          'Go to a random position',
    ),

    '⍶': (3,
          lambda code, x, y, z: (x, z, y),
          'splat',
          'Rotate top three elements right',
    ),

    '⍷': (2,
          lambda code, x, y: x in y,
          'Is x in y?',
    ),

    '⍸': (1,
          lambda code, x: list(range(int(x))),
          'Range from 1 to x',
    ),

    '⍹': (3,
          lambda code, x, y, z: (y, x, z),
          'splat',
          'Rotate top three elements left',
    ),

    ' ': (0,
          lambda code: code.mirror(' '),
          'Act as a hole',
    ),

    '!': (1,
          lambda code, x: math.gamma(x+1),
          'Factorial/gamma function',
    ),
    
    '$': (1,
          lambda code, x: code.move('$', x),
          'Skip the next command',
    ),

    '%': (2,
          lambda code, x, y: x % y,
          'Modulo',
    ),

    '&': (2,
          lambda code, x, y: x & y,
          'Bitwise AND',
    ),

    '(': (1,
          lambda code, x: x - 1,
          'Decrement',
    ),

    ')': (1,
          lambda code, x: x + 1,
          'Increment',
    ),

    '*': (2,
          lambda code, x, y: x ** y,
          'Power/exponentiation',
    ),

    '+': (2,
          lambda code, x, y: x + y,
          'x + y',
    ),

    ',': (0,
          lambda code: setattr(code, 'map_over', 0),
          'Turn off vectorising commands',
    ),

    '-': (2,
          lambda code, x, y: x - y,
          'x - y',
    ),

    '/': (0,
          lambda code: code.mirror('/'),
          'Reflect the IP at a 45° angle',
    ),

    '0': (1,
          lambda code, x: 10 * x + 0,
          'Concantenate a 0 to x',
    ),

    '1': (1,
          lambda code, x: 10 * x + 1,
          'Concantenate a 1 to x',
    ),

    '2': (1,
          lambda code, x: 10 * x + 2,
          'Concantenate a 2 to x',
    ),

    '3': (1,
          lambda code, x: 10 * x + 3,
          'Concantenate a 3 to x',
    ),

    '4': (1,
          lambda code, x: 10 * x + 4,
          'Concantenate a 4 to x',
    ),

    '5': (1,
          lambda code, x: 10 * x + 5,
          'Concantenate a 5 to x',
    ),

    '6': (1,
          lambda code, x: 10 * x + 6,
          'Concantenate a 6 to x',
    ),

    '7': (1,
          lambda code, x: 10 * x + 7,
          'Concantenate a 7 to x',
    ),

    '8': (1,
          lambda code, x: 10 * x + 8,
          'Concantenate a 8 to x',
    ),

    '9': (1,
          lambda code, x: 10 * x + 9,
          'Concantenate a 9 to x',
    ),

    ':': (2,
          lambda code, x, y: x // y,
          'Integer division',
    ),

    ';': (1,
          lambda code, x: code.move(';', x),
          'Conditionally reverse direction',
    ),

    '<': (2,
          lambda code, x, y: x < y,
          'x < y',
    ),

    '=': (2,
          lambda code, x, y: x == y,
          'Are x and y equal?',
    ),

    '>': (2,
          lambda code, x, y: x > y,
          'x > y',
    ),

    '?': (1,
          lambda code, x: bool(x),
          'Is x truthy?',
    ),

    'A': (0,
          lambda code: list(code.inputs),
          'splat',
          'Push command line arguments',
    ),

    'B': (2,
          lambda code, x, y: unbase(x, y or 10),
          'Convert from base',
    ),

    'C': (2,
          lambda code, x, y: (x[:y], x[y:]),
          'splat',
          'Split into two parts to stack',
    ),

    'D': (1,
          lambda code, x: x[1:],
          'Deque',
    ),
    
    'E': (1,
          lambda code, x: all(elem == x[0] for elem in x),
          'All equal',
    ),
    
    'F': (1,
          lambda code, x: x[:-1],
          'Pop',
    ),

    'G': (2,
          lambda code, x, y: code.get(x, y, code.ip[2]),
          'Get character at (x, y) on this level',
    ),

    'H': (2,
          lambda code, x, y: list(range(*sorted((x, y)))),
          'Range from x to y',
    ),

    'I': (0,
          lambda code: allinput,
          'splat',
          'Push all of STDIN',
    ),

    'J': (3,
          lambda code, x, y, z: code.set_delta((x, y, z)),
          'Set the IP delta',
    ),

    'K': (2,
          lambda code, x, y: y if x else None,
          'Keep y if x',
    ),

    'L': (0,
          lambda code: len(code.stack.pop(number = len(code.stack))),
          'Replace the stack with its length',
    ),

    'M': (0,
          lambda code: max(code.stack.pop(number = len(code.stack))),
          'Replace the stack with its max',
    ),

    'N': (0,
          lambda code: min(code.stack.pop(number = len(code.stack))),
          'Replace the stack with its min',
    ),

    'O': (0,
          lambda code: print(code.stack),
          'Print the stack',
    ),

    'P': (0,
          lambda code: sorted(code.stack.pop(number = len(code.stack))),
          'Sort the stack',
    ),

    'Q': (0,
          lambda code: unique(code.stack.pop(number = len(code.stack))),
          'Deduplicate the stack',
    ),

    'R': (0,
          lambda code: code.stack.reverse(),
          'stack',
          'Reverse the stack',
    ),

    'S': (0,
          lambda code: sum(code.stack.pop(number = len(code.stack))),
          'Replace the stack with its sum',
    ),

    'T': (1,
          lambda code, x: x ** 0.5,
          'Square root',
    ),

    'U': (0,
          lambda code: product(code.stack.pop(number = len(code.stack))),
          'Replace the stack with its product',
    ),

    'V': (1,
          lambda code, x: eval(x),
          'Python-eval',
    ),

    'W': (2,
          lambda code, x, y: x ** (1/y),
          'Nth root',
    ),

    'X': (3,
          lambda code, x, y, z: math_funcs2[x](y, z),
          'Run a dyadic math function',
    ),

    'Y': (1,
          lambda code, x: constants[x] if 0 <= x < len(constants) else x,
          'Retrieve a constant',
    ),

    'Z': (0,
          lambda code: code.mirror('Z'),
          'Travel in a Z-shaped path',
    ),

    '[': (1,
          lambda code, x: [x],
          'Wrap',
    ),

    '\\':(0,
          lambda code: code.mirror('\\'),
          'Reflect the IP at a 45° angle',
    ),

    ']': (1,
          lambda code, x: x,
          'splat',
          'Unpack',
    ),

    '^': (2,
          lambda code, x, y: x ^ y,
          'Bitwise XOR',
    ),

    '_': (2,
          lambda code, x, y: y - x,
          'y - x',
    ),

    '`': (2,
          lambda code, x, y: (x, y),
          'splat',
          'Swap',
    ),

    'a': (0,
          lambda code: next(iter(code.inputs)),
          'Push next command line argument',
    ),

    'b': (2,
          lambda code, x, y: base(x, y or 10),
          'Convert to base',
    ),

    'c': (4,
          lambda code, x, y, z, c: code.set(x, y, z, c),
          'Set character in program cube',
    ),

    'd': (1,
          lambda code, x: (x, x),
          'splat',
          'Duplicate',
    ),

    'e': (2,
          lambda code, x, y: [x, y],
          'Pair',
    ),

    'f': (0,
          lambda code: flatten(code.stack.pop(number = len(code.stack))),
          'splat',
          'Flatten the stack',
    ),

    'g': (3,
          lambda code, x, y, z: code.get(x, y, z),
          'Get the character at (x, y, z) in program cube',
    ),

    'h': (2,
          lambda code, x, y: (x[y:], x[:y]),
          'splat',
          'Split into two parts reversed to stack',
    ),

    'i': (0,
          lambda code: eval(input()),
          'Push line of input',
    ),

    'j': (1,
          lambda code, x: code.set_delta(code.ip_delta ** x),
          'Multiply the IP delta',
    ),

    'k': (2,
          lambda code, x, y: x[y % len(x)],
          'Find the yth element of x (modular)',
    ),

    'l': (0,
          lambda code: len(code.stack),
          'Length of the stack',
    ),

    'm': (0,
          lambda code: max(code.stack),
          'Max of the stack',
    ),

    'n': (0,
          lambda code: min(code.stack),
          'Min of the stack',
    ),

    'o': (1,
          lambda code, x: print(x),
          'Print',
    ),

    'p': (0,
          lambda code: sorted(code.stack),
          'Stack sorted',
    ),

    'q': (0,
          lambda code: unique(code.stack),
          'Stack deduplicated',
    ),

    'r': (1,
          lambda code, x: None,
          'Remove top value',
    ),

    's': (0,
          lambda code: sum(code.stack),
          'Sum of the stack',
    ),

    't': (1,
          lambda code, x: (x, x, x),
          'splat',
          'Triplicate',
    ),

    'u': (0,
          lambda code: product(code.stack),
          'Stack product',
    ),

    'v': (1,
          lambda code, x: exec(x),
          'Python-exec',
    ),

    'w': (2,
          lambda code, x, y: x[::y] if y else x + x[::-1],
          'Modular index',
    ),

    'x': (2,
          lambda code, x, y: math_funcs1[x](y),
          'Run a monadic math function',
    ),

    'y': (2,
          lambda code, x, y: [x] * y,
          'Repeat',
    ),

    'z': (2,
          lambda code, x, y: list(itertools.product(x, y)),
          'Cartesian product',
    ),

    '{': (0,
          lambda code: code.set_stack_index(code.stack_index - 1),
          'Shift one stack to the left',
    ),

    '|': (2,
          lambda code, x, y: x | y,
          'Bitwise OR',
    ),

    '}': (0,
          lambda code: code.set_stack_index(code.stack_index + 1),
          'Shift one stack to the right',
    ),

    '~': (1,
          lambda code, x: ~x,
          'Bitwise NOT',
    ),

    '¡': (0,
          lambda code: code.goto_char('‽'),
          'Negative conditional jump point',
    ),

    '×': (2,
          lambda code, x, y: x * y,
          'x × y',
    ),

    'Ā': (2,
          lambda code, x, y: x and y,
          'Logical AND',
    ),
    
    'Ą': (2,
          lambda code, x, y: x or y,
          'Logical OR',
    ),

    'Ĉ': (1,
          lambda code, x: x.split(),
          'Split on whitespace',
    ),

    'Đ': (2,
          lambda code, x, y: x.split(y),
          'Split on character',
    ),

    'Ė': (1,
          lambda code, x: all(x),
          'All',
    ),

    'Ě': (1,
          lambda code, x: any(x),
          'Any',
    ),

    # ĜĤ

    'Ī': (1,
          lambda code, x: [a - b for a, b in zip(x, x[1:])],
          'Forward increments',
    ),

    'Ĵ': (2,
          lambda code, x, y: code.set_delta((x, y, 0)),
          'Set compass delta',
    ),

    'Ķ': (3,
          lambda code, x, y, z: y if x else z,
          'Keep y if x else z',
    ),

    'Ĺ': (1,
          lambda code, x: len(x),
          'Length',
    ),

    'Ł': (1,
          lambda code, x: isprime(x),
          'Prime/Gaussian prime test',
    ),

    'Ň': (1,
          lambda code, x: flatten(x),
          'Flatten',
    ),

    'Ō': (1,
          lambda code, x: chrprint(x),
          'Print char code without popping',
    ),

    'Œ': (1,
          lambda code, x: '\n'.join(x),
          'Join with newlines',
    ),

    'Ø': (1,
          lambda code, x: print(x, end = ''),
          'Print without newline',
    ),

    'Ř': (1,
          lambda code, x: x[::-1],
          'Reverse',
    ),
    
    'Š': (1,
          lambda code, x: sorted(x),
          'Sort',
    ),

    'Ť': (1,
          lambda code, x: ''.join(x),
          'Join to string',
    ),
    
    'Ŭ': (1,
          lambda code, x: unique(x),
          'Deduplicate',
    ),

    # Ů

    'Ŵ': (0,
          lambda code: code.go(),
          'Nest then execute all paused functions',
    ),

    'Ý': (1,
          lambda code, x: x[0],
          'First element',
    ),

    'Ŷ': (1,
          lambda code, x: x[-1],
          'Last element',
    ),

    'Ž': (1,
          lambda code, x: list(map(list, zip(*x))),
          'Transpose',
    ),

    '‼': (0,
          lambda code: code.go_to((code.ip[0], code.ip[1], code.ip[2] + 1)),
          'Drop down a level',
    ),

    '⁇': (0,
          lambda code: code.go_to((0, 0, 0)),
          'Go to (0, 0, 0)',
    ),

    '⁈': (0,
          lambda code: code.goto_char('⁉', replace = '⁉'),
          'Replacing jump point',
    ),

    '⁉': (0,
          lambda code: code.goto_char('⁈', replace = '⁈'),
          'Replacing jump point',
    ),

    '‽': (1,
          lambda code, x: code.goto_char('¿' if x else '¡'),
          'Conditional jump point',
    ),

    '÷': (2,
          lambda code, x, y: x / y,
          'x ÷ y',
    ),

    'ā': (0,
          lambda code: code.rerun(),
          'Rerun the last command',
    ),

    'ą': (1,
          lambda code, x: code.rerun(x),
          'Rerun the last x commands',
    ),

    'ĉ': (3,
          lambda code, x, y, z: code.set(x, y, z),
          'Clear character at (x, y, z)',
    ),

    'đ': (2,
          lambda code, x, y: list(map(list, enumerate(x, y))),
          'Enumerate from y',
    ),

    'ė': (1,
          lambda code, x: list(map(list, enumerate(x))),
          'Enumerate',
    ),

    'ě': (1,
          lambda code, x: list(map(list, enumerate(x, 1))),
          'Enumerate from 1',
    ),

    # ĝĥī

    'ĵ': (1,
          lambda code, x: code.set_delta((code.ip_delta[0] * x, code.ip_delta[1] * x, 0)),
          'Multiply compass delta',
    ),

    'ķ': (2,
          lambda code, x, y: x.find(y),
          'Index of y in x',
    ),

    'ĺ': (2,
          lambda code, x, y: x.count(y),
          'Count occurences',
    ),

    # ł

    'ň': (1,
          lambda code, x: not x,
          'Logical NOT',
    ),

    'ō': (0,
          lambda code: chrprint(code.stack.peek()),
          'Print char code without popping',
    ),

    'œ': (0,
          lambda code: print(code.stack.peek()),
          'Print without popping',
    ),

    'ø': (0,
          lambda code: print(code.stack.peek(), end = ''),
          'Print without newline',
    ),
    
    'ř': (2,
          lambda code, x, y: list(range(*sorted((x, y)))) + list(range(*sorted((x, y))[::-1], -1)) + [min(x, y)],
          'Pyramid range',
    ),

    'š': (1,
          lambda code, x: sum(x),
          'Sum',
    ),

    'ť': (2,
          lambda code, x, y: str(y).join(x),
          'Join with character',
    ),

    'ŭ': (1,
          lambda code, x: product(x),
          'Product',
    ),

    'ů': (2,
          lambda code, x, y: [a for a, b in zip(x, y) if b],
          'Filter x on y',
    ),

    'ŵ': (0,
          lambda code: code.wait(),
          'Turn on function nesting',
    ),

    # ýŷ

    'ž': (2,
          lambda code, x, y: list(map(list, zip(x, y))),
          'Interleave',
    ),

    '¿': (0,
          lambda code: code.goto_char('‽'),
          'Positive conditional jump point',
    ),

    '©': (0,
          lambda code: code.register,
          'Retrieve register value',
    ),

    '®': (1,
          lambda code, x: setattr(code, 'register', x),
          'Set register value',
    ),

    'ª': (0,
          lambda code: setattr(code, 'map_over', 1),
          'Make commands vectorise',
    ),

    'º': (0,
          lambda code: setattr(code, 'map_over', 2),
          'Make commands vectorise',
    ),

    '⁰': (2,
          lambda code, x, y: 10 * x + y,
          '10x + y',
    ),

    '¹': (1,
          lambda code, x: 10 * x - 1,
          '10x - 1',
    ),

    '²': (1,
          lambda code, x: 10 * x - 2,
          '10x - 2',
    ),

    '³': (1,
          lambda code, x: 10 * x - 3,
          '10x - 3',
    ),

    '⁴': (1,
          lambda code, x: 10 * x - 4,
          '10x - 4',
    ),

    '⁵': (1,
          lambda code, x: 10 * x - 5,
          '10x - 5',
    ),

    '⁶': (1,
          lambda code, x: 10 * x - 6,
          '10x - 6',
    ),

    '⁷': (1,
          lambda code, x: 10 * x - 7,
          '10x - 7',
    ),

    '⁸': (1,
          lambda code, x: 10 * x - 8,
          '10x - 8',
    ),

    '⁹': (1,
          lambda code, x: 10 * x - 9,
          '10x - 9',
    ),

    '‘': (0,
          lambda code: code.go_to((0, code.ip[1], code.ip[2])),
          'Go to western edge of row',
    ),

    '’': (0,
          lambda code: code.go_to((0, 0, code.ip[2] + 1)),
          'Go to (0, 0) of level below',
    ),

    '‚': (0,
          lambda code: code.go_to((0, code.ip[1] + 1, code.ip[2])),
          'Go to west edge of row',
    ),

    '‛': (0,
          lambda code: code.go_to((0, code.ip[1] + 1, code.ip[2] + 1)),
          'Drop down diagonally by one',
    ),

    '‹': (1,
          lambda code, x: min(x),
          'Minimum',
    ),

    '›': (1,
          lambda code, x: max(x),
          'Maximum',
    ),

    '₀': (0,
          lambda code: 0,
          'Push 0',
    ),

    '₁': (0,
          lambda code: 1,
          'Push 1',
    ),

    '₂': (0,
          lambda code: 2,
          'Push 2',
    ),

    '₃': (0,
          lambda code: 3,
          'Push 3',
    ),

    '₄': (0,
          lambda code: 4,
          'Push 4',
    ),

    '₅': (0,
          lambda code: 5,
          'Push 5',
    ),

    '₆': (0,
          lambda code: 6,
          'Push 6',
    ),

    '₇': (0,
          lambda code: 7,
          'Push 7',
    ),

    '₈': (0,
          lambda code: 8,
          'Push 8',
    ),

    '₉': (0,
          lambda code: 9,
          'Push 9',
    ),

    # “”„‟

    '«': (2,
          lambda code, x, y: min(x, y),
          'Minimum of x and y',
    ),

    '»': (2,
          lambda code, x, y: max(x, y),
          'Minimum of x and y',
    ),

    # αβγ

    'δ': (2,
          lambda code, x, y: x != y,
          'Unequal',
    ),

    # εζη

    'θ': (1,
          lambda code, x: code.rotate_ip(x, 'xy'),
          'Rotate the IP in the horizontal plane',
    ),

    # ικλμνξοπ

    'ρ': (1,
          lambda code, x: code.rotate_ip(x, 'z'),
          'Rotate the IP out of the horizontal plane',
    ),

    # ςστυφχψωΔΘΛ

    'Ξ': (3,
          lambda code, x, y, z: x == (y % z),
          'Congruent mod z',
    ),

    # ΣΨΩ

}

# print(len(code_page) - len(commands))

# 41 unused characters

product = lambda a: functools.reduce(operator.mul, a)

def flatten(array):
    ret = []
    for elem in array:
        if isinstance(elem, list):
            ret += flatten(elem)
        else:
            ret.append(elem)
    return ret

def unique(array):
    ret = []
    for elem in array:
        if elem not in ret:
            ret.append(elem)
    return ret

def iterable(value):
    if not hasattr(value, '__iter__'):
        return [value]
    return list(value)

def base(base, integer):
    digits = []
    while integer:
        integer, digit = divmod(integer, base)
        digits.append(digit)
    return digits[::-1]

def unbase(digits, base):
    if isinstance(base, list):
        digits, base = base, digits
    total = 0
    power = 0
    while digits:
        total += digits.pop() * base ** power
        power += 1
    return total

def chrprint(arg):
    try: arg = chr(arg)
    except: pass
    print(arg, end = '')

def isprime(arg):
    if isinstance(arg, complex):
        a, b = int(arg.real), int(arg.imag)
        if   a == 0: return b % 4 == 3 and is_prime(b)
        elif b == 0: return a % 4 == 3 and is_prime(a)
        else: return is_prime(a ** 2 + b ** 2)
        
    else:
        for i in range(1, int(arg ** 0.5) + 1):
            if arg % i == 0:
                return False
        return True

class Tuple(tuple):
    def __pow__(self, integer):
        return tuple(map(lambda a: a * integer, self))

class Stack(list):
    def push(self, *values):
        for v in values:
            if v in [True, False]:
                v = int(v)
        
            if hasattr(v, '__iter__') and all(x in [True, False] for x in v):
                v = list(map(int, v))

            if v is None:
                return
        
            try: self.append(v.replace("'",'"'))
            except: self.append(v)
        
    def pop(self, index = -1, number = 1):
        ret = []
        for _ in range(number):
            try: ret.append(super().pop(index))
            except: ret.append(0)
        return ret

    def peek(self, index = -1):
        try: return self[index]
        except: return 0

    def reverse(self):
        elems = self.pop(number = len(self))
        self.push(*elems)
        return None

    def __str__(self):
        elements = self.copy()
        out = '['
        for element in elements:
            if hasattr(element, '__iter__') and type(element) != str:
                out += str(Stack(element)) + ' '
            else:
                out += repr(element) + ' '
        return out.strip() + ']'

class Code:
    def __init__(self, inputs, *levels):
        self.levels = []
        for level in levels:
            level = list(map(list, level.splitlines()))
            self.levels.append(level)
            
        self.size = len(self.levels)
        self.stacks = [Stack() for _ in range(self.size)]
        self.stack_index = 0
        self.cmd_stack = Stack()
        self.commands = []
        
        self.ip = (0, 0, 0)
        self.ip_delta = (1, 0, 0)
        
        self.string = False
        self.chars = False
        self.map_over = False
        self.debug = False
        self.quit = False
        self.waiting = False
        
        self.inputs = inputs
        self.register = 0
        
        self.iter = iter(self.levels) 

    def __repr__(self):
        lvls = []
        for level in self.levels:
            lvls.append(list(map(''.join, level)))

        out = []
        for new in zip(*lvls):
            out.append(' | '.join(new))
            
        return 'Code(\n  ' + '\n  '.join(out) + '\n)'

    def __iter__(self):
        yield next(self.iter)

    @property
    def stack(self):
        return self.stacks[self.stack_index]

    def set_stack_index(self, value):
        self.stack_index = value

    def set_stack(self, array):
        self.stacks[self.stack_index] = Stack(array)

    def wait(self):
        self.waiting = True

    def go(self):
        to_run = list(self.cmd_stack)
        self.cmd_stack = Stack()
        self.waiting = False

        ret = run_cmd(to_run.pop(), attrdict = True)
        while to_run:
            self.stack.push(ret)
            ret = run_cmd(to_run.pop(), attrdict = True)

        return ret

    def rerun(self, number = 1):
        cmds = self.commands[:-1][:number]
        for cmd in cmds:
            self.run_cmd(*cmd)

    def get(self, x = None, y = None, z = None):
        if x is y is z is None:
            x, y, z = self.ip
        x %= self.size; y %= self.size; z %= self.size
        return self.levels[z][y][x]

    def set(self, x = None, y = None, z = None, char = '.'):
        if x is y is z is None:
            x, y, z = self.ip
        x %= self.size; y %= self.size; z %= self.size
        
        if isinstance(char, int):
            if self.encoding == 'utf':
                char = chr(char)
            if self.encoding == 'levels':
                char = code_page[char % 256]
            
        char = str(char)[0]
        self.levels[z][y][x] = char
        return None

    def running(self, char):
        if self.quit:
            return False
        
        if char == '@':
            if self.string: return True
            return False
        
        if char == '#':
            if self.string: return True
            return bool(self.stack.pop()[0])
        
        return True

    def move(self, *options):
        ip = list(self.ip)
        if not options:
            delta = list(self.ip_delta)
        else:
            if options[0] == '$':
                if options[1]:
                    delta = self.ip_delta
                    self.ip_delta = Tuple(delta) ** 2
                    self.move()
                    self.ip_delta = delta
                else:
                    delta = list(self.ip_delta)

            if options[0] == ';':
                if options[1]:
                    self.ip_delta = self.ip_delta ** -1

            return None
    
        ip = [ip[i] + delta[i] for i in range(3)]

        if not (0 <= ip[0] < self.size):
            ip[2] += 1
            if delta[0] > 0: ip[0] = 0
            else: ip[0] = self.size - 1

        if not (0 <= ip[1] < self.size):
            ip[2] += 1
            if delta[1] > 0: ip[1] = 0
            else: ip[1] = self.size - 1

        if not (0 <= ip[2] < self.size):
            if ip[2] >= self.size: ip[2] = 0
            if ip[2] < 0: ip[2] = self.size - 1
        
        self.ip = Tuple(ip)
        self.ip_delta = Tuple(delta)

    def set_delta(self, delta):
        self.ip_delta = Tuple(delta)
        return None

    def go_to(self, ip, offset = 1):
        new_ip = []
        for index, elem in enumerate(ip):
            new_ip.append(elem - (self.ip_delta[index] * offset))
        self.ip = Tuple(new_ip)
        return None

    def goto_char(self, char = '✸', offset = 0, replace = False):
        for z, lvl in enumerate(self.levels):
            for y, row in enumerate(lvl):
                for x, cell in enumerate(row):
                    if cell == char:
                        char = None
                        self.go_to((x, y, z), offset)
        if replace:
            self.set(x, y, z, replace)
        return None

    def mirror(self, option):
        delta = [self.ip_delta[0], self.ip_delta[1]]
        if option == '/':
            if delta[0] == 0:
                mult = delta[1]
                delta = [mult, mult]
            elif delta[1] == 0:
                mult = delta[0]
                delta = [-mult, -mult]
            else:
                sgn_x = math.copysign(1, delta[0])
                sgn_y = math.copysign(1, delta[1])
                if sgn_x == sgn_y:
                    mult = self.ip_delta[0]
                    delta = [-mult, 0]

        if option == '\\':
            if delta[0] == 0:
                mult = delta[1]
                delta = [mult, -mult]
            elif delta[1] == 0:
                mult = delta[0]
                delta = [-mult, mult]
            else:
                sgn_x = math.copysign(1, delta[0])
                sgn_y = math.copysign(1, delta[1])
                if sgn_x == sgn_y:
                    mult = self.ip_delta[0]
                    delta = [-mult, 0]

        if option == '↕':
            if delta[1] != 0:
                delta[1] = -delta[1]

        if option == '↔':
            if delta[0] != 0:
                delta[0] = -delta[0]

        if option == '∕':
            if all(delta):
                delta = delta ** -1
            else:
                delta = [-delta[1], delta[0]]

        if option == '∖':
            if all(delta):
                delta = delta ** -1
            else:
                delta = delta[::-1]

        if option == 'Z':
            if delta[0] and not delta[1]:
                if delta[0] > 0:
                    self.go_to((self.ip[0] - 2, self.ip[1] + 1, self.ip[2]))
                else:
                    self.go_to((self.ip[0] + 2, self.ip[1] - 1, self.ip[2]))
                
            if not delta[0] and delta[1]:
                if delta[1] > 0:
                    self.go_to((self.ip[0] - 1, self.ip[1], self.ip[2]))
                else:
                    self.go_to((self.ip[0] + 1, self.ip[1], self.ip[2]))

        if option == ' ':
            if self.ip[2] == self.size - 1:
                self.quit = True
            else:   
                self.go_to((self.ip[0], self.ip[1], self.ip[2] + 1))
                
        self.set_delta(delta + [0])
        return None

    def run_cmd(self, char, attrdict = False):
        if self.debug:
            print(char, self.ip, self.ip_delta, self.stack, self.stacks, end = ' ', file = sys.stderr)

        self.commands.append((char, attrdict))
            
        if char == '"':
            self.string = not self.string
            if self.string: self.stack.push('"')
            else: self.stack.push(self.stack.pop()[0][1:])
            return None

        if self.string:
            string = self.stack.pop()[0]
            self.stack.push(string + char)
            return None

        if char == "'":
            self.chars = not self.chars
            return None

        if self.chars:
            self.stack.push(char)
            return None

        if char not in commands.keys():
            print('Unknown command:', char, file = sys.stderr)
            return None

        if self.waiting:
            self.cmd_stack.push(commands[char])
            return None

        if attrdict:
            arity, func, *options, description = char
        else:
            arity, func, *options, description = commands[char]
            
        if options: option = options[0]
        else: option = None

        if self.debug:
            print(description, file = sys.stderr)
            
        args = self.stack.pop(number = arity)
        
        if self.map_over and args:
            args = list(map(iterable, args))
            ret = []
            for index in range(min(map(len, args))):
                nargs = []
                for arg in args:
                    nargs.append(arg[index])
                ret.append(func(self, *nargs))
            ret += sorted(args, key = len)[-1][index+1:]
            
        else:
            ret = func(self, *args)

        if ret is not None:
            if option == 'splat':
                self.stacks[self.stack_index].push(*ret)
            if option is None:
                self.stacks[self.stack_index].push(ret)
        
def execlevels(code, argv, debug, limit, explicit):
    code.goto_char()
    code.debug = debug
    active_char = code.get()
    count = 0
    path = ''
    if not explicit:
        code.stack.push(*argv)
    
    try:
        while count < limit:
            path += active_char
            count += 1
            try: code.run_cmd(active_char)
            except Exception as e: print(e, file = sys.stderr)
            code.move()
            if code.running(active_char):
                active_char = code.get()
                continue
            break
    except:
        pass
    
    return path

def level_sort(files):
    if not any(re.search(r'lv\d+', file.split('.')[1])for file in files):
        return files
    
    sort = [None] * len(files)
    
    for index, file in enumerate(files):
        end = file.split('.')[1]
        if re.search(r'lv\d+', end):
            index = int(re.findall(r'lv(\d+)', end)[0]) - 1
            
        if sort[index] is None:
            sort[index] = file
        else:
            index = min([i for i, v in enumerate(sort) if v is None])
            sort[index] = file

    return sort

def read_file(filename, encoding = 'utf'):
    if encoding == 'utf':
        return open(filename, mode = 'r', encoding = 'utf').read()

    with open(filename, 'rb') as file:
        x = list(file.read())
        
    string = ''
    for c in x:
        string += code_page[c]
    return string

def eval_(arg):
    try: return eval(arg)
    except: return arg

def pad(string, length):
    lines = string.splitlines()
    for i, line in enumerate(lines):
        lines[i] = line.ljust(length, '.')
    return '\n'.join(lines + (['.' * length] * (length - len(lines))))

def inter(settings):
    levels = []
    for lvlnum in range((settings.empty or settings.cube) or settings.size):
        lvl = []
        print('Enter level {}:'.format(lvlnum + 1))
        for _ in range(settings.size):
            lvl.append(input('>> '))
        lvl = list(filter(None, lvl))
        levels.append('\n'.join(lvl))

    inputs = []
    print('\nEnter inputs:')
    while True:
        inputted = eval_(input('> '))
        if not bool(inputted):
            break
        inputs.append(inputted)

    settings.interactive = False
    settings.cmd = True
    settings.progs_input = levels + inputs

    print()
    main(settings)

def main(settings):
    size = settings.size
    debug = settings.debug

    if settings.interactive:
        inter(settings)
        exit(0)

    if settings.utf:
        enc = 'utf'
    if settings.levels:
        enc = 'levels'

    if settings.cube and not settings.strict:
        levels = settings.progs_input[:1] * size
        if settings.file:
            levels = list(map(read_file, level_sort(levels), itertools.cycle([enc])))
            pres = levels.copy()
        inputs = list(map(eval_, settings.progs_input[1:]))

    elif settings.empty and not settings.strict:
        levels = settings.progs_input[:1]
        if settings.file:
            levels = list(map(read_file, level_sort(levels), itertools.cycle([enc])))
            pres = levels.copy()
        levels += [(('.' * size + '\n') * size)[:-1]] * (size - 1)
        inputs = list(map(eval_, settings.progs_input[1:]))

    else:
        levels = settings.progs_input[:size]
        inputs = list(map(eval_, settings.progs_input[size:]))
        if settings.file:
            levels = list(map(read_file, level_sort(levels), itertools.cycle([enc])))
        if settings.tio:
            levels[0] = open(levels[0]).read()
        pres = levels.copy()

    if settings.strict:
        compare = lambda x, y: x != y
    else:
        compare = lambda x, y: x > y

    conds = [len(levels) >= size, True, True]
    for i, lvl in enumerate(levels):
        if compare(len(lvl.splitlines()), size):
            conds[1] = False
        for line in lvl.splitlines():
            if compare(len(line), size):
                conds[2] = False
    if not all(conds):
        print('SizeError: Code must be in the shape of a cube size {}'.format(size), file = sys.stderr)
        exit(1)

    if settings.out is None:
        out = 1
    elif settings.out == 'all':
        out = -1
    else:
        out = int(settings.out)
    if settings.explicit:
        out = 0

    if settings.strict:
        levels = Code(inputs, *levels)
    else:
        levels = Code(inputs, *map(pad, levels, itertools.cycle([size])))
        
    if settings.start:
        levels.ip = Tuple(settings.start)
    if settings.delta:
        levels.ip_delta = Tuple(settings.delta)
    levels.encoding = enc

    code_path = execlevels(levels, inputs, debug, settings.limit, settings.explicit)
    if out == -1: output = levels.stack.pop(number = len(levels.stack))
    else: output = levels.stack.pop(number = out)

    if out:
        print(*output, sep = '\n')

    print('\nNamespace(', file = sys.stderr)
    for attr, val in settings._get_kwargs():
        if attr != 'progs_input':
            print('  {:12} = {}'.format(attr, val), file = sys.stderr)
    print(')\n', file = sys.stderr)

    print(levels, file = sys.stderr)
    
    print('\nCode executed: {}\n'.format(code_path.replace('\n', '␤')), file = sys.stderr)

    if settings.hexdump:
        dump = []
            
        for i, lvl in enumerate(pres, 1):
            dumpstr = 'Level {}:'.format(i)
            lvl = list(lvl)
            num = 0
            
            while lvl:
                dumpstr += '\n'
                chars, lvl = lvl[:16], lvl[16:]
                num += 10
                line = list(map(lambda a: hex(code_page.index(a))[2:].zfill(2), chars))
                
                while len(line) < 16: line.append('  ')
                line = ' '.join(line)

                dots = []
                for char in chars:
                    if 32 <= ord(char) <= 127: dots.append(char)
                    else: dots.append('.')

                dumpstr += str(num).zfill(4) + '  '
                dumpstr += line + '  '
                dumpstr += ''.join(dots).ljust(min(16, len(chars)), '.')
                dump.append(dumpstr)
        print('\n'.join(dump), file = sys.stderr)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(prog = './levels')

    parser.add_argument('--size', help = 'Specify size of program cube', required = True, metavar = 'SIZE', type = int)
    parser.add_argument('--limit', help = 'Limit the number of commands to be run', metavar = 'LIMIT', type = int, default = 1000000)

    getcode = parser.add_mutually_exclusive_group(required = True)
    getcode.add_argument('-f', '--file', help = 'Read each level from a .lv file', action = 'store_true')
    getcode.add_argument('-c', '--cmd', help = 'Read each level from the command line', action = 'store_true')
    getcode.add_argument('-t', '--tio', help = 'Enter TIO mode for code entry', action = 'store_true')
    getcode.add_argument('-i', '--interactive', help = 'Run a Levels program in an interactive window', action = 'store_true')

    getencoding = parser.add_mutually_exclusive_group(required = True)
    getencoding.add_argument('-u', '--utf', help = 'Read each file as a UTF file', action = 'store_true')
    getencoding.add_argument('-l', '--levels', help = 'Read each file in the Levels codepage', action = 'store_true')

    padcode = parser.add_mutually_exclusive_group()
    padcode.add_argument('-r', '--strict', help = 'Disable autopadding', action = 'store_true')
    padcode.add_argument('-b', '--cube', help = 'Take a single file and repeat into a cube', action = 'store_true')
    padcode.add_argument('-e', '--empty', help = 'Take a single file and append empty levels to form a cube', action = 'store_true')

    parser.add_argument('-x', '--explicit', help = 'Turn off implicit input/output', action = 'store_true')
    parser.add_argument('-d', '--debug', help = 'Output debug information to STDERR after each command', action = 'store_true')
    parser.add_argument('-s', '--start', help = 'Set specific start point', nargs = 3, type = int)
    parser.add_argument('-j', '--delta', help = 'Set specific IP delta', nargs = 3, type = int)
    parser.add_argument('-o', '--out', help = 'Output a specified number of elements at end')
    parser.add_argument('-xxd', '--hexdump', help = 'Output a hexdump after execution', action = 'store_true')

    parser.add_argument('progs_input', nargs = '*')

    main(parser.parse_args())
