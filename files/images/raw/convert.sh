#!/bin/bash

if [ $# -eq 0 ]
  then
    echo "Please provide a scan number as an argument"
    exit 1
fi

for filename in B?_CH?_C???.jxr; do

    channelNumber=${filename#*_CH}
    channelNumber=${channelNumber%%_*}

    echo converted/$1/channel$channelNumber/${filename%.jxr}.tiff

    JxrDecApp -i $filename -o ../converted/$1/channel$channelNumber/${filename%.jxr}.tiff

done
