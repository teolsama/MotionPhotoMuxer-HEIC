what is change in this fork?
============================

First I want to let you know that the code written here is made using Chat GPT 3.5 (free model).

> [!CAUTION]
> It was tested by me and worked well as I expected, but please if you use it take a backup before using it!!!

Different operating instructions, read carefully:

I had Google Takeout with a lot of HEIC and MOV/MP4 files, originally this script doesn't support HEIC so I made it support HEIC by converting it to jpeg and continuing.

Please note, **if you use export from Google Takeout** like me, you must use [google-photos-migrate](https://github.com/garzj/google-photos-migrate)
In order not to cause problems with the EXIF data in your photos, then after you do this came back to here.

I made this script more convenient to operate:

* Now the user can specify one path that includes all the files (photos and video) and **there is no need for --video or --photo anymore.**
* The script scans for files with the HEIC extension and converts them to jpeg while preserving the EXIF data, then the script looks for a match between the name of a jpeg or jpg file and a file with a mov or mp4 extension.
* The user has the option that all files for which no mp4/mov match is found (ie all other files that are not live files) will be moved to the destination folder.
* The script then performs the merge to create a jpg file with motion.

MotionPhotoMuxer
================

> **Note**
> I've switched back to Android for the time being. I do have access to an iPhone for testing, but
> likely won't be focusing on developing this much further.

Convert Apple Live Photos into Google Motion Photos commonly found on Android phones.

# Installation

As of right now, this script only has one dependency, `py3exiv2`. Unfortunately
this requires building a C++ library to install, so you need to install a C++ toolchain.

Using Ubuntu as an example:

~~~bash
sudo apt-get install build-essential python-all-dev libexiv2-dev libboost-python-dev python3 python3-pip python3-venv
python3 -m pip install -r requirements.txt
~~~


* Install [Termux from the F-Droid App store](https://f-droid.org/en/packages/com.termux/)
* Install the following packages within Termux in order to satisfy the dependencies for `pyexiv2`:

~~~bash
'pkg install python3'
'pkg install git'
'pkg install build-essential'
'pkg install exiv2'
'pkg install boost-headers'
git clone https://github.com/mihir-io/MotionPhotoMuxer.git
python3 -m pip install -r MotionPhotoMuxer/requirements.txt
~~~

This should leave you with a working copy of MotionPhotoMuxer directly on your Pixel/other Android phone.
You may want to make sure Termux has the "Storage" permission granted from within the system settings, if
you plan on writing the output files to the `/sdcard/` partition.

# Usage

Just run the MotionPhotoMuxer.py file and follow the instraction

# Credit

This wouldn't have been possible without the excellent writeup on the process
of working with Motion Photos [here](https://medium.com/android-news/working-with-motion-photos-da0aa49b50c).
