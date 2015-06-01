#!/bin/sh
montage -tile x1 -geometry +0+0 `ls -1v *.png` gauge.png
