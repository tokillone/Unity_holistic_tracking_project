# network_server.py
import socket
import struct

import cv2
import numpy as np
import json
from config import SERVER_HOST, SERVER_PORT


def start_server(process_frame_callback, backed_make_picture, host=SERVER_HOST, port=SERVER_PORT):
    """
    启动 TCP 服务器，接收前端发送的图像数据，
    调用 process_frame_callback 进行处理，并将结果发送回前端。
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((host, port))
    sock.listen(5)
    print(f"Server started at {host}:{port}")

    while True:
        # 接收数据和发送方地址
        conn, addr = sock.accept()
        print(f"Connected by: {addr}")

        try:
            while True:
                frame = receive_frame(conn)
                if frame is None:
                    print("Received empty frame.")
                    break
                print("Processing frame...")
                result = process_frame_callback(frame)
                print(f"Processing frame results length: {len(result)}")
                if result is None:
                    print("Process frame callback returned None.")
                    break

                response = json.dumps({"landmarks": result}).encode('UTF-8')
                print(f"Sending response: {len(response)} bytes")
                print(response[0:50])
                send_data(conn, response)
        except Exception as e:
            print(f"Error:{e}")
        finally:
            conn.close()
            print(f"Connection closed{addr}")


def receive_frame(conn):
    try:
        data = receive_data(conn)
        if not data:
            return None
        np_data = np.frombuffer(data, dtype=np.uint8)
        frame = cv2.imdecode(np_data, cv2.IMREAD_COLOR)
        return frame
    except Exception as e:
        print(f"Error receiving frame: {e}")
        return None


def receive_data(conn):
    """
    读取固定长度的数据头，然后读取完整的数据。
    """
    try:
        # 先读取 4 字节的头部，表示数据长度
        header = conn.recv(4)
        if len(header) < 4:
            print("No header received.")
            return None
        # data_size = int.from_bytes(header, 'big')  # 解析数据长度
        data_size = struct.unpack('!I', header)[0]  # 解析数据长度
        print(f"Received data size: {data_size}")

        # 读取数据
        data = b""
        i = 0
        while len(data) < data_size:
            packet = conn.recv(data_size - len(data))
            i = i + 1
            print(i)
            if not packet:
                print("Connection closed by client.")
                return None
            data += packet
            print(f"Received {len(data)} bytes so far.")  # 只显示接收到的数据量
        print(f"Received all data: {data}")
        return data
    except Exception as e:
        print(f"Error receiving data: {e}")
        return None


def send_data(conn, data):
    """
    发送数据，先发送长度（4 字节），然后发送数据本身
    """
    try:
        # 发送数据长度
        data_size = len(data)
        conn.sendall(data_size.to_bytes(4, 'big'))

        # 发送数据
        conn.sendall(data)
    except Exception as e:
        print(f"Error sending data: {e}")

# def start_server(process_frame_callback, backed_make_picture, host=SERVER_HOST, port=SERVER_PORT):
#     """
#     启动 UDP 服务器，接收前端发送的图像数据，
#     调用 process_frame_callback 进行处理，并将结果发送回前端。
#     """
#     sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     sock.bind((host, port))
#     print(f"Server started at {host}:{port}")
#
#     while True:
#         # 接收数据和发送方地址
#         data, addr = sock.recvfrom(65535)
#         # 前端将帧以 JPEG 格式编码后发送
#         np_data = np.frombuffer(data, np.uint8)
#         frame = cv2.imdecode(np_data, cv2.IMREAD_COLOR)
#         # print(frame[:5])
#         if frame is not None:
#             result = process_frame_callback(frame)
#             # 将结果转换为 JSON 格式
#             response = json.dumps({"landmarks": result}).encode('UTF-8')
#             max_size = 90000
#             chunks = [response[i:i + max_size] for i in range(0, len(response), max_size)]
#             for i, chunk in enumerate(chunks):
#                 header = i.to_bytes(1, 'big')
#                 sock.sendto(header + chunk, addr)
#             print("结果返回" + str(addr))
#             print(chunks[:1])
#
#         else:
#             print("服务接收到的数据无法解码为图像！！！")
#
#
# def getPic(backed_make_picture, sock, frame, addr):
#     while True:
#         if frame is not None:
#             # 后端帧直接传输
#             max_size = 1400
#             back_frame = backed_make_picture(frame)
#             chunks = [back_frame[i:i + max_size] for i in range(0, len(back_frame), max_size)]
#             for i, chunk in enumerate(chunks):
#                 header = i.to_bytes(1, 'big')
#                 sock.sendto(header + chunk, addr)
#         else:
#             print("接收到的数据无法解码为图像")
