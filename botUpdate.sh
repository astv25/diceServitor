#!/bin/bash
git pull
ps aux | grep 'main.py' | awk '{print $2}' | xargs kill
../runDiceServitor.sh
