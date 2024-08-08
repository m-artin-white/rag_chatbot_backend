import ijson 
import json
import os

class DataTransformer:
    def __init__(self, keys_to_keep):
        self.keys_to_keep = keys_to_keep

    def process_json_file(self, file_path) -> list:
        with open(file_path, 'rb') as input_file: 
            records = ijson.items(input_file, 'records.item')
            filtered_records = []
            
            for record in records:
                filtered_record = {key: record[key] for key in self.keys_to_keep if key in record}
                filtered_records.append(filtered_record)

        return filtered_records

    def write_processed_json(self, new_file_path, filtered_records):
        json_object = {
            "records": []
        }
        if os.path.exists(new_file_path):
            with open(new_file_path, 'r', encoding='utf-8') as file:
                try:
                    json_object = json.load(file)
                    if 'records' not in json_object:
                        json_object['records'] = []
                except json.JSONDecodeError:
                    json_object['records'] = []
        json_object['records'].extend(filtered_records)
        with open(new_file_path, 'w', encoding='utf-8') as file:
            json.dump(json_object, file, indent=4)

    def load_json_file(self, file_path):
        with open(file_path, 'r', encoding="utf-8") as file:
            data = json.load(file)
        return data
    
    def transform_and_write_json(self, input_file_path, output_file_path):
        filtered_records = self.process_json_file(input_file_path)
        self.write_processed_json(output_file_path, filtered_records)