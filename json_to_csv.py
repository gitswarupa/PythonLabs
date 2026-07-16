"""JSON to CSV transition converter with data integrity validation.

Laboratory 3: The JSON to CSV Transition Matrix

This module loads a nested JSON file (simulating a REST API response),
flattens the internal dictionaries, validates data types, and exports
the resulting tabular data safely to CSV using csv.DictWriter.

Functions:
- `load_json(filepath) -> dict`: Load JSON from file
- `validate_record(record) -> bool`: Validate record data types
- `flatten_results(json_data) -> list[dict]`: Extract and flatten results array
- `write_to_csv(records, output_file) -> None`: Write records to CSV with validation
"""

from __future__ import annotations

import json
import csv
from pathlib import Path
from typing import Any, List, Dict, Optional


def load_json(filepath: str) -> dict:
	"""Load JSON data from a file.
	
	Args:
		filepath: Path to the JSON file
		
	Returns:
		Parsed JSON data as a dictionary
		
	Raises:
		FileNotFoundError: If file does not exist
		json.JSONDecodeError: If file is not valid JSON
	"""
	with open(filepath, 'r', encoding='utf-8') as f:
		return json.load(f)


def validate_record(record: Dict[str, Any]) -> bool:
	"""Validate record data types for CSV compatibility.
	
	Args:
		record: Dictionary record to validate
		
	Returns:
		True if record passes validation, False otherwise
	"""
	# Define expected types for each field
	type_constraints = {
		'consumer_id': (str,),
		'name': (str,),
		'credit_score': (int, float),
		'risk_band': (str,),
		'delinquent_accounts': (int,),
	}
	
	for field, expected_types in type_constraints.items():
		if field not in record:
			print(f"Warning: Missing field '{field}' in record")
			return False
		if not isinstance(record[field], expected_types):
			print(f"Error: Field '{field}' has type {type(record[field]).__name__}, "
				  f"expected {' or '.join(t.__name__ for t in expected_types)}")
			return False
	
	return True


def flatten_results(json_data: dict) -> List[Dict[str, Any]]:
	"""Extract and flatten the results array from paginated JSON response.
	
	Args:
		json_data: Nested JSON data with pagination metadata
		
	Returns:
		List of flattened result dictionaries
	"""
	if 'results' not in json_data:
		raise ValueError("JSON data missing 'results' key")
	
	results = json_data['results']
	
	if not isinstance(results, list):
		raise ValueError("'results' key must contain a list")
	
	return results


def write_to_csv(records: List[Dict[str, Any]], output_file: str) -> None:
	"""Write records to CSV file with data integrity validation.
	
	Args:
		records: List of dictionaries to write
		output_file: Path to output CSV file
		
	Raises:
		ValueError: If no valid records to write
	"""
	if not records:
		raise ValueError("No records to write")
	
	# Validate all records before writing
	valid_records = []
	for i, record in enumerate(records):
		if validate_record(record):
			valid_records.append(record)
		else:
			print(f"Skipping invalid record at index {i}")
	
	if not valid_records:
		raise ValueError("No valid records to write after validation")
	
	# Define fieldnames based on first record
	fieldnames = list(valid_records[0].keys())
	
	# Write to CSV
	output_path = Path(output_file)
	output_path.parent.mkdir(parents=True, exist_ok=True)
	
	with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
		writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
		writer.writeheader()
		writer.writerows(valid_records)
	
	print(f"Successfully wrote {len(valid_records)} records to {output_file}")


def process_json_to_csv(json_filepath: str, csv_filepath: str) -> None:
	"""Main orchestration function to convert JSON to CSV.
	
	Args:
		json_filepath: Path to input JSON file
		csv_filepath: Path to output CSV file
	"""
	try:
		# Load JSON
		print(f"Loading JSON from {json_filepath}...")
		json_data = load_json(json_filepath)
		
		# Extract results
		print("Flattening results array...")
		records = flatten_results(json_data)
		print(f"Found {len(records)} records")
		
		# Write to CSV with validation
		print(f"Writing to CSV: {csv_filepath}")
		write_to_csv(records, csv_filepath)
		print("Conversion complete!")
		
	except FileNotFoundError as e:
		print(f"Error: {e}")
	except json.JSONDecodeError as e:
		print(f"Error: Invalid JSON format - {e}")
	except ValueError as e:
		print(f"Error: {e}")


if __name__ == "__main__":
	# Example: Use the embedded sample data
	sample_json = {
		"total_records": 100,
		"page": 1,
		"total_pages": 50,
		"has_next": True,
		"results": [
			{
				"consumer_id": "EXP-88194",
				"name": "Alice Smith",
				"credit_score": 742,
				"risk_band": "Low",
				"delinquent_accounts": 0
			},
			{
				"consumer_id": "EXP-33091",
				"name": "Bob Jones",
				"credit_score": 612,
				"risk_band": "Medium",
				"delinquent_accounts": 2
			}
		]
	}
	
	# Save sample to a temporary JSON file
	sample_json_file = Path("sample_api_response.json")
	with open(sample_json_file, 'w', encoding='utf-8') as f:
		json.dump(sample_json, f, indent=2)
	
	# Process the JSON to CSV
	process_json_to_csv(
		json_filepath=str(sample_json_file),
		csv_filepath="output.csv"
	)
