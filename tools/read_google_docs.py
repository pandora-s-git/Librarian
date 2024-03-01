import re
import requests

def replace_google_docs_url_with_content(input_string):
    pattern = r'https:\/\/docs\.google\.com\/document\/d\/[a-zA-Z0-9_-]+\/edit'
    matches = re.findall(pattern, input_string)
    if matches:
        replaced_string = ""
        for m in matches:
            print("ID",m)
            replaced_string += re.sub(pattern, read(m), input_string)
        return replaced_string, True
    return input_string, False

def read(url: str) -> str:

    document_url = url

    document_id = document_url.split('/')[-2]

    export_url = f'https://docs.google.com/document/export?format=txt&id={document_id}'

    response = requests.get(export_url)

    if response.status_code == 200:
        document_content = response.text
        return document_content
    else:
        print(f"Failed to retrieve document. Status code: {response.status_code}")
