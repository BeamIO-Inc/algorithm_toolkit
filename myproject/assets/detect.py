from assets.models import *
from assets.utils import *
from assets.datasets import *

from sys import platform

import time

def detect(
        cfg,
        data_cfg,
        weights,
        images,  # input folder
        output, # output folder
        fourcc='H264',  # output video encoding
        img_size=416,  # resize img_size x img_size
        conf_thres=0.5,
        nms_thres=0.5,
        save_txt=False,
        save_images=False,
        backend=False,
        classofinterest = 'car'
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

    segmented_images = {}

    np_array_or_byte = None

    classTracker = None

    divisor = 30 # number of discrete points on graph, this will depend on how long the video is ...


    for i, (path, img, im0, vid_cap) in enumerate(dataloader):

        if (dataloader.mode == 'video') & (type(classTracker) == type(None)):
            vid_cap.set(cv2.CAP_PROP_POS_AVI_RATIO, 1)

            duration = vid_cap.get(cv2.CAP_PROP_POS_MSEC)

            vid_cap.set(cv2.CAP_PROP_POS_AVI_RATIO, 0)

            classTracker = np.zeros(int(vid_cap.get(cv2.CAP_PROP_FRAME_COUNT) / divisor))

            mslabels = np.around(np.linspace(0, duration, int(vid_cap.get(cv2.CAP_PROP_FRAME_COUNT)/divisor)), 2)

            #print('TYPE OF LABELS: ' + str(type(mslabels)))
            #print('TYPE OF DATA: ' + str(type(classTracker)))

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

        if det is not None and len(det) > 0:
            # Rescale boxes from 416 to true image size
            det[:, :4] = scale_coords(img.shape[2:], det[:, :4], im0.shape).round()

            # Print results to screen
            print('%gx%g ' % img.shape[2:], end='')  # print image size

            print('Millisecond: %.2f  ' % vid_cap.get(cv2.CAP_PROP_POS_MSEC), end='')

            for c in det[:, -1].unique():
                n = (det[:, -1] == c).sum()
                print('%g %s ' % (n, classes[int(c)]), end=', ')
                if (dataloader.mode == 'video'):
                    if (vid_cap.get(cv2.CAP_PROP_POS_FRAMES) % divisor == 0.0) & (classes[int(c)] == classofinterest):
                        print('Updating at index: ' + str(vid_cap.get(cv2.CAP_PROP_POS_FRAMES)/divisor))
                        classTracker[int(vid_cap.get(cv2.CAP_PROP_POS_FRAMES) / divisor)] = n

            # Draw bounding boxes and labels of detections
            for *xyxy, conf, cls_conf, cls in det:
                if save_txt:
                    with open(save_path + '.txt', 'a+') as file:
                        file.write(('%g ' * 6 + '\n') % (*xyxy, cls, conf))

                # Add bbox to the image
                label = '%s %.2f' % (classes[int(cls)], conf)
                plot_one_box(xyxy, im0, label=label, color=colors[int(cls)])

        print('Done. (%.3fs)' % (time.time() - t))

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
                if save_images:
                    vid_writer = cv2.VideoWriter(vid_path, cv2.VideoWriter_fourcc(*fourcc), fps, (width, height))
                else:
                    aspectratio = width/height
                    if (aspectratio == 16/9) & (width > 960) & (height > 540): # resize aspect ratio 16:9
                        width, height = 960, 540
                        print('Resizing video to fit browser: width %s x height %s' % (width, height))

                    if (aspectratio == 1/1) & (width > 800): # resize aspect ratio 1:1
                        width, height = 800, 800
                        print('Resizing video to fit browser: width %s x height %s' % (width, height))

                    if (aspectratio == 4/3) & (width > 960): # resize aspect ratio 4:3
                        width, height = 960, 720
                        print('Resizing video to fit browser: width %s x height %s' % (width, height))

                    vid_writer = cv2.VideoWriter(tmpFile, cv2.VideoWriter_fourcc(*fourcc), fps, (width, height))

            vid_writer.write(cv2.resize(im0, (width, height)))

    if save_images:
        if dataloader.mode == 'video':
            vid_writer.release()
        print('Results saved to %s' % output)
        if platform == 'darwin':  # macos
            os.system('open ' + output + ' ' + save_path)

    else:
        if dataloader.mode == 'video':
            vid_writer.release()
            np_array_or_byte = open(tmpFile, 'rb').read()
            segmented_images['data'] = np_array_or_byte
            segmented_images['ext'] = ext
            segmented_images['class_tracker_data'] = {'labels': mslabels.tolist(), 'datasets':[{'label': classofinterest, 'borderColor': 'rgb(255, 99, 132)', 'data': classTracker.tolist(), 'fill': 'false'}]}
            os.remove(tmpFile)  # remove temporary video
        else:
            segmented_images['data'] = np_array_or_byte # image as np array (bgr)
            segmented_images['ext'] = ext # include extension of data for mimetype


    return segmented_images
