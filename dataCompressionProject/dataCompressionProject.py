#Probe the configuration of video by function ffmpeg.probe() to get duration, audio & video bit rate and so on.
#And calculate the bit rate of the target file based on what we have. 
#Then, construct commands by ffmpeg.input() and ffmpeg.output(). 
#Finally, run it
# If video bit rate < 1000, it will throw exception Bitrate is extremely low

import os , ffmpeg

def compress_video(video_full_path, output_file_name, target_size):

    min_audio_bitrate = 32000
    max_audio_bitrate = 256000

    probe = ffmpeg.probe(video_full_path)
    # Video duration, in s.
    duration = float(probe['format']['duration'])
    # Audio bitrate, in bps.

    audio_bitrate = float(next((s for s in probe['streams'] if s['codec_type'] == 'audio'), None)['bit_rate'])
    
    # next return next iterator in list
    # - target_total_bitrate: the desired total bitrate of a video file in bits per second (bps)
    # - target_size: the desired size of the video file in kilobytes (KB)
    # - duration: the length of the video in seconds
    # The formula calculates the target_total_bitrate based on the desired file size and duration of the video. 
    # multiplies "target_size" by 1024 to convert it from kilobytes to bytes. 
    # Then, it multiplies the result by 8 to convert it from bytes to bits
    # divides it by 1.073741824 (which is 1024^3 or the number of bytes in a gigabyte)    
    # multiplied by duration to get the total number of bits needed for that duration .

    target_total_bitrate = (target_size * 1024 * 8) / (1.073741824 * duration)

    # Target audio bitrate, in bps
    # لو الفيديو نفسه البايت رات بتاعه اصغر من اللى انا طالبه فهو بيضربه فى 10 عشان يحجمه فى الرانج اللى انا محددهوله
    
    if 10 * audio_bitrate > target_total_bitrate:
        audio_bitrate = target_total_bitrate / 10
        if audio_bitrate < min_audio_bitrate < target_total_bitrate:
            audio_bitrate = min_audio_bitrate
        elif audio_bitrate > max_audio_bitrate:
            audio_bitrate = max_audio_bitrate

    # Target video bitrate, in bps.
    video_bitrate = target_total_bitrate - audio_bitrate

    # In the first pass, the video is encoded without audio and the output is sent to /dev/null . 
    # This pass is used to analyze the video and determine the best encoding settings for the second pass c=>codec b=>bitrate libx264=> H.264 high difination digital video.
    i = ffmpeg.input(video_full_path)
    ffmpeg.output(i, os.devnull,
                  **{'c:v': 'libx264', 'b:v': video_bitrate, 'pass': 1, 'f': 'mp4'}
                  ).overwrite_output().run()
    ffmpeg.output(i, output_file_name,
                  **{'c:v': 'libx264', 'b:v': video_bitrate, 'pass': 2, 'c:a': 'aac', 'b:a': audio_bitrate}
                  ).overwrite_output().run()

# Compress input.mp4 to 10MB and save as output.mp4
input_data= r"C:\Users\user\Videos\s4 p5.mp4"
output_data= r"C:\Users\user\Videos\s4 p5_Compressed.mp4"
# 10 000 kiloByte is 10 MB
compress_video(input_data, output_data , 10 * 1000)