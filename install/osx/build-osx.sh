#!/usr/bin/env bash

#Cleanup possible previous builds
rm -rf RaceCapture.app

DIR=$( cd ../.. && pwd )

#Kivy's build/packaging tools expect the Kivy app here
if [ ! -f "./Kivy.App" ]; then
	rsync -a /Applications/Kivy.App/ ./Kivy.App
fi

./package-app.sh "$DIR/"

#Customizations and file size savings
rm -rf RaceCapture.app/Contents/Frameworks/GStreamer.framework
rm -rf RaceCapture.app/Contents/Resources/kivy/examples
rm -rf RaceCapture.app/Contents/Resources/kivy/doc
rm -rf RaceCapture.app/Contents/Resources/kivy/.git

#We have to customize their theme so checkboxes show up
cp defaulttheme-0.png RaceCapture.app/Contents/Resources/kivy/kivy/data/images/ 

#Custom icon
cp racecapture.icns RaceCapture.app/Contents/Resources/appIcon.icns

#Customize plist so our name and info shows up
cp Info.plist RaceCapture.app/Contents/

./create-osx-dmg.sh RaceCapture.app

