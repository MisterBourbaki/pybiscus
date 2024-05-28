# How to use config files

Here are a few hints about how to use and customize the config files (server, client).

## Fabric

The keyword `fabric` holds a dictionnary of keywords to use by the Fabric instance. It is used by both Server and Clients. The keywords and their types are simply the one provided by the Fabric API.

Here is an example from the file `configs/server.yml`:

```yaml
...
fabric:
  accelerator: gpu
  devices:
    - 0
...
```

The keyword `devices` is waiting for either a list of integers (the id of the devices themselves) or an integer (for the number of devices wanted). To use CPU for instance, you can simply write

```yaml
...
fabric:
  accelerator: cpu
  # devices:
...
```

The keyword `devices` is left intentionnaly commented, as Fabric will automatically find a suitable device corresponding to the choice cpu.

## Models

Thanks to jsonargparse and its ability to handle dependency injection, any LightningModule can be used with Pybiscus. It just needs to be either install via a Python library, in the same virtual environment as Pybiscus, or accessible via the path.

In the `server.yml` configuration file available (and in the client files too), the model is defined by

```yaml
...
model:
  class_path: pybiscus.ml.models.cnn.lit_cnn.LitCNN
  init_args:
    input_shape: 3
    mid_shape: 6
    n_classes: 10
    lr: 0.001
...
```

which means that the CLI will use the LightningModule at the path `pybiscus.ml.models.cnn.lit_cnn.LitCNN`, and use the arguments passed after the `init_args` keyword.

To use a different model, available in the Python path, change the `class_path` to point to your model, and change the `init_args` accordingly.

## Data

(see Models)

## Others
