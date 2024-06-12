# eScriptorium Collate

[![PyPI - Version](https://img.shields.io/pypi/v/escriptorium-collate.svg)](https://pypi.org/project/escriptorium-collate)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/escriptorium-collate.svg)](https://pypi.org/project/escriptorium-collate)

---

**Table of Contents**

- [eScriptorium Collate](#escriptorium-collate)
  - [Installation](#installation)
    - [Requirements](#requirements)
      - [Vendored Binaries](#vendored-binaries)
    - [Virtual Environment](#virtual-environment)
    - [Install](#install)
  - [Quick Start](#quick-start)
    - [Instantiate the eScriptorium Connector](#instantiate-the-escriptorium-connector)
    - [Instantiate the Witness that will be Collated](#instantiate-the-witness-that-will-be-collated)
    - [Instantiate the Arguments to be Passed to CollateX](#instantiate-the-arguments-to-be-passed-to-collatex)
    - [Run the Collation](#run-the-collation)
  - [License](#license)

## Installation

### Requirements

- Python 3
- Java Runtime Environment (< 15)

#### Vendored Binaries

This package uses the CollateX `collatex-tools-1.7.1.jar` Java Archive. The Jar file is bundled with the package, so there is no need to download it separately. However, you will need to ensure that your system has a working Java Runtime Environment version < 15 accessible under `JAVA_HOME`.

### Virtual Environment

Before installing the package, it is a good idea to create a Python virtual environment:

```console
pip install virtualenv
virtualenv -p python3 venv
source venv/bin/activate
```

Alternatively:

```console
python3 -m venv venv
source venv/bin/activate
```

[Click here](https://docs.python-guide.org/dev/virtualenvs/) for a more detailed guide to Python virtual environments.

### Install

Once you have activated the virtual environment, install the package:

```console
pip install escriptorium-collate
```

## Quick Start

### Instantiate the eScriptorium Connector

```python
import os

from dotenv import load_dotenv
from escriptorium_connector import EscriptoriumConnector

load_dotenv(override=True)
url = str(os.getenv("ESCRIPTORIUM_URL"))
username = str(os.getenv("ESCRIPTORIUM_USERNAME"))
password = str(os.getenv("ESCRIPTORIUM_PASSWORD"))
api_key = str(os.getenv("ESCRIPTORIUM_API_KEY"))

if api_key:
    escr = EscriptoriumConnector(url, api_key=api_key)
else:
    escr = EscriptoriumConnector(url, username, password)

escr = EscriptoriumConnector(url, username, password)
```

The `.env` file should look like this:

```console
ESCRIPTORIUM_URL=your_escriptorium_url
ESCRIPTORIUM_API_KEY=your_escriptorium_api_key
ESCRIPTORIUM_USERNAME=your_escriptorium_username
ESCRIPTORIUM_PASSWORD=your_escriptorium_password
```

### Instantiate the Witness that will be Collated

```python
from escriptorium_collate.collate import Witness

witnesses = [
    Witness(
        pk=1,
        siglum="A",
        diplomatic_transcription_name="diplomatic",
        normalized_transcription_name="normalized",
    ),
    Witness(
        pk=2,
        siglum="B",
        diplomatic_transcription_name="diplomatic",
        normalized_transcription_name="normalized",
    ),
    Witness(
        pk=3,
        siglum="C",
        diplomatic_transcription_name="diplomatic",
        normalized_transcription_name="normalized",
    ),
]
```

### Instantiate the Arguments to be Passed to CollateX

```python
from escriptorium_collate.collate import CollatexArgs

collatex_args = CollatexArgs()
```

### Run the Collation

```python
collatex_output = collate(escr=escr, witnesses=witnesses, collatex_args=collatex_args)
```

## License

`escriptorium-collate` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
