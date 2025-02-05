# AddictionModule: Free Movement Through Any Data Format or Structure
import os
import json
import xml.etree.ElementTree as ET
from typing import Union

class AddictionModule:
    def __init__(self):
        self.supported_formats = ["json", "xml", "csv", "text"]

    def parse_data(self, file_path: str) -> Union[dict, list, str]:
        ext = os.path.splitext(file_path)[-1].lower()
        if ext == ".json":
            return self._parse_json(file_path)
        elif ext == ".xml":
            return self._parse_xml(file_path)
        elif ext == ".csv":
            return self._parse_csv(file_path)
        else:
            return self._parse_text(file_path)

    def _parse_json(self, file_path: str) -> dict:
        with open(file_path, 'r') as f:
            return json.load(f)

    def _parse_xml(self, file_path: str) -> dict:
        tree = ET.parse(file_path)
        root = tree.getroot()
        return self._xml_to_dict(root)

    def _xml_to_dict(self, element):
        return {element.tag: {child.tag: child.text for child in element}}

    def _parse_csv(self, file_path: str) -> list:
        with open(file_path, 'r') as f:
            return [line.strip().split(',') for line in f.readlines()]

    def _parse_text(self, file_path: str) -> str:
        with open(file_path, 'r') as f:
            return f.read()

    def traverse_and_extract(self, data: Union[dict, list, str]):
        if isinstance(data, dict):
            return self._extract_from_dict(data)
        elif isinstance(data, list):
            return self._extract_from_list(data)
        elif isinstance(data, str):
            return data

    def _extract_from_dict(self, data: dict) -> list:
        extracted = []
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                extracted.extend(self.traverse_and_extract(value))
            else:
                extracted.append(value)
        return extracted

    def _extract_from_list(self, data: list) -> list:
        extracted = []
        for item in data:
            if isinstance(item, (dict, list)):
                extracted.extend(self.traverse_and_extract(item))
            else:
                extracted.append(item)
        return extracted
