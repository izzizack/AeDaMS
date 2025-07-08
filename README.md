# Algae Experiment Data Management System (AEDaMS)

Table of Contents
Introduction

Features

How It Works

Getting Started

Prerequisites

Installation

Usage

Project Structure

Contributing

License

Contact

Acknowledgments

Introduction
The Algae Experiment Data Management System (AEDMS), also known as PhycoTrack, is a Python-based graphical user interface (GUI) application designed to streamline the recording, management, and real-time visualization of data from algae experiments. Researchers in the lab often deal with experimental data in various formats, such as CSV. This system provides a convenient way to import this data, convert it to a structured JSON format, apply dynamic filters, and view the results instantly, ensuring that changes in raw data are reflected live in the application's display.

This project aims to simplify data handling for phycology research, allowing researchers to focus more on their experiments and less on manual data transformation and analysis.

Features
CSV Data Import: Easily load experiment data from CSV files.

Live CSV to JSON Conversion: Automatically converts loaded CSV data into a JSON structure for easy manipulation and viewing.

Dynamic Data Filtering: Filter data based on various parameters such as date range, observation days, observation hour, tank number, and experiment name.

Real-time Data Display: View updated data instantly in the GUI as filters are applied or new data is loaded.

Multiple File Support: Integrate data from different sources, e.g., primary experiment data (v1.csv) and supplementary data like weather conditions (Weather.csv).

User-Friendly GUI: An intuitive graphical interface built with Tkinter for ease of use.

JSON Export: Option to save the filtered or complete dataset as a JSON file.

How It Works
The Algae Experiment Data Management System is built using Python and the tkinter library for its GUI.

Data Loading: Users can select one or more CSV files (e.g., experiment data, weather data). The system reads these CSVs and stores their content in memory.

Parameter Input: The GUI allows users to input various experiment-specific parameters such as URL/Local File Link, Sensor File, Weather File, Start Date, Observation Days, Observation Hour, Tank Number, and Experiment Name.

Dynamic Filtering: When the "Apply Filter" button is pressed, the system processes the loaded CSV data based on the user-defined parameters.

CSV to JSON Transformation: The filtered data rows are then converted into a list of dictionaries, which can be easily represented and viewed as JSON.

Live Display: The filtered and transformed data is immediately displayed within the GUI, providing a "live" view of the results based on the current filters and loaded data. Changes to filter parameters or source CSV files (after reloading) instantly update the displayed output.

JSON Export: The current filtered dataset can be exported to a JSON file for further use or analysis.

Getting Started
Follow these instructions to get a copy of the project up and running on your local machine.

Prerequisites
Python 3.x: Ensure you have Python installed. You can download it from python.org.

Installation
Clone the repository (or download the files):

Bash

git clone https://github.com/your-username/algae-data-system.git
cd algae-data-system
(Replace your-username and algae-data-system with your actual repository details if you're hosting it on GitHub/GitLab.)

No specific package installations are required beyond standard Python libraries, as tkinter, csv, json, os, datetime, collections, and glob are typically included with Python installations.

Usage
Run the application:

Bash

python csvtojson_gui.py
Load CSV Files:

Click "Browse CSV" to load your primary experiment data (e.g., 20250624v1.csv).

You can also specify paths for "Sensor File" and "Weather File" if your experiment incorporates separate data sources.

Input Parameters:

Fill in the relevant experiment details such as "Start Date" (e.g., YYYY-MM-DD or YYYY-MM-DD HH:MM:SS), "Obs Days", "Obs Hour", "Tank", and "Exp Name".

Apply Filters:

Click the "Apply Filter" button to process the data based on your inputs. The "Filtered CSV Data" and "JSON Output" text areas will update automatically.

View Data:

The Filtered CSV Data section shows the rows from your CSV that match the applied filters.

The JSON Output section displays the same filtered data in a JSON format.

Export Data:

Click "Export JSON" to save the currently displayed JSON data to a file.

Example Data:
You can use the provided sample CSV files (20250624v1.csv, 20250624Weather.csv) to test the application's functionality.

Project Structure
.
├── csvtojson_gui.py        # Main application script with the GUI logic
├── 20250624v1.csv          # Example primary algae experiment data
├── 20250624Weather.csv     # Example supplementary weather data
└── README.md               # This README file
Contributing
Contributions are welcome! If you have suggestions for improvements or find any bugs, please feel free to:

Fork the repository.

Create a new branch (git checkout -b feature/AmazingFeature).

Commit your changes (git commit -m 'Add some AmazingFeature').

Push to the branch (git push origin feature/AmazingFeature).

Open a Pull Request.

License
This project is licensed under the MIT License - see the LICENSE file for details.
(Create a LICENSE file in your repository and paste the MIT License text into it.)

Contact
If you have any questions or feedback, feel free to reach out:

Your Name/Team Name - Your Email Address

Project Link: https://github.com/your-username/algae-data-system (Replace with your actual repo link)

Acknowledgments
Thanks to the lab for the opportunity to develop this system.

Inspired by the need for efficient data management in biological research.

