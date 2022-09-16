import time
from brownie import Arb, network, accounts


def deploy():
    aaveLendingPoolProvider = '0xd05e3E715d945B59290df0ae8eF85c1BdB684744'
    account = getAccount()
    print(account)
    Arb.deploy(aaveLendingPoolProvider, {"from": account})


def getAccount():
    PRIVATE_KEY = 0x0000
    if network.show_active() == "development":
        return accounts[0]
    else:
        return accounts.add(PRIVATE_KEY)
        # return accounts[0]


def runIt(_tokenBorrow, _tokenTrade, _amountBorrow, _router1, _router2):
    account = getAccount()
    Arb[-1].run(_tokenBorrow, _tokenTrade, _amountBorrow, _router1, _router2, {"from": account})


def getBalanceOf(_token):
    account = getAccount()
    balance = Arb[-1].getBalanceOf(_token, {"from": account})
    print(balance)


def withdraw(_token):
    account = getAccount()
    Arb[-1].withdraw(_token, {"from": account})


def getPrice(_borrow, _token1, _token2, _weiInput, _router):
    weiOutput = Arb[-1].getAmountOutMin(_token1, _token2, _weiInput, _router)
    if _token1 == _borrow:
        return _weiInput/weiOutput
    else:
        return weiOutput/_weiInput


def getConversion(_borrow, _token, _router1, _router2, _weiInput):
    tax = 0  # input parameter?
    priceBuy1 = getPrice(_borrow, _borrow, _token, _weiInput, _router1)
    priceSell2 = getPrice(_borrow, _token, _borrow, _weiInput, _router2)
    gain = (priceSell2 * (1 - tax / 100) ** 2 - priceBuy1) / priceBuy1
    return gain


def search():
    thresh = .002  # as decimal
    wCheck = 10 ** 19  # as wei
    bMult = 1  # changes weiInput based on borrowed token
    borrows = ['0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270', '0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619']  # WMATIC, WETH
    tokens = ['0x53E0bca35eC356BD5ddDFebbD1Fc0fD03FaBad39', '0xD6DF932A45C0f255f85145f286eA0b292B21C90B', '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174', '0xc2132D05D31c914a87C6611C10748AEb04B58e8F', '0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619', '0x1BFD67037B42Cf73acF2047067bd4F2C47D9BfD6', '0x172370d5Cd63279eFa6d502DAB29171933a610AF', '0xBbba073C31bF03b8ACf7c28EF0738DeCF3695683', '0xE06Bd4F5aAc8D0aA337D13eC88dB6defC6eAEefE', '0x64060aB139Feaae7f06Ca4E63189D86aDEb51691', '0xA1c57f48F0Deb89f569dFbE6E2B7f46D33606fD4', '0x385Eeac5cB85A38A9a07A70c73e0a3271CfB54A7', '0xdF7837DE1F2Fa4631D716CF2502f8b230F1dcc32', '0x1599fE55Cda767b1F631ee7D414b41F5d6dE393d', '0x831753DD7087CaC61aB5644b308642cc1c33Dc13', '0xD85d1e945766Fea5Eda9103F918Bd915FbCa63E6', '0x91c89A94567980f0e9723b487b0beD586eE96aa7', '0x6DdB31002abC64e1479Fc439692F7eA061e78165', '0xee7666aACAEFaa6efeeF62ea40176d3eB21953B9', '0x8765f05adce126d70bcdf1b0a48db573316662eb', '0xDAB625853c2B35D0a9C6bD8e5a097a664ef4CcFb', '0x45c32fA6DF82ead1e2EF74d17b76547EDdFaFF89', '0x5fe2B58c013d7601147DcdD68C143A77499f5531', '0x6f7C932e7684666C9fd1d44527765433e01fF61d', '0x41b3966B4FF7b427969ddf5da3627d6AEAE9a48E', '0x50B728D8D964fd00C2d0AAD81718b71311feF68a', '0xDA537104D6A5edd53c6fBba9A898708E465260b6', '0x9c2C5fd7b07E95EE044DDeba0E97a665F142394f', '0x3066818837c5e6eD6601bd5a91B0762877A6B731']
    routers = ['0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff', '0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506', '0x3a1D87f206D12415f5b0A33E786967680AAb4f6d', '0x5C6EC38fb0e2609672BDf628B1fD605A523E5923', '0xcF0feBd3f17CEf5b47b0cD257aCf6025c5BFf3b7', '0x546C79662E028B661dFB4767664d0273184E4dD1', '0xC60aE14F2568b102F8Ca6266e8799112846DD088']
    weiInputs = [wCheck, wCheck * 10**5, wCheck * 10**4, wCheck * 10**3, wCheck * 10**2, wCheck * 10, wCheck]  # first w checks for profit
    for t in tokens:
        print(t)
        for r1 in range(len(routers)):
            print(r1)
            for r2 in range(len(routers)):
                for b in borrows:
                    for w in weiInputs:
                        if r1 == r2:  # to not repeat routers
                            break

                        if b == '0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619':
                            # WETH
                            bMult = 10 ** 3
                            w = w / bMult
                        elif b == '0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270':
                            # WMATIC
                            bMult = 1

                        try:
                            gain = getConversion(b, t, routers[r1], routers[r2], w)
                        except:
                            # print('ERROR: RETRIEVING PRICE FAILED')
                            break
                        if gain < thresh and w * bMult == wCheck:
                            break

                        if gain > thresh and w * bMult != wCheck:
                            print(gain)
                            print('borrow ' + str(w/10**18) + ' ' + str(b))
                            print(routers[r1])
                            print(routers[r2])
                            try:
                                runIt(b, t, w, routers[r1], routers[r2])
                            except:
                                print('ERROR: RUN FAILED')
                                try:
                                    runIt(b, t, w, routers[r1], routers[r2])
                                except:
                                    break
                            break


def main():
    # deploy()
    print(Arb[-1])
    getBalanceOf('0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270')

    while True:
        search()

