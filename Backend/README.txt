BACKEND
    一、main函数后端开启入口
    二、holistic.py实现图像关键点识别并输出归一化关键点：以列表形式返回
    三、network_server.py后端开启tcp服务，接收前端图像数据，返回前端关键点数据————格式：[b'{"landmarks": {"face": [], "pose": [], "left_hand": [], "right_hand": []}}']，数据分片返回
    四、config.py参数配置
    五、local_test_facetracking.py  backed_make_picture.py测试文件
    接收数据类型：JPEG 压缩后的二进制数据，byte[]类型，可以用
    发送数据类型：[b'{"landmarks": {"face": [], "pose": [], "left_hand": [], "right_hand": []}}']
                具体如[b'{"landmarks": {"face": [], "pose": [{"x": 0.14313547313213348, "y": 0.6625226140022278,

UNITY
    一、HolisticDisplay 通过Cam获取摄像头字节数据,调用Net发送字节数据并接受关键点数据，解析关键点数据（JSON），利用Cam绘制关键点
    二、CameraCapture   直接获取摄像头数据，启动携程保持显示尺寸不变，提供将帧转换为二进制方法，
                       UpdateKeypoints（）更新关键点数据，
                       NormalizedToLocalPosition（）实现坐标点翻转契合摄像头原始图片显示。
    三、NetworkClient   SendFrameGetPoint(byte[] data)，发送视频数据帧，分批次接收并合并后端关键点数据，返回值json
                       GetUdpChunks(Dictionary<int, byte[]> recChunks, byte[] data, ref int recCount, ref int expChunks)处理后端分片数据
数据传输说明：每次传输数据帧时，会先发送大小为4字节的长度消息，之后会发送本次的数据（前端发送JPEG转化的二进制数据，后端返回关键点数据）