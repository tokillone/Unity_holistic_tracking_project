using UnityEngine;
using System;
using System.Collections;
using UnityEngine.UI;
using System.Collections.Generic;

public class CameraCapture : MonoBehaviour
{
    public RawImage display; // 显示摄像头预览（可选）

    public GameObject keypointPrefab;
    public Transform keypointContainer;
    private WebCamTexture webcamTexture;
    private List<GameObject> keypoints =new();

    void Awake()
    {
        // 使用默认摄像头（Pico 摄像头），根据需要指定设备名
        webcamTexture = new WebCamTexture();
        display.texture = webcamTexture;//show at the rawimage 
        webcamTexture.Play();
        Debug.Log("摄像头已经打开");

        StartCoroutine(AdjustRawImageSize());
    }

    private IEnumerator AdjustRawImageSize()
    {
        while (webcamTexture.width <= 100 || webcamTexture.height <= 100)
        {
            yield return null;
        }
        Debug.Log($"摄像头分辨率: {webcamTexture.width}x{webcamTexture.height}");
        RectTransform rectTransform = display.GetComponent<RectTransform>();
        // 计算摄像头的宽高比
        float cameraAspect = (float)webcamTexture.width / webcamTexture.height;

        // 根据摄像头的宽高比调整RawImage的尺寸
        if (cameraAspect > 1)
        { // 横向画面
            rectTransform.sizeDelta = new Vector2(rectTransform.rect.height * cameraAspect, rectTransform.rect.height);
        }
        else
        { // 纵向画面
            rectTransform.sizeDelta = new Vector2(rectTransform.rect.width, rectTransform.rect.width / cameraAspect);
        }

        // 在控制台输出RawImage调整后的尺寸
        Debug.Log($"RawImage 尺寸已调整为: {rectTransform.sizeDelta}");



    }

    // 将摄像头当前帧转换为 JPEG 数据
    public byte[] GetFrameBytes()
    {
        // Texture2D tex = new Texture2D(webcamTexture.width, webcamTexture.height);
        Texture2D tex = new(webcamTexture.width, webcamTexture.height);
        tex.SetPixels(webcamTexture.GetPixels());
        tex.Apply();
        return tex.EncodeToJPG(5);
    }

    public void UdpdateKeypoints(List<Vector2> normalizedPositions){
        ClearKeypoints();

        foreach(var pos in normalizedPositions){
            Vector2 localPosition =NormalizedToLocalPosition(pos);

            GameObject keypoint=Instantiate(keypointPrefab,keypointContainer);
            keypoint.GetComponent<RectTransform>().anchoredPosition=localPosition;
            keypoints.Add(keypoint);
        }

    }
    private Vector2 NormalizedToLocalPosition(Vector2 normalizedPos){
        RectTransform rectTransform=display.GetComponent<RectTransform>();
        Vector2 imageSize=rectTransform.rect.size;

        float x=(normalizedPos.x-0.5f)*imageSize.x;
        float y=(0.5f-normalizedPos.y)*imageSize.y;
        return new Vector2(x,y);
    }
    private void ClearKeypoints(){
        foreach (var keypoint in keypoints){
            Destroy(keypoint);
        }
        keypoints.Clear();
    }
}

