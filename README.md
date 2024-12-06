# Reports Manager

A Python-based application to generate and export reports from a PostgreSQL database. The program features a user-friendly graphical interface built with `tkinter` and supports exporting data to CSV format.

## Features

- Connects to a PostgreSQL database.
- Generates predefined reports based on SQL queries.
- Exports reports as CSV files.
- User-friendly interface for managing configurations and generating reports.

## Prerequisites

Before running the application, ensure the following software and libraries are installed:

- **Python**: Version 3.8 or higher.
- **PostgreSQL**: Ensure the server is accessible and credentials are configured.
- Python Libraries:
  - `tkinter`
  - `psycopg2`
  - `pandas`
  - `json`

You can install the required Python modules using pip:

```bash
pip install psycopg2 pandas
