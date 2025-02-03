#! /opt/homebrew/bin/python3

from collections.abc import Callable
from typing import IO
import subprocess
import tempfile
import argparse
import shutil
import pickle
import time
import os

from helpers import *
from configparse import parse_config


def type_and_run_commands(prompt: str, commands: list[Command]) -> bool:
    """Execute a list of commands: type input in a terminal and displaying output.

    Commands are considered to have executed successfully if they have returncode 0
    and no output on stderr.

    Params:
        prompt: prompt to display in terminal
        commands: list of commands to execute in terminal

    Returns:
        True if every command executed successfully, False otherwise.
    """

    no_error = True
    for command in commands:
        raw_write(prompt, end=" ")
        time.sleep(1)

        print_with_typing(command.command, end=os.linesep)
        output_byte_sizes = command.get_stdout_byte_sizes()

        try:
            proc = command.get_process()
        except subprocess.SubprocessError as e:
            print_error(f"Error creating subprocess\n{e}")
            return no_error

        assert proc.stdin, "Could not open subprocess stdin"
        assert proc.stdout, "Could not open subprocess stdout"
        assert proc.stdin.writable(), "Subprocess stdin not writable"
        assert proc.stdout.readable(), "Subprocess stdout not readable"

        # Skips for commands not providing input, since output_byte_sizes == 0
        for i, size in enumerate(output_byte_sizes):
            raw_write(proc.stdout.read(size))
            proc.stdin.write(command.stdin_input[i] + os.linesep)
            proc.stdin.flush()

            time.sleep(0.5)
            print_with_typing(command.stdin_input[i] + os.linesep)
            time.sleep(0.2)

        # Show remaining stdout output
        raw_write(proc.stdout.read())

        if proc.wait() != 0:
            no_error = False
            if proc.stderr and proc.stderr.readable():
                print(proc.stderr.read())

    raw_write(prompt, end=" ")
    time.sleep(2)
    print()
    return no_error


def execute_config(config: Config) -> bool:
    """Execute all commands in a configuration.

    Because we want to intermingle stdout and stdin, the commands must have
    predictable output. Most importantly, given certain lines of input on stdin,
    the number of bytes returned per line must remain constant.

    Params:
        config: configuration to execute

    Returns:
        True if configuration executed without problems, False otherwise
    """
    
    # TODO move these to config
    user = "NexEd"
    decorator = "\033[32m➜\033[0m"
    colored_user = f"\033[33m{user}\033[0m"
    prompt = f"{decorator} {colored_user}"

    cwd = os.getcwd()
    os.chdir(config.dir)
    result = type_and_run_commands(prompt, config.commands)
    os.chdir(cwd)
    return result


def do_run(config_filename: str, pickled=False) -> tuple[bool, Config]:
    """Run mode: type commands on stdin and print stdout output.

    The execution of this function is what is to be recorded by asciinema.

    Params:
        config_filename: either a filepath to a valid TOML configuration describing
                         commands to be run, or filepath to a pickled Config object
        pickled: True if 'config_filename' stores a pickled Config object

    Returns:
        (success, config), where:
            - success is True if configuration executed without problems, False otherwise
            - config is the parsed configuration file
    """
    if pickled:
        config = pickle.load(open(config_filename, "rb"))
    else:
        success, config = parse_config(config_filename)
        if not success:
            return False, config
    result = execute_config(config)
    return result, config


def on_record_end(
    cmd: str, working_directory: str, parsed_config_filename: str = ""
) -> Callable[[], bool]:
    """Start a process to see if run mode executes succesfully.

    Params:
        cmd: The terminal command used to record a video with asciinea
        working_directory: The working directory to switch to after recording ends
        parsed_config_filename: The (pickled) configuration file path to delete

    Returns:
        A callback function to be called when everything has been recorded and converted.
    """
    # Run to see if any errors occur when running configuration
    test_process = subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        shell=True,
    )

    def die() -> bool:
        """Callback function to call when recording ends.

        Returns:
            True if run mode executed without errors.
        """
        if parsed_config_filename and os.path.isfile(parsed_config_filename):
            os.remove(parsed_config_filename)
        test_process.wait()
        if test_process.returncode != 0:
            print_warn("Could not execute recorded comands without error.")
            os.chdir(working_directory)
            return False
        return True

    return die


def prepare_config(config_filename: str) -> tuple[bool, Config]:
    """Try to parse and execute a TOML configuration file.

    To interleave input and output in recordings we must know the size in bytes
    of stdout before each line of input on stdin. Calculating this before
    recording decreases delays in eventual recording.

    Params:
        config_filename: filepath to a valid TOML configuration describing
                         commands to be run

    Returns:
        (success, config), where:
            - success is True if configuration executed without problems, False otherwise
            - config is the prepared configuration file
    """
    success, config = parse_config(config_filename)
    if not success:
        return False, config
    working_directory = os.getcwd()
    os.chdir(config.dir)
    for cmd in config.commands:
        cmd.get_stdout_byte_sizes()
    os.chdir(working_directory)
    return True, config


def pickle_config(config: Config) -> IO:
    """Pickle and store a configuration.

    Params:
        config: Config object to pickle

    Returns:
        File object representing stored Config.
    """
    parsed_config_file = tempfile.NamedTemporaryFile(delete=False)
    pickle.dump(config, parsed_config_file)
    parsed_config_file.close()
    return parsed_config_file


def do_record(
    config_filename: str,
    output_filename: str,
    dry_run: bool = False,
    theme: str = "monokai",
    cols: int = 80,
    rows: int = 20,
    font_size: int = 20,
    dir: str | None = None,
    pickled: bool = False,
    overwrite_output: bool = True,
) -> bool:
    """Record mode: record a terminal video.

    This function spawns a subprocess of itself using run mode.
    This subprocess is recorded by asciinema.
    Afterwards, the recording is converted to a video using agg and ffmpeg.


    Params:
        config_filename: filepath to (pickled) TOML configuration
        output_filename: filename for recorded video
        dry_run: perform dry run without recording video
        theme: terminal theme (passed to agg)
        cols: terminal column width (passed to agg)
        font_size: terminal font size (passed to agg)
        dir: directory to switch to before recording
        pickled: True if config_filename is pickled Config object
        overwrite_output: don't ask before overwriting output_filename

    Returns:
       True if run mode returned True and recording and conversion
       to video succeeded, False otherwise.
    """
    if not check_dependencies_exist(["record.py", "asciinema", "agg", "ffmpeg"]):
        return False

    working_directory = os.getcwd()
    if dir and os.path.isdir(dir):
        os.chdir(dir)
    elif dir:
        print_warn(f"Could not record in '{dir}': directory not found")

    if dry_run:
        success, _ = do_run(config_filename)
        if not success:
            print_warn("Encountered error when executing commands.")
            os.chdir(working_directory)
        return success

    pickled_filename = ""
    if not pickled:
        # Pre-calculate stdout byte size array.
        # This ensures that there is little delay in the eventual recording.
        print_info("Warming up, please be patient")
        success, config = prepare_config(config_filename)
        if not success:
            print_error("Unable to prepare configuration")
            return False
        config_filename = pickle_config(config).name
        pickled_filename = config_filename
    # IDEA: use shutil.get_terminal_size for column number

    recording_subcmd = f"record.py run -c {config_filename} -p"
    die = on_record_end(recording_subcmd, working_directory, pickled_filename)

    files = [
        tempfile.NamedTemporaryFile(suffix=suffix)
        for suffix in ["", ".gif", ".mp4"]
    ]
    rec, gif, output = files
    
    # Warn: The values within scales are escaped
    ffmpeg_options = "-movflags faststart -pix_fmt yuv420p -vf scale=trunc\(iw/2\)*2:trunc\(ih/2\)*2"

    cmds = [
        f"asciinema rec -c '{recording_subcmd}' {rec.name}",
        f"agg {rec.name} {gif.name} --theme {theme} --font-size {font_size} --cols {cols} --rows {rows}",
        f"ffmpeg -y -i {gif.name} {ffmpeg_options} {output.name}"
    ]

    divide = "-" * cols
    print_info(f"Recording video\n{divide}")
    for i, cmd in enumerate(cmds):
        if i == 1:
            print(divide)
            print_info("Converting recording...")
        proc = subprocess.run(
            cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )

        if proc.returncode != 0:
            print_error(
                f"Encountered error when recording and converting. Command: '{cmds[i]}'"
            )
            die()
            return False

    if overwrite_output or should_make_output_file(output_filename):
        shutil.copy(output.name, output_filename)

    return die()


def do_crawl(
    config_filename: str,
    output_filename: str,
    dry_run: bool = False,
    theme: str = "monokai",
    cols: int = 80,
    rows: int = 20,
    font_size: int = 20,
    overwrite_output: bool = True,
) -> None:
    """Crawl mode: search directory for configuration files and execute record mode
    in each directory.

    Params:
        config_filename: filepath to (pickled) TOML configuration
        output_filename: filename for recorded video
        dry_run: perform dry run without recording videos
        theme: terminal theme (passed to agg)
        cols: terminal column width (passed to agg)
        font_size: terminal font size (passed to agg)
        overwrite_output: don't ask before overwriting output_filename
    """
    print_warn("Crawling support is experimental")
    if dry_run:
        assert False, "Dry run not implemented"

    working_directory = os.getcwd()
    if not check_dependencies_exist(["record.py"]):
        print_error("record.py not found in PATH")
        exit(1)

    search_dirs = []
    for entry, _, files in os.walk(os.getcwd()):
        if config_filename in files:
            search_dirs.append(os.path.abspath(entry))

    print_info(f"Found {len(search_dirs)} configuration files.")
    print_info(f"Warming up, please be patient")

    tasks, unparsed = [], []
    for i, dir in enumerate(search_dirs):
        os.chdir(dir)  # Must happen before parsing config
        success, config = prepare_config(os.path.join(dir, config_filename))
        if not success:
            unparsed.append(dir)
            print_warn(
                f"Could not prepare configuration: '{os.path.join(dir, config_filename)}'"
            )
            continue
        pickled_filename = pickle_config(config).name
        tasks.append((dir, pickled_filename))
        print_info(f"Processed {i+1}/{len(search_dirs)} configurations")

    good, bad = [], []
    for dir, pickled_filename in tasks:
        print_info(f"Recording in {dir}")
        result = do_record(
            config_filename=pickled_filename,
            output_filename=output_filename,
            dry_run=dry_run,
            theme=theme,
            cols=cols,
            rows=rows,
            font_size=font_size,
            dir=dir,
            pickled=True,
            overwrite_output=overwrite_output,
        )
        os.remove(pickled_filename)
        if result:
            good.append(dir)
        else:
            bad.append(dir)

    prefix = "\n  - "
    good_message = prefix + prefix.join(good)
    bad_message = prefix + prefix.join(bad)
    unparsed_message = prefix + prefix.join(unparsed)
    if len(good) > 0:
        print_info(
            f"Recorded {len(good)}/{len(tasks)} configurations with no issue {good_message}"
        )
        print()
    if len(bad) > 0:
        print_warn(
            f"Encountered errors when recording {len(bad)}/{len(tasks)} configurations {bad_message}"
        )
        print()

    if len(unparsed) > 0:
        print_warn(
            f"Could not parse {len(unparsed)} configuration file(s) {unparsed_message}"
        )
        print()
    os.chdir(working_directory)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="bit-record",
        usage="%(prog)s [mode] [options]",
        formatter_class=argparse.RawTextHelpFormatter,
        description="""
mode:
    record  Record a terminal video (default mode)
            Note that command line options override values found in
            a configuration file
    crawl   Recursively search directory for configuration files
            and record a terminal video if a configuration is found
    run     Preview the video that would be generated when recording.
""",
    )
    parser.add_argument(
        "mode",
        nargs="?",
        choices=["record", "crawl", "run"],
        default="record",
        help=argparse.SUPPRESS,
    )
    parser.add_argument(
        "-c",
        "--config",
        metavar="FILE",
        type=str,
        required=False,
        default="config.toml",
        help="Configuration file filename. (default: '%(default)s')",
    )
    parser.add_argument(
        "-d",
        "--dir",
        metavar="PATH",
        type=str,
        required=False,
        default="",
        help="""Directory where commands are executed. Overrides configuration file. (run/record mode).
Directory to recursively search for configuration files (crawl mode).
(default: '%(default)s')""",
    )
    parser.add_argument(
        "-o",
        "--output",
        metavar="FILE",
        type=str,
        required=False,
        default="output.mp4",
        help="Output video filename. (default '%(default)s')",
    )
    parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        required=False,
        default=False,
        help="Overwrite output file if it exists.",
    )
    parser.add_argument(
        "--dry",
        action="store_true",
        required=False,
        help="""Dry run: try to parse configuration file and show result (record mode).""",
    )
    # TODO: suppress asciinema/ffmpeg output except when verbose
    # parser.add_argument(
    #     "-v",
    #     "--verbose",
    #     required=False,
    #     action="count",
    #     help="""Verbosity level: use up to three times"""
    # )

    extra_opts = parser.add_argument_group(
        "extra options", description="Options to configure recorded video (record/crawl mode)"
    )
    extra_opts.add_argument(
        "--theme",
        default="monokai",
        type=str,
        required=False,
        help="Color theme. Option passed to agg. Available themes: run 'agg -h'. (default: '%(default)s')",
    )
    extra_opts.add_argument(
        "--font-size",
        metavar="SIZE",
        default=20,
        type=int,
        required=False,
        help="Font size. Option passed to agg. (default: '%(default)s')",
    )
    extra_opts.add_argument(
        "--cols",
        metavar="cols",
        default=80,
        type=int,
        required=False,
        help="Terminal column width. Option passed to agg. (default: '%(default)s')",
    )
    extra_opts.add_argument(
        "--rows",
        metavar="rows",
        default=20,
        type=int,
        required=False,
        help="Terminal column height. Option passed to agg. (default: '%(default)s')",
    )
    # Internal flags
    # Flag to indicate whether configuration file is pickled
    parser.add_argument(
        "-p", required=False, action="store_true", help=argparse.SUPPRESS
    )

    opts = parser.parse_args()
    if opts.dir and os.path.isdir(opts.dir):
        os.chdir(opts.dir)
        opts.dir = None
    elif opts.dir:
        print_error(f"{opts.dir} is not a directory")
        exit(1)

    match opts.mode:
        case "record":
            do_record(
                config_filename=opts.config,
                output_filename=opts.output,
                dry_run=opts.dry,
                theme=opts.theme,
                cols=opts.cols,
                rows=opts.rows,
                font_size=opts.font_size,
                pickled=opts.p,
                overwrite_output=True,
            )
        case "crawl":
            do_crawl(
                config_filename=opts.config,
                output_filename=opts.output,
                dry_run=opts.dry,
                theme=opts.theme,
                cols=opts.cols,
                rows=opts.rows,
                font_size=opts.font_size,
                overwrite_output=opts.yes,
            )
        case "run":
            success, _ = do_run(config_filename=opts.config, pickled=opts.p)
            if not success:
                exit(1)
        case _:
            pass
