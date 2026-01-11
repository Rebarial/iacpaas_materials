from selenium import webdriver
from bs4 import BeautifulSoup, Tag
import requests
import re
from urllib.parse import urljoin, urlparse, urlsplit
import time
from typing import Union, Dict, List, Any, Optional

def get_next_links_feature(links: dict, url: str, cur_feature: str):

    parsed = urlsplit(url)
    base_url = f"{parsed.scheme}://{parsed.netloc}"
    path = parsed.path  


    try:
        print(f'Get: {url}')
        resp = requests.get(url, timeout=10)
        
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'lxml')
        time.sleep(1)
        
        #Check if product
        detection_result = detect_and_extract(soup, cur_feature)
        if detection_result:
            print(detection_result["type"])
            #div = soup.find('div', class_="uss_shop_content2")
            links[url] = {"IsProduct": True, "Type":detection_result["type"], "Soup": detection_result["content"]["Soup"], "Text": detection_result["content"]["Text"]}

        # Recursion for all links
        for a in soup.find_all('a', href=re.compile(f'{path}', re.IGNORECASE)):
            #if is_internal_link(a['href'], cur_domain):
                full_url = urljoin(base_url, a['href'])
                if full_url not in links:
                    links[full_url] = {"IsProduct": False, "Soup": None, "Text": ""}
                    get_next_links_feature(links, full_url, cur_feature)

        return links

    except Exception as e:
        print(f"Ошибка при загрузке {url}: {e}")
        return links
    

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