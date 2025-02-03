# Code Snippets

Om gemakkelijk en snel reviews te doen hebben we een aantal functies gemaakt.

```bash
review() {
    cd ~/nakijken/reviews # Change to your directory
    rm -rf code
    git clone $1 code
    ls -hal
    code .
}
```

## Recorder

```bash
# For consistency in the terminal videos we say they are from NexEd.

export PS1="NexEd %1~ %# ";

# Add to path
export PATH="/Users/sander/NexEd/bitrecorder:$PATH"
```
