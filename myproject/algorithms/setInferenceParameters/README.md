# Set Inference Parameters
Set parameters for object detection model
Version: 0.0.1
License: MIT
Homepage: []

## Parameters:
Name|Description|Required
---|---|:---:
cfg_file_path|Set file path to network configuration file *.cfg|Yes
data_cfg_path|Set data config file path: *.data|Yes
weights_file_path|Set file path for pretrained weights: *.weights|Yes
image_file_path|Set image/video path|Yes
img_size|Image resized to img_size x img_size during inference. If unsure, default value generally works well|
fourcc|Four character code for output video encoding|
conf_thresh|Confidence threshold for image prediction. Predictions with probabilities below this threshold are ignored.|
nms_thresh|Non-maximum suppression threshold for removing duplicate boxes around the same object.|
backend|Backend to use|
save_text|Save text file of bounding box predictions|
save_image|Save Image/Video to output folder. If image/video is not saved, it can be output to browser with outputImageToBrowser algorithm.|
output_path|Include path to output folder if save images is true|

## Outputs:
Name|Description
---|---
jsonObject|Parameters JSON object for use as input to load and run inference algorithm
