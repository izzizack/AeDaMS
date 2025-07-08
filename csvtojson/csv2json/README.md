# CSV to JSON Converter

This project provides a simple utility to convert CSV files into JSON format. It is designed to be easy to use and efficient for handling CSV data.

## Features

- Convert CSV files to JSON format.
- Specify an optional output JSON file name.
- Automatically generates a JSON file with the same name as the CSV file if no output name is provided.

## Installation

To use this project, you need to have Python installed on your machine. You can install the required dependencies using pip. 

1. Clone the repository:
   ```
   git clone <repository-url>
   cd csvtojson
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

To convert a CSV file to JSON, run the following command in your terminal:

```
python src/csvtojson.py <csv_file_path> [json_file_path]
```

- `<csv_file_path>`: Path to the input CSV file.
- `[json_file_path]`: Optional path for the output JSON file. If not provided, the output file will be named the same as the CSV file with a `.json` extension.

## Running Tests

To ensure the functionality of the converter, unit tests are provided. You can run the tests using:

```
python -m unittest discover -s tests
```

## License

This project is open-source and available under the MIT License.