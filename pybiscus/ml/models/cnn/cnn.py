import torch.nn as nn
from einops.layers.torch import Rearrange


def net(input_shape: int = 3, mid_shape: int = 6, n_classes: int = 10):
    """Create a simple CNN module.

    This module is definitely NOT here to provide a powerful architecture,
    but only to provide a simple example, to use out-of-the-box with Pybiscus.
    The presence of two BatchNorm and one LayerNorm instances are only for
    educational purposes. BatchNorms are known to have a lot of issues, in particular
    with the way they handle their internal state. To avoid issues, please turn
    the parameter 'track_running_stats' to False, like below.

    Parameters
    ----------
    input_shape : int, optional
        the number of channels of the input, by default 3
    mid_shape : int, optional
        number of channels at mid module, by default 6
    n_classes : int, optional
        number of classes, by default 10

    Returns
    -------
    nn.Sequential
    """
    model = nn.Sequential(
        nn.BatchNorm2d(num_features=input_shape, track_running_stats=False),
        nn.Conv2d(input_shape, mid_shape, 5),
        nn.LayerNorm(normalized_shape=[mid_shape, 28, 28]),
        nn.ReLU(),
        nn.MaxPool2d(2, 2),
        nn.Conv2d(mid_shape, 16, 5),
        nn.ReLU(),
        nn.MaxPool2d(2, 2),
        nn.BatchNorm2d(num_features=16, track_running_stats=False),
        Rearrange("b c h w -> b (c h w)"),
        nn.Linear(16 * 5 * 5, 120),
        nn.ReLU(),
        nn.Linear(120, 84),
        nn.ReLU(),
        nn.Linear(84, n_classes),
    )
    return model
