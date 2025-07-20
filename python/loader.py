import argparse
import os
import json
from pathlib import Path
from ingredient_parser import parse_ingredient
from elasticsearch import Elasticsearch, helpers

client = Elasticsearch(
    "https://sandbox-search-genai-e76ccd.es.us-east-1.aws.elastic.cloud",
    api_key="",
    request_timeout=600
)

def is_json_file(file_path):
    return file_path.lower().endswith('.json')

def add_custom_attribute(data):
    # Add a new attribute "ingredients_keywords" using ingredient_parser
    ingredients = data.get("ingredients", [])
    keywords = []
    for ing in ingredients:
        try:
            parsed = parse_ingredient(ing)
            # Extract the ingredient name(s) as keywords
            if hasattr(parsed, "name") and parsed.name:
                keywords.extend([n.text.lower() for n in parsed.name if hasattr(n, "text")])
        except Exception as e:
            print(f"Warning: Could not parse ingredient '{ing}': {e}")
    # Store keywords as an array
    data["ingredients_keywords"] = keywords
    return data

def process_file(file_path, output_list):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        data = add_custom_attribute(data)
        output_list.append(data)
    except Exception as e:
        print(f"Warning: Could not process {file_path}: {e}")

def process_folder(folder_path, output_list, max_files=None):
    count = 0
    for root, _, files in os.walk(folder_path):
        for file in files:
            if is_json_file(file):
                if max_files is not None and count >= max_files:
                    return
                process_file(os.path.join(root, file), output_list)
                count += 1

def process_line_delimited_json(file_path, output_list, max_lines=None):
    count = 0
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            if max_lines is not None and count >= max_lines:
                break
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                data = add_custom_attribute(data)
                output_list.append(data)
                count += 1
            except Exception as e:
                print(f"Warning: Could not process line: {e}")

def bulk_upload_to_elastic(docs, index_name="cooking-recipes"):
    actions = [
        {
            "_index": index_name,
            "_source": doc
        }
        for doc in docs
    ]
    # Write actions to dump.out before uploading
    with open("dump.out", "w", encoding="utf-8") as dump_file:
        for action in actions:
            dump_file.write(json.dumps(action, ensure_ascii=False) + "\n")

    print(f"Uploading {len(actions)} documents to Elasticsearch index '{index_name}'...")
    success_count = 0
    error_count = 0
    # Re-create the actions generator for parallel_bulk
    actions_gen = (
        {
            "_index": index_name,
            "_source": doc
        }
        for doc in docs
    )
    for ok, result in helpers.parallel_bulk(client, actions_gen, thread_count=4, chunk_size=500):
        if ok:
            success_count += 1
        else:
            error_count += 1
            print("Error indexing document:")
            print(json.dumps(result, indent=2))
    print(f"Bulk upload complete: {success_count} succeeded, {error_count} errors.")

def main():
    parser = argparse.ArgumentParser(description="Process JSON files and add custom attributes, then upload to Elasticsearch.")
    parser.add_argument("input_path", help="Path to a JSON file or a folder containing JSON files.")
    parser.add_argument("--limit", type=int, default=None, help="Maximum number of files/lines to process.")
    parser.add_argument("--console", action="store_true", help="If set, print the processed documents to the console instead of uploading.")
    parser.add_argument("--index", default="cooking-recipes", help="Elasticsearch index name.")
    args = parser.parse_args()

    input_path = Path(args.input_path)
    output_list = []

    if input_path.is_file():
        # Try to detect line-delimited JSON by reading the first line
        with open(str(input_path), 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
        if first_line.startswith('{') and first_line.endswith('}'):
            process_line_delimited_json(str(input_path), output_list, max_lines=args.limit)
        elif is_json_file(str(input_path)):
            process_file(str(input_path), output_list)
        else:
            print("Error: Input file format not recognized.")
            return
    elif input_path.is_dir():
        process_folder(str(input_path), output_list, max_files=args.limit)
    else:
        print("Error: Input must be a JSON file or a directory containing JSON files.")
        return

    if args.console:
        for obj in output_list:
            print("=" * 40)
            print(json.dumps(obj, ensure_ascii=False, indent=2))
    else:
        bulk_upload_to_elastic(output_list, index_name=args.index)

if __name__ == "__main__":
    main()