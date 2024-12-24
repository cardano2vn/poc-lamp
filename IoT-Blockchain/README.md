
This poc-lamp is a project of how to use the [PyCardano](https://github.com/Python-Cardano/pycardano) library 
with [opshin](https://github.com/OpShin/opshin) on Cardano.

PyCardano is a Cardano library written in Python. It allows users to create and sign transactions without depending on third-party Cardano serialization tools, such as cardano-cli and cardano-serialization-lib, making it a lightweight library, which is simple and fast to set up in all types of environments.

opshin is a Smart Contract language based on Python. It allows users to define and compile Smart Contracts directly within a python environment.
It also interacts seemlessly with PyCardano.


## What is Included

We have included a number of python scripts for executing specific actions.
You can find scripts to initialize addresses and interact with the cardano-node in `scripts`.
`src` contains two folders, `on_chain` which hosts the actual opshin contract and `off-chain` which
hosts tooling to interact with the contract.


## Setup


1. Install Python 3.8, 3.9 or 3.10.

On demeter.run or Linux/Ubuntu, this version of python is usually already pre-installed. You can skip this step.
For other Operating Systems, you can download the installer [here](https://www.python.org/downloads/release/python-3810/).

2. Ensure `python3 --version` works in your command line. Open a Terminal in the browser VSCode interface (F1 -> Terminal: Create New Terminal)
In Windows, you can do this by copying the `python.exe` file to `python3.exe` in your `PATH` environment variable.

3. Install python poetry.

On demeter.run or Linux/Ubuntu run 
```bash
curl -sSL https://install.python-poetry.org | python3 -
```
Follow the instructions diplayed to add poetry to your local shell.

Otherwise, follow the official documentation [here](https://python-poetry.org/docs/#installation).


4. Install a python virtual environment with poetry:
```bash
# install python dependencies
poetry install
# run a shell with the virtual environment activated
poetry shell
```

## Running the scripts

Go to the directory without smart contract

```
cd /xxx/poc-lamp/IoT-Blockchain
```
Run the environment

```
source venv/bin/activate
```

set the path variable for python

```
export PYTHONPATH=/xxx/poc-lamp/IoT-Blockchain/
```


Once you have entered the poetry shell, you can start interacting with the contract through the prepared scripts.

First, we have to build the vesting contract and generate two key pairs, one for the
owner of funds and one for the intended beneficiary.

```bash

python3 scripts/create_key_pair.py owner
python3 scripts/create_key_pair.py wallet
```

build smart contract into plutus scripts (cbor) 

```
python3 scripts/build.py
```

Make sure that the owner is loaded up with some testnet ada before proceeding,
by using the [testnet faucet](https://docs.cardano.org/cardano-testnet/tools/faucet).
You can find the address of the owner key by running this command

```bash
cat keys/owner.addr
```

Open file **xxx/poc-lamp/IoT-Blockchain/src/utils/network.py** and add method to interact with blockchain. here i use blockforst. you can go to blockforst.io to register account and use API

```python
def get_chain_context() -> ChainContext:
    chain_backend = os.getenv("CHAIN_BACKEND", "blockfrost")
    # chain_backend = os.getenv("CHAIN_BACKEND", "cardanocli")
    # chain_backend = os.getenv("CHAIN_BACKEND", "ogmios")
    if chain_backend == "ogmios":
        return OgmiosChainContext(ws_url=ogmios_url, network=network)
    elif chain_backend == "kupo":
        return OgmiosChainContext(ws_url=ogmios_url, network=network, kupo_url=kupo_url)
    elif chain_backend == "blockfrost":
        return BlockFrostChainContext("preprodxxxxxxxxxxxxxxxx", base_url="https://cardano-preprod.blockfrost.io/api/")
    elif chain_backend == "cardanocli":
        return CardanoCliChainContext(
                    binary=Path("/home/ada/.local/bin/cardano-cli"),
                    socket=Path("/opt/cardano/cnode/sockets/node.socket"),
                    network=CardanoCliNetwork.PREVIEW,
                    config_file=Path("/opt/cardano/cnode/files/config.json"),
                    network_magic_number=int(2),
                )
    else:
        raise ValueError(f"Chain backend not found: {chain_backend}")
```

Deploy smart contract to blockchain as input ref scripts

```
python3 src/off_chain/poc_deploy.py wallet owner
```

Mint NFT with CIP68

```
python3 src/off_chain/mint_nft_datum.py owner NFTxxx
```

Update metedata

```
python3 src/off_chain/update_datum_server.py 
```


 
 

