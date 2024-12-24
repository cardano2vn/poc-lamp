import time

import click
from pycardano import *
# from pycardano import (
#     OgmiosChainContext,
#     TransactionBuilder,
#     TransactionOutput,
#     VerificationKeyHash, Network,
# )

#from opshin.ledger.api_v2 import *
from src.on_chain import poc_lamp
from src.on_chain.poc_lamp import MintRedeemer, UpdateRedeemer,  TrueRedeemer
from src.utils import get_signing_info, get_address, network
from src.utils.network import get_chain_context
from src.utils.contracts import get_contract


# ==============================================
# from dotenv import load_dotenv
# load_dotenv()

# ==============================================



@click.command()
@click.argument("name")
@click.argument("beneficiary")
@click.option(
    "--amount",
    type=int,
    default=30000000,
    help="Amount of lovelace to send to the script address.",
)
@click.option(
    "--wait_time",
    type=int,
    default=0,
    help="Time until the vesting contract deadline from current time",
)



def main(name: str, beneficiary: str, amount: int, wait_time: int):
    # Load chain context
    #context = OgmiosChainContext(ogmios_url, network=network, kupo_url=kupo_url)
    context = get_chain_context()

    # wallet = Wallet()
    # context=wallet.context
    
    # # Get payment address
    payment_address = get_address(name)
    vkey_owner_hash: VerificationKeyHash = payment_address.payment_part


    # # Get the beneficiary VerificationKeyHash (PubKeyHash)
    # beneficiary_address = get_address(beneficiary)
    # vkey_hash: VerificationKeyHash = beneficiary_address.payment_part


    bot_addr=Address.decode("addr_test1qq9mrj6gxeny2cl99thrd6wvv3vr8n3tvtxa78jgdxegjp3p4neh4ew5j446xthascrs6t6k3x48jqum62yq06gf8wkslw2scz")
    vkey_owner_hash: VerificationKeyHash = VerificationKeyHash(bytes.fromhex('0bb1cb4836664563e52aee36e9cc645833ce2b62cddf1e4869b28906')) #bot_addr.payment_part #
    print(f"vkey_owner_hash: {vkey_owner_hash}")

    bot_addr1=Address.decode("addr_test1qpkxr3kpzex93m646qr7w82d56md2kchtsv9jy39dykn4cmcxuuneyeqhdc4wy7de9mk54fndmckahxwqtwy3qg8pums5vlxhz")
    vkey_hash: VerificationKeyHash = VerificationKeyHash(bytes.fromhex('6c61c6c1164c58ef55d007e71d4da6b6d55b175c18591225692d3ae3')) #bot_addr1.payment_part #
    print(f"vkey_hash: {vkey_hash}")
    
   

    _, _, fee_address = get_signing_info(beneficiary)
    fee_address=fee_address.payment_part.to_primitive() #đưa vào datum


    script_cbor, script_hash, script_address = get_contract("poc_lamp")
    validator_hash=script_address.payment_part.to_primitive() #đưa vào datum
    #contract_script = PlutusV2Script(bytes.fromhex(script_cbor))
    


    datum_metadata = poc_lamp.metadata(
        pocOwner = bytes(vkey_owner_hash),
        validator_address=bytes(validator_hash),
        pocName = b"Nguyen Van A",
        pocPhone = b"0912xxx",
        pocLocation =  b"105.000;21.0101",
        pocType = b"COVID-19"
    )
    # Make datum
    datum = datum_metadata
    amount_send=37500000

    # Build the transaction
    builder = TransactionBuilder(context)
    builder.add_input_address(payment_address)
    builder.add_output(
        TransactionOutput(address=script_address, amount=amount_send, datum=datum, script=script_cbor)
    )
    # builder.add_output(
    #     TransactionOutput(address=payment_address, amount=int(5000000))
    # )

    # Sign the transaction
    payment_vkey, payment_skey, payment_address = get_signing_info(name)
    signed_tx = builder.build_and_sign(
        signing_keys=[payment_skey],
        change_address=payment_address,
    )

    
    # Submit the transaction
    context.submit_tx(signed_tx.to_cbor())

    print(f"transaction id: {signed_tx.id}")
    if network == Network.TESTNET:
        print(f"Cexplorer: https://preview.cexplorer.io/tx/{signed_tx.id}")
    else:
        print(f"Cexplorer: https://cexplorer.io/tx/{signed_tx.id}")


if __name__ == "__main__":
    main()
