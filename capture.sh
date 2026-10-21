#!/bin/bash
# Run a command and keep a copy of exactly what the terminal showed, for the video's screen captures.
# usage: ./capture.sh <name> <command...>
name="$1"; shift
out="media/terminal/$name.log"
{ echo "sreemanti@MacBook-Pro team-knowledge-base % $*"; "$@" 2>&1; } | tee "$out"
