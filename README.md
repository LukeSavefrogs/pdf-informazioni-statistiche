# pdf-informazioni-statistiche

Estrattore campi compilati per il file PDF "Informazioni statistiche".

## Development

### :bangbang: Prerequisites

1. **Install** [**Python**](https://www.python.org/downloads/) (supported version between 3.8 and 3.12)
1. **Install** [**Poetry**](https://python-poetry.org/docs/)
1. **Run** the following command to create the **virtual environment** and install all the **dependencies**:

    ```shell
    poetry install
    ```

### 🚀 Usage

To use the script:

1. **Create a folder** named `data` right beside the script
2. **Put** all the **`.pdf` files** that need to be processed inside the **`data` folder**
3. Run the script:

```shell
poetry run python ./src/main.py
```

### :hammer_and_wrench: Build

To build the script into an executable just run the `build` task:

```shell
poetry run poe build
```

You will find the executable under the `dist` folder.
