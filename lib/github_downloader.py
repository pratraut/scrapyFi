import requests
import os
import re
import sys

headers = {'Authorization' : 'Token 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'}
API = 'https://api.github.com/repos/{author}/{repo}/contents/'

def parse(url):
    regex = r'https?://[www.]*github.com(.+)'
    result = re.match(regex, url)
    if not result:
        print(f"Invalid URL : {url}")
        return

    # print(f"repo path = {result.group(1)}")
    repo_path = result.group(1)
    split_path = repo_path.split('/')
    author = split_path[1]
    repository = split_path[2]
    branch = split_path[4]
    remaining_path = repo_path[repo_path.index(branch) + len(branch) + 1:]
    # print(f"author = {author}, repo = {repository}, branch = {branch}, remaining path = {remaining_path}")
    return author, repository, branch, remaining_path

path_to_urls = {}
def get_file_paths(api_url):
    if not api_url:
        return
    response = requests.get(api_url, headers=headers)
    data = response.json()
    if type(data) == dict:
        if data['type'] == 'file':
            if data['download_url']:
                path_to_urls[data['path']] = data['download_url']
            else:
                print(data)
        else:
            get_file_paths(data['url'])
    else:
        for record in data:
            if record['type'] == 'file':
                if record['download_url']:
                    path_to_urls[record['path']] = record['download_url']
                else:
                    print(record)
            else:
                get_file_paths(record['url'])
 
def get_all_file_path(url):
    author, repository, branch, remaining_path = parse(url)
    api_prefix = API.format(author=author, repo=repository)
    api_postfix = f'?ref={branch}'
    api_url = f'{api_prefix}{remaining_path}{api_postfix}'
    # print(f"api = {api_url}")
    get_file_paths(api_url)

def download_files(path_to_urls, folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    for path in path_to_urls:
        folder_path, file_name = path[: path.rindex('/')], path[path.rindex('/') + 1:]
        relative_folder_path = os.path.join(folder_name, folder_path)
        relative_file_path = os.path.join(relative_folder_path, file_name)
        if not os.path.exists(relative_folder_path):
            os.makedirs(relative_folder_path)
        with open(relative_file_path, "wb") as file_handle:
            response = requests.get(path_to_urls[path], headers=headers)
            file_handle.write(response.content)

def count_github_files(link_list):
    if not link_list:
        return 0
    path_to_urls = {}
    for link in link_list:
        try:
            get_all_file_path(link)
        except Exception as err:
            print("Github Exception =", err)

    return len(path_to_urls)

def download_github(link_list, project_name):
    if not link_list:
        print(f"Github link list for \"{project_name}\" is empty.")
        return
    path_to_urls = {}
    for link in link_list:
        print(f"Downloading files from : {link}")
        get_all_file_path(link)
    try:
        path = os.path.join('../downloaded_contracts', project_name)
        download_files(path_to_urls, folder_name=path)
        print(f"Files are downloaded at path : {path}")
    except Exception as err:
        print(f"Exception occured : {err}")

# LINK = ["https://github.com/makerdao/dss/blob/master/src/", "https://github.com/certusone/wormhole/tree/dev.v2/solana"]
# download(LINK)
# print("Data = ", path_to_urls)