import argparse
import itertools
import math
import random
import sys

code_page = r'''
→←↓↑↖↗↘↙⇑␉␊⇓↕↔∕∖
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

code_page = code_page.replace('\n', '').replace('␊', '\n').replace('␉', '\t')
cp = list(code_page)

# ␉
# °ß⍶⍷⍸⍹$',;?ABCDEFGHIKLMNOPQRSTUVWXYZ[]`abcdefghiklmnopqrstuvwxyz{}¡ĀĄĈĐĖĚĜĤĪĶĹŁŇŌŒØŘŠŤŬŮŴÝŶŽ‼⁇⁈⁉‽āąĉđėěĝĥīķĺłňōœøřšťŭůŵýŷž¿©®ªº‘’‚‛“”„‟αβγδεζηθικλμνξοπρςστυφχψωΔΘΛΞΣΨΩ

commands = {

    '✸':(0, lambda code: None),
    ' ':(0, lambda code: None),
    '#':(0, lambda code: None),
    '.':(0, lambda code: None),
    '@':(0, lambda code: None),

    '→': (0,
          lambda code: code.set_delta((1, 0, 0)),
    ),

    '←': (0,
          lambda code: code.set_delta((-1, 0, 0)),
    ),

    '↓': (0,
          lambda code: code.set_delta((0, 1, 0)),
    ),

    '↑': (0,
          lambda code: code.set_delta((0, -1, 0)),
    ),

    '↖': (0,
          lambda code: code.set_delta((-1, -1, 0)),
    ),

    '↗': (0,
          lambda code: code.set_delta((1, -1, 0)),
    ),

    '↘': (0,
          lambda code: code.set_delta((1, 1, 0)),
    ),

    '↙': (0,
          lambda code: code.set_delta((-1, 1, 0)),
    ),

    '⇑': (0,
          lambda code: code.set_delta((0, 0, -1)),
    ),

    '⇓': (0,
          lambda code: code.set_delta((0, 0, 1)),
    ),

    '↕': (0,
          lambda code: code.mirror('↕'),
    ),

    '↔': (0,
          lambda code: code.mirror('↔'),
    ),

    '∕': (0,
          lambda code: code.mirror('∕'),
    ),

    '∖': (0,
          lambda code: code.mirror('∖'),
    ),

    '↥': (1,
          lambda code, x: code.set_delta((0, 0, -bool(x))),
    ),

    '↧': (1,
          lambda code, x: code.set_delta((0, 0, bool(x))),
    ),

    '≤': (2,
          lambda code, x, y: x <= y,
    ),

    '≥': (2,
          lambda code, x, y: x >= y,
    ),

    '¦': (2,
          lambda code, x, y: abs(x - y),
    ),

    '§': (0,
          lambda code: code.stack.sort(),
    ),

    '±': (2,
          lambda code, x, y: (x+y, x-y),
    ),

    'Þ': (1,
          lambda code, x: list(filter(None, x)),
    ),

    'þ': (1,
          lambda code, x: list(filter(operator.not_, x)),
    ),
    
    

    '!': (1,
          lambda code, x: math.factorial(x),
    ),

    '%': (2,
          lambda code, x, y: x % y,
    ),

    '&': (2,
          lambda code, x, y: x & y,
    ),

    '(': (1,
          lambda code, x: x - 1,
    ),

    ')': (1,
          lambda code, x: x + 1,
    ),

    '*': (2,
          lambda code, x, y: x ** y,
    ),

    '+': (2,
          lambda code, x, y: x + y,
    ),

    '-': (2,
          lambda code, x, y: x - y,
    ),

    '/': (0,
          lambda code: code.mirror('/'),
    ),

    '0': (1,
          lambda code, x: 10 * x + 0,
    ),

    '1': (1,
          lambda code, x: 10 * x + 1,
    ),

    '2': (1,
          lambda code, x: 10 * x + 2,
    ),

    '3': (1,
          lambda code, x: 10 * x + 3,
    ),

    '4': (1,
          lambda code, x: 10 * x + 4,
    ),

    '5': (1,
          lambda code, x: 10 * x + 5,
    ),

    '6': (1,
          lambda code, x: 10 * x + 6,
    ),

    '7': (1,
          lambda code, x: 10 * x + 7,
    ),

    '8': (1,
          lambda code, x: 10 * x + 8,
    ),

    '9': (1,
          lambda code, x: 10 * x + 9,
    ),

    ':': (2,
          lambda code, x, y: x // y,
    ),

    '<': (2,
          lambda code, x, y: x < y,
    ),

    '=': (2,
          lambda code, x, y: x == y,
    ),

    '>': (2,
          lambda code, x, y: x > y,
    ),

    'J': (3,
          lambda code, x, y, z: code.set_delta((x, y, z)),
    ),

    'Z': (0,
          lambda code: code.mirror('Z'),
    ),

    '\\':(0,
          lambda code: code.mirror('\\'),
    ),

    '^': (2,
          lambda code, x, y: x ^ y,
    ),

    '_': (2,
          lambda code, x, y: y - x,
    ),

    'j': (1,
          lambda code, x: code.set_delta(code.ip_delta ** x),
    ),

    '|': (2,
          lambda code, x, y: x | y,
    ),

    '~': (1,
          lambda code, x: ~x,
    ),

    '¡': (1,
          lambda code, x: code.move('¡', x),
    ),

    '×': (2,
          lambda code, x, y: x * y,
    ),

    'Ĵ': (2,
          lambda code, x, y: code.set_delta((x, y, 0)),
    ),

    '÷': (2,
          lambda code, x, y: x / y,
    ),

    'ĵ': (1,
          lambda code, x: code.set_delta((code.ip_delta[0] * x, code.ip_delta[1] * x, 0)),
    ),

    '⁰': (1,
          lambda code, x: 10 * x + 10,
    ),

    '¹': (1,
          lambda code, x: 10 * x + 11,
    ),

    '²': (1,
          lambda code, x: 10 * x + 12,
    ),

    '³': (1,
          lambda code, x: 10 * x + 13,
    ),

    '⁴': (1,
          lambda code, x: 10 * x + 14,
    ),

    '⁵': (1,
          lambda code, x: 10 * x + 15,
    ),

    '⁶': (1,
          lambda code, x: 10 * x + 16,
    ),

    '⁷': (1,
          lambda code, x: 10 * x + 17,
    ),

    '⁸': (1,
          lambda code, x: 10 * x + 18,
    ),

    '⁹': (1,
          lambda code, x: 10 * x + 19,
    ),

    '‹': (1,
          lambda code, x: min(x),
    ),

    '›': (1,
          lambda code, x: max(x),
    ),

    '₀': (0,
          lambda code: 0,
    ),

    '₁': (1,
          lambda code, x: 10 * x - 1,
    ),

    '₂': (1,
          lambda code, x: 10 * x - 2,
    ),

    '₃': (1,
          lambda code, x: 10 * x - 3,
    ),

    '₄': (1,
          lambda code, x: 10 * x - 4,
    ),

    '₅': (1,
          lambda code, x: 10 * x - 5,
    ),

    '₆': (1,
          lambda code, x: 10 * x - 6,
    ),

    '₇': (1,
          lambda code, x: 10 * x - 7,
    ),

    '₈': (1,
          lambda code, x: 10 * x - 8,
    ),

    '₉': (1,
          lambda code, x: 10 * x - 9,
    ),

    '«': (2,
          lambda code, x, y: min(x, y),
    ),

    '»': (2,
          lambda code, x, y: max(x, y),
    ),

}

def flatten(array):
    ret = []
    for elem in array:
        if isinstance(elem, list):
            ret += flatten(elem)
        else:
            ret.append(elem)
    return ret

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
        return self[index]

    def swap(self):
        self[-1], self[-2] = self[-2], self[-1]

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
        self.ip = (0, 0, 0)
        self.ip_delta = (1, 0, 0)
        self.string = self.chars = False
        self.debug = False
        self.inputs = inputs

    def __repr__(self):
        out = []
        for level in self.levels:
            level = '\n'.join(map(''.join, level))
            out.append(level)
        return 'Code' + str(tuple(out))

    @property
    def stack(self):
        return self.stacks[self.stack_index]

    def set_stack(self, array):
        self.stacks[self.stack_index] = Stack(array)

    def get(self, x = None, y = None, z = None):
        if x is y is z is None:
            x, y, z = self.ip
        x %= self.size; y %= self.size; z %= self.size
        return self.levels[z][y][x]

    def set(self, x = None, y = None, z = None, char = None):
        if x is y is z is None:
            x, y, z = self.ip
        x %= self.size; y %= self.size; z %= self.size
        if isinstance(char, int):
            char = chr(char)
        char = str(char)[0]
        self.levels[z][y][x] = char
        return None

    def running(self, char):
        if char == '@':
            return self.string
        if char == '#':
            return self.string or bool(self.stack.pop())
        return True

    def move(self, *options):
        ip = list(self.ip)
        if not options:
            delta = list(self.ip_delta)
        else:
            if options[0] == '¡':
                if options[1]:
                    delta = self.ip_delta
                    self.ip_delta = Tuple(delta) ** 2
                    self.move()
                    self.ip_delta = delta
                else:
                    delta = list(self.ip_delta)
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

    def find_start(self):
        char = '✸'
        for z, lvl in enumerate(self.levels):
            for y, row in enumerate(lvl):
                for x, cell in enumerate(row):
                    if cell == char:
                        char = None
                        self.ip = Tuple((x, y, z))
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
                    self.ip = Tuple((self.ip[0] - 2, self.ip[1] + 1, self.ip[2]))
                else:
                    self.ip = Tuple((self.ip[0] + 2, self.ip[1] - 1, self.ip[2]))
                
            if not delta[0] and delta[1]:
                if delta[1] > 0:
                    self.ip = Tuple((self.ip[0] - 1, self.ip[1], self.ip[2]))
                else:
                    self.ip = Tuple((self.ip[0] + 1, self.ip[1], self.ip[2]))
        
        self.set_delta(delta + [0])
        return None

    def run_cmd(self, char):
        if self.debug:
            print(char, self.ip, self.ip_delta, self.stack, self.stacks, file = sys.stderr)
            
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

        arity, func = commands[char]
        args = self.stack.pop(number = arity)
        ret = func(self, *args)

        if ret is not None:
            self.stacks[self.stack_index].push(ret)
        
def execlevels(code, argv, debug, limit):
    code.find_start()
    code.debug = debug
    active_char = code.get()
    count = 0
    path = ''
    for arg in argv[::-1]:
        code.stack.push(arg)
    
    while code.running(active_char) and count < limit:
        path += active_char
        count += 1
        code.run_cmd(active_char)
        code.move()
        active_char = code.get()
    
    if debug:
        print(active_char, code.ip, code.ip_delta, code.stack, code.stacks, file = sys.stderr)
    return path + active_char

def read_file(filename, encoding = 'utf'):
    if encoding == 'utf':
        return open(filename, mode = 'r', encoding = 'utf').read()
    
    if encoding == 'levels':
        func = lambda i: code_page[i]

    with open(filename, 'rb') as file:
        x = list(file.read())
        
    string = ''
    for c in x:
        string += func(c)
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

    if settings.cube:
        levels = settings.progs_input[:1] * size
        if settings.file:
            levels = list(map(read_file, levels, itertools.cycle([enc])))
        inputs = list(map(eval_, settings.progs_input[1:]))

    elif settings.empty:
        levels = settings.progs_input[:1]
        if settings.file:
            levels = list(map(read_file, levels, itertools.cycle([enc])))
        levels += [(('.' * size + '\n') * size)[:-1]] * (size - 1)
        inputs = list(map(eval_, settings.progs_input[1:]))

    else:
        levels = settings.progs_input[:size]
        inputs = list(map(eval_, settings.progs_input[size:]))
        if settings.file:
            levels = list(map(read_file, levels, itertools.cycle([enc])))
        if settings.tio:
            levels[0] = open(levels[0]).read()

    print(levels)

    conds = [len(levels) >= size, True, True]
    for i, lvl in enumerate(levels):
        if len(lvl.splitlines()) > size:
            conds[1] = False
        for line in lvl.splitlines():
            if len(line) > size:
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

    levels = Code(inputs, *map(pad, levels, itertools.cycle([size])))
    if settings.start:
        levels.ip = Tuple(settings.start)

    code_path = execlevels(levels, inputs, debug, settings.limit)
    if out == -1: output = levels.stack.pop(number = len(levels.stack))
    else: output = levels.stack.pop(number = out)

    print(*output, sep = '\n')

    print('\nNamespace(', file = sys.stderr)
    for attr, val in settings._get_kwargs():
        if attr != 'progs_input':
            print(' ', attr, '=', val, file = sys.stderr)
    print(')', file = sys.stderr)

    print('\nCode(', file = sys.stderr)
    for lvl in levels.levels:
        lvl = repr('\n'.join(map(''.join, lvl)))
        print(' ', lvl, file = sys.stderr)
    print(')', file = sys.stderr)
    
    print('\nCode executed: {}'.format(code_path.replace('\n', '␤')), file = sys.stderr)

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

    parser.add_argument('-b', '--cube', help = 'Take a single file and repeat into a cube', action = 'store_true')
    parser.add_argument('-e', '--empty', help = 'Take a single file and append empty levels to form a cube', action = 'store_true')
    parser.add_argument('-x', '--explicit', help = 'Turn off implicit input/output', action = 'store_true')
    parser.add_argument('-d', '--debug', help = 'Output debug information to STDERR after each command', action = 'store_true')
    parser.add_argument('-s', '--start', help = 'Set specific start point', nargs = 3, type = int)
    parser.add_argument('-o', '--out', help = 'Output a specified number of elements at end')

    parser.add_argument('progs_input', nargs = '*')

    main(parser.parse_args())
