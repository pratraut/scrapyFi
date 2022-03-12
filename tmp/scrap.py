from bs4 import BeautifulSoup
import requests, urllib, os, json, argparse, re
import terminal_banner, termcolor, platform, datetime

op = ''

banner_text = """
▒█▀▀▀█ █▀▀ █▀▀█ █▀▀█ █▀▀█ █▀▀ █▀▀█ 
░▀▀▀▄▄ █░░ █▄▄▀ █▄▄█ █░░█ █▀▀ █▄▄▀ 
▒█▄▄▄█ ▀▀▀ ▀░▀▀ ▀░░▀ █▀▀▀ ▀▀▀ ▀░▀▀

"""
desc = "Reports and articles scraper for Web3 bug bounty hunters."
dev_info = """
v1.0
Developed by: Prathamesh Raut
"""

if(platform.system() == 'Windows'):
    os.system('cls')
if (platform.system() == 'Linux'):
    os.system('clear')

banner = terminal_banner.Banner(banner_text)
print(termcolor.colored(banner.text,'cyan'), end="")
print(termcolor.colored(desc,'white', attrs=['bold']), end = "")
print(termcolor.colored(dev_info,'yellow'))

def create_url(query, count='10'):
    global url
    url = "https://medium.com/search/posts?q="+urllib.parse.quote(query)+"&count="+count

def do_medium():
    global op
    create_url(query, count)
    print("[+] Finding atmost %s articles on medium..." %count)
    
    try:
        page = requests.get(url)
    except requests.ConnectionError:
        print("[-] Can't connect to the server. Are you connected to the internet?")
        exit()

    soup = BeautifulSoup(page.content, 'html.parser')
    # print(page.content)
    print("[+] FOUND")
    print("[+] Listing articles...")
    for divs in soup.find_all('div', class_='postArticle-content'):
        for anchors in divs.find_all('a'):
            for h3 in anchors.find_all('h3'):
                try:
                    op += "-"*70 + "\n" + h3.contents[0] + ": " + anchors['href'] + "\n"
                except:
                    pass
    print(op)

argp = argparse.ArgumentParser(usage = "scraper.py -t TYPE -q QUERY -c [COUNT]")
argp.add_argument("-t","--type",required=False)
argp.add_argument("-q","--query")
argp.add_argument("-c","--count")
argp.add_argument("-o","--output")
parser = argp.parse_args()
type = parser.type
query = parser.query
count = parser.count
output = parser.output
if(count == None): count = '10'

def do_hackerone():

    global query
    global op
    query_ql=r"""
    {"operationName":"HacktivityPageQuery","variables":{"querystring":"%s","where":{"report":{"disclosed_at":{"_is_null":false}}},"orderBy":{"field":"popular","direction":"DESC"},"secureOrderBy":null,"count":%s,"maxShownVoters":10,"cursor":"MTI1"},"query":"query HacktivityPageQuery($querystring: String, $orderBy: HacktivityItemOrderInput, $secureOrderBy: FiltersHacktivityItemFilterOrder, $where: FiltersHacktivityItemFilterInput, $count: Int, $cursor: String, $maxShownVoters: Int) {\n  me {\n    id\n    __typename\n  }\n  hacktivity_items(first: $count, after: $cursor, query: $querystring, order_by: $orderBy, secure_order_by: $secureOrderBy, where: $where) {\n    total_count\n    ...HacktivityList\n    __typename\n  }\n}\n\nfragment HacktivityList on HacktivityItemConnection {\n  total_count\n  pageInfo {\n    endCursor\n    hasNextPage\n    __typename\n  }\n  edges {\n    node {\n      ... on HacktivityItemInterface {\n        id\n        databaseId: _id\n        ...HacktivityItem\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment HacktivityItem on HacktivityItemUnion {\n  type: __typename\n  ... on HacktivityItemInterface {\n    id\n    votes {\n      total_count\n      __typename\n    }\n    voters: votes(last: $maxShownVoters) {\n      edges {\n        node {\n          id\n          user {\n            id\n            username\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    upvoted: upvoted_by_current_user\n    __typename\n  }\n  ... on Undisclosed {\n    id\n    ...HacktivityItemUndisclosed\n    __typename\n  }\n  ... on Disclosed {\n    id\n    ...HacktivityItemDisclosed\n    __typename\n  }\n  ... on HackerPublished {\n    id\n    ...HacktivityItemHackerPublished\n    __typename\n  }\n}\n\nfragment HacktivityItemUndisclosed on Undisclosed {\n  id\n  reporter {\n    id\n    username\n    ...UserLinkWithMiniProfile\n    __typename\n  }\n  team {\n    handle\n    name\n    medium_profile_picture: profile_picture(size: medium)\n    url\n    id\n    ...TeamLinkWithMiniProfile\n    __typename\n  }\n  latest_disclosable_action\n  latest_disclosable_activity_at\n  requires_view_privilege\n  total_awarded_amount\n  currency\n  __typename\n}\n\nfragment TeamLinkWithMiniProfile on Team {\n  id\n  handle\n  name\n  __typename\n}\n\nfragment UserLinkWithMiniProfile on User {\n  id\n  username\n  __typename\n}\n\nfragment HacktivityItemDisclosed on Disclosed {\n  id\n  reporter {\n    id\n    username\n    ...UserLinkWithMiniProfile\n    __typename\n  }\n  team {\n    handle\n    name\n    medium_profile_picture: profile_picture(size: medium)\n    url\n    id\n    ...TeamLinkWithMiniProfile\n    __typename\n  }\n  report {\n    id\n    title\n    substate\n    url\n    __typename\n  }\n  latest_disclosable_action\n  latest_disclosable_activity_at\n  total_awarded_amount\n  severity_rating\n  currency\n  __typename\n}\n\nfragment HacktivityItemHackerPublished on HackerPublished {\n  id\n  reporter {\n    id\n    username\n    ...UserLinkWithMiniProfile\n    __typename\n  }\n  team {\n    id\n    handle\n    name\n    medium_profile_picture: profile_picture(size: medium)\n    url\n    ...TeamLinkWithMiniProfile\n    __typename\n  }\n  report {\n    id\n    url\n    title\n    substate\n    __typename\n  }\n  latest_disclosable_activity_at\n  severity_rating\n  __typename\n}\n"}
    """ % (query, int(count))
    #print(query)

    print("[+] Finding atmost %s public reports on Hackerone..." %count)
    headers = {"content-type": "application/json"}

    try:
        request = requests.post('https://hackerone.com/graphql', data=query_ql, headers=headers)
    except requests.ConnectionError:
        print("[-] Can't connect to the server. Are you connected to the internet?")
        exit()

    if request.status_code == 200:

        json_response = json.loads(json.dumps(request.json()))

        if not len(json_response['data']['hacktivity_items']['edges']):
            print("[-] No data retrieved.")
            exit()

        print("[+] Listing reports...")
        
        for i in range(len(json_response['data']['hacktivity_items']['edges'])):
            try:
                op +=  "-"*70 + "\n" + json_response['data']['hacktivity_items']['edges'][i]['node']['report']['title'] +": " + json_response['data']['hacktivity_items']['edges'][i]['node']['report']['url'] + "\n"
            except:
                pass
        print(op)
    else:
        raise Exception("Query failed to run by returning code of {}. {}".format(request.status_code, request.headers))

def get_api_uri(id, address):
    uri = "https://smart-contract-downloader.vercel.app/api/contract/"
    uri = uri + id + "/" + address
    return id, uri, address

def get_details(link):
    # Return api and address
    address = link.split('/')[-1]
    # ethmain - https://etherscan.io/
    # rinkeby - https://rinkeby.etherscan.io/
    # ropsten - https://ropsten.etherscan.io/
    # kovan - https://kovan.etherscan.io/
    # goerli - https://goerli.etherscan.io/
    # polygon - https://polygonscan.com/
    # polygonTest - https://mumbai.polygonscan.com/
    # bsc - https://bscscan.com/
    # bscTest - https://testnet.bscscan.com/
    scanners = {
        'rinkeby.etherscan.io' : 'rinkeby', 
        'ropsten.etherscan.io' : 'ropsten', 
        'kovan.etherscan.io' : 'kovan', 
        'goerli.etherscan.io' : 'goerli',        
        'etherscan.io' : 'ethmain', 
        'mumbai.polygonscan.com' : 'polygonTest', 
        'polygonscan.com' : 'polygon', 
        'testnet.bscscan.com' : 'bscTest', 
        'bscscan.com' : 'bsc'
    }
    for scanner in scanners:
        if scanner in link:
            return get_api_uri(scanners[scanner], address)            
    return None, None, None

def do_immunefi():
    global op
    # create_url(query, count)
    # print("[+] Finding atmost %s articles on medium..." %count)
    url = 'https://immunefi.com/explore'
    main_url = 'https://immunefi.com'
    try:
        page = requests.get(url)
    except requests.ConnectionError:
        print("[-] Can't connect to the server. Are you connected to the internet?")
        exit()

    soup = BeautifulSoup(page.content, 'html.parser')    
    # print(page.content)
    details = []
    for section in soup.find_all('section', class_='container'):
        for li in section.find_all('li'):
            detail = []
            for div in li.find_all('div', class_='font-medium'):
                detail.append(div.string)
                # detail.append(div.next_sibling)
            for a in li.find_all('a'):                
                if 'bounty' in a.get('href'):
                    bounty_url = main_url + a.get('href')                    
                    detail.append(bounty_url)
                    try:
                        bounty_page = requests.get(bounty_url)
                    except requests.ConnectionError:
                        print("[-] Can't connect to the server. Are you connected to the internet?")
                        pass
                    bounty_soup = BeautifulSoup(bounty_page.content, 'html.parser')
                    for section in bounty_soup.find_all(re.compile(r"Asset*")):
                        print(section.string)

                    
            details.append(detail)
            # if len(details) >= 5:
            #     break

    print(len(details))
    print(details[:5])
    print("%-20s %-20s %-20s %-20s" % ("Name", "Reward", "Tech", "URL"))
    for detail in details:
        try:
            print("%-20s %-20s %-20s %-20s" % (detail[0], detail[1], detail[2], detail[3]))
        except:
            # pass
            print("%-20s %-20s %-20s %-20s" % (detail[0], detail[1], detail[2], ''))
    '''
    print("[+] FOUND")
    print("[+] Listing articles...")
    for divs in soup.find_all('div', class_='postArticle-content'):
        for anchors in divs.find_all('a'):
            for h3 in anchors.find_all('h3'):
                try:
                    op += "-"*70 + "\n" + h3.contents[0] + ": " + anchors['href'] + "\n"
                except:
                    pass
    print(op)
    '''

if type == 'medium':
    do_medium() 
elif type == 'hackerone':
    do_hackerone()
else:
    do_immunefi()
    '''
    bounty_url = 'https://immunefi.com/bounty/wormhole/' #https://immunefi.com/bounty/polygon/
    try:
        bounty_page = requests.get(bounty_url)
    except requests.ConnectionError:
        print("[-] Can't connect to the server. Are you connected to the internet?")
        pass
    bounty_soup = BeautifulSoup(bounty_page.content, 'html.parser')
    code_links = {}
    for section in bounty_soup.find_all('section'):
        h3 = section.find('h3')
        # print(h3.string)
        if h3 and 'Asset' in h3.string:
            a_list = [t_a.find('a') for t_a in section.find_all('dd') if t_a] 
            for anchor in a_list:
                if anchor:
                    if 'github' in anchor.string.lower():
                        code_links['github'] = code_links.get('github', [])
                        code_links['github'].append(anchor.string)
                    elif '0x' in anchor.string.lower():
                        code_links['contract'] = code_links.get('contract', [])
                        code_links['contract'].append(anchor.string)
                    else:
                        code_links['other'] = code_links.get('other', [])
                        code_links['other'].append(anchor.string)
    # print(code_links)

    for link in code_links['contract']:
        id, API, address = get_details(link)
        print(f"API = {API}, id = {id}")

        if API is None:
            print(f"API is None for URL : {link}")
            continue            
        
        PATH = f'contracts/{id}/{address}/'
        os.makedirs(PATH, exist_ok=True)
        try:
            contract_page = requests.get(API)
        except requests.ConnectionError:
            print("[-] Can't connect to the server. Are you connected to the internet?")
            pass
        # contract_soup = BeautifulSoup(bounty_page.content, 'html.parser')
        code = json.loads(contract_page.text)
        sourceCode = json.loads(code['result'][0]['SourceCode'][1:-1])
        # print(sourceCode['sources'])
        for c_name in sourceCode['sources']:
            cond = [True if x in c_name else False for x in ['://', '@']]
            # print(cond)
            if any(cond):
                contract_name = c_name
                os.makedirs(PATH + contract_name[:contract_name.rfind('/')], exist_ok=True)
                # print(contract_name)
            else:
                contract_name = c_name.split('/')[-1]
            with open(PATH + contract_name, 'w') as fp:
                content = sourceCode['sources'][c_name]['content']
                fp.write(content)
            # break
    '''

if(output):
    try:
        file = open(output,"w", encoding= "UTF-8")
        file.write("SecScraper Scan Results at %s" %datetime.datetime.now()+"\n\n")
        file.write("Query: %s for %s results from %s\n\n" %(query, count, type))
        file.write(op)
        file.close()
        print("Output written to file %s" %output)
    except FileExistsError:
        print("Writing to output failed: File already exists")
    except IOError:
        print("Writing to file failed. Does the path exists? Check permissions and disk space.")