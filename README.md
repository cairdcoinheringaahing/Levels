# Levels
A 3-dimensional programming language, where all programs are cubes.

Given the difficulty of representing a 3D cube in 2D ASCII, the program input format is rather odd, and specified on the command line when called. For example, if the program is a cube of size 3x3x3, each of the three program 'levels' are in the files `file.lv1`, `file.lv2` and `file.lv3`, and the command line arguments (`ARGV`) are `10` and `20`, then the program is run with the invocation

    python levels.py --size=3 --file --utf file.lv1 file.lv2 file.lv3 10 20

The `--size` flag is required, every other option can be swapped out for another, or removed entirely.
