from algorithm_toolkit import Algorithm, AlgorithmChain


class Main(Algorithm):

    def run(self):
        cl = self.cl  # type: AlgorithmChain.ChainLedger
        params = self.params  # type: dict
        # Add your algorithm code here
        try:
            paramJsonObject = {}
            paramJsonObject['cfg_file_path'] = params['cfg_file_path']
            paramJsonObject['weights_file_path'] = params['weights_file_path']
            paramJsonObject['data_cfg_path'] = params['data_cfg_path']
            paramJsonObject['file_path'] = params['image_file_path']
            paramJsonObject['output_path'] = params['output_path'] if 'output_path' in params else 'output'
            paramJsonObject['fourcc'] = params['fourcc'] if 'fourcc' in params else 'H264'
            paramJsonObject['img_size'] = params['img_size']
            paramJsonObject['conf_thresh'] = params['conf_thresh']
            paramJsonObject['nms_thresh'] = params['nms_thresh']
            paramJsonObject['backend'] = params['backend'] == 'CPU'
            paramJsonObject['save_text'] = params['save_text'] == 'True'
            paramJsonObject['save_images'] = params['save_image'] == 'True'

            cl.add_to_metadata('jsonObject', paramJsonObject)
        except KeyError as e:
            self.raise_client_error('Missing key in setInferenceParameters: ' + str(e.args[0]))
        except Exception as e:
            self.raise_client_error('Error in setInferenceParameters: ' + str(e))

        # Do not edit below this line
        return cl
