# eScriptorium Collate

[![PyPI - Version](https://img.shields.io/pypi/v/escriptorium-collate.svg)](https://pypi.org/project/escriptorium-collate)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/escriptorium-collate.svg)](https://pypi.org/project/escriptorium-collate)

A Python library for collating eScriptorium documents. This is a pre-release version in public alpha.

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
    - [Return the CollateX Results as a Python Dictionary](#return-the-collatex-results-as-a-python-dictionary)
  - [API](#api)
    - [`escriptorium_collate.collate`](#escriptorium_collatecollate)
      - [`escriptorium_collate.collate.Witness`](#escriptorium_collatecollatewitness)
      - [`escriptorium_collate.collate.CollatexArgs`](#escriptorium_collatecollatecollatexargs)
      - [`escriptorium_collate.collate.get_collatex_input`](#escriptorium_collatecollateget_collatex_input)
      - [`escriptorium_collate.collate.get_collatex_output`](#escriptorium_collatecollateget_collatex_output)
      - [`escriptorium_collate.collate.collate`](#escriptorium_collatecollatecollate)
    - [`escriptorium_collate.transcription_layers`](#escriptorium_collatetranscription_layers)
      - [`escriptorium_collate.transcription_layers.create`](#escriptorium_collatetranscription_layerscreate)
      - [`escriptorium_collate.transcription_layers.copy`](#escriptorium_collatetranscription_layerscopy)
      - [`escriptorium_collate.transcription_layers.get_transcription_pk_by_name`](#escriptorium_collatetranscription_layersget_transcription_pk_by_name)
  - [License](#license)

## Installation

### Requirements

- Python 3
- Java Runtime Environment (< 15)

#### Vendored Binaries

This package uses the CollateX `collatex-tools-1.7.1.jar` Java Archive. The Jar file is bundled with the package, so there is no need to download it separately. However, you will need to ensure that your system has a working Java Runtime Environment version < 15 accessible under `JAVA_HOME`. [Click here](https://collatex.net/doc/) for more information about CollateX.

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

Once the virtual environment is activated, install the package:

```console
pip install escriptorium-connector @ git+https://gitlab.com/oeshera/escriptorium_python_connector
pip install escriptorium-collate
```

> [!NOTE]  
> This package depends on `escriptorium-connector`. However, the version of `escriptorium-connector` currently published on PyPi is not up to date with the latest development version of eScriptorium. Depending on the version of eScriptorium you are using, the PyPi version of `escriptorium-connector` may fail. As a temporary solution, the above-mentioned fork of `escriptorium-connector` can be used. It will work in most cases.

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
api_key = os.getenv("ESCRIPTORIUM_API_KEY")

if api_key:
    escr = EscriptoriumConnector(url, api_key=str(api_key))
else:
    escr = EscriptoriumConnector(url, username, password)
```

The `.env` file should look like this:

```console
ESCRIPTORIUM_URL=your_escriptorium_url
ESCRIPTORIUM_API_KEY=your_escriptorium_api_key
ESCRIPTORIUM_USERNAME=your_escriptorium_username
ESCRIPTORIUM_PASSWORD=your_escriptorium_password
```

You need only provide `ESCRIPTORIUM_API_KEY` or both `ESCRIPTORIUM_USERNAME` and `ESCRIPTORIUM_PASSWORD`.

### Instantiate the Witness that will be Collated

```python
from escriptorium_collate.collate import Witness

witnesses = [
    Witness(
        doc_pk=1,
        siglum="A",
        diplomatic_transcription_name="diplomatic",
        normalized_transcription_name="normalized",
    ),
    Witness(
        doc_pk=2,
        siglum="B",
        diplomatic_transcription_name="diplomatic",
        normalized_transcription_name="normalized",
    ),
    Witness(
        doc_pk=3,
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

### Return the CollateX Results as a Python Dictionary

```python
from escriptorium_collate.collate import collate

collatex_output = collate(escr=escr, witnesses=witnesses, collatex_args=collatex_args)
```

## API

This packaged contains two modules: `escriptorium_collate/collate.py` and `escriptorium_collate/transcription_layers.py`.

### `escriptorium_collate.collate`

#### `escriptorium_collate.collate.Witness`

An interface for defining an eScriptorium document as a witness to be passed to CollateX.

```python
class Witness(BaseModel):
  doc_pk: int # Primary key of an eScriptorium document (int)
  siglum: str # Arbitrary siglum to be used in the critical apparatus (str)
  diplomatic_transcription_pk: int | None
  diplomatic_transcription_name: str | None
  normalized_transcription_pk: int | None
  normalized_transcription_name: str | None
```

If `diplomatic_transcription_pk` is provided, `diplomatic_transcription_name` is ignored. Likewise, if `normalized_transcription_pk` is provided, `normalized_transcription_name` is ignored.

The "diplomatic" transcription is not collated, rather, it is simply "passed through" to the CollateX output. It is the "normalized" transcription that is collated.

#### `escriptorium_collate.collate.CollatexArgs`

A (Python) interface for passing arguments to the CollateX command line interface. For more details about the arguments accepted by the CollateX Jar CLI, consult [CollateX's documentation](https://collatex.net/doc/).

```python
class CollatexArgs(BaseModel):
  algorithm: Literal["needleman-wunsch", "medite", "dekker"] = "needleman-wunsch"
  distance: int | None
  dot_path: str | None
  format: Literal["tei", "json", "dot", "graphml", "tei"] = "json"
  input: str | None
  input_encoding: str | None
  max_collation_size: int | None
  max_parallel_collations: int | None
  output_encoding: str | None
  output: str | None
  tokenized: bool = False
  token_comparator: Literal["equality", "levenshtein"] = "equality"
```

#### `escriptorium_collate.collate.get_collatex_input`

Given two or more Witness instances and a set of CollateX arguments, return the input JSON that will be later passed to CollateX.

```python
from escriptorium_collate.collate import get_collatex_input

collatex_input = get_collatex_input(
  escr=escr, # An EscriptoriumConnector instance
  witnesses=witnesses, # A list of two or more Witness instances to be collated
  collatex_args=collatex_args, # An instance of CollatexArgs
)
```

#### `escriptorium_collate.collate.get_collatex_output`

Pass a given instance of CollatexArgs to the CollateX JAR.

```python
from escriptorium_collate.collate import get_collatex_output

collatex_output = get_collatex_output(
  collatex_args=collatex_args, # An instance of CollatexArgs
)
```

In this case, `CollatexArgs.input` is mandatory; in other words, the CollateX input JSON must be manually passed in.

#### `escriptorium_collate.collate.collate`

Run the complete collation pipeline via one function call. See the "Quick Start" section above.

### `escriptorium_collate.transcription_layers`

This module contains helper functions for dealing with the transcription layers of any given eScriptorium document.

#### `escriptorium_collate.transcription_layers.create`

Create and initialize an arbitrarily named transcription layer within a given eScriptorium document.

```python
from escriptorium_collate import transcription_layers

transcription_layers.create(
  escr=escr, # EscriptoriumConnector instance
  doc_pk=1, # Primary key of an eScriptorium document (int)
  layer_name="New Layer" # Name of the transcription layer to be created (str)
)
```

#### `escriptorium_collate.transcription_layers.copy`

Copy the content of one transcription layer to another transcription layer in a given eScriptorium document.

```python
from escriptorium_collate import transcription_layers

transcription_layers.copy(
  escr=escr, # EscriptoriumConnector instance
  doc_pk=1, # Primary key of an eScriptorium document (int)
  source_transcription_layer_name="Source Layer" # Name of the transcription layer to be copied (str)
  target_transcription_layer_name="Target Layer" # Name of the transcription layer to be written into (str)
  overwrite=True # If True, content of the target transcription layer is overwritten (default: False)
)
```

#### `escriptorium_collate.transcription_layers.get_transcription_pk_by_name`

Each transcription layer is assigned a unique identifier (primary key) by eScriptorium, but it is not easy to retrieve the primary key via eScriptorium's user interface. This simple helper function returns the transcription layer's primary key, given its name and the primary key of the document to which it belongs.

```python
from escriptorium_collate import transcription_layers

transcription_layers.get_transcription_pk_by_name(
  escr=escr, # EscriptoriumConnector instance
  doc_pk=1, # Primary key of an eScriptorium document (int)
  transcription_name="Source Layer" # Name of the desired transcription layer (str)
)
```

## License

`escriptorium-collate` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
