import errno
import os
import sys
import threading
from datetime import datetime
from time import sleep
import yaml
import cv2

config = yaml.safe_load(open(os.path.join(sys.path[0], "config.yml")))
image_number = 0


def create_timestamped_dir(dir):
    try:
        os.makedirs(dir)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


def set_camera_options(camera):
    # Set camera resolution.
    if config['resolution']:
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, config['resolution']['width'])
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, config['resolution']['height'])

    # Set ISO.
    if config['iso']:
        camera.set(cv2.CAP_PROP_ISO_SPEED, config['iso'])

    # Set shutter speed.
    if config['shutter_speed']:
        camera.set(cv2.CAP_PROP_EXPOSURE, config['shutter_speed'])
        # Sleep to allow the shutter speed to take effect correctly.
        sleep(1)

    # Set white balance.
    if config['white_balance']:
        camera.set(cv2.CAP_PROP_WHITE_BALANCE_BLUE_U, config['white_balance']['blue_gain'])
        camera.set(cv2.CAP_PROP_WHITE_BALANCE_RED_V, config['white_balance']['red_gain'])

    # Set camera rotation
    if config['rotation']:
        camera.set(cv2.CAP_PROP_ROTATION, config['rotation'])

    return camera


def capture_image():
    try:
        global image_number

        # Set a timer to take another picture at the proper interval after this
        # picture is taken.
        if (image_number < (config['total_images'] - 1)):
            thread = threading.Timer(config['interval'], capture_image).start()

        # Start up the camera.
        cap = cv2.VideoCapture(0)
        cv2.waitKey(1)
        if not cap.isOpened():
            raise IOError("Cannot open USB webcam")

        # Set camera options (if necessary).
        # Example: cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        # Example: cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        set_camera_options(cap)
        # Capture a picture.
        ret, frame = cap.read()
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

        # Hiển thị thời gian lên ảnh
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame, dt_string, (50, 50), font, 1, (255, 25, 25), 2, cv2.LINE_AA)

        cv2.imwrite(dir + '/image{0:08d}.jpg'.format(image_number), frame)

        cap.release()

        if (image_number < (config['total_images'] - 1)):
            image_number += 1
        else:
            print ('\nTime-lapse capture complete!\n')
            # TODO: This doesn't pop user into the except block below :(.
            sys.exit()

    except (KeyboardInterrupt):
        print ("\nTime-lapse capture cancelled.\n")
    except (SystemExit):
        print ("\nTime-lapse capture stopped.\n")


# Initialize the path for files to be saved
dir_path = str(config['dir_path'])

# Create directory based on current timestamp.
dir = os.path.join(
    sys.path[0],
    dir_path + '/series-' + datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
)
# Create directory with current time stamp
create_timestamped_dir(dir)

# Print where the files will be saved
print("\nFiles will be saved in: " + str(dir_path) + "\n")

# Kick off the capture process.
capture_image()

# Create an animated gif (Requires ImageMagick).
#TODO: These may not get called after the end of the threading process...
# Create an animated gif (Requires ImageMagick).
if config['create_gif']:
    print ('\nCreating animated gif.\n')
    os.system('convert -delay 10 -loop 0 ' + dir + '/image*.jpg ' + dir + '-timelapse.gif')  # noqa

# Create a video (Requires avconv - which is basically ffmpeg).
if config['create_video']:
    print ('\nCreating video.\n')
    # os.system('avconv -framerate 20 -i ' + dir + '/image%08d.jpg -vf format=yuv420p ' + dir + '/timelapse.mp4')  # noqa
    os.system('ffmpeg -framerate 30 -i ' + dir + '/image%08d.jpg -vf "format=yuv420p" ' + dir + '/day_by_day.mp4')

