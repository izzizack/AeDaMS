import csv
import json
import sys
import os

def csv_to_json (csv_file_path, json_file_path=None):
    """
    Convert a CSV file to JSON format.
    
    Args:
        csv_file_path (str): Path to the input CSV file
        json_file_path (str, optional): Path for the output JSON file. 
                                       If not provided, uses the same name as CSV with .json extension
    
    Returns:
        dict: The converted data as a Python dictionary
    """
    data = []
    
    try:
        with open(csv_file_path, mode='r', encoding='utf-8') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                data.append(row)
        
        if json_file_path is None:
            json_file_path = os.path.splitext(csv_file_path)[0] + '.json'
        
        with open(json_file_path, mode='w', encoding='utf-8') as json_file:
            json.dump(data, json_file, indent=4)
        
        return data
    except Exception as e:
        print(f"Error processing file: {e}", file=sys.stderr)
        return None
    
def main():
    """Main function to handle command line arguments and call the conversion function."""
    if len(sys.argv) < 2:
        csv_file = input("Enter the path to your CSV file: ").strip()
        if not csv_file:
            print("CSV file path is required.")
            return
        json_file = input("Enter the path for the output JSON file (leave blank for default): ").strip()
        if not json_file:
            json_file = None
    else:
        csv_file = sys.argv[1]
        json_file = sys.argv[2] if len(sys.argv) > 2 else None

    csv_to_json(csv_file, json_file)

if __name__ == "__main__":
    main()