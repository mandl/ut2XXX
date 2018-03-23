#!/bin/bash

echo "Converting resource"
pyrcc4 images.qrc -o images_rc.py

echo "Converting ui file"
pyuic4 simpleUI.ui -o simpleUI.py


