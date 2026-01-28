import json


def compare_responses(responses, properties_template):
    # Парсим ответы от llm, если возможно
    parsed_responses = []
    for response in responses:
        response_str = str(response)
        istart = response_str.find("{") if "{" in response_str else -1
        iend = response_str.rfind("}") if "}" in response_str else -1
        if (istart < iend and istart != -1 and iend != -1):
            parsed_response = response_str[istart:iend + 1]
            try:
                parsed_response = json.loads(parsed_response)
                # print(parsed_response)
                parsed_responses.append(parsed_response)
            except:
                print("Неверный формат1")
        else:
            print("Неверный формат2")

    # Сравниваем ответы, отсеиваем несовпадающие характеристики
    return compare_properties(parsed_responses, properties_template)

def compare_properties(responses, properties_template):
    verified_response = {}
    for key in properties_template.keys():
        if isinstance(properties_template[key], dict):
            item_properties_template = properties_template[key]
            item_responses = []
            for response in responses:
                if ((key in response) and isinstance(response[key], dict)):
                    item_responses.append(response[key])
            verified_response[key] = compare_properties(item_responses, item_properties_template)
        elif isinstance(properties_template[key], list):
            item_properties_template = properties_template[key]
            item_responses = []
            for response in responses:
                if ((key in response) and isinstance(response[key], list)):
                    item_responses.append(response[key])
            verified_response[key] = compare_lists(item_responses, item_properties_template[0])
        elif isinstance(properties_template[key], str):
            value = ''
            valid = True
            for response in responses:
                if (not (key in response) or ((value != '') and (not compare_text(response[key], value)))):
                    valid = False
                elif (key in response):
                    if len(response[key]) > len(value):
                        value = response[key]
            if (valid and value):
                verified_response[key] = value
            else:
                verified_response[key] = "?"

    return verified_response

def compare_text(string1, string2):
    words = string1.partition(' ')
    return string2.lower().startswith(words[0].lower())

def compare_lists(lists, properties_template):
    print(lists)
    threshold = 3
    result = []
    score = []
    groups = []

    main_key_options = ['name', 'property', 'size_value', 'shape', 'component', 'gas', 'component_formula', 'element']
    main_key = ''
    for option in main_key_options:
        if option in properties_template:
            main_key = option

    n = len(lists)
    m = []
    for i in range(n):
        m.append(len(lists[i]))
        score.append([0] * len(lists[i]))
        groups.append([-1] * len(lists[i]))
    for i1 in range(n):
        for j1 in range(m[i1]):
            if (score[i1][j1] == 0 and (main_key in lists[i1][j1])):
                best_matches = [-1] * n
                best_matches_len = [0] * n
                match_count = 0
                for i2 in range(n):
                    best_match = -1
                    best_match_len = 0
                    for j2 in range(m[i2]):
                        if (score[i2][j2] == 0 and (main_key in lists[i2][j2])):
                            match = compare_text(lists[i1][j1][main_key], lists[i2][j2][main_key])
                            if (match and not best_match_len):
                                best_match_len = match
                                best_match = j2
                    if (best_match_len):
                        best_matches[i2] = best_match
                        best_matches_len[i2] = best_match_len
                        match_count += 1
                
                comparison_list = []
                for i2 in range(n):
                    if (best_matches[i2] != -1):
                        score[i2][best_matches[i2]] = match_count
                        groups[i2][best_matches[i2]] = {i1, j1}
                        comparison_item = lists[i2][best_matches[i2]]
                        comparison_list.append(comparison_item)
                comparison_result = compare_properties(comparison_list, properties_template)
                comparison_result['result_appearance'] = match_count / n
                result.append(comparison_result)
    return result



