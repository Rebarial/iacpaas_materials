import json
import os
from typing import List, Dict, Any

def load_sources(filename: str = "parser_config.json") -> Dict[str, Any]:
    if not os.path.exists(filename):
        return {"sources": []}
    with open(filename, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {"sources": []}

def save_sources(data: Dict[str, Any], filename: str = "product_links.json") -> None:
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def update_or_add_source(sources_data: Dict[str, Any], new_source: Dict[str, Any]) -> None:
    for i, existing in enumerate(sources_data["sources"]):
        if existing.get("name") == new_source["name"]:
            sources_data["sources"][i]["product_links"] = new_source["product_links"]
            return
    sources_data["sources"].append(new_source)