#!/bin/bash

echo "Converting resource"
pyrcc4 UI/images.qrc -o UI/images_rc.py

echo "Converting ui file"
pyuic4 UI/simpleUI.ui -o UI/simpleUI.py


