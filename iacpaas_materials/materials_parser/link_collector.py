from typing import Dict, Any, List
from .storage import load_sources, save_sources, update_or_add_source
from .crawler import crawl_site



def collect_product_links(source: Dict[str, Any], max_pages: int = 777777, max_depth: int = 10, max_workers: int = 10) -> Dict[str, Any]:

    results = crawl_site(
    start_url= source['root_url'],
    detection_rules= source['product_detection'],
    max_pages=max_pages,
    max_depth=max_depth,
    max_workers=max_workers
    )

    product_links = [
        {
            "link": url,
            "type":data["Type"],
            "text": data["Text"]
        }
        for url, data in results.items()
        if data['IsProduct'] is True
    ]

    return {
        "name": source['name'],
        "product_links": product_links
    }

def process_and_save_source(source: Dict[str, Any], output_file: str = "product_links.json", max_pages: int = 777777, max_depth: int = 10, num_threads: int = 10) -> None:
    """Обёртка: собрать + сохранить."""
    new_source = collect_product_links(source, max_pages, max_depth, num_threads)
    data = load_sources(output_file)
    update_or_add_source(data, new_source)
    save_sources(data, output_file)