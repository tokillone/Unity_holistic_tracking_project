using UnityEngine;
using System.Collections;
using UnityEngine.UI;
using System.Threading.Tasks;
using Newtonsoft.Json.Linq;
using TMPro;
using System;
using System.Collections.Generic; // 可使用 Json.NET for Unity

public class HolisticDisplay : MonoBehaviour
{
    public CameraCapture cameraCapture;
    public NetworkClient networkClient;

    void Start()
    {
        StartCoroutine(SendAndReceiveLoop());
    }

    IEnumerator SendAndReceiveLoop()
    {
        // 先连接
        Task connectTask = networkClient.ConnectToServer();
        yield return new WaitUntil(() => connectTask.IsCompleted);

        if (connectTask.IsFaulted)
        {
            Debug.LogError($"Failed to connect to server: {connectTask.Exception}");
            yield break;
        }

        Debug.Log("Connected to server successfully.");
        while (true)
        {
            byte[] frameData = cameraCapture.GetFrameBytes();//得到摄像头
            Debug.Log("frameData length:"+frameData.Length);
            
            if (frameData == null || frameData.Length == 0)
            {
                Debug.LogWarning("Frame data is empty.");
                yield return new WaitForSeconds(0.1f);
                continue;
            }
            Task<string> task = networkClient.SendFrameGetPoint(frameData);
            yield return new WaitUntil(() => task.IsCompleted);

            if (task.IsFaulted)
            {
                Debug.LogError($"Failed to send/receive data: {task.Exception}");
                yield return new WaitForSeconds(1); // 等待 1 秒后重试
                continue;
            }
            string response = task.Result;
            try
            {
                Debug.Log($"收到的消息long:{response.Length}context:{response[..100]}");
            }
            catch (Exception e)
            {
                Debug.Log($"出现了错误：{e}");
            }
            if (!string.IsNullOrEmpty(response))
            {
                try
                {
                    JObject json = JObject.Parse(response);
                    JObject landmarks = (JObject)json["landmarks"];
                    List<Vector2> normalizedPositions = new();
                    ParseLandmarks(landmarks, "face", normalizedPositions);
                    ParseLandmarks(landmarks, "pose", normalizedPositions);
                    ParseLandmarks(landmarks, "left_hand", normalizedPositions);
                    ParseLandmarks(landmarks, "right_hand", normalizedPositions);
                    cameraCapture.UdpdateKeypoints(normalizedPositions);
                }
                catch (Exception e)
                {
                    Debug.Log($"JSON解析失败了：你干嘛哎嘿呦？{e.Message}");
                }
            }
            // JObject json = JObject.Parse(response);
            // 根据 json 数据绘制关键点或驱动动画

            yield return new WaitForSeconds(0.1f); // 根据需要设置帧率
        }
    }
    private void ParseLandmarks(JObject landmarks, string key, List<Vector2> normalizedPositions)
    {
        if (landmarks.ContainsKey(key))
        {
            JArray points = (JArray)landmarks[key];
            if (points != null)
            {
                foreach (JObject point in points)
                {
                    float x = (float)point["x"];
                    float y = (float)point["y"];
                    normalizedPositions.Add(new Vector2(x, y));
                }
            }
        }
        else
        {
            Debug.LogWarning($"Key '{key}' not found in landmarks.");
        }
    }
}