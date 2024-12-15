import json

def extract_json_structure(json_file):
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    def traverse_structure(obj):
        if isinstance(obj, dict):
            result = {}
            for key, value in obj.items():
                if isinstance(value, str) and key == "extraInfo":
                    result[key] = value
                else:
                    result[key] = traverse_structure(value)
            return result
        elif isinstance(obj, list):
            result = []
            for item in obj:
                result.append(traverse_structure(item))
            return result
        else:
            return type(obj).__name__
    
    return json.dumps(traverse_structure(data), indent=2)
json_file_path = '/Users/sean10/Downloads/notes.json'
# 使用示例
result = extract_json_structure(json_file_path)
print(result)