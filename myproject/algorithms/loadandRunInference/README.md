# Load and run inference model
Load a yolo model for inference on an image or video.
Parameter JSON must be configured using the enclosed methods. Required parameters are: cfg file path, data cfg, weights path, image/video path, image size, fourcc, confidence threshold, and nms threshold. If unsure, the default parameters are generally robust. Many thanks to ultralytics for their wonderful open-source implementation.
Version: 0.0.1
License: MIT
Homepage: [https://github.com/ultralytics/yolov3]

## Parameters:
Name|Description|Required
---|---|:---:
parametersJSON||Yes

## Outputs:
Name|Description
---|---
image_data_obj|Image data object: {'ext': extension of file, 'data': byte string for video, or bgr numpy array for images}
