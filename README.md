# Google Photos Matcher Mac/Unix (v 1.0)

Simple executable to match metadata from JSONs to original images/videos (Forked from anderbggo/GooglePhotosMatcher which was Windows only compatible).

Same work than [MetadataFixer](https://metadatafixer.com/pricing) but its free!

## Wiki 📖

When you download the images from google photos, they lose some metadata such as the date and the coordinates in which they were taken.

This algorithm is able to match this information in the image/video from the downloaded JSONs

## Usage

1. Download your _Google Photos_ media from [Takeout](https://takeout.google.com/)

2. Download this sourcecode in a folder with:

   ```
   git clone https://github.com/mtmarco87/GooglePhotosMatcher-Mac-Unix.git
   ```

3. Install **python 3** on your system. There are multiple ways to do this depending on your OS, e.g.:

   - On mac:
     ```
     brew install python3
     ```
   - On linux:
     ```
     sudo apt-get install python3
     ```

4. Install **exiftool** on your system:

   - On mac:
     ```
     brew install exiftool
     ```
   - On linux:
     ```
     sudo apt-get install exiftool
     ```

5. Install python app requirements (from project folder):

   ```
   pip install -r requirements.txt
   ```

6. Make the file **run.sh** in the project folder executable:

   ```
   chmod 777 run.sh
   ```

7. Now you are all set to match and fix your Google Photos from Takeout simply executing **_run.sh_** **from the project folder** targeting any takeout folder containing json and media files.

8. Usage instructions:

   - To simply match all json/photos/videos in a specific Takeout folder with default settings:

     ```
     ./run.sh Takeout/Google\ Photos/Photos\ from\ 2025
     ```

   - Full app parameters list:

     ```
     ./run.sh target_folder edited_prefix convert_all_to_jpg convert_if_needed
     ```

     **target_folder:** the path of the folder containing json and media files you want to fix/match

     **edited_prefix:** tells the app what tags Google uses for edited images in your local language. Google generally adds an _"edited"_ suffix to the modified/customized images keeping both the original version (without this suffix) and the newly edited version. Thanks to this the app may look and fix metadata/gps information for all the image variants, including the original and edited image (**default value: edited**, possible values: anything depending on your language [e.g.: modificato (IT), editado (ES), etc.])

     **convert_all_to_jpg:** tells the app whether to reconvert any exif compatible image file found (TIF, TIFF, JPEG, JPG) to be always converted to JPG (**default value: false**, possible values: true, false)

     **convert_if_needed:** tells the app to reconvert an exif compatible image file to JPG in case the exif editing fails for the current image format; it may reduce errors while reapplying image tags at the cost of reconverting some wrongly encoded image (**default value: true**, possible values: true, false)

9. Matched images/videos will be on directory _Matched_ inside the same path

## Bonus tools

Inside the **tools** folder you can find some tools that further help into Google Photos takeout process.

1. **convertVP9toMP4.sh** => sometimes Google re-encodes video files in VP9 google codec. This codec is not supported by all devices (especially, you will never guess :D, Apple devices). Using this tool you can quickly reconvert a video file into h264 codec supported by most devices (including Apple device) with no loss of quality.

   - Prerequisites:

     ```
     brew install ffmpeg
     chmod 777 ./tools/convertVP9toMP4.sh
     ```

   - Usage:
     ```
     ./tools/convertVP9toMP4.sh source_video_file converted_video_file
     ```

2. **terabox-file-counter-fetch.js** => in case you want to freely store your taked out photos on [Terabox](https://www.terabox.com) you may surprisingly face difficulties in checking the number of uploaded files (in case you are trying to double check with your original folders). A "custom" and hacky solution is to run this javascript snippet directly into the a terabox web app page while you are logged into it using browser developer tools, by just customizing the variables like in the example provided in the code snippet. More info directly in the source code (a variant based on XHR is provided as well, even though this fetch based one should work well on most modern browsers).

## FAQs

### Why is there another folder called _EditedRaw_?

Images and videos edited from _Google Photos's_ editor will have 2 different versions:

1. Edited version
2. Original version

Edited version will be stored in _Matched_ while original in _EditedRaw_

### Why some images/videos stay unmatched?

Sometimes, the algorithm does not recognize the names of the images due to the presence of some special characters. These files will remain in the same folder. To fix it, rename both the JSON and the original file.

#### For example:

- Algorithm fails with image _%E&xample.jpg_

#### Solution

1. Rename _%E&xample.jpg_ to _Example.jpg_ and _%E&xample.json_ to _Example.json_

2. Open JSON and change title attribute to _Example.jpg_

3. Run again

### Debugging

1. Run the app this way to get the debug output into a **results.txt** file:

   ```
   ./run.sh Takeout/Google\ Photos/Photos\ from\ 2025 > results.txt
   ```

2. Open **results.txt** with any text editor and look the contents:

   - **Success condition:** If everything went well you should find at the bottom of the file **0 errors** and **many successes** (as much as the amount of image files in your takeout folder)

   - **Errors debugging:** If there are any errors you can analyze them searching for the word **Error**: every error generated in the app is printed with this prefix and some details which may help solving it should be shown

   - **Useful information:** some special output is produced by the app depending on the processing:
     - **Image Exif updated** => the exif data (creation date) has been updated for the image file printed above
     - **Image GPS Data added/updated for: _filepath_** => the exif data (gps) has been updated for the image file specified. Supplemental info is shown at the end: **version, altitude, latitude, longitude** in any combination to specify which gps exif properties have been added/updated.
     - **Warning: Image coordinates not settled** => means that an error happened while trying to add/update image exif gps data
     - **Video Exif updated** => the exif data (gps) has been updated for the video file printed above. Supplemental info is shown at the end: **Apple** and/or **Android** to specify which of the platform specific tags have been added
     - **Warning: Video coordinates not settled** => means that an error happened while trying to add/update video exif gps data
     - **Warn: Fixed Exif** => the image file exif data has been fixed: this is rare but it can occasionally happen due to insertion of non exif standard tags into images by software/hardware/camera manufacturers. The fix consists in converting the wrong exif fields into standard compliant fields and allows the app to update the image exif tags regularly.
       Supplemental information is shown at the end, e.g.: **37121, 37500, 41728, 41729** in any combination to indicate which Exif Tag Id has been fixed (these are well known and common issues, you can google for it).

## Contributors ✒️

- **mtmarco87** - Author of the Google Photos Matcher Mac/Unix variant
- **anderbggo** - Author of the original Google Photos Matcher
- **Freepik** - Icon creator

## Buy me a coffee☕

- [Buy me a coffee](https://buymeacoffee.com/mtmarco87): https://buymeacoffee.com/mtmarco87
- Btc address: bc1qzy6e99pkeq00rsx8jptx93jv56s9ak2lz32e2d
- Eth address: 0x38cf74ED056fF994342941372F8ffC5C45E6cF21
