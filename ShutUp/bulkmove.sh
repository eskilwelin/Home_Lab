#!/bin/bash

for dir in /home/*/;do
    echo "Copying into $dir"
    cp -r /srv/shutup/*.py $dir
done