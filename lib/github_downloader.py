import requests
import os
import re
import sys

headers = {
    "User-Agent" : "Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36",
}

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

    content = requests.head(new_link, headers=headers, timeout=int(os.environ['TIMEOUT']), allow_redirects=True)
    # print("Status code =", content.status_code)
    # print("Redirect URL =", content.url)

    redirect_url = content.url
    content = requests.get(redirect_url, headers=headers, allow_redirects=True, timeout=int(os.environ['TIMEOUT']))
    # print("Content:", content.content)

    DOWNLOAD_PATH = os.path.join(os.getcwd(), "downloaded_contracts", proj_name)
    print(f"[#] Downloading repo/files from {link}:")
    path = os.path.join(DOWNLOAD_PATH, repository)
    if is_file:        
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"[#] Directory {path} has been created.")

        filename = remaining_path.split("/")[-1]   
        if not os.path.exists(os.path.join(path, filename)):     
            with open(os.path.join(path, filename), "wb"):
                pass
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