what is change in this fork?
============================

First I want to let you know that the code written here is made using Chat GPT 3.5 (free model).

> [!CAUTION]
> **It was tested by me and worked well as I expected, but please if you use it take a backup before using it!!!**

Different operating instructions, read carefully:

I had Google Takeout with a lot of HEIC and MOV/MP4 files, originally this script doesn't support HEIC so I made it support HEIC by converting it to jpeg and continuing.

Please note, **if you use export from Google Takeout** like me, you must use [google-photos-migrate](https://github.com/garzj/google-photos-migrate)
In order not to cause problems with the EXIF data in your photos, then after you do this came back to here.

I made this script more convenient to operate:

<details>
  <summary>How its work?</summary>

The script operates in several distinct steps:

1. **Scanning and Conversion of HEIC Files:**
   - It begins by scanning the specified directory for files with the HEIC extension.
   - Each HEIC file found is converted to JPEG format while ensuring preservation of EXIF data.
   - If successful, the script logs the conversion and copies EXIF data from the original HEIC to the newly created JPEG file.

2. **Matching JPEG Files with Video Files:**
   - For each converted JPEG file, the script attempts to find a matching video file (MOV or MP4) within the same directory.
   - If a matching video file is found, the script proceeds to merge the JPEG and video files together.

3. **Merging Files:**
   - The script merges the JPEG and video files, creating a single file that combines both image and motion.
   - It calculates the offset between the sizes of the original photo and the merged file, essential for later XMP metadata addition.

4. **Adding XMP Metadata:**
   - XMP metadata is added to the merged file, crucial for recognizing it as a Google Motion Photo.
   - Existing metadata in the file is read and potentially affected XMP keys are logged as a warning.

5. **Processing Directory:**
   - The script iterates through all files in the specified directory, processing HEIC files first and then JPEG files.
   - For each file, it checks for a matching video file and performs the conversion process if found.
   - Optionally, non-matching files can be moved to the output directory.

6. **User Interaction:**
   - The user is prompted to provide input and output directories.
   - Additionally, the user can choose whether to move non-matching images to the output directory.

7. **Error Handling and Logging:**
   - The script logs various messages throughout its execution, including errors encountered during file processing.
   - Problematic files are recorded and logged for the user's reference.

By following these steps, the script efficiently converts Apple Live Photos into Google Motion Photos, ensuring a seamless user experience while handling various file formats and preserving essential metadata.

</details>

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
