from urllib.parse import urljoin, urlparse, urlsplit
from bs4 import BeautifulSoup
import requests
import re
from typing import Dict, List, Optional, Tuple, Any
from collections import deque
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock


def is_internal_link(url: str, base_netloc: str) -> bool:
    try:
        parsed = urlparse(url)
        return not parsed.netloc or parsed.netloc == base_netloc
    except Exception:
        return False


def extract_internal_links(soup: BeautifulSoup, current_url: str, base_netloc: str) -> List[str]:
    
    parsed = urlsplit(current_url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    path = parsed.path  

    links = []
    for a in soup.find_all('a', href=re.compile(f'{path}', re.IGNORECASE)):
            #if is_internal_link(a['href'], cur_domain):
                full_url = urljoin(base_url, a['href'])
                links.append(full_url)

    return links


def process_page(url: str, detection_rules: Dict) -> Tuple[List[str], Optional[Dict]]:

    try:
        print(f"Fetching: {url}")
        resp = requests.get(url, timeout=50)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'lxml')

        
        parsed = urlparse(url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        base_netloc = parsed.netloc

        
        detection_result = detect_and_extract(soup, detection_rules)
        product_data = None
        if detection_result:
            print(f"✅ Product found at {url}: {detection_result['type']}")
            product_data = {
                "IsProduct": True,
                "Type": detection_result["type"],
                "Text": detection_result["content"]["Text"]
            }

        
        new_links = extract_internal_links(soup, url, base_netloc)

        return new_links, product_data

    except Exception as e:
        print(f"❌ Error on {url}: {e}")
        return [], None
    

def detect_and_extract(soup: BeautifulSoup, detection_rules: Dict) -> Optional[Dict[str, Any]]:
    return _match_and_extract(soup, detection_rules)

def _match_and_extract(soup: BeautifulSoup, rule: Any) -> Optional[Dict[str, Any]]:
    if isinstance(rule, dict):
        if "or" in rule:
            for item in rule["or"]:
                result = _match_and_extract(soup, item)
                if result is not None:
                    return result
            return None

        elif "condition" in rule and "type" in rule:
            if _evaluate_condition(soup, rule["condition"]):
                extracted = None
                if "extract" in rule:
                    extracted = _extract_value(soup, rule["extract"])
                return {
                    "type": rule["type"],
                    "content": extracted
                }
            else:
                return None

    return None

def _evaluate_condition(soup: BeautifulSoup, cond: Any) -> bool:
    if isinstance(cond, list):
        return all(_evaluate_condition(soup, c) for c in cond)
    if not isinstance(cond, dict):
        return False
    if "and" in cond:
        return all(_evaluate_condition(soup, c) for c in cond["and"])
    if "or" in cond:
        return any(_evaluate_condition(soup, c) for c in cond["or"])

    tag = cond.get("tag")
    if not tag:
        return False
    elements = soup.find_all(tag)

    if cond.get("exists") is True:
        return len(elements) > 0

    attribute = cond.get("attribute")
    value = cond.get("value")
    content_expected = cond.get("content")
    text_contains = cond.get("text_contains")

    for el in elements:
        attr_ok = True
        if attribute is not None:
            attr_val = el.get(attribute)
            if isinstance(attr_val, list):
                attr_val = " ".join(attr_val)
            attr_ok = (attr_val == value)

        content_ok = True
        if content_expected is not None:
            content_ok = (el.get("content") == content_expected)

        text_ok = True
        if text_contains is not None:
            txt = (el.get_text() or "").strip()
            if isinstance(text_contains, str):
                text_ok = (text_contains in txt)
            elif isinstance(text_contains, bool):
                text_ok = bool(txt) if text_contains else True

        if attr_ok and content_ok and text_ok:
            return True
    return False

def _extract_value(soup: BeautifulSoup, rule: Dict) -> Optional[Dict[str, str]]:
    from_tag = rule.get("from_tag")
    if not from_tag:
        return None

    attrs = {}
    if "attribute" in rule and "value" in rule:
        attrs[rule["attribute"]] = rule["value"]

    candidates = soup.find_all(from_tag, attrs=attrs)

    if "text_contains" in rule:
        substr = rule["text_contains"]
        candidates = [el for el in candidates if substr in (el.get_text() or "")]

    if not candidates:
        return None

    el = candidates[0]

    #inner_html = "".join(str(child) for child in el.children)
    inner_html = str(el)
    text = el.get_text(separator=" ", strip=True)

    return {
        "Soup": inner_html,
        "Text": text
    }


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

        print(f'Visiteds:{len(visited)}')
        print(f'Products:{len(results)}')


    return results