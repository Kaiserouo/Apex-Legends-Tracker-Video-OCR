# Apex Tracker Video OCR

Do OCR for trackers by recorded videos.

## Motivation
Apex Legend Status (ALS) and other API websites are good, but since they can only access selected legend, and they cannot read all trackers for a legend (only those 3 you put on your banner), so for someone wanting to take a snapshot of **all** trackers of all legends, this is not practical to use.

Manually typing all trackers to a file will be time-consuming. There is OCR in this world, why not use this?

## Demonstration
See `./example` for example files for demonstration.
+ `example.mkv` is the video I recorded, to demonstrate roughly the starting point of recording, and the speed to flip through the trackers. It is in 10 fps, which is recommended.
+ `out.json` is the output file. It will have some mistakes, but checking the numbers is faster than typing them. You can postprocess this file to a format you desire.

For the video, here is a youtube version (in 60fps). Click the image to see:

[![](https://img.youtube.com/vi/R5QHAjEeHPI/default.jpg)](https://youtu.be/R5QHAjEeHPI)

## Procedure
1. Open OBS Studio for recording. Set the recording to 10fps (or don't).
   + **MUST BE 1920x1080**. You can upscale your video if you only have access to 720p or something.
   + If you record your video in 60fps etc, it will work but the processing will be very, very slow. Please convert it to 10fps with `ffmpeg` or something.
2. Open Apex Legends and set OBS to record the game.
3. Go to `Legends` page in the game, and start recording.
4. Scroll through the trackers for each legends (or the legends of your choice).
   + **ONLY SCROLL WITH YOUR MOUSE SCROLL**. Use the scroll bar on the right will cause the program to break.
   + **DON'T SCROLL TOO QUICKLY**. My example video (`example.mkv`) flipped too quickly for some latter legends and some trackers are not recorded. You can scroll front or back, as long as you don't use the scroll bar.
5. After you scroll through all trackers you want, return back to `Legends` page and stop recording.
6. Convert your video to 10fps (if you didn't set OBS studio to 10fps).
   + For reference, `ffmpeg -i <input_video_name> -filter:v fps=10 <output_video_name>`
7. Go to `main.py` and set up the variables in `Config`.
   + Mainly, `VIDEO` and `OUT_FILE`.
8. Do `python main.py`
   + For `example.mkv` (10fps, 2 min 39 sec), it took like 10 minutes.
9.  Profit. Check output json file for result.

## Requirements
+ Python 3.10
+ `pytesseract`, and thus also [Tesseract-OCR](https://github.com/tesseract-ocr/tesseract).
+ OpenCV for python