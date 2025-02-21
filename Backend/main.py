# main.py
from network_server import start_server
from tracker import getFrame
from holistic_tracker import HolisticTracker
from backed_make_picture import backed_make_picture
from config import MIN_DETECTION_CONFIDENCE, MIN_TRACKING_CONFIDENCE

holistic_tracker = HolisticTracker()
def process_frame(frame):
    # landmarks = getFrame(frame)
    landmarks = holistic_tracker.track(frame)
    return landmarks


if __name__ == '__main__':
    start_server(process_frame,backed_make_picture)
