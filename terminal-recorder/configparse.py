import tomllib
import os

from helpers import *


def parse_config(filename: str) -> tuple[bool, Config]:
    """Open filename and try to parse it as a valid Config object.

    Function prints errors as they are found.

    Params:
        filename: path to a TOML configuration file.

    Returns:
        (success, config), where:
            - success is True if configuration could be parsed without problems, False otherwise
            - config is the parsed configuration file
    """

    # ---- Start helper functions to transform config dictionary

    def check_config_dir(config: dict) -> bool:
        """Transform config to contain the working directory as an absolute path.

        Use current working directory if no directory is given.

        Function prints errors as they are found.

        Params:
            config: dictionary representing loaded TOML file

        Returns:
            False if configuration file did not contain a valid directory, True otherwise.
        """
        dir = os.getcwd()

        if "dir" in config:
            if not os.path.exists(config["dir"]):
                print_error(f"Invalid path entered: '{config['dir']}'")
                return False
            if not os.path.isdir(config["dir"]):
                print_error(f"Path must be directory: '{config['dir']}'")
                return False
            dir = config["dir"]
        config["dir"] = os.path.abspath(dir)
        return True

    def check_exec_command(config: dict) -> bool:
        """Transform config by moving possible single command to 'commands' list.

        Check if key 'exec' is in the config. If so, move to associated data
        to array under 'commands'. If keys 'exec' and 'commands' are both not
        found the config is not formatted correctly.

        Function prints errors as they are found.

        Params:
            config: dictionary representing loaded TOML file

        Returns:
            True if `exec` or `commands` was found, False otherwise
        """
        if "exec" in config:
            if "input" not in config:
                config["input"] = []
            if "commands" in config:
                print_warn(
                    "You are using both 'exec' and 'commands'. Skipping 'commands'"
                )
            config["commands"] = [{"exec": config["exec"], "input": config["input"]}]
            del config["input"]
            del config["exec"]
        elif "commands" not in config:
            print_error("Did not find 'exec' or 'commands'")
            return False
        return True

    def check_commands(config: dict) -> bool:
        """Transform config to contain Command objects.

        If key 'exec' is found, use only that command. Otherwise use array
        under 'commands'.

        Function prints errors as they are found.

        Params:
            config: dictionary representing loaded TOML file

        Returns:
            True commands could be parsed correctly, False otherwise.
        """
        if not check_exec_command(config):
            return False

        if not isinstance(config["commands"], list):
            print_error(
                f"Must pass a list to 'commands', instead passed: '{config['commands']}'"
            )
            return False

        found_error = False
        new_commands = []
        for command in config["commands"]:
            if "exec" not in command:
                print_error(
                    f"Must use 'exec' as a key in command, instead used: {command}"
                )
                found_error = True
                continue
            if "input" not in command:
                command["input"] = []

            if not isinstance(command["exec"], str):
                print_error(
                    f"Must pass a string to 'exec', instead passed {type(command['exec'])}: '{command['exec']}'"
                )
                found_error = True
                continue

            if isinstance(command["input"], str):
                command["input"] = command["input"].splitlines()
            elif not isinstance(command["input"], list):
                command["input"] = [str(command["input"])]
            command["input"] = [str(x) for x in command["input"]]

            new_commands.append(Command(command["exec"], command["input"]))

        if found_error:
            print_error("Unable to parse configuration file")
            return False

        config["commands"] = new_commands
        return True

    # --- End helper funcions

    with open(filename, mode="rb") as f:
        try:
            config = tomllib.load(f)
        except tomllib.TOMLDecodeError as e:
            print_error(f"Could not parse {filename}. Must be valid TOML.")
            print(e)
            return False, Config()

    if not check_config_dir(config):
        return False, Config()
    if not check_commands(config):
        return False, Config()

    return True, Config(dir=config["dir"], commands=config["commands"])
