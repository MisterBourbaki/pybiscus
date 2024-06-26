from collections import OrderedDict
from typing import Union

import flwr as fl
import torch
from lightning.fabric import Fabric
from lightning.pytorch import LightningDataModule, LightningModule
from pydantic import BaseModel, ConfigDict, Field

from pybiscus.console import console
from pybiscus.ml.data.cifar10.cifar10_datamodule import ConfigData_Cifar10
from pybiscus.ml.loops_fabric import test_loop, train_loop
from pybiscus.ml.models.cnn.lit_cnn import ConfigModel_Cifar10
from pybiscus.ml.registry import datamodule_registry, model_registry

torch.backends.cudnn.enabled = True


class ConfigFabric(BaseModel):
    """A Pydantic Model to validate the Client configuration given by the user.

    This is a (partial) reproduction of the Fabric API found here:
    https://lightning.ai/docs/fabric/stable/api/generated/lightning.fabric.fabric.Fabric.html#lightning.fabric.fabric.Fabric

    Attributes
    ----------
    accelerator:
        the type of accelerator to use: gpu, cpu, auto... See the Fabric documentation for more details.
    devices: optional
        either an integer (the number of devices needed); a list of integers (the id of the devices); or
        the string "auto" to let Fabric choose the best option available.
    """

    accelerator: str
    devices: Union[int, list[int], str] = "auto"


class ConfigClient(BaseModel):
    """A Pydantic Model to validate the Client configuration given by the user.

    Attributes
    ----------
    cid: int
        client identifier
    pre_train_val: optional, default to False
        if true, at the beginning of a new fit round a validation loop will be performed.
        This allows to perform a validation loop on the validation dataset of the Client,
        after the client received the new, aggregated weights.
    server_adress: str
        the server adress and port
    root_dir: str
        the path to a "root" directory, relatively to which can be found Data, Experiments and other useful directories
    fabric: dict
        a dictionnary holding all necessary keywords for the Fabric instance
    model: dict
        a dictionnary holding all necessary keywords for the LightningModule used
    data: dict
        a dictionnary holding all necessary keywords for the LightningDataModule used.
    """

    cid: int
    pre_train_val: bool = Field(default=False)
    server_adress: str
    root_dir: str
    fabric: ConfigFabric
    model: ConfigModel_Cifar10
    data: ConfigData_Cifar10

    # Below is used when several models and/or datasets are available.
    # model: Union[ConfigModel_Cifar10, ...] = Field(discriminator="name")
    # data: Union[ConfigData_Cifar10, ...] = Field(discriminator="name")

    model_config = ConfigDict(extra="forbid")


class FlowerClient(fl.client.NumPyClient):
    """A Fabric-based, modular Flower Client.

    The present FlowerClient override the usual Flower Client, by using Fabric as a backbone.
    The Client now holds data, the model and a Fabric instance which takes care of everything regarding
    hardware, precision and such.

    """

    def __init__(
        self,
        cid: int,
        model: LightningModule,
        data: LightningDataModule,
        num_examples: dict[str, int],
        conf_fabric: ConfigFabric,
        pre_train_val: bool = False,
    ) -> None:
        """Initialize the FlowerClient instance.

        Override the usual fl.client.NumPyClient configuration and add data, model and fabric attributes.

        Parameters
        ----------
        cid : int
            the client identifier
        model : LightningModule
            the model used for the FL training
        data : LightningDataModule
            the data used for the training/validation process
        num_examples : dict[str, int]
            needed by Flower, for the FedAvg Streategy typically
        conf_fabric : ConfigFabric
            a Pydantic-validated configuration for the Fabric instance
        """
        super().__init__()
        self.cid = cid
        self.model = model
        self.data = data

        self.conf_fabric = dict(conf_fabric)
        self.num_examples = num_examples
        self.pre_train_val = pre_train_val

        self.optimizer = self.model.configure_optimizers()

        self.fabric = Fabric(**self.conf_fabric)

    def initialize(self):
        self.fabric.launch()
        self.model, self.optimizer = self.fabric.setup(self.model, self.optimizer)
        (
            self._train_dataloader,
            self._validation_dataloader,
        ) = self.fabric.setup_dataloaders(
            self.data.train_dataloader(), self.data.val_dataloader()
        )

    def get_parameters(self, config):
        console.log(f"[Client] get_parameters, config: {config}")
        return [val.cpu().numpy() for _, val in self.model.state_dict().items()]

    def set_parameters(self, parameters):
        console.log("[Client] set_parameters")
        params_dict = zip(self.model.state_dict().keys(), parameters)
        state_dict = OrderedDict({k: torch.tensor(v) for k, v in params_dict})
        self.model.load_state_dict(state_dict, strict=True)

    def fit(self, parameters, config):
        console.log(f"[Client {self.cid}] fit, config: {config}")
        self.set_parameters(parameters)
        metrics = {}

        if self.pre_train_val:
            console.log(
                f"Round {config['server_round']}, pre train validation started..."
            )
            results_pre_train = test_loop(
                self.fabric, self.model, self._validation_dataloader
            )
            for key, val in results_pre_train.items():
                metrics[f"{key}_pre_train_val"] = val

        console.log(f"Round {config['server_round']}, training Started...")
        results_train = train_loop(
            self.fabric,
            self.model,
            self._train_dataloader,
            self.optimizer,
            epochs=config["local_epochs"],
        )
        console.log(f"Training Finished! Loss is {results_train['loss']}")
        metrics["cid"] = self.cid
        for key, val in results_train.items():
            metrics[key] = val
        return self.get_parameters(config={}), self.num_examples["trainset"], metrics

    def evaluate(self, parameters, config):
        console.log(f"[Client {self.cid}] evaluate, config: {config}")
        self.set_parameters(parameters)
        metrics = {}
        console.log(f"Round {config['server_round']}, evaluation Started...")
        results_evaluate = test_loop(
            self.fabric, self.model, self._validation_dataloader
        )
        console.log(
            f"Evaluation finished! Loss is {results_evaluate['loss']}, metric {list(results_evaluate.keys())[0]} is {results_evaluate[list(results_evaluate.keys())[0]]}"
        )
        metrics["cid"] = self.cid
        for key, val in results_evaluate.items():
            metrics[key] = val
        return results_evaluate["loss"], self.num_examples["valset"], metrics


class Client:
    """Launch a FlowerClient.

    This is a Typer command to launch a Flower Client, using the configuration given by config.

    Parameters
    ----------
    config: Path
        path to a config file
    cid: int, optional
        the client id
    root_dir: str, optional
        the path to a "root" directory, relatively to which can be found Data, Experiments and other useful directories
    server_adress: str, optional
        the server adress and port

    Raises
    ------
    ValidationError
        the Pydantic error raised if the config is not validated.
    """

    def __init__(
        self,
        cid: int,
        conf_data: ConfigData_Cifar10,
        conf_model: ConfigModel_Cifar10,
        conf_fabric: ConfigFabric,
        pre_train_val: bool,
    ) -> None:
        name_data = conf_data.name
        conf_data = dict(conf_data.config)
        name_model = conf_model.name
        conf_model = dict(conf_model.config)
        conf_fabric = dict(conf_fabric)

        data = datamodule_registry[name_data](**conf_data)
        data.setup(stage="fit")
        num_examples = {
            "trainset": len(data.train_dataloader()),
            "valset": len(data.val_dataloader()),
        }

        model = model_registry[name_model](**conf_model)
        self.client = FlowerClient(
            cid=cid,
            model=model,
            data=data,
            num_examples=num_examples,
            conf_fabric=conf_fabric,
            pre_train_val=pre_train_val,
        )

    def start(self, server_adress: str):
        self.client.initialize()
        client = self.client.to_client()
        fl.client.start_client(
            server_address=server_adress,
            client=client,
        )
