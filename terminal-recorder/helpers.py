"""
helpers.py

Utility classes and helper functions
"""
from dataclasses import dataclass, field
from subprocess import Popen, PIPE, TimeoutExpired
from shutil import which
from time import sleep
from os import path, X_OK, linesep as LINE_SEPERATOR


@dataclass
class Command:
    """A command is something entered on the command line
    and a list of lines entered on stdin

    Attributes:
        command: to be entered on command line on execution
        stdin_input: list of lines entered on stdin
        stdout_byte_sizes: list of the amount of bytes of stdout output
                           preceding each line of stdin input
    """

    command: str = ""
    stdin_input: list[str] = field(default_factory=list)
    stdout_byte_sizes: None | list[int] = None

    def get_process(self) -> Popen:
        """Start a shell process using command.

        Returns:
            Popen object representing shell process.
        """
        return Popen(
            self.command,
            stdin=PIPE,
            stdout=PIPE,
            stderr=PIPE,
            encoding="utf8",
            shell=True,
            text=True,
        )

    def get_stdout_byte_sizes(self) -> list[int]:
        """Get the size of stdout output before each line of stdin input

        The byte size is retrieved by running the command multiple times
        and providing an extra line on each successive run.

        Assumes that command output size is constant for certain input.

        Returns:
            list of byte sizes preceding each line of stdin input.
        """
        if self.stdout_byte_sizes is not None:
            return self.stdout_byte_sizes.copy()
        stdout_data, stdin_data = "", None
        lengths = []

        timeouts = [1, 3, 5, 10, 0.01]
        # We add to stdin_input, since we also want to input nothing (None)
        for input_line in [None] + self.stdin_input:
            if input_line is None:
                stdin_data = input_line
            elif stdin_data is None:
                stdin_data = input_line + LINE_SEPERATOR
            else:
                stdin_data += input_line + LINE_SEPERATOR

            # Very ugly loop to check whether command can be executed in reasonable time
            for i, timeout in enumerate(timeouts):
                try:
                    proc = self.get_process()
                    stdout_data, _ = proc.communicate(stdin_data, timeout=timeout)
                    # Use utf8 encoding to correctly get size in bytes
                    lengths.append(len(stdout_data) - sum(lengths))
                    break
                except TimeoutExpired:
                    # TODO: ensure proc exists
                    proc.kill()
            else:
                print_error(
                    f"Experienced timeout > 10s while waiting for '{self.command}'"
                )
                exit(1)
            # Remove timeouts that are too short
            timeouts = timeouts[i:]

        self.stdout_byte_sizes = lengths[:-1]
        return self.stdout_byte_sizes.copy()


@dataclass()
class Config:
    """A configuration defines a serie of commands to be executed.

    Attributes:
        dir: Working directory to excute commands
        commands: list of commands
    """

    dir: str = ""
    commands: list[Command] = field(default_factory=list)


def should_make_output_file(filename: str) -> bool:
    """Check if filename exists and potentially prompt user to overwrite.

    Params:
        filename: filepath to check

    Returns:
        True if file does not exists or user enters 'yes' to prompt, False otherwise.
    """
    if path.exists(filename):
        while True:
            response = input(
                f"File {filename} already exists. Overwrite? [y/n]:"
            ).lower()
            if response in ("yes", "y", "no", "n"):
                if response in ("no", "n"):
                    return False
                break
    return True


def check_dependencies_exist(programs: list[str]) -> bool:
    """Check if a list of programs is found in PATH.

    Params:
        programs: list of programs to check

    Returns:
        True if all programs are found, False otherwise.
    """
    for program in programs:
        if not which(program, mode=X_OK):
            print_error(f"'{program}' not found")
            return False
    return True


def raw_write(text: str | bytes, end: str = "", flush: bool = True) -> None:
    """Write raw message on stdout. Flushes stdout immediately by default.

    Params:
        text: message to print
        end: text to print after message
        flush: flush immediately after printing
    """
    print(text, end=end, flush=flush)


def print_with_typing(text: str, delay: float = 0.15, end: str = "") -> None:
    """Simulate typing on stdout.

    Params:
        text: message to type
        delay: seconds to sleep after writing each character of message
        end: output on stdout after writing entire message
    """
    for char in text:
        raw_write(char)
        sleep(delay)
    raw_write(end)


# --- Utility funcs for debug messages


def print_error(message: str) -> None:
    print(f"ERROR: {message}")


def print_warn(message: str) -> None:
    print(f"WARNING: {message}")


def print_info(message: str) -> None:
    print(f"INFO: {message}")
