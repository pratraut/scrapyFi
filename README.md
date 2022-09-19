# scrapyFi
```                                                                 
                                                 '||''''|  ||  
 ....    ....  ... ..   ....   ... ...  .... ...  ||  .   ...  
||. '  .|   ''  ||' '' '' .||   ||'  ||  '|.  |   ||''|    ||  
. '|.. ||       ||     .|' ||   ||    |   '|.|    ||       ||  
|'..|'  '|...' .||.    '|..'|'  ||...'     '|    .||.     .||. 
                                ||      .. |                   
                               ''''      ''                                                                                                
```
Scraper for Immunefi. It will help you to perform below task:
1. List all the projects from immunefi with basic details in tabular form
2. Query particular project with its project name and list basic details alongs with all smart contract links. It will also let you download all those contracts.
3. Download all contracts from provided links

## Requirement
Python 3.9+

## Supported Platform
[Immunefi](https://immunefi.com/explore/)

### Supported blockchain scanner for downloading contracts
* [https://etherscan.io/](https://etherscan.io/)
* [https://rinkeby.etherscan.io/](https://rinkeby.etherscan.io/)
* [https://ropsten.etherscan.io/](https://ropsten.etherscan.io/)
* [https://kovan.etherscan.io/](https://kovan.etherscan.io/)
* [https://goerli.etherscan.io/](https://goerli.etherscan.io/)
* [https://polygonscan.com/](https://polygonscan.com/)
* [https://mumbai.polygonscan.com/](https://mumbai.polygonscan.com/)
* [https://bscscan.com/](https://bscscan.com/)
* [https://testnet.bscscan.com/](https://testnet.bscscan.com/)
* [https://blockscout.com/](https://blockscout.com/)
* [https://aurorascan.dev/](https://aurorascan.dev/)

## Usage
```
$ scrapyfi.py [-h] [-t TIMEOUT] {list,search,download} ...

positional arguments:
  {list,search,download}
                        Commands
    list                List programs
    search              Search programs
    download            Download code from link

optional arguments:
  -h, --help            show this help message and exit
  -t TIMEOUT, --timeout TIMEOUT
                        timeout for each request in seconds (default: 10 sec)
```
**Default download folder is** `$(PWD)/downloaded_contracts/<project-name>`

### Details of List option
```
$ scrapyfi.py list [-h] [-lcl] [-lgl] [-lol] [-ltl] [-ltc] [-t]

  -lcl, --least-contract-link
                        list project by least contract link
  -lgl, --least-github-link
                        list project by least github link
  -lol, --least-other-link
                        list project by least other link
  -ltl, --least-total-link
                        list project by least total link
  -ltc, --least-total-contracts
                        list project by least total contracts
```
**Note:** `-ltc` is a very slow.

### Details of Search option
```
$ scrapyfi.py search [-h] -q QUERY [-d] [-f FILTER]

  -q QUERY, --query QUERY
                        Query particular program by its name. Ex. MakerDAO
  -d, --download        Download all contracts code from queried program
  -f FILTER, --filter FILTER
                        Filter results of a queried program
```

### Details of Download option
```
$ scrapyfi.py download [-h] [-fn FOLDER_NAME] links [links ...]

  -fn FOLDER_NAME, --folder-name FOLDER_NAME
                        Folder name to store contracts
  links                 Download all contracts code from provided links (space separated)
```

## Demo
### List
```
$ python3 scrapyfi.py list              
                                                                 
                                                 '||''''|  ||  
 ....    ....  ... ..   ....   ... ...  .... ...  ||  .   ...  
||. '  .|   ''  ||' '' '' .||   ||'  ||  '|.  |   ||''|    ||  
. '|.. ||       ||     .|' ||   ||    |   '|.|    ||       ||  
|'..|'  '|...' .||.    '|..'|'  ||...'     '|    .||.     .||. 
                                ||      .. |                   
                               ''''      ''                                                                                                
                    Author: savi0ur
Helps in Searching and Downloading contracts of a program from Immunefi
v1.0

122.7532970905304 seconds to process 291 projects.
NOTE: Ignoring programs with zero contract links
┏━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┓
┃ SN  ┃        Project         ┃   Reward    ┃                      Technologies                       ┃ #Links ┃
┡━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━┩
│  1  │        Wormhole        │ $10,000,000 │ Smart Contract|Websites and Applications|Blockchain/DLT │   8    │
│  2  │        MakerDAO        │ $10,000,000 │        Smart Contract|Websites and Applications         │  131   │
│  3  │         Aurora         │ $6,000,000  │        Smart Contract|Websites and Applications         │   31   │
|[...]|         [...]          |    [...]    |                        [...]                            |  [...] |
│ 287 │         Pillar         │   $1,250    │                     Smart Contract                      │   2    │
│ 288 │        CRO Max         │   $1,000    │                     Smart Contract                      │   1    │
│ 289 │        Nuggies         │   $1,000    │                     Smart Contract                      │   1    │
└─────┴────────────────────────┴─────────────┴─────────────────────────────────────────────────────────┴────────┘
```

**CLI Demo**

![](./demogifs/1List.gif)

### Search 
```
$ python3 scrapyfi.py search -q "wormhole"
                                                                 
                                                 '||''''|  ||  
 ....    ....  ... ..   ....   ... ...  .... ...  ||  .   ...  
||. '  .|   ''  ||' '' '' .||   ||'  ||  '|.  |   ||''|    ||  
. '|.. ||       ||     .|' ||   ||    |   '|.|    ||       ||  
|'..|'  '|...' .||.    '|..'|'  ||...'     '|    .||.     .||. 
                                ||      .. |                   
                               ''''      ''                                                                                                
                    Author: savi0ur
Helps in Searching and Downloading contracts of a program from Immunefi
v1.0

Searching for wormhole...
3.4474568367004395 seconds to process 1 projects.
NOTE: Ignoring programs with zero contract links
┏━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┓
┃ SN ┃ Project  ┃   Reward    ┃                      Technologies                       ┃ #Links ┃
┡━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━┩
│ 1  │ Wormhole │ $10,000,000 │ Smart Contract|Websites and Applications|Blockchain/DLT │   8    │
└────┴──────────┴─────────────┴─────────────────────────────────────────────────────────┴────────┘
Links for Wormhole:
GITHUB:
	1. https://github.com/certusone/wormhole/tree/dev.v2/ethereum
	2. https://github.com/certusone/wormhole/tree/dev.v2/solana
	3. https://github.com/certusone/wormhole/tree/dev.v2/terra
	4. https://github.com/certusone/wormhole/tree/dev.v2/sdk/rust
	5. https://github.com/certusone/wormhole/tree/dev.v2/node

CONTRACT:
	NO DATA FOUND


OTHER:
	1. https://docs.wormholenetwork.com/wormhole/contracts#mainnet
	2. https://portalbridge.com
	3. https://wormholenetwork.com/explorer/
```
**CLI Demo**

![](./demogifs/2SearchAndDownload.gif)

### Download
```
$ python3 scrapyfi.py download -fn "Custom Download" https://etherscan.io/address/0x98f3c9e6E3fAce36bAAd05FE09d375Ef1464288B https://github.com/makerdao/dss/blob/master/src/dai.sol
                                                                 
                                                 '||''''|  ||  
 ....    ....  ... ..   ....   ... ...  .... ...  ||  .   ...  
||. '  .|   ''  ||' '' '' .||   ||'  ||  '|.  |   ||''|    ||  
. '|.. ||       ||     .|' ||   ||    |   '|.|    ||       ||  
|'..|'  '|...' .||.    '|..'|'  ||...'     '|    .||.     .||. 
                                ||      .. |                   
                               ''''      ''                                                                                                
                    Author: savi0ur
Helps in Searching and Downloading contracts of a program from Immunefi
v1.0

Downloading contract(s) from https://etherscan.io/address/0x98f3c9e6E3fAce36bAAd05FE09d375Ef1464288B#code:
[#] Directory /Users/pratraut/Public/scrapyFi/downloaded_contracts/Custom Download/Wormhole_1 has been created.
Contract address is  0x98f3c9e6E3fAce36bAAd05FE09d375Ef1464288B
[+] Download Wormhole.sol...
[+] Download ERC1967Proxy.sol...
[+] Download ERC1967Upgrade.sol...
[+] Download Proxy.sol...
[+] Download IBeacon.sol...
[+] Download Address.sol...
[+] Download StorageSlot.sol...
[#] Wormhole smart contract code downloaded successfully in /Users/pratraut/Public/scrapyFi/downloaded_contracts/Custom Download/Wormhole_1.

[#] Downloading repo/files from https://github.com/makerdao/dss/blob/master/src/dai.sol:
[#] Directory /Users/pratraut/Public/scrapyFi/downloaded_contracts/Custom Download/dss has been created.
[+] Downloading dai.sol...
[#] File "dai.sol" downloaded successfully in /Users/pratraut/Public/scrapyFi/downloaded_contracts/Custom Download/dss
```

**CLI Demo**

![](./demogifs/3DLSingleContract.gif) 
