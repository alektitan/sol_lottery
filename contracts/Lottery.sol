// SPDX-License-Identifier: MIT

pragma solidity ^0.6.6;

import "@chainlink/contracts/src/v0.6/VRFConsumerBase.sol";

contract Lottery is VRFConsumerBase{

    address owner;
    uint256 public usdEntryFee;
    mapping (address=>uint256) public players;
    mapping (address=>bool) isExist;
    address[] public  player_array;
    uint256 randomness;
    uint256 public fee;
    bytes32 public keyhash;
    address payable public recentWinner;

    enum LOTTERY_STATE {OPEN, CLOSED, CALCULATING_WINNER}
    //This diff. state are calculated by number which is OPEN = 0, CLOSED = 1, CALC = 2

    LOTTERY_STATE public lottery_state;
    

    constructor(address _vrfCoordinator, address _link, uint256 _fee, bytes32 _keyhash) public VRFConsumerBase(_vrfCoordinator,_link){
        owner = msg.sender;
        usdEntryFee = 50 * 1 ether;
        lottery_state = LOTTERY_STATE.CLOSED;
        fee = _fee;
        keyhash = _keyhash;
    }

    modifier OnlyOwner() {
        require(msg.sender == owner);
        _;
    }

    function enter(uint256 _current_price) payable public{
        require(msg.value >= getEntranceFee(_current_price), 'Not enough Eth');
        require(lottery_state == LOTTERY_STATE.OPEN, "The Lottery is not open yet.");
        if (!isExist[msg.sender]){
            isExist[msg.sender] = true;
            player_array.push(msg.sender);
        }
        players[msg.sender] += msg.value;
    }
    function getEntranceFee(uint256 _current_price) public pure returns(uint256){
        uint256 entraceInWei = (50 * 10**24/ _current_price);
        return entraceInWei;
    }
    function startLottery() public OnlyOwner{
        require(lottery_state == LOTTERY_STATE.CLOSED, "Can't start a new lottery yet");
        lottery_state = LOTTERY_STATE.OPEN;
    }
    function endLottery() public OnlyOwner {
        lottery_state = LOTTERY_STATE.CALCULATING_WINNER; 
        bytes32 requestId = requestRandomness(keyhash, fee);

    }

    function fulfillRandomness(bytes32 _requestId, uint256 _randomness) internal override{
        require(lottery_state == LOTTERY_STATE.CALCULATING_WINNER, "You aren't there yet!" );
        require(_randomness > 0, "Random player not found.");
        uint256 indexOfWinner = _randomness % player_array.length;
        recentWinner = payable(player_array[indexOfWinner]);
        recentWinner.transfer(address(this).balance);
        // reset lottery
        lottery_state = LOTTERY_STATE.CLOSED;
        for (uint256 playerIndex=0;playerIndex<=player_array.length;playerIndex++){
            players[player_array[playerIndex]] = 0;
            isExist[player_array[playerIndex]] = false;
        }
        randomness = _randomness;
        delete player_array;
    }
}
