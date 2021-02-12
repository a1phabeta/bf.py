#!/usr/bin/python

import collections
import logging
import sys     
import termios
import tty

from typing import Dict

def getch() -> str:
    """
    Utility function to get a single character from the user

    Returns:
        str: A single character
    """
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

class Array:
    """
    Implements the state machine model used by Brainfuck
    """
    def __init__(self) -> None:
        self.array = [0] * 30000
        self.ptr = 0

    def get_data(self) -> int:
        """
        Gets the value of the current cell

        Returns:
            int: [description]
        """
        return self.array[self.ptr]

    def set_data(self, n: int) -> None:
        """
        Sets the value of the current cell

        Args:
            n (int): The value to be used
        """
        self.array[self.ptr] = n

    def increment(self) -> None:
        """
        Increments the value of the current cell
        """
        self.array[self.ptr] += 1

        # Handling buffer overflow
        if self.array[self.ptr] > 256:
            logging.error("Buffer overflow at position %d", self.ptr)
            self.array[self.ptr] %= 256

    def decrement(self) -> None:
        """
        Decrements the value of the current cell
        """
        self.array[self.ptr] -= 1

        # Handling buffer underflow
        if self.array[self.ptr] < 0:
            logging.error("Buffer underflow at position %d", self.ptr)
            self.array[self.ptr] %= 256

    
    def right(self) -> None:
        """
        Moves the data pointer to the right by one, with automatic array expansion if needed
        """
        self.ptr += 1

        # Auto expanding array
        if self.ptr >= len(self.array):
            self.array.append(0)

    def left(self) -> None:
        """Moves the data pointer to the left by one

        Raises:
            ValueError: Called if the pointer value goes below 0
        """
        if self.ptr > 0:
            self.ptr -= 1
        else:
            raise ValueError("Segmentation Fault")

def make_brace_map(program: str) -> Dict:
    """Creates a brace map for interpreting command blocks

    Args:
        code (str): The code to be run

    Returns:
        Dict: The brace map
    """
    temp_stack = collections.deque()
    brace_map = {}

    for position, command in enumerate(program):
        if command == '[':
            temp_stack.append(position)
        if command == ']':
            start = temp_stack.popleft()
            brace_map[start] = position
            brace_map[position] = start
    return brace_map

def interpret(program: str) -> None:
    """Interprets the Brainfuck code

    Args:
        chars (str): The code to be interpreted
    """

    brace_map = make_brace_map(program)
    machine = Array()

    position = 0

    while position < len(program):
        #time.sleep(0.5)
        current_char = program[position]

        if current_char == '>':
            machine.right()
        elif current_char == '<':
            machine.left()
        elif current_char == '+':
            machine.increment()
        elif current_char == '-':
            machine.decrement()
        elif current_char == '.':
            sys.stdout.write(chr(machine.get_data()))
        elif current_char == ',':
            machine.set_data(ord(getch()))
        elif (current_char == '[' and machine.get_data() == 0):
            position = brace_map[position]
        elif (current_char == ']' and machine.get_data() != 0):
            position = brace_map[position]
        else:
            pass

        position += 1

def cleanup(code: str) -> str:
    return ''.join(filter(lambda x: x in ['.', ',', '[', ']', '<', '>', '+', '-'], code))

def execute(filename: str) -> None:
    """Reads in the Brainfuck code and passes it to the interpreter

    Args:
        filename (str): The file to read the code from
    """
    with open(filename) as f:
        interpret(cleanup(f.read()))


def main() -> None:
    if len(sys.argv) == 2:
        execute(sys.argv[1])
    else:
        print(f"Usage: {sys.argv[0]} filename")


if __name__ == "__main__":
    main()