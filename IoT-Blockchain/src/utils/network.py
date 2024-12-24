import os
from pathlib import Path

from pycardano import Network, OgmiosChainContext, ChainContext, BlockFrostChainContext,    CardanoCliChainContext, CardanoCliNetwork

ogmios_protocol = os.getenv("OGMIOS_API_PROTOCOL", "ws")
ogmios_host = os.getenv("OGMIOS_API_HOST", "localhost")
ogmios_port = os.getenv("OGMIOS_API_PORT", "1337")
ogmios_url = f"{ogmios_protocol}://{ogmios_host}:{ogmios_port}"

kupo_protocol = os.getenv("KUPO_API_PROTOCOL", "http")
kupo_host = os.getenv("KUPO_API_HOST", "localhost")
kupo_port = os.getenv("KUPO_API_PORT", "1442")
kupo_url = f"{kupo_protocol}://{kupo_host}:{kupo_port}"


network_name = os.getenv("NETWORK", "preview")#"preprod")

if network_name == "mainnet":
    network = Network.MAINNET
else:
    network = Network.TESTNET


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
