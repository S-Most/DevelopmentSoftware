# Bash Functions for Terminal Video Generation and Conversion

This repository contains two useful Bash functions that can be added to your `.bashrc` file to simplify the process of generating a `config.toml` file and converting `.mov` videos to `.mp4` format.

## Functions

### `toml`

Generates a `config.toml` file used for terminal video generation.

#### Usage

```sh
toml
```

This command creates a `config.toml` file with predefined settings for executing a Node.js script.

#### Generated `config.toml` Example:

```toml
commands = [
    { exec = "node script.js 20 85 70" },
]
```

### `transvid`

Converts a `.mov` video file to `.mp4` format with optimized settings for NexEd and file size reduction.

#### Usage:

```sh
transvid input.mov output.mp4
```

- `input.mov`: The source video file.
- `output.mp4`: The destination file after conversion.

#### ffmpeg Settings

- Resizes the video to a width of `1280px` while maintaining the aspect ratio.
- Uses `libx264` for video compression with a CRF (Constant Rate Factor) of `23`.
- Uses `AAC` for audio encoding at `128k` bitrate.
- Applies a `medium` preset for a balance between speed and compression.

## Installation

To use these functions, add them to your `~/.bashrc` file:

```sh
# Generate an example config.toml for terminal video generation
toml() {
  cat << EOF > config.toml
commands = [
  { exec = "node script.js 20 85 70" },
]
EOF
}

# Convert .mov to .mp4 with optimized settings
transvid() {
    local inputfile="$1"
    local outputfile="$2"
    ffmpeg -i "$inputfile" -vf "scale=1280:-2" -c:v libx264 -crf 23 -preset medium -c:a aac -b:a 128k "$outputfile"
}
```

After adding the functions, apply the changes by running:

```sh
source ~/.bashrc
```

## Requirements

- `ffmpeg` must be installed for the `transvid` function to work.

  - Install on Ubuntu/Debian:

    ```sh
    sudo apt install ffmpeg
    ```

  - Install on macOS (via Homebrew):

    ```sh
    brew install ffmpeg
    ```

## License

This script is available under the MIT License.
