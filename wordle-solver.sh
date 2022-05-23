#! /bin/bash
if ! command -v python3 &> /dev/null
then
    echo "python 3 could not be found"
    exit
fi
python3 wordle_helper.py $1
