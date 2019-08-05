from algorithm_toolkit import Algorithm, AlgorithmChain


class Main(Algorithm):

    def run(self):
        cl = self.cl  # type: AlgorithmChain.ChainLedger
        params = self.params  # type: dict
        # Add your algorithm code here
        try: # set inference parameters from user input in atk
            paramJsonObject = {}

            for k in params:
                paramJsonObject[k] = params[k]

            paramJsonObject['output_path'] = params['output_path'] if 'output_path' in params else 'output'
            paramJsonObject['fourcc'] = params['fourcc'] if 'fourcc' in params else 'H264'
            paramJsonObject['img_size'] = params['img_size']
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
