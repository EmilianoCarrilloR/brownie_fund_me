from brownie import FundMe, MockV3Aggregator, network, config
from scripts.helpful_scripts import (
    get_account,
    deploy_mocks,
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
)


def deploy_fund_me():
    account = get_account()

    # Anything that is in the FundMe.sol constructor we can pass through brownie to our deploy script.
    # Here we need to pass the price feed address to our fundme contract
    # if we are on a persistent network like Rinkeby, use the associated address in the config file. Otherwise, deploy mocks (i.e. deploying our own version of the price feed contract).

    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        # i.e. deploy if we are on a live chain
        price_feed_address = config["networks"][network.show_active()][
            "eth_usd_price_feed"
        ]
    else:  # i.e. deploy if we are on a development chain, using a mock
        deploy_mocks()
        # With the -1 below we take the most recent version of the mock deployed
        price_feed_address = MockV3Aggregator[-1].address

    fund_me = FundMe.deploy(
        price_feed_address,
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify"),
        # Here the publish_source=True would states that after we deploy, we want to publish & verify it as well, but since we are in a development network, we rather take whatever we gave in config.yaml (i.e. "FALSE" for dev networks)
    )
    print(f"Contract deployed to {fund_me.address}")
    return fund_me  # we ask this script to "return" the fund_me so that our test_fund_me.py can afterwards import it and use it


def main():
    deploy_fund_me()
