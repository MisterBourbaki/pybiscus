# Pybiscus: a flexible Federated Learning Framework

## Introduction

Pybiscus is a simple tool to perform Federated Learning on various models and datasets.
It aims at automated as much as possible the FL pipeline, and allows to add virtually any kind of dataset and model.

Pybiscus is built on top of Flower, a mature Federated Learning framework; jsonargparse (script and CLI parts) and Lightning/Fabric for all the Machine Learning machinery.

The project is still a work-in-progress, and Pybiscus is not yet available as a proper Python package. To use Pybiscus, the best course of action for now is to use [Rye](https://rye.astral.sh/), a very powerful comprehensive project and package management solution for Python.

## Get started

Using Rye, it is as simple as

```bash
rye sync --all-features
```

if you aim at contributing to the project, or simply

```bash
rye sync
```

to install only the core dependencies.

## Documentation

Documentation is available at [docs](docs/).

## Contributing

If you are interested in contributing to the Pybiscus project, start by reading the [Contributing guide](/CONTRIBUTING.md).

## Who uses Pybiscus

Pybiscus is on active development at Thales, both for internal use and on some collaborative projects. One major use is in the Europeean Project [PAROMA-MED](https://paroma-med.eu), dedicated to Federated Learning in the context of medical data distributed among several Hospitals.

## License

The License is Apache 2.0. You can find all the relevant information here [LICENSE](/LICENSE.md)

<!-- The chosen license in accordance with legal department must be defined into an explicit [LICENSE](https://github.com/ThalesGroup/template-project/blob/master/LICENSE) file at the root of the repository
You can also link this file in this README section. -->
