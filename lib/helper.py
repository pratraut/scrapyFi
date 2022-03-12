import os
import re
import sys
import requests
import html.parser

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

class EtherscanPattern:
    CODE = r"<pre class='js-sourcecopyarea editor' id='editor\d*' style='margin-top: \d+px;'>(.*?)</pre>"
    FILENAME = r"File \d+ of \d+ : (.*?)</span>"
    CONTRACT_NAME = r"Contract Name.*?<span.*?>(.*?)</span>"

class RinkebyEtherscanPattern:
    CODE = r"<pre class='js-sourcecopyarea editor' id='editor\d*' style='margin-top: \d+px;'>(.*?)</pre>"
    FILENAME = r"File \d+ of \d+ : (.*?)</span>"
    CONTRACT_NAME = r"Contract Name.*?<span.*?>(.*?)</span>"

class RopstenEtherscanPattern:
    CODE = r"<pre class='js-sourcecopyarea editor' id='editor\d*' style='margin-top: \d+px;'>(.*?)</pre>"
    FILENAME = r"File \d+ of \d+ : (.*?)</span>"
    CONTRACT_NAME = r"Contract Name.*?<span.*?>(.*?)</span>"

class KovanEtherscanPattern:
    CODE = r"<pre class='js-sourcecopyarea editor' id='editor\d*' style='margin-top: \d+px;'>(.*?)</pre>"
    FILENAME = r"File \d+ of \d+ : (.*?)</span>"
    CONTRACT_NAME = r"Contract Name.*?<span.*?>(.*?)</span>"

class GoerliEtherscanPattern:
    CODE = r"<pre class='js-sourcecopyarea editor' id='editor\d*' style='margin-top: \d+px;'>(.*?)</pre>"
    FILENAME = r"File \d+ of \d+ : (.*?)</span>"
    CONTRACT_NAME = r"Contract Name.*?<span.*?>(.*?)</span>"

class MumbaiPolygonscanPattern:
    CODE = r"<pre class='js-sourcecopyarea editor' id='editor\d*' style='margin-top: \d+px;'>(.*?)</pre>"
    FILENAME = r"File \d+ of \d+ : (.*?)</span>"
    CONTRACT_NAME = r"Contract Name.*?<span.*?>(.*?)</span>"

class PolygonscanPattern:
    CODE = r"<pre class='js-sourcecopyarea editor' id='editor\d*' style='margin-top: \d+px;'>(.*?)</pre>"
    FILENAME = r"File \d+ of \d+ : (.*?)</span>"
    CONTRACT_NAME = r"Contract Name.*?<span.*?>(.*?)</span>"

class TestnetBscscanPattern:
    CODE = r"<pre class='js-sourcecopyarea editor' id='editor\d*' style='margin-top: \d+px;'>(.*?)</pre>"
    FILENAME = r"File \d+ of \d+ : (.*?)</span>"
    CONTRACT_NAME = r"Contract Name.*?<span.*?>(.*?)</span>"

class BscscanPattern:
    CODE = r"<pre class='js-sourcecopyarea editor' id='editor\d*' style='margin-top: \d+px;'>(.*?)</pre>"
    FILENAME = r"File \d+ of \d+ : (.*?)</span>"
    CONTRACT_NAME = r"Contract Name.*?<span.*?>(.*?)</span>"

class BlockscoutPattern:
    CODE = r"<button type=\"button\" class=\"btn-line\" id=\"button\" data-toggle=\"tooltip\" data-placement=\"top\" data-clipboard-text=\"(.*?)\""
    FILENAME = r"File \d+ of \d+ : (.*?)</span>"
    CONTRACT_NAME = r"Contract name:.*?<dd.*?>(.*?)</dd>"

PWD = os.getcwd()

headers = {
    "User-Agent" : "Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36",
}

def get_patterns(link):
    scanners = {
        'rinkeby.etherscan.io' : RinkebyEtherscanPattern, 
        'ropsten.etherscan.io' : RopstenEtherscanPattern, 
        'kovan.etherscan.io' : KovanEtherscanPattern, 
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

    return pattern.CODE, pattern.FILENAME, pattern.CONTRACT_NAME

def download(link, project_name):
    CODE_PATTERN, FILENAME_PATTERN, CONTRACT_NAME_PATTERN = get_patterns(link)
    try:
        res = requests.get(f"{link}", headers=headers).text
        code_pattern = re.compile(CODE_PATTERN, re.S)
        filename_pattern = re.compile(FILENAME_PATTERN)
        contract_name = re.search(CONTRACT_NAME_PATTERN, res, re.S).group(1)
        source_codes = code_pattern.findall(res)
        filenames = filename_pattern.findall(res)
        output_path = os.path.join(PWD, 'downloaded_contracts', project_name, contract_name)
    except Exception as err:
        raise err

    if not os.path.exists(output_path):
        os.makedirs(output_path)
        print(f"[#] The {output_path} directory has been created.")

    if not filenames:
        filenames = [f'{contract_name}.sol']
    
    # print(source_codes, filenames)
    # return
    for code, filename in zip(source_codes, filenames):
        with open(os.path.join(output_path, filename), "w") as fp:
            html_parser = html.parser.HTMLParser()
            code = html_parser.unescape(code)
            print(f"[+] Download {filename}...")
            fp.write(code)
        
    print(f"[#] {contract_name} smart contract code downloaded successfully in {output_path}.\n")

def download_contracts(contract_list, project_name):
    if not contract_list:
        print(f"Contract list for \"{project_name}\" is empty.")
        return

    for contract_link in contract_list:
        if '#code' not in contract_link and 'blockscout' not in contract_link:
            contract_link += '#code'
        elif 'blockscout' in contract_link and 'contracts' not in contract_link:
            contract_link += '/contracts'
        print(f"Downloading contract(s) from {contract_link}:")
        try:
            download(contract_link, project_name)
        except Exception as err:
            # print(err)
            print(f'Error: while downloading - Contract might be updated/deleted or contains bytecode\n')

# if __name__== "__main__":
#     banner()
#     if len(sys.argv) != 3:
#         print("Usage: python3 download_contracts.py chain_id contract_address")
#         sys.exit(0)
#     elif len(sys.argv) == 3:
#         chain = str(sys.argv[1])
#         target = str(sys.argv[2])
#         main(chain, target)