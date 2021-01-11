#!/bin/bash

echo "Converting resource"
pyrcc5 UI/images.qrc -o images_rc.py

echo "Converting ui file"
pyuic5 UI/simpleUI.ui -o UI/simpleUI.py


