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
αβγδεζηθικλμνΔΘΛ
ξοπρςστυφχψωΞΣΨΩ
'''

code_page = code_page.replace('\n', '').replace('␊', '\n').replace('␉', '\t')
cp = list(code_page)

commands = {

	'.':(0, lambda code: None),
	'✸':(0, lambda code: None),

	'→': (0,
		lambda code: code.set_delta((1, 0, 0))
	),

	'←': (0,
		lambda code: code.set_delta((-1, 0, 0))
	),

	'↓': (0,
		lambda code: code.set_delta((0, 1, 0))
	),

	'↑': (0,
		lambda code: code.set_delta((0, -1, 0))
	),

	'↖': (0,
		lambda code: code.set_delta((-1, -1, 0))
	),

	'↗': (0,
		lambda code: code.set_delta((1, -1, 0))
	),

	'↘': (0,
		lambda code: code.set_delta((1, 1, 0))
	),

	'↙': (0,
		lambda code: code.set_delta((-1, 1, 0))
	),

	'⇑': (0,
		lambda code: code.set_delta((0, 0, -1))
	),

	'⇓': (0,
		lambda code: code.set_delta((0, 0, 1))
	),

	'/': (0,
		lambda code: code.mirror('/')
	),

	'\\':(0,
		lambda code: code.mirror('\\')
	),

	'↕': (0,
		lambda code: code.mirror('↕')
	),

	'↔': (0,
		lambda code: code.mirror('↔')
	),

	'∕': (0,
		lambda code: code.mirror('∕')
	),

	'∖': (0,
		lambda code: code.mirror('∖')
	),

	'↥': (1,
		lambda code, x: code.set_delta((0, 0, -bool(x)))
	),

	'↧': (1,
		lambda code, x: code.set_delta((0, 0, bool(x)))
	),

	'≤': (2,
		lambda code, x, y: x <= y,
	),

	'≥': (2,
		lambda code, x, y: x >= y,
	),

	'J': (3,
		lambda code, x, y, z: code.set_delta((x, y, z))
	),

	'j': (1,
		lambda code, x: code.set_delta(code.ip_delta ** x)
	),

	'Ĵ': (2,
		lambda code, x, y: code.set_delta((x, y, 0))
	),

	'ĵ': (1,
		lambda code, x: code.set_delta((code.ip_delta[0] * x, code.ip_delta[1] * x, 0))
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
                
		try:
			self.append(v.replace("'",'"'))
		except:
			self.append(v)
            
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
	def __init__(self, *levels):
		self.levels = []
		for level in levels:
			level = list(map(list, level.splitlines()))
			self.levels.append(level)
		self.size = len(self.levels)
		self.stacks = [Stack() for _ in range(self.size)]
		self.stack_index = 0
		self.ip = (0, 0, 0)
		self.ip_delta = (1, 0, 0)

	def __repr__(self):
		out = []
		for level in self.levels:
			level = '\n'.join(map(''.join, level))
			out.append(level)
		return 'Code' + str(tuple(out))

	@property
	def stack(self):
		return self.stacks[self.stack_index]

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
			return False
		if char == '#':
			return self.stack.pop()
		return True

	def move(self):
		ip = list(self.ip)
		delta = list(self.ip_delta)
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
		return None

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
				return delta ** -1
			delta = [-delta[1], delta[0]]

		if option == '∖':
			if all(delta):
				return delta ** -1
			delta = delta[::-1]
		
		self.set_delta(delta + [0])
		return None

	def run_cmd(self, char):
		# arity, func = commands[char]
		try:
			arity, func = commands[char]
		except:
			arity, func = commands['.']
		args = self.stack.pop(number = arity)
		ret = func(self, *args)

		if ret is not None:
			self.stacks[self.stack_index].push(ret)
		return None

def execlevels(code, argv, explicit, debug):
	code.find_start()
	active_char = code.get()
	count = 0
	path = ''
	while code.running(active_char) and count < 1000:
		path += active_char
		count += 1
		code.run_cmd(active_char)
		if debug:
			print(active_char, code.ip, code.ip_delta, code.stack, code.stacks)
		code.move()
		active_char = code.get()
	if debug:
		print(active_char, code.ip, code.ip_delta, code.stack, code.stacks)
	return path + active_char

def read_file(filename, encoding = 'utf'):
	if encoding == 'utf':
		func = chr
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

if __name__ == '__main__':

	parser = argparse.ArgumentParser(prog = './levels')

	parser.add_argument('--size', help = 'Specify size of program cube', required = True, metavar = 'SIZE', type = int)

	getcode = parser.add_mutually_exclusive_group(required = True)
	getcode.add_argument('-f', '--file', help = 'Read each level from a .lv file', action = 'store_true')
	getcode.add_argument('-c', '--cmd', help = 'Read each level from the command line', action = 'store_true')
	getcode.add_argument('-t', '--tio', help = 'Enter TIO mode for code entry', action = 'store_true')

	getencoding = parser.add_mutually_exclusive_group(required = True)
	getencoding.add_argument('-u', '--utf', help = 'Read each file as a UTF file', action = 'store_true')
	getencoding.add_argument('-l', '--levels', help = 'Read each file in the Levels codepage', action = 'store_true')

	parser.add_argument('-b', '--cube', help = 'Take a single file and repeat into a cube', action = 'store_true')
	parser.add_argument('-e', '--empty', help = 'Take a single file and append empty levels to form a cube', action = 'store_true')
	parser.add_argument('-x', '--explicit', help = 'Turn off implicit input/output', action = 'store_true')
	parser.add_argument('-d', '--debug', help = 'Output debug information to STDERR after each command', action = 'store_true')
	parser.add_argument('-s', '--start', help = 'Set specific start point', nargs = 3, type = int)

	parser.add_argument('progs_input', nargs = '*')

	settings = parser.parse_args()
	size = settings.size
	explicit = settings.explicit
	debug = settings.debug
	print(settings)

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

	conds = [len(levels) >= size, True, True]
	for i, lvl in enumerate(levels):
		if len(lvl.splitlines()) > size:
			conds[1] = False
		conds[2] = not any(len(line) > size for line in lvl.splitlines())
	if not all(conds):
		print('SizeError: Code must be in the shape of a cube size {}'.format(size), file = sys.stderr)
		exit(1)

	levels = Code(*map(pad, levels, itertools.cycle([size])))
	print(levels, inputs, explicit, debug)
	if settings.start:
		levels.ip = Tuple(settings.start)

	code_path = execlevels(levels, inputs, explicit, debug)
	print('Code executed: {}'.format(code_path.replace('\n', '␤')), file = sys.stderr)
