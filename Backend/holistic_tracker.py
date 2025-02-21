import cv2
import mediapipe as mp

class HolisticTracker:
    def __init__(self):
        self.mp_holistic = mp.solutions.holistic
        self.holistic = self.mp_holistic.Holistic(
            static_image_mode=False,
            model_complexity=1,            # 模型复杂度，可根据性能需求调整：0、1或2
            smooth_landmarks=True,         # 是否平滑关键点
            enable_segmentation=False,     # 是否启用人体分割（可根据需要开启）
            smooth_segmentation=True,      # 是否平滑分割结果
            min_detection_confidence=0.5,  # 最小检测置信度
            min_tracking_confidence=0.5    # 最小跟踪置信度
        )

    def track(self, frame):
        # 转换颜色空间为 RGB
        print("Received frame with shape:", frame.shape)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.holistic.process(rgb_frame)
        data = {}

        # 提取面部关键点（如果有检测到）
        if results.face_landmarks:
            data['face'] = [{"x": lm.x, "y": lm.y, "z": lm.z} for lm in results.face_landmarks.landmark]
        else:
            data['face'] = []

        # 提取姿态关键点（如果有检测到）
        if results.pose_landmarks:
            data['pose'] = [{"x": lm.x, "y": lm.y, "z": lm.z, "visibility": lm.visibility}
                            for lm in results.pose_landmarks.landmark]
        else:
            data['pose'] = []

        # 提取左手关键点（如果有检测到）
        if results.left_hand_landmarks:
            data['left_hand'] = [{"x": lm.x, "y": lm.y, "z": lm.z} for lm in results.left_hand_landmarks.landmark]
        else:
            data['left_hand'] = []

        # 提取右手关键点（如果有检测到）
        if results.right_hand_landmarks:
            data['right_hand'] = [{"x": lm.x, "y": lm.y, "z": lm.z} for lm in results.right_hand_landmarks.landmark]
        else:
            data['right_hand'] = []

        return data
