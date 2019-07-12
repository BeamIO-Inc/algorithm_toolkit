from algorithm_toolkit import Algorithm, AlgorithmChain
import json

class Main(Algorithm):

    def run(self):
        cl = self.cl  # type: AlgorithmChain.ChainLedger
        params = self.params  # type: dict
        # Add your algorithm code here

        try:
            file =  open(params['txt_file_path'], 'r')
            configstr = file.read()
            jsonObj = json.loads(configstr)
            if type(jsonObj['conf_thresh']) != float:
                jsonObj['conf_thresh'] = float(jsonObj['conf_thresh'])
            if type(jsonObj['nms_thresh']) != float:
                jsonObj['nms_thresh'] = float(jsonObj['nms_thresh'])
            if type(jsonObj['img_size']) != int:
                jsonObj['img_size'] = int(jsonObj['img_size'])
            jsonObj['save_text'] = jsonObj['save_text'] == 'True'
            jsonObj['save_images'] = jsonObj['save_images'] == 'True'
            cl.add_to_metadata('jsonObject', jsonObj)

        except FileNotFoundError as e:
            self.raise_client_error('Config file could not be read, check file path')
        except json.decoder.JSONDecodeError as e:
            self.raise_client_error('Problem with decoding JSON, please make sure format is correct, (use double quotes around all strings): ' + str(e))
        except ValueError as e:
            self.raise_client_error(str(e) + ', check argument')

        # Do not edit below this line
        return cl
