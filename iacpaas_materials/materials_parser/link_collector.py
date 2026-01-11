from typing import Dict, Any, List
from .storage import load_sources, save_sources, update_or_add_source
from .crawler import get_next_links_feature



def collect_product_links(source: Dict[str, Any]) -> Dict[str, Any]:
    """
    Собирает ссылки продуктов для одного источника.
    Возвращает словарь ссылок с метаданными.
    """
    links = {
        source['root_url']: {"IsProduct": False, "Soup": None, "Text": ""}
    }

    try:
        get_next_links_feature(links, source['root_url'], source['product_detection'])
    except KeyboardInterrupt as e:
        print('KeyboardInterrupt')

    product_links = [
        {
            "link": url,
            "type":data["Type"],
            "soup": data["Soup"],
            "text": data["Text"]
        }
        for url, data in links.items()
        if data['IsProduct'] is True
    ]

    return {
        "name": source['name'],
        "product_links": product_links
    }

def process_and_save_source(source: Dict[str, Any], output_file: str = "product_links.json") -> None:
    """Обёртка: собрать + сохранить."""
    new_source = collect_product_links(source)
    data = load_sources(output_file)
    update_or_add_source(data, new_source)
    save_sources(data, output_file)
