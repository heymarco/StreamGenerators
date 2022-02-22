import numpy as np
from skmultiflow.data import random_rbf_generator, led_generator
from tensorflow import keras

from changeds.abstract import GradualChangeStream, RegionalChangeStream


class GradualMNIST(GradualChangeStream, RegionalChangeStream):
    def __init__(self, num_changes: int = 100, drift_length: int = 100, stretch: bool = True, preprocess=None):
        (x_train, y_train), (x_test, y_test) = keras.datasets.mnist.load_data()
        x_train = np.reshape(x_train, newshape=(len(x_train), x_train.shape[1] * x_train.shape[2]))
        x_test = np.reshape(x_test, newshape=(len(x_test), x_test.shape[1] * x_test.shape[2]))
        x = np.vstack([x_train, x_test])
        y = np.hstack([y_train, y_test])
        super(GradualMNIST, self).__init__(X=x, y=y, num_changes=num_changes, drift_length=drift_length,
                                           stretch=stretch, preprocess=preprocess)

    def id(self) -> str:
        return "MNIST"


class GradualFashionMNIST(GradualChangeStream, RegionalChangeStream):
    def __init__(self, num_changes: int = 100, drift_length: int = 100, stretch: bool = True, preprocess=None):
        (x_train, y_train), (x_test, y_test) = keras.datasets.fashion_mnist.load_data()
        x_train = np.reshape(x_train, newshape=(len(x_train), x_train.shape[1] * x_train.shape[2]))
        x_test = np.reshape(x_test, newshape=(len(x_test), x_test.shape[1] * x_test.shape[2]))
        x = np.vstack([x_train, x_test])
        y = np.hstack([y_train, y_test])
        super(GradualFashionMNIST, self).__init__(X=x, y=y, num_changes=num_changes, drift_length=drift_length,
                                                  stretch=stretch, preprocess=preprocess)

    def id(self) -> str:
        return "FMNIST"


class GradualCifar10(GradualChangeStream, RegionalChangeStream):
    def __init__(self, num_changes: int = 100, drift_length: int = 100, stretch: bool = True, preprocess=None):
        (x_train, y_train), (x_test, y_test) = keras.datasets.cifar10.load_data()
        x_train = x_train.dot([0.299, 0.587, 0.114])
        x_test = x_test.dot([0.299, 0.587, 0.114])
        x_train = np.reshape(x_train, newshape=(len(x_train), x_train.shape[1] * x_train.shape[2]))
        x_test = np.reshape(x_test, newshape=(len(x_test), x_test.shape[1] * x_test.shape[2]))
        x = np.vstack([x_train, x_test])
        y = np.hstack([y_train.reshape(-1), y_test.reshape(-1)])
        super(GradualCifar10, self).__init__(X=x, y=y, num_changes=num_changes, drift_length=drift_length,
                                             stretch=stretch, preprocess=preprocess)

    def id(self) -> str:
        return "CIFAR"


class GradualRBF(GradualChangeStream, RegionalChangeStream):
    def __init__(self, num_changes: int = 100, n_per_concept: int = 2000, drift_length: int = 100, stretch: bool = True,
                 dims: int = 100, n_centroids: int = 10, add_dims_without_drift=True, preprocess=None):
        self.add_dims_without_drift = add_dims_without_drift
        self.dims = dims
        sample_random_state = 0
        x = []
        no_drift = []
        for i in range(num_changes):
            model_random_state = i
            x.append(random_rbf_generator.RandomRBFGenerator(model_random_state=model_random_state,
                                                             sample_random_state=sample_random_state, n_features=dims,
                                                             n_centroids=n_centroids).next_sample(n_per_concept)[0])
            if add_dims_without_drift:
                no_drift_model_random_state = num_changes  # a random seed that we will not use to create drifts
                no_drift.append(random_rbf_generator.RandomRBFGenerator(model_random_state=no_drift_model_random_state,
                                                                        sample_random_state=sample_random_state,
                                                                        n_features=dims, n_centroids=n_centroids
                                                                        ).next_sample(n_per_concept)[0])
        y = np.asarray([i for i in range(num_changes) for _ in range(n_per_concept)])
        x = np.concatenate(x, axis=0)
        if add_dims_without_drift:
            noise = np.concatenate(no_drift, axis=0)
            x = np.concatenate([x, noise], axis=1)
        if preprocess:
            x = preprocess(x)
        super(GradualRBF, self).__init__(X=x, y=y, num_changes=num_changes, drift_length=drift_length,
                                         stretch=stretch, preprocess=preprocess)

    def id(self) -> str:
        return "RBF"


class GradualLED(GradualChangeStream, RegionalChangeStream):
    def __init__(self, num_changes: int = 100, n_per_concept: int = 2000, drift_length: int = 100, stretch: bool = True,
                 has_noise=True, preprocess=None):
        self.has_noise = has_noise
        random_state = 0
        x = []
        for i in range(num_changes):
            x.append(led_generator.LEDGenerator(random_state=random_state, has_noise=has_noise,
                                                noise_percentage=(i + 1) / num_changes if i % 2 == 1 else 0
                                                ).next_sample(n_per_concept)[0])
        y = np.asarray([i for i in range(num_changes) for _ in range(n_per_concept)])
        x = np.concatenate(x, axis=0)
        super(GradualLED, self).__init__(X=x, y=y, num_changes=num_changes, drift_length=drift_length,
                                         stretch=stretch, preprocess=preprocess)

    def id(self) -> str:
        return "LED"