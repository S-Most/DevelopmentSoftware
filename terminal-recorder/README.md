# Terminal Recorder

Easily record terminal commands as videos for tutorials, demonstrations, and documentation.

## Installation

### Add `record.py` to Your `$PATH`

Ensure `record.py` is accessible from your terminal by adding it to your `$PATH`.

### MacOS

Install dependencies using Homebrew:

```bash
brew install agg imagemagick gifsicle
```

### Ubuntu

Install dependencies using APT:

```bash
sudo apt update && sudo apt install -y agg ffmpeg asciinema
```

### Dependencies

Terminal Recorder requires the following dependencies:

- `Python`
- `asciinema`
- `ffmpeg`
- `agg`

## Usage

To use Terminal Recorder, define the commands you want to record in a TOML configuration file. The script supports three operation modes:

- **Run Mode**: Previews the video without recording.
- **Record Mode** (default): Executes and records the commands as specified in the configuration file.
- **Crawl Mode (WIP)**: Recursively searches a directory for configuration files and records videos for each.

## Configuration

The configuration file must be written in TOML format and can contain a single command or multiple commands. Commands should be defined using the `exec` key. If multiple commands are used, they should be listed under the `commands` key.

Each command can accept input via `stdin`, which can be defined as:

- A list where each entry represents a single input line.
- A multiline string that is split by line separators.

Additionally, you can specify a `dir` key at the top level to set the working directory for command execution.

### Example Configurations

#### Simple Command

```toml
exec = "ls"
```

#### Single Command with Multiline Input

```toml
exec = "python3 somescript.py"
input = """
First input line
Second input line
Third input line
"""
```

#### Multiple Commands Using a List

```toml
commands = [
    { exec = "ls" },
    { exec = "python3 somescript.py", input = ["First line", "Second line"] },
]
```

#### Alternative TOML Syntax for Multiple Commands

```toml
[[commands]]
exec = "ls"

[[commands]]
exec = "python3 somescript.py"
input = ["First line", "Second line"]
```

For more examples, see the `examples` directory.

## License

Terminal Recorder is licensed under the **GNU GPLv3**.
