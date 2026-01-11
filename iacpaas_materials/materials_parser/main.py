import json
from link_collector import process_and_save_source

with open('parser_config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)


process_and_save_source(config["sources"][0], "product_links.json")

