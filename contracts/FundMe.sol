// SPDX-License-Identifier: MIT

pragma solidity ^0.6.6;

import "@chainlink/contracts/src/v0.6/interfaces/AggregatorV3Interface.sol";

//after solidity v0.8 this is no longer necessary, but otherwise it is good to put it in there. Even if uint256 is a big number, a uint8 (max is 255), if we sum + uint8(1) then it would reset to 0, and if we sum + uint(100) it resets and starts and gets to 99.
//this is called a "library", and is reusable code where A can be used for B, by attaching library functions (from the library A) to any type (B) in the context of a contract.
import "@chainlink/contracts/src/v0.6/vendor/SafeMathChainlink.sol";

contract FundMe {
    // This library is to avoid overflows of uint256 variables, and here is how we utilize it:
    using SafeMathChainlink for uint256;

    mapping(address => uint256) public addressToAmountFunded;

    address[] public funders;

    address public owner;

    // This creates a global aggregator instead of having it hardcoded below.
    AggregatorV3Interface public priceFeed;

    // In the constructor we add a global aggregator instead and tell it in the constructor(XXXX) what price feed it should use.
    // In this case we use: _priceFeed, instead of having it hardcoded below in the getVersion() function.
    constructor(address _priceFeed) public {
        priceFeed = AggregatorV3Interface(_priceFeed);
        owner = msg.sender;
    }

    function fund() public payable {
        uint256 minimumUSD = 50 * 10**18;
        require(
            getConversionRate(msg.value) >= minimumUSD,
            "You need to spend more ETH!"
        );
        addressToAmountFunded[msg.sender] += msg.value;

        //with this line  we push a funder's address to the funders[] array to keep track of which address founded how much, so that we can reset it to 0 after withdrawals.
        //If someone funds multiple times, then we will have a redundancy in the array, but we will keep it like this for now:
        funders.push(msg.sender);
    }

    function getVersion() public view returns (uint256) {
        // AggregatorV3Interface priceFeed = AggregatorV3Interface(
        //    0x8A753747A1Fa494EC906cE90E9f37563A8AF630e
        // ); --> these are replaced in the constructor right when we deploy this contract
        return priceFeed.version();
    }

    function getPrice() public view returns (uint256) {
        // AggregatorV3Interface priceFeed = AggregatorV3Interface(
        //    0x8A753747A1Fa494EC906cE90E9f37563A8AF630e
        // ); --> these are replaced in the constructor right when we deploy this contract
        (, int256 answer, , , ) = priceFeed.latestRoundData();
        return uint256(answer * 10000000000);
    }

    // 1000000000
    function getConversionRate(uint256 ethAmount)
        public
        view
        returns (uint256)
    {
        uint256 ethPrice = getPrice();
        uint256 ethAmountInUsd = (ethPrice * ethAmount) / 1000000000000000000;
        //both ethPrice and weiAmount come in wei units, for which we need to divide it by 10**18
        return ethAmountInUsd;
    }

    function getEntranceFee() public view returns (uint256) {
        // mimimumUSD
        uint256 minimumUSD = 50 * 10**18;
        uint256 price = getPrice();
        uint256 precision = 1 * 10**18;
        return (minimumUSD * precision) / price;
    }

    modifier onlyOwner() {
        require(
            msg.sender == owner,
            "Your are not the owner of this contract, don´t try to steal the funds!"
        );
        _;
    }

    function withdraw() public payable onlyOwner {
        //"this" is a so called "keyword" in Solidity, and refers to the contract which we are currently in. By adding the onlyOwner variable on top, where we define that onlyOwner should be the one who deployed the contract, we avoid external people withdrawing funds from our contract.
        //in the start of the contract we use a "constructor" item which defines that the deployer of the contract is the owner (i.e. the initial msg.sender), and with the modifier clause above we require that only the onlyOwner can run the withdraw function
        //so in a nutshell: whoever calls this withdraw function (i.e. the msg.sender), activates a transfer task that transfers the ".balance" of this address (i.e. the address of this contract). That is why we need to ensure only the contract Admin owner (i.e. the onlyOwner) can be the msg.sender and withdraw
        msg.sender.transfer(address(this).balance);

        //logic here is is done to reset someone's balance to 0 in the array after someone withdrew:
        for (
            uint256 funderIndex = 0; /*starting value of index*/
            funderIndex < funders.length; /*loop finishes when value of index = length of the array*/
            funderIndex++ /*adds 1 every time loop finishes*/
        ) {
            //here we grab the address of the funder from the funders array (which we pushed in the fund function), and set it to 0 for each of the array addresses until funderIndex = founders.length
            address funder = funders[funderIndex];
            addressToAmountFunded[funder] = 0;
        }

        funders = new address[](0);
    }
}
