from brownie import network, config, accounts, MockV3Aggregator
from web3 import Web3

FORKED_LOCAL_ENVIRONMENTS = [
    "mainnet-fork-dev"
]  # I ran "brownie networks delete mainnet-fork", so that is why in the brackets "mainnet-fork" is not included but otherwise it should be.
LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]

DECIMALS = 8  # This has to resemble the Eth/Usd price feed, which has 8 decimals! i.e. in the getpric() function of FundMe.sol, we know that the return value has 8 decimal places so we multiply it by additional 10 decimals. So we want to resemble that and also use 8 decimals.
STARTING_PRICE = 200000000000


def get_account():
    if (
        network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS
        or network.show_active() in FORKED_LOCAL_ENVIRONMENTS
    ):
        return accounts[0]
    else:
        return accounts.add(
            config["wallets"]["from_key"]
        )  # This pulls from our account as per metmask


def deploy_mocks():
    print(f"The active network is {network.show_active()}")
    print("Deploying Mocks...")
    # We choose 18 as the # of decimals, and 2**21 as initial answer, both of which are the 2 arguments in the constructor function of the MockV3Aggregator.sol contract.
    # With <= 0 we check if there is already a Mock contract deployed, so that we don´t deploy it every time.
    if len(MockV3Aggregator) <= 0:
        MockV3Aggregator.deploy(
            DECIMALS,
            STARTING_PRICE,
            {"from": get_account()},
        )
        # Or use above: DECIMALS, Web3.toWei(STARTING_PRICE, "ether"), {"from": get_account()}
    print("Mocks Deployed!")
