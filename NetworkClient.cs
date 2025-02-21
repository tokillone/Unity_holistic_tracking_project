using UnityEngine;
using System.Net.Sockets;
using System.Net;
using System.Text;
using System.Threading.Tasks;
using System;
using System.Data.SqlTypes;
using System.Collections.Generic;
using UnityEngine.XR.Interaction.Toolkit;
using Unity.VisualScripting;
using Unity.Mathematics;
using UnityEditor.PackageManager;


public class NetworkClient : MonoBehaviour
{
    public string serverIP;
    public int serverPort;
    private TcpClient tcpClient;
    private NetworkStream stream;

    void Start()
    {
        tcpClient = new TcpClient();
        Debug.Log("tcp client initialized");
    }

    public async Task ConnectToServer()
    {
        try
        {
            await tcpClient.ConnectAsync(serverIP, serverPort);
            stream = tcpClient.GetStream();
            Debug.Log("Connected to server" + serverIP + ":" + serverPort);
        }
        catch (Exception e)
        {
            Debug.LogError("Connection error" + e.Message);
        }
    }

    void OnDestroy()
    {
        if (stream != null) stream.Close();
        if (tcpClient != null) tcpClient.Close();
        Debug.Log("tcp client closed");
    }

    // 异步发送数据并等待返回结果
    public async Task<string> SendFrameGetPoint(byte[] data)
    {
        try
        {
            if (stream == null || !tcpClient.Connected)
            {
                Debug.LogError("Not connected to server");
                return null;
            }
            await SendData(stream, data);
            Debug.Log($"Data send to {serverIP}:{serverPort},data size:{data.Length}bytes");
            byte[] receivedData = await ReceiveData(stream);
            if (receivedData == null)
            {
                Debug.Log("Server response timeout or error");
                return null;
            }
            string jsonString = Encoding.UTF8.GetString(receivedData);
            if (jsonString.TrimStart().StartsWith("{\"landmarks\""))
            {
                return jsonString;
            }
            else
            {
                Debug.Log($"Invalid JSON: {jsonString[..Math.Min(100, jsonString.Length)]}");
                return null;
            }
        }
        catch (Exception e)
        {
            Debug.LogError("Network error:" + e.Message);
            return null;
        }
    }
    private async Task SendData(NetworkStream stream, byte[] data)
    {
        try
        {
            byte[] lengthBytes = BitConverter.GetBytes(data.Length);
            if (BitConverter.IsLittleEndian)
            {
                Array.Reverse(lengthBytes); // 转换为大端序
            }
            await stream.WriteAsync(lengthBytes, 0, lengthBytes.Length);

            await stream.WriteAsync(data, 0, data.Length);
        }
        catch (Exception e)
        {
            Debug.LogError("Error sending data:" + e.Message);
        }
    }
    // 异步接收数据
    private async Task<byte[]> ReceiveData(NetworkStream stream)
    {
        try
        {
            // 读取数据长度

            byte[] lengthBytes = new byte[4];
            int bytesRead = await stream.ReadAsync(lengthBytes, 0, lengthBytes.Length);
            if (bytesRead != 4)
            {
                Debug.LogError("Failed to read data length.");
                return null;
            }

            // int dataLength = BitConverter.ToInt32(lengthBytes, 0);
            // 检查字节序是否需要转换
            if (BitConverter.IsLittleEndian)
            {
                Array.Reverse(lengthBytes);  // 如果是小端序，反转字节数组
            }

            int dataLength = BitConverter.ToInt32(lengthBytes, 0);

            if (dataLength <= 0 || dataLength > 10 * 1024 * 1024) // 限制最大 10MB
            {
                Debug.LogError($"Invalid data length: {dataLength}");
                return null;
            }

            // 读取数据
            byte[] data = new byte[dataLength];
            int totalBytesRead = 0;
            while (totalBytesRead < dataLength)
            {
                int bytesToRead = dataLength - totalBytesRead;
                bytesRead = await stream.ReadAsync(data, totalBytesRead, dataLength - totalBytesRead);
                if (bytesRead == 0)
                {
                    Debug.LogError("Connection closed by server.");
                    return null;
                }
                totalBytesRead += bytesRead;
            }
            Debug.Log($"Received data:{totalBytesRead} bytes");
            return data;
        }
        catch (Exception e)
        {
            Debug.LogError($"Error receiving data: {e.Message}");
        }
        return null;
    }
}
