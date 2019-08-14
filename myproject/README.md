An example project with ATK, using [image recognition](https://github.com/ultralytics/yolov3) and public twitter data, we can generate insights of temporal points in videos where there might be 'high traffic'. We accept user input for hyperparameters, as well as time and date information for the twitter information. The input video is run frame-by-frame through an image recognition and twitter data from lat, lon, fromdate, todate inputs are used to pull twitter data.

Code for the image recognition functionality was borrowed generously from [ultralytics](https://github.com/ultralytics)

All credit goes to https://github.com/ultralytics/yolov3 for the 
working pytorch yolo model
