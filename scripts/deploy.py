from time import sleep
from brownie import config, network, Lottery
from scripts.helpful_scripts import get_account, get_contract, fund_with_link
import requests

nomics_url = "https://api.nomics.com/v1/currencies/ticker"

nomics_params = {
    'ids':'ETH',
    'interval':'1h',
    'page':1,
    'key':config['api_keys']['nomics_key']
}

account = get_account()

def deploy_main():
    print(f"Account's balance is {account.balance()/10**18} eth")
    network_type = config['networks'][network.show_active()]
    Lottery.deploy(get_contract("vrf_coordinator").address, get_contract('link_token').address, network_type['fee'],network_type['keyhash'], {'from':account},publish_source=network_type.get('verify', False))
    print("Deployed Lottery")
    
    
def start_lottery():
    lottery = Lottery[-1]
    tx = lottery.startLottery({'from':account})
    tx.wait(1)
    print("Lottery is started!")
    
def enter_lottery():
    lottery = Lottery[-1]
    response = requests.get(url=nomics_url, params=nomics_params)
    result = response.json()[0]['price']
    eth_current_price = (float(result)+10)*10**6
    value = lottery.getEntranceFee(eth_current_price)
    tx = lottery.enter(eth_current_price, {'from':account, 'value':value})
    tx.wait(1)
    print("You entered the lottery!")
    
def end_lottery():
    # Fund the contract with link token
    lottery = Lottery[-1]
    fund_with_link(lottery.address)
    ending_transaction = lottery.endLottery({'from':account})
    ending_transaction.wait(1)
    sleep(60)
    print(f"{lottery.recentWinner()} is the new winner! Congratulations")
    
def main():
    deploy_main()
    start_lottery()
    enter_lottery()
    end_lottery()
    