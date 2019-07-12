from algorithm_toolkit import Algorithm, AlgorithmChain

from PIL import Image
import numpy as np
import io, base64
import cv2 as cv

ext2Mime = { # supported types: jpeg, png, bmp, ico
    'jpeg' : 'image/jpeg',
    'jpg' : 'image/jpeg',
    'png' : 'image/png',
    'bmp' : 'image/bmp',
    'ico' : 'image/ico',
    'mp4' : 'video/mp4'
}

videotypes = ['mp4']
imagetypes = ['jpeg', 'jpg', 'png', 'bmp', 'ico']

class Main(Algorithm):

    def tmpImgWrite(self, img, ext):
        img = cv.cvtColor(img, cv.COLOR_BGR2RGB)
        im = Image.fromarray(img)
        imgByteString = io.BytesIO()

        im.save(imgByteString, ext)
        return str(base64.b64encode(imgByteString.getvalue()), 'utf-8')

    def run(self):
        cl = self.cl  # type: AlgorithmChain.ChainLedger
        params = self.params  # type: dict
        # Add your algorithm code here

        try:
            if 'file_path' in params:
                filepath = params['file_path']
                slashInd = filepath.rfind('/')
                file_name = filepath[slashInd + 1:]

                dotIndex = file_name.find('.')
                ext = file_name[dotIndex+1:]

                if (file_name.find('.') == -1) | (ext not in ext2Mime):
                    raise TypeError(
                        'This type of image not supported right now, or file name format is wrong, please use /.../[filename].[extension]')

                mimeType = ext2Mime[ext]
                fileog = open(filepath, 'rb').read()
                encoded = base64.b64encode(fileog)
                decoded = encoded.decode('utf-8')

            elif 'image_array' in params:
                img = params['image_array'] # Image array must be in BGR format
                ext = params['extension']
                mimeType = ext2Mime[ext]

                decoded = self.tmpImgWrite(img, ext)
                file_name = ''

            elif 'image_data_object' in params:
                ext = params['image_data_object']['ext']
                mimeType = ext2Mime[ext]
                data = params['image_data_object']['data']
                includeGraph = False
                if ext in videotypes:
                    decoded = base64.b64encode(data).decode('utf-8')
                    graphDataObj = params['image_data_object']['class_tracker_data']
                    includeGraph = True
                else:
                    decoded = self.tmpImgWrite(data, ext)
                file_name = ''

            else:
                raise IOError('Please include image data or file path ')

            chain_output = {
                'output_type': 'binary',
                'output_value': {
                    "mimetype": mimeType,
                    "file": decoded,
                    "filename": file_name,
                    "graphData": graphDataObj if includeGraph else 'none'
                }
            }

        except KeyError as e:
            self.raise_client_error('Error thrown in outputImageToBrowser, missing parameter: ' + str(e.args[0]))

        except Exception as e:
            self.raise_client_error('Error thrown in outputImageToBrowser: ' + str(e))

        cl.add_to_metadata('chain_output_value', chain_output)
        # Do not edit below this line
        return cl
