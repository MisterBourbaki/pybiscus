import torch
from jsonargparse import ActionConfigFile, ArgumentParser
from rich.traceback import install

from pybiscus.console import console
from pybiscus.flower.client_fabric import Client

install()

torch.backends.cudnn.enabled = True


def client_cli():
    parser = ArgumentParser(description="This is it!", parser_mode="omegaconf")
    parser.add_class_arguments(Client, "client.init")
    parser.add_method_arguments(Client, "start", "client.start")

    parser.add_argument("--config", action=ActionConfigFile)

    cfg = parser.parse_args()
    console.log(cfg.as_dict())
    cfg = parser.instantiate_classes(cfg)
    console.log(cfg)
    client = cfg.client.init
    console.log(client)
    client.start(**cfg.client.start.as_dict())


if __name__ == "__main__":
    client_cli()
