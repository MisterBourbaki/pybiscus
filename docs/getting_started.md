# Pybiscus

A simple tool to perform Federated Learning on various models and datasets. Build on top of Flower (FL part), jsonargparse (script and CLI parts) and Lightning/Fabric (ML part).

## Uses of Pybiscus

You have two ways of using Pybiscus. Either by cloning the repo and installing (using Rye) all dependencies, and working on the code itself; or (in a later version) by just downloading the wheel and installing as a package.

### Installation

Using Rye, it is as simple as

```bash
rye sync --all-features
```

if you aim at contributing to the project, or simply

```bash
rye sync
```

to install only the core dependencies.

### Basic usage

The Pybiscus project comes with two applications, `pybiscus_server` and `pybiscus_client`. You can test if everything is working by running

```bash
rye run pybiscus_server --help
```

or, if you activated the virtual environnement created automatically by Rye

```bash
(.venv) pybiscus_server --help
```

For the client side, run

```bash
rye run pybiscus_client --help
```

Both server and client applications come with an `init` method that basically initializes the core Python class dedicated to the server or the client. The app `pybiscus_server` has a method `launch` to launch the Flower Server. The client app `pybiscus_client` has a method `start` to start a Flower Client.

The best way to use both CLI is by using directly a YAML configuration file, which holds all arguments necessary for launching a Federated training. Some templates are in the `configs/` folder.

To launch a full Federated training, for instance with the three clients whose configuration files are in `configs/`, you need to open four terminal windows and run successively

```bash
rye run pybiscus_server --config configs/server.yml
rye run pybiscus_client --config configs/client_1.yml
rye run pybiscus_client --config configs/client_2.yml
rye run pybiscus_client --config configs/client_3.yml
```

This will run a two-rounds training on a simple CNN model, using the classicla CIFAR10 dataset. This will run on CPU for all server and clients. To run on GPU, you can simply change the configuration files, as documented [here](configuration.md).


## Features

## Work in Progress

- [ ] Improving the Documentation part (Sphinx ?) and docstrings of the code.

- [ ] Implementation of the Simulation part of Flower.

- [ ] Organizing dependencies in pyproject.toml: dep from Typer/Flower/Fabric part (the core), dep from Paroma, dep from next data/model.

- [ ] Integration of Differential Privacy.

- [ ] Using only LightningDataModule, and getting rid of load_data.

- [x] Logging with tensorboard.

## Road Map

Here is a list of more mid/long term ideas to implement in Pybiscus for Federated Learning.
