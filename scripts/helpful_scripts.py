from brownie import network, config, accounts, MockV3Aggregator, Contract, VRFCoordinatorMock, LinkToken, interface

LOCAL_BLOCKCHAIN_ENVIRONMENTS = ['development','ganache-local']
FORKED_LOCAL_ENV = ['mainnet-fork','mainnet-fork-dev']
DECIMALS = 8
STARTING_PRICE = 200000000000

def get_account(index=None, id=None):
    
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS or network.show_active() in FORKED_LOCAL_ENV:
            return accounts[0]
    return accounts.add(config['wallets']['from_key'])
    
def deploy_mocks():
    print(f'The active network is {network.show_active()}')
    print("Deploying Mocks...")
        
    if len(MockV3Aggregator) <= 0:
        MockV3Aggregator.deploy(DECIMALS, STARTING_PRICE, {'from':get_account()})
        link_token = LinkToken.deploy({'from':get_account()})
        VRFCoordinatorMock.deploy(link_token.address,{'from':get_account()})
    print("Mocks Deployed!")
    
    return MockV3Aggregator[-1].address

contract_to_mock ={
    'eth_usd_price_feed':MockV3Aggregator,"vrf_coordinator":VRFCoordinatorMock,
    "link_token": LinkToken
    }

def get_contract(contract_name):
    '''Ths function will grab the contract address from the brownie config if defined, otherwise, it will deploy a mock version of that contract, and return that mock contract
    
        Args:
            contract_name - string
            
        Returns: brownie.network.contract.ProjectContract
    '''
    
    contract_type = contract_to_mock[contract_name]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        if len(contract_type) <=0:
            deploy_mocks()
        
        contract = contract_type[-1]
        
    else:
        contract_address = config['networks'][network.show_active()][contract_name]
        
        contract = Contract.from_abi(contract_type._name, contract_address, contract_type.abi)
        
    return contract

def fund_with_link(contract_address,account=None, link_token=None, amount=100000000000000000):
    account = account if account else get_account()
    link_token = link_token if link_token else get_contract('link_token')
    # link_token_contract = interface.LinkTokenInterface(link_token.address)
    # tx = link_token_contract.tranfer(contract_address, amount, {'from':account})
    tx = link_token.transfer(contract_address, amount, {'from':account})
    tx.wait(1)
    print("Fund contract")
    return tx