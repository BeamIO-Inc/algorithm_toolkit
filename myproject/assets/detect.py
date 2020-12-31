from assets.models import *
from assets.utils import *
from assets.datasets import *
from atkEnv.keys import * # secret keys stored here, ignored in git commits, *change this to .env file secret keys

from sys import platform

import time, base64

def detect(
        cfg,
        data_cfg,
        weights,
        images,  # input folder
        output, # output folder
        fourcc='H264',  # output video encoding
        img_size=416,  # resize images for inferencing
        conf_thres=0.5,
        nms_thres=0.5,
        save_txt=False,
        save_images=False,
        backend=False,
        classofinterest = 'car',
        includetwittergraph = False, # graph options are set in load and run inference layer
        twitterOptions=None
    ):

    device = torch_utils.select_device(force_cpu=backend)

    if save_images | save_txt:
        if os.path.exists(output) & (save_images | save_txt):
            shutil.rmtree(output)  # delete output folder
        os.makedirs(output)  # make new output folder

    model = Darknet(cfg, (img_size, img_size))

    # Load weights
    if weights.endswith('.pt'):  # pytorch format
        model.load_state_dict(torch.load(weights, map_location=device)['model'])
    else:  # darknet format
        _ = load_darknet_weights(model, weights)

    # Fuse Conv2d + BatchNorm2d layers
    model.fuse()

    # Eval mode
    model.to(device).eval()

    # Set Dataloader
    vid_path, vid_writer = None, None
    dataloader = LoadImages(images, img_size=img_size)

    # Get classes and colors
    names_directory = parse_data_cfg(data_cfg)['names']
    # print(names_directory)
    classes = load_classes(names_directory)
    colors = [[random.randint(0, 255) for _ in range(3)] for _ in range(len(classes))]

    segmented_images = {} # return object

    np_array_or_byte = None

    classTracker = None

    interval = 1 # # of frames between points on the graph i.e. 30 frames, interval 10 -> 0,10,20,30

    for i, (path, img, im0, vid_cap) in enumerate(dataloader):
        if (dataloader.mode == 'video') & (type(classTracker) == type(None)):

            graphPts = int(dataloader.nframes / interval) + 1

            classTracker = np.zeros(graphPts)

            mslabels = np.zeros(graphPts) # populate graph labels as inference runs

        t = time.time()
        im_name = Path(path).name
        save_path = str(Path(output) / im_name)
        _, ext = os.path.splitext(im_name)
        ext = 'jpeg' if ext[1:] == 'jpg' else ext[1:] # exclude the dot

        tmpFile = 'tmp_'+im_name

        # Get detections
        img = torch.from_numpy(img).unsqueeze(0).to(device)
        pred, _ = model(img)
        det = non_max_suppression(pred, conf_thres, nms_thres)[0]

        currentFrame = vid_cap.get(cv2.CAP_PROP_POS_FRAMES)
        # currentMS = vid_cap.get(cv2.CAP_PROP_POS_MSEC)

        if (dataloader.mode == 'video') & (currentFrame % interval == 0.0):
            mslabels[int(currentFrame/interval)] = round(vid_cap.get(cv2.CAP_PROP_POS_MSEC), 2)
            # print('Updating ms {} labels at index: {}'.format(vid_cap.get(cv2.CAP_PROP_POS_MSEC),str(i)))

        if det is not None and len(det) > 0:
            # Rescale boxes from prediction size to true image size
            det[:, :4] = scale_coords(img.shape[2:], det[:, :4], im0.shape).round()

            # Print results to screen
            print('%gx%g ' % img.shape[2:], end='') # print image size

            for c in det[:, -1].unique():
                n = (det[:, -1] == c).sum()
                if (dataloader.mode == 'video') & (classes[int(c)] == classofinterest):
                    if (currentFrame % interval == 0.0):
                        classTracker[int(currentFrame / interval)] = n
                print('%g %s ' % (n, classes[int(c)]), end=', ')

            # Draw bounding boxes and labels of detections
            for *xyxy, conf, cls_conf, cls in det:
                if save_txt:
                    with open(save_path + '.txt', 'a+') as file:
                        file.write(('%g ' * 6 + '\n') % (*xyxy, cls, conf))

                # Add bbox to the image
                label = '%s %.2f' % (classes[int(cls)], conf)
                plot_one_box(xyxy, im0, label=label, color=colors[int(cls)])

        print('Done. (%.3fs)' % (time.time() - t))

        # print('Frames Processed: ' + str(frames))

        if dataloader.mode == 'images':
            if save_images:
                cv2.imwrite(save_path, im0)
            else:
                np_array_or_byte = im0
        else:
            if vid_path != save_path:  # start of video, set up videowriter + save path
                vid_path = save_path
                fps = vid_cap.get(cv2.CAP_PROP_FPS)
                width = int(vid_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(vid_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                resize = False

                # make sure aspect ratio for fourcc is ok
                aspectratio = width / height
                if (aspectratio == 4/3) | (aspectratio == 16/9) | (aspectratio == 1/1):
                    f = fourcc
                else:
                    f = 'mp4v'

                if save_images:
                    vid_writer = cv2.VideoWriter(vid_path, cv2.VideoWriter_fourcc(*f), fps, (width, height))
                else:
                    # https://sibsoft.net/xvideosharing/info_video_dimensions.html
                    # h264/avc1 dimensions should be in multiples of 8 or 16
                    ffmpegConvert = False
                    if (aspectratio == 16/9) & (width > 896): # resize aspect ratio 16:9
                        width, height = 896, 504
                        print('Resizing video to fit browser: width %s x height %s' % (width, height))
                        resize = True
                    if (aspectratio == 1/1) & (width > 800): # resize aspect ratio 1:1
                        width, height = 800, 800
                        print('Resizing video to fit browser: width %s x height %s' % (width, height))
                        resize = True
                    if (aspectratio == 4/3) & (width > 960): # resize aspect ratio 4:3
                        width, height = 960, 720
                        print('Resizing video to fit browser: width %s x height %s' % (width, height))
                        resize = True

                    # For displaying video to browser:
                    # if aspect ratio is fine for h264, force encoding to be h264 (html5 video only supports h264)
                    # otherwise, write video as mp4v then use ffmpeg to -> h264
                    if (aspectratio == 4/3) | (aspectratio == 16/9):
                        vid_writer = cv2.VideoWriter(tmpFile, cv2.VideoWriter_fourcc(*'h264'), fps, (width, height))
                    else:
                        vid_writer = cv2.VideoWriter(tmpFile, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))
                        ffmpegConvert = True
            if resize:
                vid_writer.write(cv2.resize(im0, (width, height)))
            else:
                vid_writer.write(im0)

    if save_images:
        if dataloader.mode == 'video':
            vid_writer.release()
        print('Results saved to %s' % output)
        if platform == 'darwin':  # macos
            os.system('open ' + output + ' ' + save_path)

    else: # write images to browser
        if dataloader.mode == 'video':
            vid_writer.release()

            # for videos with strange aspect ratios (i.e. shot on iphone), the opencv
            # h264 compression doesn't work. Temporary workaround for now is to use mp4v then
            # convert to h264 with ffmpeg cli.

            if ffmpegConvert:
                tmpfile1 = 'tmp_h264_' + im_name
                os.system('ffmpeg -i {0} -an -vcodec libx264 -crf 17 {1}'.format(tmpFile, tmpfile1))
                os.remove(tmpFile)  # convert temporary video to h264 via ffmpeg
                np_array_or_byte = open(tmpfile1, 'rb').read()
                os.remove(tmpfile1)  # remove temporary video
            else:
                np_array_or_byte = open(tmpFile, 'rb').read()
                os.remove(tmpFile)  # remove temporary video
            segmented_images['data'] = np_array_or_byte
            segmented_images['ext'] = ext
            segmented_images['class_tracker_data'] = {'labels': mslabels.tolist(), 'datasets': [
                {'label': classofinterest, 'borderColor': 'rgb(255, 99, 132)', 'data': classTracker.tolist(),
                 'fill': 'false'}]}

            # add location and time range info into segmented_images to pull twitter data:
            segmented_images['twitter'] = includetwittergraph
            if twitterOptions != None:
                segmented_images['twitterOptions'] = twitterOptions
            else:
                segmented_images['twitter'] = False

            authkeystr = cons_api_key+':'+cons_api_secret

            encodedBytes = base64.b64encode(authkeystr.encode("utf-8"))
            encodedStr = str(encodedBytes, "utf-8")
            segmented_images['authKey'] = encodedStr

        else:
            segmented_images['data'] = np_array_or_byte # image as np array (bgr)
            segmented_images['ext'] = ext # include extension of data for mimetype

    return segmented_images
