contract Arb is FlashLoanReceiverBase {

    using SafeMath for uint256;
    ILendingPoolAddressesProvider provider;
    ILendingPool lendingPool = ILendingPool(lendingPoolAddress);
    address lendingPoolAddress;
    address tokenBorrow;
    address tokenTrade;
    uint256 amountBorrow;
    address router1;
    address router2;
    address WETH = 0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619;
    address WMATIC = 0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270;

    constructor(address _addressProvider) FlashLoanReceiverBase(ILendingPoolAddressesProvider(_addressProvider)) public {
        provider = ILendingPoolAddressesProvider(_addressProvider);
        lendingPoolAddress = provider.getLendingPool();
        lendingPool = ILendingPool(lendingPoolAddress);
    }

    function getAmountOutMin(address _tokenIn, address _tokenOut, uint256 _amountIn, address _router) external view returns (uint256) {
        address[] memory path = new address[](2);
        path[0] = _tokenIn;
        path[1] = _tokenOut;
        uint256[] memory amountOutMins = IUniswapV2Router01(_router).getAmountsOut(_amountIn, path);
        return amountOutMins[path.length -1];  
    }  

    function swapWei(
        address _tokenIn,
        address _tokenOut, 
        uint256 _amountIn, //input wei
        address _to,
        address _router
        ) public payable {

        uint256 _amountOutMin = this.getAmountOutMin(_tokenIn, _tokenOut, _amountIn, _router);
        IERC20(_tokenIn).approve(_router, _amountIn);

        address[] memory path = new address[](2);
        path[0] = _tokenIn;
        path[1] = _tokenOut;

        IUniswapV2Router01(_router).swapExactTokensForTokens(
            _amountIn, 
            _amountOutMin, 
            path, 
            _to, 
            block.timestamp
        );
    }

    function withdraw(address _token) public payable {
        IERC20(_token).transfer(msg.sender, IERC20(_token).balanceOf(address(this)));
    }

    function setUseless(address _a, bytes memory _b) public {

    }

    function getBalanceOf(address _token) external view returns (uint[] memory) {
        uint[] memory outp = new uint[](2);
        outp[0] = IERC20(_token).balanceOf(msg.sender) / 10 ** 18;
        outp[1] = IERC20(_token).balanceOf(address(this)) / 10 ** 18;
        return outp;
    }

     function executeOperation(
        address[] calldata assets,
        uint256[] calldata amounts,
        uint256[] calldata premiums,
        address initiator,
        bytes calldata params
    )
        external
        override
        returns (bool)
    {
        setUseless(initiator, params);

        //do swaps
        swapWei(tokenBorrow, tokenTrade, amountBorrow, address(this), router1);
        swapWei(tokenTrade, tokenBorrow, IERC20(tokenTrade).balanceOf(address(this)), address(this), router2);

        //repay flashloan
        for (uint i = 0; i < assets.length; i++) {
            uint amountOwing = amounts[i].add(premiums[i]);
            IERC20(assets[i]).approve(address(lendingPool), amountOwing);
        }

        return true;
    }

    function executeFlashLoans(address _tokenBorrow, uint256 _amt) private {
        address receiverAddress = address(this);

        // the various assets to be flashed
        address[] memory assets = new address[](1);
        assets[0] = _tokenBorrow; 
        
        // the amount to be flashed for each asset
        uint256[] memory amounts = new uint256[](1);
        amounts[0] = _amt;

        // 0 = no debt, 1 = stable, 2 = variable
        uint256[] memory modes = new uint256[](1);
        modes[0] = 0;

        address onBehalfOf = address(this);
        bytes memory params = "";
        uint16 referralCode = 0;

        lendingPool.flashLoan(
            receiverAddress,
            assets,
            amounts,
            modes,
            onBehalfOf,
            params,
            referralCode
        );
    }

    function run(
        address _tokenBorrow,
        address _tokenTrade,
        uint256 _amountBorrow, //input wei
        address _router1,
        address _router2)
        external {
        
        tokenBorrow = _tokenBorrow;
        tokenTrade = _tokenTrade;
        amountBorrow = _amountBorrow;
        router1 = _router1;
        router2 = _router2;
        executeFlashLoans(tokenBorrow, amountBorrow);
        withdraw(tokenBorrow);
    }
}
