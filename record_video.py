import cv2
import pyrealsense2 as rs
import time
import numpy as np
import os
import json

"""
USAGE INSTRUCTIONS: Run the script with the camera connected. Every time you want to record a video,
hit the Enter button. The script will pause for a moment and then start recording.

The parameters for the recording length and delay are shown below. Set USE_SOUND to True if you want the recording
start and stop to be indicated by a beep.

Dependencies: cv2, pyrealsense2, pydub (if using sound)
"""

VIDEO_LENGTH = 2.0          # The length of the recorded video
WAIT = 1.0                  # The length of the delay between hitting enter and the recording starting
USE_SOUND = False           # Whether or not a sound should be played to indicate recording stop/start

root = os.path.dirname(os.path.realpath(__file__))
output_dir = os.path.join(root, 'videos')
if not os.path.exists(output_dir):
    os.mkdir(output_dir)

if __name__ == '__main__':
    pipe = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.color, 640, 480, rs.format.rgb8, 30)
    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
    pipe.start(config)
    counter = 1
    if USE_SOUND:
        from pydub import AudioSegment
        from pydub.playback import play
        sound = AudioSegment.from_wav('beep.wav')
        play_sound = lambda: play(sound)
    else:
        play_sound = lambda: None

    try:
        while input('Type q to quit, Enter to continue: ').strip() != 'q':
            print(f'Waiting {WAIT} seconds...')
            time.sleep(WAIT)
            play_sound()
            while True:
                path = os.path.join(output_dir, 'video_{}.avi'.format(counter))
                if not os.path.exists(path):
                    break
                counter += 1

            format = cv2.VideoWriter_fourcc(*'MPEG')
            out = cv2.VideoWriter(path, format, 30, (1280, 480))
            start = time.time()
            count_frames = 0
            save_depth = []
            while time.time() - start < VIDEO_LENGTH:
                frames = pipe.wait_for_frames()
                depth_frame = frames.get_depth_frame()
                color_frame = frames.get_color_frame()
                if not depth_frame or not color_frame:
                    continue

                # Convert images to numpy arrays
                count_frames += 1
                depth_image = np.asanyarray(depth_frame.get_data())
                color_image = np.asanyarray(color_frame.get_data())

                # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
                depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
                save_depth.append([int(np.min(depth_image)), int(np.max(depth_image))])

                # Stack both images horizontally
                images = np.hstack((color_image, depth_colormap))
                #rgb_img = np.asanyarray(frames.get_color_frame().get_data())
                out.write(cv2.cvtColor(images, cv2.COLOR_RGB2BGR))

            fname = "videos/depth_{0}.json".format(counter)
            with open(fname, 'w') as f:
                json.dump(save_depth, f)
            counter += 1
            out.release()
            play_sound()
            print('Output to {}, {} frames'.format(path, count_frames))
    finally:
        pipe.stop()
