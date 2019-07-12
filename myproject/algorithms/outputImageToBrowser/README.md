# Output Image To Browser
Print image (jpeg, png) or video (mp4) to browser as chain output. Enter either file path, image as numpy array, or image data object (output from load and run inference)
Version: 0.0.1
License: MIT
Homepage: []

## Parameters:
Name|Description|Required
---|---|:---:
file_path|File Path|
image_data_object|Output of load and run inference model outputs an object with the data and the compression information|
image_array|Output an image from a numpy array input (must be bgr colorspace)|
extension|If inputting a numpy image array, please specify which compression to use|

## Outputs:
Name|Description
---|---
