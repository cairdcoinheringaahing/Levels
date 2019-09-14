import argparse
import itertools
import random
import sys

commands = {

}

class Stack(list):
	def push(self, *values):
		for v in values:
			if v in [True, False]:
				v = int(v)
		
		if hasattr(v, '__iter__') and all(x in [True, False]for x in v):
			v = list(map(int, v))
                
		try:
			self.append(v.replace("'",'"'))
		except:
			self.append(v)
            
	def pop(self, index = -1):
		return super().pop(index)
    
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
		return str(tuple(out))

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
		
		self.ip = tuple(ip)
		self.ip_delta = tuple(delta)

	def run_cmd(self, char):
		func, arity = commands[char]

def execlevels(code, argv, explicit, debug):
	active_char = code.get()
	while code.running(active_char):
		if debug:
			print(active_char, code.ip, code.ip_delta, code.stack, code.stacks)
		code.run_cmd(active_char)
		code.move()
		active_char = code.get()

def read_file(filename):
	char = chr(random.randrange(33, 128))
	return ((char * 3 + '\n') * 3)[:-1]
	with open(filename, 'rb') as file:
		return file.read()

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

	getcode = parser.add_mutually_exclusive_group()
	getcode.add_argument('-f', '--file', help = 'Read each level from a .lv file', action = 'store_true')
	getcode.add_argument('-c', '--cmd', help = 'Read each level from the command line', action = 'store_true')
	getcode.add_argument('-t', '--tio', help = 'Enter TIO mode for code entry', action = 'store_true')

	parser.add_argument('-u', '--utf', help = 'Read each file as a UTF file', action = 'store_true')
	parser.add_argument('-l', '--levels', help = 'Read each file in the Levels codepage', action = 'store_true')
	parser.add_argument('-b', '--cube', help = 'Take a single file and repeat into a cube', action = 'store_true')
	parser.add_argument('-e', '--empty', help = 'Take a single file and append empty levels to form a cube', action = 'store_true')
	parser.add_argument('-x', '--explicit', help = 'Turn off implicit input/output', action = 'store_true')
	parser.add_argument('-d', '--debug', help = 'Output debug information to STDERR after each command', action = 'store_true')

	parser.add_argument('progs_input', nargs = '*')

	settings = parser.parse_args()
	size = settings.size - settings.tio
	explicit = settings.explicit
	debug = settings.debug
	print(settings)

	if settings.cube:
		levels = settings.progs_input[:1] * size
		if settings.file:
			levels = list(map(read_file, levels))
		inputs = list(map(eval_, settings.progs_input[1:]))

	elif settings.empty:
		levels = settings.progs_input[:1]
		if settings.file:
			levels = list(map(read_file, levels))
		levels += [(('.' * size + '\n') * size)[:-1]] * (size - 1)
		inputs = list(map(eval_, settings.progs_input[1:]))

	else:
		levels = settings.progs_input[:size]
		inputs = list(map(eval_, settings.progs_input[size:]))
		if settings.file:
			levels = list(map(read_file, levels))
		if settings.tio:
			levels = [open('.code.tio').read()] + levels

	conds = [len(levels) >= size, True, True]
	for i, lvl in enumerate(levels):
		if len(lvl.splitlines()) > size:
			conds[1] = False
		conds[2] = not any(len(line) < size for line in lvl.splitlines())
	if not all(conds):
		print('SizeError: Code must be in the shape of a cube size {}'.format(size), file = sys.stderr)
		exit(1)

	levels = Code(*map(pad, levels, itertools.cycle([size])))
	print(levels, inputs, explicit, debug)
	execlevels(levels, inputs, explicit, debug)
