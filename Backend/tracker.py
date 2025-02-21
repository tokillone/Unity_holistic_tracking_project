import threading
import time
import queue
import cv2
import mediapipe as mp


class FaceTracker:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

    def track(self, frame):
        # 转换颜色空间为RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)
        if results.multi_face_landmarks:
            # 取第一张人脸的关键点
            landmarks = results.multi_face_landmarks[0]
            # 将关键点信息转换为列表，便于序列化
            points = [{"x": lm.x, "y": lm.y, "z": lm.z} for lm in landmarks.landmark]
            return points
        else:
            return []


class HandTracker:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,  # 允许检测双手
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

    def track(self, frame):
        # 转换颜色空间为 RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        if results.multi_hand_landmarks:
            # 对每一只手的关键点信息进行提取
            hands_data = []
            for hand_landmarks in results.multi_hand_landmarks:
                # 将每个关键点的 x,y,z 坐标保存为字典
                points = [{"x": lm.x, "y": lm.y, "z": lm.z} for lm in hand_landmarks.landmark]
                hands_data.append(points)
            return hands_data
        else:
            return []


class PoseTracker:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            enable_segmentation=False,  # 人体分割，若需要可设为 True
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

    def track(self, frame):
        # 转换颜色空间为 RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb_frame)
        if results.pose_landmarks:
            # 将检测到的人体关键点（包含 visibility）转换为列表
            points = [
                {"x": lm.x, "y": lm.y, "z": lm.z, "visibility": lm.visibility}
                for lm in results.pose_landmarks.landmark
            ]
            return points
        else:
            return []


face_tracker = FaceTracker()
pose_tracker = PoseTracker()
hand_tracker = HandTracker()


def getFrame(frame):
    # face_queue = queue.Queue()
    # pose_queue = queue.Queue()
    # hand_queue = queue.Queue()
    #
    # def track_face():
    #     result = face_tracker.track(frame)
    #     face_queue.put(result)
    #
    # def track_pose():
    #     result = pose_tracker.track(frame)
    #     pose_queue.put(result)
    #
    # def track_hand():
    #     result = hand_tracker.track(frame)
    #     hand_queue.put(result)
    #
    # face_thread = threading.Thread(target=track_face())
    # pose_thread = threading.Thread(target=track_pose())
    # hand_thread = threading.Thread(target=track_hand())
    #
    # face_thread.start()
    # pose_thread.start()
    # hand_thread.start()
    #
    # face_thread.join()
    # pose_thread.join()
    # hand_thread.join()
    #
    # landmark1 = face_queue.get()
    # landmark2 = pose_queue.get()
    # landmark3 = hand_queue.get()
    landmark1=face_tracker.track(frame)
    landmark2=pose_tracker.track(frame)
    landmark3=hand_tracker.track(frame)

    landmarks = landmark1 + landmark2 + landmark3
    return landmarks
