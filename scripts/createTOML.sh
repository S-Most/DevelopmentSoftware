# Copy function in .bashrc

# Generate an example config.toml for the generation of terminal videos
toml() {
  cat << EOF > config.toml
commands = [
{ exec = "node script.js 20 85 70" },
]
EOF
}