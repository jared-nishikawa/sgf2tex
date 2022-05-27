#!/bin/bash

for file in $(find sgf -name "*.sgf")
do
    path=$(echo $file | awk -F. '{print $1}')
    base=$(echo $path | awk -F/ '{print $2}')
    new="./tex/$base.tex"
    echo "Now working on $file"
    ./maketex.py -i $file $new
done
