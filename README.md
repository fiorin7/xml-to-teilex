# XML to TEI Lex-0 (for Lat-Bul dictionary)

Web app for transforming entries of the Latin-Bulgarian dictionary into XML format which follows the [TEI Lex-0](https://dariah-eric.github.io/lexicalresources/pages/TEILex0/TEILex0.html) standard. It works with XML files, converted from DOCX by [OxGarage](https://oxgarage.tei-c.org/).

The app is [deployed](https://xml-to-teilex-64tb5hoepa-ey.a.run.app/) on Google [Cloud Run](https://cloud.google.com/run).

## Background

This app was commissioned by Sofia University to aid the creation of a digital Latin-Bulgarian dictionary. The original dictionary entries exist in DOCX format. With the help of the [OxGarage](https://oxgarage.tei-c.org/) tool they can be converted to XML which retains information about the original DOCX formatting. The result of this conversion is in turn transformed by the app into XML files which follow the [TEI Lex-0](https://dariah-eric.github.io/lexicalresources/pages/TEILex0/TEILex0.html) standard.

## Getting Started

### Requirements

* Python 3.8+
* [Pipenv](https://pipenv.pypa.io/en/latest/)

### Installation

Download and install [Pipenv](https://pipenv.pypa.io/en/latest/). In the project directory install all the dependencies through `pipenv`:

```shell
$ pipenv install
```
### Usage

#### In VSCode

Settings for VSCode are provided in the `launch.json`.

1. Select the virtual environment created by Pipenv as your interpreter: Command Palette (Ctrl+Shift+P) > Python: Select Interpreter.
2. Go to View > Run (Ctrl + Shift + D) and select "Python: Flask" configuration.
3. Go to Run > Run Without Debugging (Ctrl + F5). Make sure your working directory is set to the project folder.
4. The UI is available at http://localhost:5000/.

#### In the terminal

Use `pipenv` to setup proper environment for the python interpreter:

```shell
$ pipenv run python app.py
```

Alternatively, use `pipenv shell` to activate the virtualenv and then simply run `python app.py`.

## Deployment

The app is deployed on Google [Cloud Run](https://cloud.google.com/run) as a Docker container.  The easiest way to build the container is by using docker-compose:

```shell
$ docker-compose build
```

or by using docker directly:

```shell
$ docker build -t gcr.io/xml-to-teilex/xml-to-teilex .
```

Use

```shell
$ docker-compose up -d
```

to start the container locally.  The UI will be available at http://localhost:5000.

## Configuration

Configuration is done with environment variables.  Currently, the following options are supported:

| Name | Description | Default |
|-----|----------|---------------|
| SECRET_KEY | Secret key used for sessions by Flask | "secret_key" |

Make sure to set this in production to prevent session stealing.

## Architecture & Workflow

The application is split into two parts: the transform engine (`transform.py`) and the frontend UI (`app.py`).

The transformation workflow follows a few steps:

1. Load the input XML and the output template XML
2. Preprocess the input XML to fix irregularities in the markup.
3. Loop through the input XML nodes and process each dictionary entry into its own output file (using the output template).
    1. Determine the part of speech of currently processed entry.
    2. Based on the part of speech encode the morphological section (the output varies by POS).
    3. Encode the lexical part (senses and examples).
    4. For unrecognized entries (for example entries with invalid syntax or too short content) try to partially encode them (as fallback just append to the output template for human intervention).
4. Create a zip archive from all the generated output files.

The frontend is a simple Flask application which runs the transformation and serves the generated zip file.

## Contributing and Contact

The code is released under MIT Licence.  Contributions are welcome.
