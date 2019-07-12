# input yolo configuration text file
Input file path to text file with json configuration for yolo network:
{
cfg_file_path: [file path to *.cfg],
data_cfg_path: [file path to *.data],
weights_file_path: [file path to *.weights],
file_path: [file path to image],
fourcc: [type of video compression, mpv4 by default],
img_size: [images scaled down to this size during inference, 416 by default],
conf_thresh: [confidence threshold, 0.5 by default],
nms_thresh: [nms threshold, 0.5 by default],
save_text: [true or false],
save_images: [true or false],
backend: [CPU or GPU],
+save_path: [optional parameter, include if save_text or save_images is true]
}
Version: 0.0.1
License: MIT
Homepage: []

## Parameters:
Name|Description|Required
---|---|:---:
txt_file_path|File path to json config file|Yes

## Outputs:
Name|Description
---|---
jsonObject|JSON object parsed from text file
