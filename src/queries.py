import json
from dotenv import load_dotenv
import os
import requests
from helpers import initialize_rpc
from pycoingecko import CoinGeckoAPI

def getFiatPrice(pairs):
    """Get's the Currency Pairs from Coingecko.

    Parameter
    -------
        pairs :  'ETH-USD', 'GRT-USD' , 'GRT-ETH'

    Returns
    -------
    float
        Exchange Rate for given Currency Pair
    """
    cg = CoinGeckoAPI()

    if pairs == "ETH-USD":
        eth_usd_resp = cg.get_price(ids='ethereum', vs_currencies='usd')
        eth_usd = eth_usd_resp.get('ethereum').get('usd')
        return eth_usd
    if pairs == "GRT-USD":
        grt_usd_resp = cg.get_price(ids='the-graph', vs_currencies="usd")
        grt_usd = grt_usd_resp.get('the-graph').get('usd')
        return grt_usd
    if pairs == "GRT-ETH":
        grt_eth_resp = cg.get_price(ids='the-graph', vs_currencies="eth")
        grt_eth = grt_eth_resp.get('the-graph').get('eth')
        return grt_eth

def getGasPrice(speed='fast'):
    """Get's the Gas Price for the latest 200 Blocks in GWEI.Can Choose
       From Transaction Speed. Divided in Percentiles (30/60/90/100).
    Parameter
    -------
        speed :  'slow', 'standard' , 'fast', 'instant'
    Returns
    -------
    int
        Gas Price in GWEI
    """

    gas_price_resp = requests.get("https://api.anyblock.tools/latest-minimum-gasprice/",
                                  headers={'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}).json()
    gasprice = gas_price_resp.get(speed)
    return gasprice

def getCurrentBlock():
    """Get's the current block.

    Returns
    -------
    int
        Current Active block
    """
    web3 = initialize_rpc()
    return web3.eth.blockNumber


def getCurrentEpoch():
    """Get's the current active Epoche from the Mainnet Subgraph.

    Returns
    -------
    int
        Current Active Epoch
    """
    # Load .env File with Configuration
    load_dotenv()
    API_GATEWAY = os.getenv('API_GATEWAY')

    query = """
            {
              graphNetworks {
                currentEpoch
              }

            }
            """
    request_json = {'query': query}
    resp = requests.post(API_GATEWAY, json=request_json)
    response = json.loads(resp.text)

    current_epoch = response['data']['graphNetworks'][0]['currentEpoch']

    return current_epoch


def getStartBlockEpoch(epoch):
    """Get's the startBlock for an Epoch from the Mainnet Subgraph.
       And then it get's the Block Hash via RPC Calls.

    Returns
    -------
    int,int
        StartBlock of Epoche, StartBlock BlockHash
    """
    load_dotenv()
    API_GATEWAY = os.getenv('API_GATEWAY')

    query = """
         query get_epoch_block($input: ID!) {
              epoch(id: $input) {
                startBlock
              }
            }

            """
    request_json = {'query': query}

    variables = {'input': epoch}
    request_json['variables'] = variables

    resp = requests.post(API_GATEWAY, json=request_json)
    response = json.loads(resp.text)

    startBlock = response['data']['epoch']['startBlock']

    # get Block-Hash from BlockHeight
    web3 = initialize_rpc()
    startBlockHash = web3.eth.getBlock(startBlock)['hash'].hex()

    return startBlock, startBlockHash


def getAllocationDataById(allocation_id, variables=None, ):
    """Get's the data for an allocation by allocation_id
       Dumps the results into a dictionary.

    Returns
    -------
    dict
         Allocation Metadata
    """
    load_dotenv()
    API_GATEWAY = os.getenv('API_GATEWAY')

    query = """
            query AllocationById($input: ID!){
          allocation(id: $input) {
            indexingRewards
            allocatedTokens
            status
            id
            createdAt
            subgraphDeployment {
              signalledTokens
              createdAt
              stakedTokens
              originalName
              id
              ipfsHash
                    }
            createdAtEpoch
            createdAtBlockNumber
            closedAtBlockNumber
                }
            }
            """

    variables = {'input': allocation_id}

    request_json = {'query': query}
    if allocation_id:
        request_json['variables'] = variables
    resp = requests.post(API_GATEWAY, json=request_json)
    response = json.loads(resp.text)

    allocations = response['data']['allocation']

    return allocations


def getActiveAllocations(indexer_id, variables=None, ):
    """Get's the currently active Allocations for a specific Indexer from the Mainnet Subgraph.
       Dumps the results into a dictionary.

    Returns
    -------
    dict
        Active Allocations for Indexer
    """
    load_dotenv()
    API_GATEWAY = os.getenv('API_GATEWAY')

    query = """
        query AllocationsByIndexer($input: ID!) {
            indexer(id: $input) {
                allocations(where: {status: Active}) {
                    indexingRewards
                    allocatedTokens
                    status
                    id
                    createdAt
                    subgraphDeployment {
                        signalledTokens
                        createdAt
                        stakedTokens
                        originalName
                        id
                        ipfsHash

                    }
                    createdAtEpoch
                    createdAtBlockNumber
                }
            allocatedTokens
            stakedTokens
            delegatedTokens
            }
        }
    """
    variables = {'input': indexer_id}

    request_json = {'query': query}
    if indexer_id:
        request_json['variables'] = variables
    resp = requests.post(API_GATEWAY, json=request_json)
    response = json.loads(resp.text)

    allocations = response['data']['indexer']

    return allocations


def getAllAllocations(indexer_id, variables=None, ):
    """Get's the currently active Allocations for a specific Indexer from the Mainnet Subgraph.
       Dumps the results into a dictionary.

    Returns
    -------
    dict
        Active Allocations for Indexer
    """
    load_dotenv()
    API_GATEWAY = os.getenv('API_GATEWAY')

    query = """
        query AllocationsByIndexer($input: ID!) {
            indexer(id: $input) {
    totalAllocations {
      closedAt
      closedAtBlockHash
      closedAtBlockNumber
      closedAtEpoch
      createdAt
      createdAtBlockHash
      createdAtBlockNumber
      createdAtEpoch
      allocatedTokens
      id
      indexingRewards
      status
      subgraphDeployment {
        signalledTokens
        createdAt
        stakedTokens
        originalName
        id
        ipfsHash
                }
            }
    allocatedTokens
    stakedTokens
    delegatedTokens
        }
    }

    """
    variables = {'input': indexer_id}

    request_json = {'query': query}
    if indexer_id:
        request_json['variables'] = variables
    resp = requests.post(API_GATEWAY, json=request_json)
    response = json.loads(resp.text)

    allocations = response['data']['indexer']

    return allocations


def getClosedAllocations(subgraph_url, indexer_id, variables=None):
    """Get's all closed Allocations for a specific Indexer from the Mainnet Subgraph.
       Dumps the results into a dictionary.

    Returns
    -------
    dict
        Closed Allocations for Indexer
    """
    ALLOCATION_DATA = """

    query AllocationsByIndexer($input: ID!) {
        indexer(id: $input) {
            totalAllocations(where: {status_not: Active}) {
          closedAt
          closedAtBlockHash
          closedAtBlockNumber
          closedAtEpoch
          createdAt
          createdAtBlockHash
          createdAtBlockNumber
          createdAtEpoch
          allocatedTokens
          id
          indexingRewards
          status
              subgraphDeployment {
                id
                originalName
              }
            }
          }
        }
    """
    variables = {'input': indexer_id}

    request_json = {'query': ALLOCATION_DATA}
    if indexer_id:
        request_json['variables'] = variables
    resp = requests.post(subgraph_url, json=request_json)
    response = json.loads(resp.text)
    response = response['data']['indexer']

    return response


def getSubgraphsFromDeveloper(developer_id, variables=None, ):
    """Get's the deployed Subgraphs with the Hashes for a specific Subgraph Developer.

    Returns
    -------
    List
        [SubgraphIpfsHash, ...]
    """
    # Load .env File with Configuration
    load_dotenv()

    API_GATEWAY = os.getenv('API_GATEWAY')

    query = """
            query subgraphDeveloperSubgraphs($input: ID!){
              graphAccount(id: $input) {
                id
                subgraphs {
                  active
                  createdAt
                  id
                  displayName
                  versions {
                    version
                    subgraphDeployment {
                      id
                      ipfsHash
                    }
                  }
                }
              }
            }

            """
    variables = {'input': developer_id}
    request_json = {'query': query}
    if developer_id:
        request_json['variables'] = variables

    resp = requests.post(API_GATEWAY, json=request_json)
    subgraphs = json.loads(resp.text)['data']['graphAccount']['subgraphs']

    subgraphList = list()
    for subgraph in subgraphs:
        for version in subgraph['versions']:
            subgraphList.append(version['subgraphDeployment']['ipfsHash'])
    return subgraphList


def getInactiveSubgraphs():
    """Get's all inactive subgraphs with their Hash

    Returns
    -------
    List
        [SubgraphIpfsHash, ...]
    """
    # Load .env File with Configuration
    load_dotenv()

    API_GATEWAY = os.getenv('API_GATEWAY')

    query = """
            query inactivesubgraphs {
              subgraphs(where: {active: false}) {
                versions {
                  subgraphDeployment {
                    id
                    ipfsHash
                    originalName
                  }
                }
              }
            }

            """
    request_json = {'query': query}

    resp = requests.post(API_GATEWAY, json=request_json)
    subgraphs = json.loads(resp.text)['data']['subgraphs']

    inactive_subgraph_list = list()
    for subgraph in subgraphs:
        for version in subgraph['versions']:
            inactive_subgraph_list.append(version['subgraphDeployment']['ipfsHash'])
    return inactive_subgraph_list


def getAllSubgraphDeployments():
    """Get's all Subgraph Hashes

    Returns
    -------

    list
        [SubgraphHash1, ...]

    """
    load_dotenv()

    API_GATEWAY = os.getenv('API_GATEWAY')
    query = """
        {
          subgraphDeployments {
            originalName
            id
            ipfsHash
          }
        }
        """
    request_json = {'query': query}

    resp = requests.post(API_GATEWAY, json=request_json)
    data = json.loads(resp.text)
    subgraph_deployments = data['data']['subgraphDeployments']

    # create list with subgraph IpfsHashes
    list_subgraph_hashes = list()
    for subgraph in subgraph_deployments:
        list_subgraph_hashes.append(subgraph['ipfsHash'])

    return list_subgraph_hashes


def checkSubgraphStatus(subgraph_id, variables=None, ):
    """Grabs Subgraph Health Status Data for Subgraph

    Returns
    -------

    Dict with subgraph, sync status, health, and possible fatalErrors


    """

    API_GATEWAY = "https://api.thegraph.com/index-node/graphql"

    query = """
            query subgraphStatus($input:[String]!){
          indexingStatuses(subgraphs: $input) {
            subgraph
            synced
            health
            fatalError {
              handler
              message
              deterministic
              block {
                hash
                number
              }
            }
            node
          }
        }
        """
    variables = {'input': subgraph_id}

    request_json = {'query': query}
    if subgraph_id:
        request_json['variables'] = variables
    resp = requests.post(API_GATEWAY, json=request_json)
    data = json.loads(resp.text)
    subgraph_health = data['data']['indexingStatuses']

    return subgraph_health

def getDataAllocationOptimizer(indexer_id, variables=None, ):
    """
    Grabs all relevant Data from the Mainnet Meta Subgraph which are used for the
    Optimizer

    Parameter
    -------
        indexer_id : Address of Indexer to get the Data From
    Returns
    -------

    Dict with Subgraph Data (All Subgraphs with Name, SignalledTokens, Stakedtokens, Id),
    Indexer Data (Allocated Tokens Total and all Allocations),
    Graph Network Data (Total Tokens Allocated, total TokensStaked, Total Supply, GRT Issurance)
    """

    load_dotenv()

    API_GATEWAY = os.getenv('API_GATEWAY')
    OPTIMIZATION_DATA = """
        query MyQuery($input: String){
          subgraphDeployments {
            originalName
            signalledTokens
            stakedTokens
            id
          }
          indexer(id: $input) {
            tokenCapacity
            allocatedTokens
            stakedTokens
            allocations {
              allocatedTokens
              subgraphDeployment {
                originalName
                id
              }
              indexingRewards
            }
            account {
              defaultName {
                name
              }
            }
          }
          graphNetworks {
            totalTokensAllocated
            totalTokensStaked
            totalIndexingRewards
            totalTokensSignalled
            totalSupply
            networkGRTIssuance
          }
        }
        """
    variables = {'input': indexer_id}

    request_json = {'query': OPTIMIZATION_DATA}
    if indexer_id:
        request_json['variables'] = variables
    resp = requests.post(API_GATEWAY, json=request_json)
    data = json.loads(resp.text)
    data = data['data']

    return data

