import os
import re
import requests
import html.parser
import concurrent.futures

class Project(object):
    def __init__(self, **kwargs):
        self.id = kwargs['id']
        self.project = kwargs['project']
        self.date = kwargs['date']
        self.maximum_reward = kwargs['maximum_reward']
        self.technologies = kwargs['technologies']
        self.kyc = kwargs['kyc']
        self.assets_in_scope = kwargs['assets_in_scope']
        self.url = kwargs['url']
        self.num_contracts = kwargs['num_contracts']

class EtherscanPattern:
    CODE = r"<pre class='.*?' id='editor\d*' style='margin-top: \d+px;'>(.*?)</pre>"
    FILENAME = r"File \d+ of \d+\s*:\s*(.*?)</span>"
    CONTRACT_NAME = r"Contract Name.*?<span.*?>(.*?)</span>"
    IMPLEMENTATION_ADDRESS = r"ABI for the implementation contract at.*?<a.*?>(.*?)</a>"

class GoerliEtherscanPattern:
    CODE = r"<pre class='.*?' id='editor\d*' style='margin-top: \d+px;'>(.*?)</pre>"
    FILENAME = r"File \d+ of \d+\s*:\s*(.*?)</span>"
    CONTRACT_NAME = r"Contract Name.*?<span.*?>(.*?)</span>"
    IMPLEMENTATION_ADDRESS = r"ABI for the implementation contract at.*?<a.*?>(.*?)</a>"

class MumbaiPolygonscanPattern:
    CODE = r"<pre class='.*?' id='editor\d*' style='margin-top: \d+px;'>(.*?)</pre>"
    FILENAME = r"File \d+ of \d+\s*:\s*(.*?)</span>"
    CONTRACT_NAME = r"Contract Name.*?<span.*?>(.*?)</span>"
    IMPLEMENTATION_ADDRESS = r"ABI for the implementation contract at.*?<a.*?>(.*?)</a>"

class PolygonscanPattern:
    CODE = r"<pre class='.*?' id='editor\d*' style='margin-top: \d+px;'>(.*?)</pre>"
    FILENAME = r"File \d+ of \d+\s*:\s*(.*?)</span>"
    CONTRACT_NAME = r"Contract Name.*?<span.*?>(.*?)</span>"
    IMPLEMENTATION_ADDRESS = r"ABI for the implementation contract at.*?<a.*?>(.*?)</a>"

class TestnetBscscanPattern:
    CODE = r"<pre class='.*?' id='editor\d*' style='margin-top: \d+px;'>(.*?)</pre>"
    FILENAME = r"File \d+ of \d+\s*:\s*(.*?)</span>"
    CONTRACT_NAME = r"Contract Name.*?<span.*?>(.*?)</span>"
    IMPLEMENTATION_ADDRESS = r"ABI for the implementation contract at.*?<a.*?>(.*?)</a>"

class BscscanPattern:
    CODE = r"<pre class='.*?' id='editor\d*' style='margin-top: \d+px;'>(.*?)</pre>"
    FILENAME = r"File \d+ of \d+\s*:\s*(.*?)</span>"
    CONTRACT_NAME = r"Contract Name.*?<span.*?>(.*?)</span>"
    IMPLEMENTATION_ADDRESS = r"ABI for the implementation contract at.*?<a.*?>(.*?)</a>"

class BlockscoutPattern:
    CODE = r"<button type=\"button\" class=\"btn-line\" id=\"button\" data-toggle=\"tooltip\" data-placement=\"top\" data-clipboard-text=\"(.*?)\""
    FILENAME = r"File \d+ of \d+\s*:\s*(.*?)</span>"
    CONTRACT_NAME = r"Contract name:.*?<dd.*?>(.*?)</dd>"
    IMPLEMENTATION_ADDRESS = r"ABI for the implementation contract at.*?<a.*?>(.*?)</a>"

PWD = os.getcwd()

headers = {
    "User-Agent" : "Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36",
}

def get_patterns(link):
    scanners = {
        'goerli.etherscan.io' : GoerliEtherscanPattern,        
        'etherscan.io' : EtherscanPattern,
        'mumbai.polygonscan.com' : MumbaiPolygonscanPattern, 
        'polygonscan.com' : PolygonscanPattern, 
        'testnet.bscscan.com' : TestnetBscscanPattern, 
        'bscscan.com' : BscscanPattern,
        'blockscout.com' : BlockscoutPattern
    }
    pattern = EtherscanPattern
    for scanner in scanners:
        if scanner in link:
            pattern = scanners[scanner]
            break

    return pattern.CODE, pattern.FILENAME, pattern.CONTRACT_NAME, pattern.IMPLEMENTATION_ADDRESS

def download(link, project_name):
    CODE_PATTERN, FILENAME_PATTERN, CONTRACT_NAME_PATTERN, IMPLEMENTATION_ADDRESS_PATTERN = get_patterns(link)
    
    try:
        is_proxy = False
        proxy_contract_name = ""
        if '#readProxyContract' in link:
            # fetch proxy contract name
            proxy_link = re.sub(r'#readProxyContract', '#code', link)
            res = requests.get(f"{proxy_link}", headers=headers, timeout=int(os.environ['TIMEOUT'])).text
            proxy_contract_name = re.search(CONTRACT_NAME_PATTERN, res, re.S).group(1).strip()
            # print("Proxy Contract name:", proxy_contract_name, repr(proxy_contract_name))
            # proxy_contract_name = proxy_contract_name.strip()
            # fetch implementation contract address
            res = requests.get(f"{link}", headers=headers, timeout=int(os.environ['TIMEOUT'])).text
            impl_address = re.search(IMPLEMENTATION_ADDRESS_PATTERN, res, re.S).group(1)
            link = re.sub(r'0x.*', impl_address, link) + "#code"
            is_proxy = True
    except Exception as err:
        # print("Proxy Error: ", err)
        return

    try:
        res = requests.get(f"{link}", headers=headers, timeout=int(os.environ['TIMEOUT'])).text
        code_pattern = re.compile(CODE_PATTERN, re.S)
        filename_pattern = re.compile(FILENAME_PATTERN)
        contract_name = re.search(CONTRACT_NAME_PATTERN, res, re.S).group(1).strip()
        # print("Contract name:", contract_name, repr(contract_name))
        # contract_name = contract_name.strip()
        source_codes = code_pattern.findall(res)
        filenames = filename_pattern.findall(res)
        # print("FileNames: ", filenames)
        if not is_proxy:
            output_path = os.path.join(PWD, 'downloaded_contracts', project_name, contract_name)
            dir_count = 1
            dir_path = output_path
            while os.path.exists(dir_path):
                dir_path = output_path + "_" + str(dir_count)
                dir_count += 1
                
            output_path = dir_path
        else:
            output_path = os.path.join(PWD, 'downloaded_contracts', project_name, proxy_contract_name)
            dir_count = 1
            prev_path = output_path
            next_path = output_path
        
            while os.path.exists(next_path):
                prev_path = next_path
                next_path = output_path + "_" + str(dir_count)
                dir_count += 1
            output_path = prev_path

            output_path = os.path.join(output_path, "implementation", contract_name)
    except Exception as err:
        print(err)
        raise err

    if not os.path.exists(output_path):
        os.makedirs(output_path)
        print(f"[#] Directory {output_path} has been created.")        

    contract_address = re.search(r"0x\w+", link).group(0)
    print("Contract address is ", contract_address)
    with open(os.path.join(output_path, contract_address + ".txt"), "w"):
        pass

    if not filenames:
        filenames = [f'{contract_name}.sol']
    
    # print(len(source_codes), len(filenames))
    # return
    for code, filename in zip(source_codes, filenames):
        filename = filename.strip()
        with open(os.path.join(output_path, filename), "w") as fp:
            # html_parser = html.parser.HTMLParser()
            code = html.unescape(code)
            print(f"[+] Download {filename}...")
            fp.write(code)
        
    print(f"[#] {contract_name} smart contract code downloaded successfully in {output_path}.\n")

def get_contract_count(link):
    if '#code' not in link and 'blockscout' not in link:
        link += '#code'
    elif 'blockscout' in link and 'contracts' not in link:
        link += '/contracts'

    _, FILENAME_PATTERN, _ = get_patterns(link)
    try:
        res = requests.get(f"{link}", headers=headers, timeout=int(os.environ['TIMEOUT'])).text
        filename_pattern = re.compile(FILENAME_PATTERN)
        filenames = filename_pattern.findall(res)
    except Exception as err:
        raise err

    try:
        if not filenames:
            return 1   
        return len(filenames)
    except Exception as err:
        print("Exception = ", err)
        return 0
    
def download_contracts(contract_list, project_name):
    if not contract_list:
        print(f"Contract list for \"{project_name}\" is empty.")
        return

    for contract_link in contract_list:
        proxy_contract_link = re.sub(r'#code', '', contract_link)
        impl_contract_link = re.sub(r'#readProxyContract', '', contract_link)
        if 'blockscout' not in proxy_contract_link:
            proxy_contract_link += '#code'
            impl_contract_link += '#readProxyContract'
        elif 'contracts' not in proxy_contract_link:
            proxy_contract_link += '/contracts'

        print(f"Downloading contract(s) from {proxy_contract_link}:")
        try:
            download(proxy_contract_link, project_name)
            download(impl_contract_link, project_name)
        except Exception as err:
            print(err)
            print(f'Error: while downloading - Contract might be updated/deleted or contains bytecode\n')

def get_number_of_contracts(contract_list):
    contract_count = {}
    
    if not contract_list:
        return 0        
    
    MAX_THREADS = 30
    threads = min(MAX_THREADS, len(contract_list))
    for url in contract_list:
        contract_count[url] = 0

    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        # executor.map(get_contract_count, contract_list)
        future_to_url = {executor.submit(get_contract_count, url): url for url in contract_list}
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                data = future.result()
            except Exception as exc:
                print('%r generated an exception: %s' % (url, exc))
            else:
                # print('%r is having %d contracts' % (url, data))
                contract_count[url] += data

    return sum(contract_count.values())
    
    '''
    for contract_link in contract_list:
        if '#code' not in contract_link and 'blockscout' not in contract_link:
            contract_link += '#code'
        elif 'blockscout' in contract_link and 'contracts' not in contract_link:
            contract_link += '/contracts'
        # print(f"Downloading contract(s) from {contract_link}:")
        try:
            # contract_count[contract_link] = get_contract_count(contract_link)
            contract_count += get_contract_count(contract_link)
        except Exception as err:
            # print(err)
            print(f'Error: while counting contracts - Contract might be updated/deleted or contains bytecode\n')
    return contract_count
    '''