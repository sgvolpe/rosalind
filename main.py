from pathlib import Path

rosalind_domain = "https://rosalind.info"

endpoint = f"{rosalind_domain}/problems/list-view/"
session_id = "21ae1e0c205bb5f10473abb7ab70d929"
auth_cookie = {"sessionid": session_id}


import requests
import json
from bs4 import BeautifulSoup
import pandas as pd


problems_path = Path() / "problems"
dataset_path = Path() / "datasets"


def extract_table_rows_as_json(html_text):
    soup = BeautifulSoup(html_text, 'html.parser')
    table = soup.find('table', class_='problem-list table table-striped table-bordered table-condensed')
    rows_json = []
    if table:
        for row in table.find_all('tr'):
            cells = [cell.get_text(strip=True) for cell in row.find_all(['td', 'th'])]
            if cells:  # skip empty rows
                rows_json.append(cells)
    return json.dumps({'rows': rows_json})

def extract_problem_statement(html_text):
    soup = BeautifulSoup(html_text, 'html.parser')
    div = soup.find('div', class_='problem-statement problem-statement-bordered')
    return div.get_text(separator=' ', strip=True) if div else None

def extract_problems():
    response = requests.get(endpoint)
    if response.status_code == 200:
        with open('problems.html', 'w') as f:
            f.write(response.text)
    problems = extract_table_rows_as_json(response.text)
    print(f'{problems=}')

    problems_dict = json.loads(problems)
    rows = problems_dict['rows']

    # Use the first row as header if present
    if rows:
        df = pd.DataFrame(rows[1:], columns=rows[0])
    else:
        df = pd.DataFrame()

    df.to_csv('problems.csv', index=False)



def download_problem(problem_id: str):
    print(f'{problem_id=}')
    problem_endpoint = f"{rosalind_domain}/problems/{problem_id}"
    response = requests.get(problem_endpoint)
    print(f'{problem_endpoint=}')
    if response.status_code == 200:
        with open(problems_path / f'{problem_id}.html', 'w') as f:
            f.write(response.text)
def download_data_set(problem_id: str):
    print(f"Downloading Data set for {problem_id=}")
    dataset_path.mkdir(parents=True, exist_ok=True)
    dataset_endpoint = f"{rosalind_domain}/problems/{problem_id}/dataset"
    print(f'{dataset_endpoint=}')
    response = requests.get(
        dataset_endpoint, stream=True, cookies=auth_cookie
    )
    if response.status_code == 200:
        file_path = dataset_path / f'{problem_id}.txt'
        with open(file_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        print(f"Saved to {file_path}")
    else:
        print(f"Failed to download dataset: {response.status_code}")

def read_problem_statement(problem_id: str):
    with open(problems_path / f'{problem_id}.txt', 'r') as f:
        problem_statement = extract_problem_statement(f.read())
        print(f'{problem_statement=}')

def submit_output(problem_id: str, output_text: str):
    submit_endpoint = f"{rosalind_domain}/problems/{problem_id}"
    csrf_token = "nrPOweCAqHLkoO3zutY8YCxfCwS3kKeV"
    data = {
        "csrfmiddlewaretoken": csrf_token,
        "output_text": output_text,
    }
    headers = {
        "Referer": submit_endpoint,
    }
    print(f'{submit_endpoint=}')
    response = requests.post(
        submit_endpoint,
        data=data,
        cookies=auth_cookie,
        headers=headers,
    )
    print(f"Status: {response.status_code}")
    # print(f"Response: {response.text}")

if __name__ == "__main__":
    extract_problems()
    df = pd.read_csv('problems.csv')
    
    # 
    for problem_id in df['ID'][6:7]:
        print(f'{problem_id=}')
        download_problem(problem_id)



        download_data_set(problem_id)
        submit_output(problem_id, "AGCTAGCTAGCTAGCT")