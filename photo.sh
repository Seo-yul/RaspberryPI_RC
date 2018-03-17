#!/bin/bash


argc="$1"
NOW=$(date +%Y%m%d%H%M%S)

#argc =yf1
function takePhoto(){
    raspistill -v -o ./gallery/${NOW}.jpg
}

    case $argc in
        yf1)
            takePhoto;;
    esac
















exit 0
