#!/bin/bash
cd ~/Desktop/ide
setsid python3 -m medha < /dev/null > /tmp/medha.log 2>&1 &
