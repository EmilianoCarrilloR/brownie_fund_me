from scripts.helpful_scripts import get_account, LOCAL_BLOCKCHAIN_ENVIRONMENTS
from scripts.deploy import deploy_fund_me
from brownie import (
    network,
    accounts,
    exceptions,
)  # Exceptions is imported to be able to use wanted exceptions like when we use the bad_actor line trying to withdraw.
import pytest  # we had to install it by running pip install pytest to be able to work with wanted exceptions


def test_can_fund_and_withdraw():
    account = get_account()
    fund_me = deploy_fund_me()
    entrance_fee = fund_me.getEntranceFee() + 100
    tx = fund_me.fund({"from": account, "value": entrance_fee})
    tx.wait(1)
    assert fund_me.addressToAmountFunded(account.address) == entrance_fee
    tx2 = fund_me.withdraw({"from": account})
    tx2.wait(1)
    assert fund_me.addressToAmountFunded(account.address) == 0


def test_only_owner_can_withdraw():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip(
            "only for local testing"
        )  # in this case, we do this so that if we don´t run on what we defined as local networks (i.e. dev networks) we command it to skip it just to avoid long delayed testing on a test net. This is just to stick to quick local testing.
    fund_me = deploy_fund_me()
    bad_actor = accounts.add()
    with pytest.raises(
        exceptions.VirtualMachineError
    ):  # this is the command (for which we needed to import "exceptions")
        fund_me.withdraw({"from": bad_actor})
