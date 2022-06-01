from bs4 import BeautifulSoup
import requests, os, json, argparse, re
from lib.helper import *
from lib.github_downloader import *

import terminal_banner, termcolor, platform, time

from rich.console import Console
from rich.table import Table

COLOR = '\033[32m'
banner_text = f"""{COLOR}                                                                 
                                                 '||''''|  ||  
 ....    ....  ... ..   ....   ... ...  .... ...  ||  .   ...  
||. '  .|   ''  ||' '' '' .||   ||'  ||  '|.  |   ||''|    ||  
. '|.. ||       ||     .|' ||   ||    |   '|.|    ||       ||  
|'..|'  '|...' .||.    '|..'|'  ||...'     '|    .||.     .||. 
                                ||      .. |                   
                               ''''      ''                                                                                                
                    Author: savi0ur
"""

desc = "Helps in Searching and Downloading contracts of a program from Immunefi"
dev_info = """
v1.0
"""

if(platform.system() == 'Windows'):
    os.system('cls')
if(platform.system() == 'Linux'):
    os.system('clear')

banner = terminal_banner.Banner(banner_text)
print(termcolor.colored(banner.text,'cyan'), end="")
print(termcolor.colored(desc,'white', attrs=['bold']), end = "")
print(termcolor.colored(dev_info,'yellow'))

argp = argparse.ArgumentParser()
sub_argp = argp.add_subparsers(help="Commands")

# List
list_argp = sub_argp.add_parser("list", help="List programs")
list_argp.add_argument("list_programs", help="List all the programs with basic info", action="store_true")
list_argp.add_argument("-lcl", "--least-contract-link", help="list projects by least contract link", action="store_true")
list_argp.add_argument("-lgl", "--least-github-link", help="list projects by least github link", action="store_true")
list_argp.add_argument("-lol", "--least-other-link", help="list projects by least other link", action="store_true")
list_argp.add_argument("-ltl", "--least-total-link", help="list projects by least total link", action="store_true")
list_argp.add_argument("-ltc", "--least-total-contracts", help="list projects by least total contracts", action="store_true")
# list_argp.add_argument("-t", "--test", help="test", action="store_true")

# Search
search_argp = sub_argp.add_parser("search", help="Search programs")
search_argp.add_argument("-q", "--query", help="Query particular program by its name. Ex. MakerDAO", required=True)
search_argp.add_argument("-d", "--download", help="Download all contracts code from queried program", action="store_true")

# Download
download_argp = sub_argp.add_parser("download", help="Download code from link")
download_argp.add_argument("links", help="Download all contracts code from provided links (space separated)", nargs='+')
download_argp.add_argument("-fn", "--folder-name", help="Folder name to store contracts", default="Custom Downloads")

parser = vars(argp.parse_args())

# print(parser)

def get_dollar_repr(num):
    return "${:,}".format(num)

def get(obj, id):
    if id in obj and obj[id]:
        return obj[id]
    return None

def get_assets(assets):    
    new_assets = {}
    new_assets['github'] = []
    new_assets['contract'] = []
    new_assets['other'] = []
    if not assets:
        return new_assets

    for asset in assets:
        if 'github' in asset['url']:
            # new_assets['github'] = new_assets.get('github', [])
            new_assets['github'].append(asset['url'])
        elif '/0x' in asset['url']:
            # new_assets['contract'] = new_assets.get('contract', [])
            new_assets['contract'].append(asset['url'])
        else:
            # new_assets['other'] = new_assets.get('other', [])
            new_assets['other'].append(asset['url'])
    return new_assets

def get_project_data(url):
    try:
        page = requests.get(url)
    except requests.ConnectionError:
        print(f"[-] Unable to fetch URL : {url}. Make sure you are connected to the internet")
        exit()

    soup = BeautifulSoup(page.content, 'html.parser')   

    soup = soup.find("script", id="__NEXT_DATA__")
    json_data = json.loads(soup.string)
    bounty = json_data['props']['pageProps']['bounty']
    return bounty
    
def get_data(query=None):
    url = 'https://immunefi.com/explore/'
    main_url = 'https://immunefi.com'
    try:
        page = requests.get(url)
    except requests.ConnectionError:
        print(f"[-] Unable to fetch URL : {url}. Make sure you are connected to the internet")
        exit()

    soup = BeautifulSoup(page.content, 'html.parser')   

    soup = soup.find("script", id="__NEXT_DATA__")
    json_data = json.loads(soup.string)
    bounties = json_data['props']['pageProps']['bounties']
    # print("Total number of projects :", len(bounties))
    projects = []
    if query:
        for project in bounties:
            if query.lower() in project['project'].lower():
                try:
                    project_detail = {}
                    project_detail['id'] = get(project, 'id')
                    project_detail['project'] = get(project, 'project')
                    project_detail['date'] = get(project, 'date')
                    project_detail['maximum_reward'] = get(project, 'maximum_reward')
                    project_detail['technologies'] = get(project, 'technologies')
                    bounty_url = main_url + '/bounty/' + project_detail['id']
                    project_detail['url'] = bounty_url
                    project_ext_data = get_project_data(bounty_url)
                    project_detail['kyc'] = get(project_ext_data, 'kyc')

                    assets = project_ext_data['assets']
                    project_detail['assets_in_scope'] = get_assets(assets)
                    project_detail['num_contracts'] = 0
                    if parser.get('least_total_contracts', None):
                        # print("Project = ", project_detail['project'])
                        project_detail['num_contracts'] = get_number_of_contracts(contract_list=project_detail['assets_in_scope']['contract']) 
                        # count_github_files(project_detail['assets_in_scope']['github'])
                    projects.append(Project(**project_detail))
                except Exception as err:
                    print("Exception =", err)
    else:
        for project in bounties:
            if project['is_external']:
                continue

            try:
                project_detail = {}
                project_detail['id'] = get(project, 'id')
                project_detail['project'] = get(project, 'project')
                project_detail['date'] = get(project, 'date')
                project_detail['maximum_reward'] = get(project, 'maximum_reward')
                project_detail['technologies'] = get(project, 'technologies')
                bounty_url = main_url + '/bounty/' + project_detail['id']
                project_detail['url'] = bounty_url
                project_ext_data = get_project_data(bounty_url)
                project_detail['kyc'] = get(project_ext_data, 'kyc')

                assets = project_ext_data['assets']
                project_detail['assets_in_scope'] = get_assets(assets)
                project_detail['num_contracts'] = 0
                if parser.get('least_total_contracts', None):
                    # print("Project = ", project_detail['project'])
                    project_detail['num_contracts'] = get_number_of_contracts(contract_list=project_detail['assets_in_scope']['contract']) 
                        # count_github_files(project_detail['assets_in_scope']['github'])
                projects.append(Project(**project_detail))
            except Exception as err:
                print("Exception =", err)

    return projects
  
def display_projects(projects, type=None, option=None):
    print(f"NOTE: Ignoring programs with zero contract links")
    
    console = Console()

    table = Table(show_header=True, header_style="bold magenta")

    # FORMAT = "%5s %-40s %-20s %-30s %20s"
    # print('-'*120)
    if option == 'ltc':
        # print(FORMAT % ("SN", "Project", "Reward($)", "Tech", "#Contracts"))
        for col in ["SN", "Project", "Reward", "Technologies", "#Contracts"]:
            if col == "Reward":
                table.add_column(col, justify="center", header_style="cyan", style="green")
            else:
                table.add_column(col, justify="center", header_style="cyan")
    else:
        # print(FORMAT % ("SN", "Project", "Reward($)", "Tech", "#Links"))
        for col in ["SN", "Project", "Reward", "Technologies", "#Links"]:
            if col == "Reward":
                table.add_column(col, justify="center", header_style="cyan", style="green")
            else:
                table.add_column(col, justify="center", header_style="cyan")
    # print('-'*120)
    
    # print(projects[0].__dict__)
    sn = 1
    for project in projects:
        tech = '|'.join(project.technologies) if project.technologies else None
        if type:
            if project.assets_in_scope[type]:
                # print(FORMAT % (sn, project.project, project.maximum_reward, tech, len(project.assets_in_scope[type])))
                table.add_row(str(sn), project.project, get_dollar_repr(project.maximum_reward), tech, str(len(project.assets_in_scope[type])))
                sn += 1
        elif option == 'ltc':
            # number_contracts = sum((project.num_contracts[k]) for k in project.num_contracts)
            number_contracts = project.num_contracts
            if number_contracts:
                # print(FORMAT % (sn, project.project, project.maximum_reward, tech, number_contracts))
                table.add_row(str(sn), project.project, get_dollar_repr(project.maximum_reward), tech, str(number_contracts))
                sn += 1   
        else:
            number_contract_links = sum(len(project.assets_in_scope[k]) for k in project.assets_in_scope)
            if number_contract_links:
                # print(FORMAT % (sn, project.project, project.maximum_reward, tech, number_contract_links))
                table.add_row(str(sn), project.project, get_dollar_repr(project.maximum_reward), tech, str(number_contract_links))
                sn += 1
    # print('-'*120)
    console.print(table)

def search_contract(projects, query):
    results = []
    for project in projects:
        if query.lower() in project.project.lower():
            results.append(project)
    return results

projects = []
if parser.get('list_programs', None):
    t0 = time.time()
    projects = get_data()
    t1 = time.time()
    print(f"{t1-t0} seconds to process {len(projects)} projects.")

if parser.get('list_programs', None):      
    if parser.get('least_contract_link', None):
        print(f"Filtering by Least number of contract links...")
        filtered_projects = sorted(projects, key=lambda x: len(x.assets_in_scope['contract']), reverse=False)
        display_projects(filtered_projects, type='contract')            
    elif parser.get('least_github_link', None):
        print(f"Filtering by Least number of github links...")
        filtered_projects = sorted(projects, key=lambda x: len(x.assets_in_scope['github']), reverse=False)
        display_projects(filtered_projects, type='github')
    elif parser.get('least_other_link', None):
        print(f"Filtering by Least number of other links...")
        filtered_projects = sorted(projects, key=lambda x: len(x.assets_in_scope['other']), reverse=False)
        display_projects(filtered_projects, type='other')
    elif parser.get('least_total_link', None):
        print(f"Filtering by Least total number of links...")
        filtered_projects = sorted(projects, key=lambda x: sum(len(x.assets_in_scope[k]) for k in x.assets_in_scope), reverse=False)
        display_projects(filtered_projects)
    elif parser.get('least_total_contracts', None):
        print(f"Filtering by Least total number of contracts...")
        # filtered_projects = sorted(projects, key=lambda x: sum((x.num_contracts[k]) for k in x.num_contracts), reverse=False)
        # import pdb; pdb.set_trace()
        filtered_projects = sorted(projects, key=lambda x: x.num_contracts, reverse=False)
        display_projects(filtered_projects, option='ltc')
    # elif parser.get('test', None):
    #     print('Testing')
    #     LINK = ['https://etherscan.io/address/0xeecee260a402fe3c20e5b8301382005124bef121a', \
    #         'https://etherscan.io/address/0xde229e52bdb72c449db7912968e51d9d5e793005', \
    #         'https://etherscan.io/address/0xca1bf9e6add6155e92dc1dc7c0bf210c159a2f43']
    #     print(get_number_of_contracts(contract_list=LINK))
    else:
        display_projects(projects)

if parser.get('query', None):
    print(f"Searching for {parser.get('query')}...")
    t0 = time.time()
    res = get_data(parser.get('query'))
    t1 = time.time()
    print(f"{t1-t0} seconds to process {len(res)} projects.")
    # res = search_contract(projects, parser.get('query'))
    if res:
        display_projects(res)
        for item in res:
            print(f"Links for {item.project}:")
            for rec in item.assets_in_scope:
                print(f"{rec.upper()}:")
                i = 1
                if not item.assets_in_scope[rec]:
                    print("\tNO DATA FOUND\n")
                for link in item.assets_in_scope[rec]:
                    print(f"\t{i}. {link}")
                    i += 1
                print()

        for item in res:
            if parser.get('download', None):
                download_contracts(item.assets_in_scope['contract'], project_name=item.project)
                download_github(item.assets_in_scope['github'], project_name=item.project)
    else:
        print(f"Not able to find project : {parser.get('query')}")

if parser.get('links', None):
    prepare_links = [{'url': link} for link in parser.get('links')]
    links = get_assets(prepare_links)
    download_contracts(links['contract'], project_name=parser.get('folder_name'))
    download_github(links['github'], project_name=parser.get('folder_name'))