import json
import os
from typing import List, Dict, Any
from pathlib import Path

def merge_product_data(existing_dict: Dict[str, Any], new_data: Dict[str, Any]):
    existing_dict.update(new_data)
    return existing_dict

def load_sources(filename: str = "parser_config.json") -> Dict[str, Any]:
    config_file = Path(__file__).parent / filename
    
    if not os.path.exists(config_file):
        return {"sources": []}
    with open(config_file, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {"sources": []}

def save_sources(links: Dict[str, Any], data: Dict[str, Any], links_filename: str = "product_links.json", data_filename: str = "product_data.json") -> None:
    output_links_file = Path(__file__).parent / links_filename
    with open(output_links_file, 'w', encoding='utf-8') as f:
        json.dump(links, f, ensure_ascii=False, indent=2)

    output_data_file = Path(__file__).parent / data_filename
    if os.path.exists(output_data_file):
        with open(output_data_file, 'r', encoding='utf-8') as f:
            existing = json.load(f)
    else:
        existing = {}
    if not isinstance(existing, dict):
            existing = {}

    merged = merge_product_data(existing, data)

    with open(output_data_file, 'w', encoding='utf-8') as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)

def update_or_add_source(sources_data: Dict[str, Any], new_source: Dict[str, Any]) -> None:
    for i, existing in enumerate(sources_data["sources"]):
        if existing.get("name") == new_source["name"]:
            sources_data["sources"][i]["product_links"] = new_source["product_links"]
            return
    sources_data["sources"].append(new_source)