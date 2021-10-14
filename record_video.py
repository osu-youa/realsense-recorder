import cv2
import pyrealsense2 as rs
import time
import numpy as np
import os

"""
USAGE INSTRUCTIONS: Run the script with the camera connected. Every time you want to record a video,
hit the Enter button. The script will pause for a moment and then start recording.

The parameters for the recording length and delay are shown below. Set USE_SOUND to True if you want the recording
start and stop to be indicated by a beep.

Dependencies: cv2, pyrealsense2, pydub (if using sound)
"""

VIDEO_LENGTH = 5.0          # The length of the recorded video
WAIT = 2.0                  # The length of the delay between hitting enter and the recording starting
USE_SOUND = False           # Whether or not a sound should be played to indicate recording stop/start

root = os.path.dirname(os.path.realpath(__file__))
output_dir = 'videos'

if __name__ == '__main__':
    pipe = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.color, 424, 240, rs.format.rgb8, 30)
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
                path = os.path.join(root, output_dir, 'video_{}.avi'.format(counter))
                if not os.path.exists(path):
                    break
                counter += 1

            format = cv2.VideoWriter_fourcc(*'MPEG')
            out = cv2.VideoWriter(path, format, 30, (424, 240))
            start = time.time()
            while time.time() - start < VIDEO_LENGTH:
                frames = pipe.wait_for_frames()
                rgb_img = np.asanyarray(frames.get_color_frame().get_data())
                out.write(cv2.cvtColor(rgb_img, cv2.COLOR_RGB2BGR))
            counter += 1
            out.release()
            play_sound()
            print('Output to {}'.format(path))
    finally:
        pipe.stop()