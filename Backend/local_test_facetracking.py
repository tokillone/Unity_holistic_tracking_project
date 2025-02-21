import mediapipe as mp
import cv2

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

# 摄像头
cap = cv2.VideoCapture(0)
while cap.isOpened():
    # 读取摄像头的帧
    ret, frame = cap.read()
    if not ret:
        break;
    # 将BGR格式转换为RGB格式（Mediapipe需要RGB输入）
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # 面部检测
    result = face_mesh.process(image)

    #如果监测到面部
    if result.multi_face_landmarks:
        for face_landmarks in result.multi_face_landmarks:
            #绘制面部关键点和连接线
            mp_drawing.draw_landmarks(
                image=frame,
                landmark_list=face_landmarks,
                connections=mp_face_mesh.FACEMESH_TESSELATION,
                landmark_drawing_spec=None,
                connection_drawing_spec=mp_drawing.DrawingSpec(
                    color=(0, 255, 0),#颜色
                    thickness=1,#线条粗细
                    circle_radius=1#关键点半径
                )
            )
            landmarks = result.multi_face_landmarks[0]
            # 将关键点信息转换为列表，便于序列化
            points = [{"x": lm.x, "y": lm.y, "z": lm.z} for lm in landmarks.landmark]
            print(points)
    #显示结果窗口
    cv2.imshow('Face Detection', frame)
    #q键退出
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()
