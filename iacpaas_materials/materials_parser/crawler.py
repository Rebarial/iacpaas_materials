from urllib.parse import urljoin, urlparse
import requests
from typing import Dict, List, Optional, Tuple, Any
from collections import deque
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from lxml import html, etree


def is_internal_link(url: str, base_netloc: str) -> bool:
    try:
        parsed = urlparse(url)
        return not parsed.netloc or parsed.netloc == base_netloc
    except Exception:
        return False


def extract_internal_links(tree, current_url: str, base_netloc: str) -> List[str]:
    cur_path = urlparse(current_url).path.strip('/')
    cur_segments = cur_path.split('/') if cur_path else []
    
    links = []
    for href in tree.xpath('//a[@href]/@href'):
        full_url = urljoin(current_url, href)
        parsed = urlparse(full_url)
        
        if parsed.netloc and parsed.netloc != base_netloc:
            continue
            
        path = parsed.path.strip('/')
        segments = path.split('/') if path else []
        
        if len(segments) > len(cur_segments) and segments[:len(cur_segments)] == cur_segments:
            links.append(f"{parsed.scheme}://{base_netloc}/{path}/")
            
    return links


def process_page(url: str, detection_rules: Dict) -> Tuple[List[str], Optional[Dict]]:
    try:
        print(f"Fetching: {url}")
        resp = requests.get(url, timeout=50)
        resp.raise_for_status()
        resp.encoding = 'utf-8'
        tree = html.fromstring(resp.content)
        tree.make_links_absolute(url)

        base_netloc = urlparse(url).netloc

        # Проверка по правилам
        detection_result = detect_and_extract(tree, detection_rules)
        product_data = None
        if detection_result:
            print(f"✅ Product found at {url}: {detection_result['type']}")
            product_data = {
                "IsProduct": True,
                "Type": detection_result["type"],
                "Text": detection_result["content"]["Text"]
            }

        new_links = extract_internal_links(tree, url, base_netloc)
        return new_links, product_data

    except Exception as e:
        print(f"❌ Error on {url}: {e}")
        return [], None



def detect_and_extract(tree: etree._ElementTree, detection_rules: Dict) -> Optional[Dict[str, Any]]:
    return _match_and_extract(tree, detection_rules)


def _match_and_extract(tree: etree._ElementTree, rule: Any) -> Optional[Dict[str, Any]]:
    if isinstance(rule, dict):
        if "or" in rule:
            for item in rule["or"]:
                result = _match_and_extract(tree, item)
                if result is not None:
                    return result
            return None

        elif "condition" in rule and "type" in rule:
            if _evaluate_condition(tree, rule["condition"]):
                extracted = None
                if "extract" in rule:
                    extracted = _extract_value(tree, rule["extract"])
                return {
                    "type": rule["type"],
                    "content": extracted
                }
            else:
                return None
    return None


def _evaluate_condition(tree: etree._ElementTree, cond: Any) -> bool:
    if isinstance(cond, list):
        return all(_evaluate_condition(tree, c) for c in cond)
    if not isinstance(cond, dict):
        return False
    if "and" in cond:
        return all(_evaluate_condition(tree, c) for c in cond["and"])
    if "or" in cond:
        return any(_evaluate_condition(tree, c) for c in cond["or"])


    xpath_expr = cond.get("xpath")
    if not xpath_expr:
        return False

    try:
        elements = tree.xpath(xpath_expr)
        exists = cond.get("exists", True)

        if exists:
            return len(elements) > 0
        else:
            return len(elements) == 0

    except Exception as e:
        print(f"⚠️ XPath error in condition: {xpath_expr} — {e}")
        return False


def _extract_value(tree: etree._ElementTree, rule: Dict) -> Optional[Dict[str, str]]:
    xpath_expr = rule.get("xpath")
    if not xpath_expr:
        return None

    try:
        elements = tree.xpath(xpath_expr)
        if not elements:
            return None

        el = elements[0]

        # Получаем текст (включая текст потомков)
        if isinstance(el, str):
            text = el.strip()
            inner_html = el
        else:
            text = ' '.join(el.xpath('.//text()')).strip()
            inner_html = etree.tostring(el, encoding='unicode', method='html')

        return {
            "Soup": inner_html,
            "Text": text
        }

    except Exception as e:
        print(f"⚠️ XPath extraction error: {xpath_expr} — {e}")
        return None


def crawl_site(
    start_url: str,
    detection_rules: Dict,
    max_pages: int = 50,
    max_depth: int = 3,
    max_workers: int = 10
) -> Dict[str, Dict]:
    
    parsed_start = urlparse(start_url)
    base_netloc = parsed_start.netloc

    to_visit = deque([(start_url, 0)])
    visited = set()
    results = {}
    visited_lock = Lock()

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        while to_visit and len(visited) < max_pages:
            batch = []
            while to_visit and len(batch) < max_workers and len(visited) < max_pages:
                url, depth = to_visit.popleft()
                if url in visited or depth > max_depth:
                    continue
                with visited_lock:
                    if url in visited:
                        continue
                    visited.add(url)
                batch.append((url, depth))

            if not batch:
                break

            future_to_url = {
                executor.submit(process_page, url, detection_rules): (url, depth)
                for url, depth in batch
            }

            for future in as_completed(future_to_url):
                url, depth = future_to_url[future]
                try:
                    new_links, product_data = future.result()
                    if product_data:
                        results[url] = product_data

                    if depth + 1 <= max_depth:
                        for link in new_links:
                            if link not in visited:
                                to_visit.append((link, depth + 1))

                except Exception as e:
                    print(f"⚠️ Unexpected error processing {url}: {e}")

        print(f'Visited: {len(visited)}')
        print(f'Products: {len(results)}')

    return results