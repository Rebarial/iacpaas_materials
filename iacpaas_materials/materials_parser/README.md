Инструмент для автоматического определения страниц продуктов на разных сайтах и извлечения данных из их HTML-разметки с помощью JSON-конфигурации.

Структура конфигурационного файла (parser_config.json)

```json
{
  "sources": [
    {
      "name": "Hype Wires",    # Название сайта
      "root_url": "https://www.example.ru/products/",    # Корневой адрес, с которого начинается поиск
      "product_detection": {       # Описание условий для определения страницы конкретного продукта
        "or": [     # В корне условий - "or" для поиска различных типов материалов
          {
            "condition": {     #Условие
              "and":[ # Поддерживается "and", "or"
                {
                  "tag": "div",  # Обязательно - Тэг, который ищем
                  "attribute": "class", # Какой атрибут тега проверяем
                  "value": "product_class", # С каким значением сравниваем значение атрибута (ищетсся div с классом "product class")
                  "text_contains": "Физико-химические свойства", # Содержится ли такой текст в тэге
                  "exists": true # "Есть ли такой тег на странице"
                },
                {
                  "tag": "div",
                  "attribute": "class",
                  "value":"product-description__wrap",
                  "exists":"True"
                }
              ]
                
              },
            "type": "gas",   # Если условия выполняются - возвращается этот тип
            "extract": { # Правила извлечения текста и html
                "from_tag": "div", # Из какого тэга извлекаем
                "attribute": "class", # Какой атрибут ищем у тэга
                "value": "product-description__wrap" # Какое значение атрибута ищем. 
              } # Если такой тег находится - из него извлекаются данные
          },
          {
            "condition": {
                "tag": "td",
                "text_contains": "Сортамент"
              },
            "type": "metal",
            "extract": {
                "from_tag": "div",
                "attribute": "class",
                "value": "uss_shop_content2"
              }
          }
        ]
      }
    }
  ]
}
```
Структура выходного файла (product_links.json)
```json
{
  "sources": [
    {
      "name": "Hype wires",
      "product_links": [
        {
          "link": "https://www.example.ru/products/azot/nitrogen_26/",
          "type": "gas", # Тип продукта
          "soup": "...", # Полный html элемента
          "text": "..." # Чистый текст из элемента
        }
      ]
    }
  }
}
```

```python
link_collector.collect_product_links(source: Dict[str, Any]) -> Dict[str, Any]:
    """
    Собирает ссылки продуктов для одного источника.
    Возвращает словарь ссылок с метаданными.
    """
```

```python
link_collector.process_and_save_source(source: Dict[str, Any], output_file: str = "product_links.json") -> Dict[str, Any]:
    """
    Сбор ссылок, сохранение в output_file
    """
```
   
