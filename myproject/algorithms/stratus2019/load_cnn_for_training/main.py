from algorithm_toolkit import Algorithm, AlgorithmChain
from keras.models import Model
import resippy.image_recognition.neural_net_model_training.keras_model_training as keras_retraining


class Main(Algorithm):

    def run(self):
        cl = self.cl  # type: AlgorithmChain.ChainLedger
        params = self.params  # type: dict
        # Add your algorithm code here
        model_type = params['model_type']
        pretrained_weights_path = params['pretrained_weights_path']

        cnn_model_key = 'cnn_model'

        cnn_model = None        # type: Model

        if model_type == 'vgg16':
            cnn_model = keras_retraining.load_vgg16_model(weights_path=pretrained_weights_path, include_top=False)
        elif model_type == 'vgg19':
            cnn_model = keras_retraining.load_vgg19_model(weights_path=pretrained_weights_path, include_top=False)
        elif model_type == 'resnet50':
            cnn_model = keras_retraining.load_resnet50_model(weights_path=pretrained_weights_path, include_top=False)

        cl.add_to_metadata(cnn_model_key, cnn_model)
        # Do not edit below this line
        return cl
