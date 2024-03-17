# AdBlast Scraper

## Overview
The Shopee AdBlast Scraper is a Python project designed to scrape product advertisements and open multiple ad links simultaneously in multiple tabs.

## Scope
The project aims to automate the process of scraping product advertisements and opening multiple ad links in tabs, simulating high-volume user engagement. Key tasks include:

Scraping product advertisements from specified sources.
Opening each ad link in multiple tabs simultaneously (e.g., 50-100 tabs per link).

## Prerequisites
Before setting up the project, ensure you have the following prerequisites installed on your system:
Python 3.x: The project requires Python 3.10 to be installed. You can download and install Python from [the official Python website](https://www.python.org/downloads/).

## Setup
### Virtual Environment
A virtual environment is recommended to manage project dependencies and ensure a consistent development environment. Follow these steps to set up the virtual environment on different operating systems:
#### Linux and macOS
```bash
# Navigate to project directory
cd path/to/project

# Activate the virtual environment
source .venv/bin/activate

# Install project dependencies
pip install -r requirements.txt
````

#### Windows
```bash
# Navigate to project directory
cd path\to\project

# Create a virtual environment named .venv
python -m venv .venv

# Activate the virtual environment
.venv\Scripts\activate

# Install project dependencies
pip install -r requirements.txt
```

## Usage
Once the virtual environment is set up, you can run the `main.py` script to execute the scraping and tab-opening functionalities. Further instructions on usage and additional features will be provided in future updates to this README.