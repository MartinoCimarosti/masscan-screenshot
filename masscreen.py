import json
import os
import sys
import concurrent.futures
import imgkit
from datetime import datetime
import requests

file_path = sys.argv[1]
subfolder_name = datetime.now().strftime("%d-%m-%Y-%H%M")
folder_name = f'output/{subfolder_name}'

if not os.path.exists(folder_name):
    os.makedirs(folder_name)

index_base = """
<!DOCTYPE html>
<html>

<body>
<h1 style="text-align: center"> SCANNED WEBSITES </h1>
<object type="text/html" data="data.html" width="100%" height="1000"></object>
</body>
</html>
"""

with open(f'{folder_name}/index.html', 'w') as html_file:
    html_file.write(index_base)

with open(file_path, 'r') as file:
    data = json.load(file)

targets = []

for site in data:
    ip = site.get("ip")
    port = site.get("ports")[0].get("port")
    full = f"{ip}:{port}"
    targets.append(full)


def write_html_content(filename, url):
    html_content = f'<div><a style="text-align: center" href="{url}"><h1>{url}</h1></a><img src="{filename}"/></div>'
    html_filename = f'{folder_name}/data.html'
    mode = 'a'
    if not os.path.exists(html_filename):
        mode = 'w'
    with open(html_filename, mode) as html_file:
        html_file.write(html_content)


def process_item(target):
    print(f"{target} - processing")
    filename = f'{"".join(target.split(":")[0])}.jpg'
    output_path = f'{folder_name}/{filename}'
    try:
        response = requests.get(f'http://{target}', verify=False, allow_redirects=True)
        target = response.url
        try:
            imgkit.from_url(target, output_path)
            print(f'{target} - SCREENSHOT SUCCESS ')
            write_html_content(filename, target)
        except Exception as e:
            print(f"{target} - screenshot fail {e} - Trying fallback")
            imgkit.from_string(response.text, output_path)
            print(f'{target} - fallback ok')
            write_html_content(filename, target)
    except Exception as e:
        print(f'connection to {target} failed or no response received: {e}')


num_threads = 32
with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
    future_results = [executor.submit(process_item, target) for target in targets]
    results = [future.result() for future in concurrent.futures.as_completed(future_results)]


print(f"HTML file with img tags created")