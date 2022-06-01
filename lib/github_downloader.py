import requests
import os
import re
import sys

# headers = {'Authorization' : 'Token tkn'}
# API = 'https://api.github.com/repos/{author}/{repo}/contents/'

def safe_list_get(lst, idx, default):
  try:
    return lst[idx]
  except IndexError:
    return default

def parse(url):
    regex = r'https?://[www.]*github.com(.+)'
    result = re.match(regex, url)
    if not result:
        print(f"Invalid URL : {url}")
        return

    # print(f"repo path = {result.group(1)}")
    repo_path = result.group(1)
    # print("repo path =", repo_path)
    split_path = repo_path.split('/')
    author = safe_list_get(split_path, 1, "")
    repository = safe_list_get(split_path, 2, "")
    branch = safe_list_get(split_path, 4, "")
    if not branch:
        branch = "master"
        remaining_path = ""
    else:
        remaining_path = repo_path[repo_path.index(branch) + len(branch) + 1:]
    
    # print(f"author = {author}, repo = {repository}, branch = {branch}, remaining path = {remaining_path}")
    return author, repository, branch, remaining_path

# path_to_urls = {}
# def get_file_paths(api_url):
#     if not api_url:
#         return
#     response = requests.get(api_url, headers=headers)
#     data = response.json()
#     if type(data) == dict:
#         if data['type'] == 'file':
#             if data['download_url']:
#                 path_to_urls[data['path']] = data['download_url']
#             else:
#                 print(data)
#         else:
#             get_file_paths(data['url'])
#     else:
#         for record in data:
#             if record['type'] == 'file':
#                 if record['download_url']:
#                     path_to_urls[record['path']] = record['download_url']
#                 else:
#                     print(record)
#             else:
#                 get_file_paths(record['url'])
 
# def get_all_file_path(url):
#     author, repository, branch, remaining_path = parse(url)
#     api_prefix = API.format(author=author, repo=repository)
#     api_postfix = f'?ref={branch}'
#     api_url = f'{api_prefix}{remaining_path}{api_postfix}'
#     # print(f"api = {api_url}")
#     get_file_paths(api_url)

# def download_files(path_to_urls, folder_name):
#     if not os.path.exists(folder_name):
#         os.makedirs(folder_name)

#     for path in path_to_urls:
#         folder_path, file_name = path[: path.rindex('/')], path[path.rindex('/') + 1:]
#         relative_folder_path = os.path.join(folder_name, folder_path)
#         relative_file_path = os.path.join(relative_folder_path, file_name)
#         if not os.path.exists(relative_folder_path):
#             os.makedirs(relative_folder_path)
#         with open(relative_file_path, "wb") as file_handle:
#             response = requests.get(path_to_urls[path], headers=headers)
#             file_handle.write(response.content)

# def count_github_files(link_list):
#     if not link_list:
#         return 0
#     path_to_urls = {}
#     for link in link_list:
#         try:
#             get_all_file_path(link)
#         except Exception as err:
#             print("Github Exception =", err)

#     return len(path_to_urls)

# def download_github(link_list, project_name):
#     if not link_list:
#         print(f"Github link list for \"{project_name}\" is empty.")
#         return
#     path_to_urls = {}
#     for link in link_list:
#         print(f"Downloading files from : {link}")
#         get_all_file_path(link)
#     try:
#         path = os.path.join('../downloaded_contracts', project_name)
#         download_files(path_to_urls, folder_name=path)
#         print(f"Files are downloaded at path : {path}")
#     except Exception as err:
#         print(f"Exception occured : {err}")

def isFile(link):
    SMART_CONTRACT_EXTENSIONS = [".sol", ".ts", ".vy", ".rs"]
    for ext in SMART_CONTRACT_EXTENSIONS:
        if link.endswith(ext):
            return True
    return False

def raw_download(link, proj_name=""):
    author, repository, branch, remaining_path = parse(link)
    # print(f"Author = {author}, Repository = {repository}, Branch = {branch}, Remaining path = {remaining_path}")
    is_file = isFile(link)
    new_link = ""
    if is_file:
        # https://github.com/makerdao/dss-cdp-manager/raw/master/src/DssCdpManager.sol
        new_link = f"https://github.com/{author}/{repository}/raw/{branch}/{remaining_path}"
    else:
        # https://github.com/makerdao/dss-cdp-manager/archive/refs/heads/master.zip
        new_link = f"https://github.com/{author}/{repository}/archive/refs/heads/{branch}.zip"
    
    # print("New link =", new_link)
    # print("Is File =", is_file)

    content = requests.head(new_link, allow_redirects=True)
    # print("Status code =", content.status_code)
    # print("Redirect URL =", content.url)
    redirect_url = content.url
    content = requests.get(redirect_url, allow_redirects=False)

    DOWNLOAD_PATH = os.path.join(os.getcwd(), "downloaded_contracts", proj_name)
    print(f"[#] Downloading repo/files from {link}:")
    path = os.path.join(DOWNLOAD_PATH, repository)
    if is_file:        
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"[#] Directory {path} has been created.")

        filename = remaining_path.split("/")[-1]   
        if not os.path.exists(os.path.join(path, filename)):     
            with open(os.path.join(path, filename), "wb") as f:
                print(f"[+] Downloading {filename}...")
                f.write(content.content)
        print(f"[#] File \"{filename}\" downloaded successfully in {path}")
    else:
        # unzip the content    
        from io import BytesIO
        from zipfile import ZipFile, Path
        with ZipFile(BytesIO(content.content)) as my_zip_file:
            for contained_file in my_zip_file.namelist():
                temp_path = os.path.join(path, contained_file)
                # print("Path =", path)
                if not os.path.exists(temp_path):
                    path_obj = Path(my_zip_file, at=contained_file)
                    if path_obj.is_file():
                        # print("File :", contained_file)
                        print(f"[+] Downloading {contained_file}...")
                        with open(temp_path, "wb") as file_handle:
                            file_handle.write(path_obj.read_bytes())
                    else:
                        # print("Dir :", contained_file)
                        os.makedirs(temp_path)
        print(f"[#] Repo \"{repository}\" downloaded successfully in {path}")

def download_github(links, project_name=""):
    if not links:
        print(f"Github link list for \"{project_name}\" is empty.")
        return

    for link in links:
        raw_download(link, project_name)
        print()

# LINK = ["https://github.com/makerdao/dss", "https://github.com/makerdao/dss-cdp-manager/blob/master/src/DssCdpManager.sol", "https://github.com/makerdao/dss-gem-joins/tree/v1.2"]

# https://github.com/makerdao/dss -> https://github.com/makerdao/dss/archive/refs/heads/master.zip
# https://github.com/makerdao/dss-cdp-manager/blob/master/src/DssCdpManager.sol -> https://github.com/makerdao/dss-cdp-manager/raw/master/src/DssCdpManager.sol
# https://github.com/makerdao/dss-cdp-manager -> https://github.com/makerdao/dss-cdp-manager/archive/refs/heads/master.zip
# https://github.com/makerdao/dss-gem-joins/tree/v1.2 -> https://github.com/makerdao/dss-gem-joins/archive/refs/heads/v1.2.zip

#download_github(link, "dummy2")