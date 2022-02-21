# expected min price for entrance fee in ether is 0.018 or 18000000000000000
from brownie import Lottery, accounts, config
from web3 import Web3
import requests

nomics_url = "https://api.nomics.com/v1/currencies/ticker"

nomics_params = {
    'ids':'ETH',
    'interval':'1h',
    'page':1,
    'key':config['api_keys']['nomics_key']
}

def test_get_entrace_fee():
    account = accounts[0]
    response = requests.get(url=nomics_url, params=nomics_params)
    result = response.json()[0]['price']
    eth_current_price = float(result)*10**6
    lottery = Lottery.deploy({'from':account})
    
    
    # assert lottery.getEntraceFee(eth_current_price) > Web3.toWei(0.018, 'ether')
    # assert lottery.getEntraceFee(eth_current_price) < Web3.toWei(0.022, 'ether')