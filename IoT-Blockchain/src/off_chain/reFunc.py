import json
import click
from pycardano import (
    OgmiosChainContext,
    TransactionBuilder,
    TransactionOutput,
    UTxO,
    Redeemer,
    VerificationKeyHash,
    DeserializeException, Network,
    Value, Address,
    MultiAsset,
    AssetName,
    Asset,

)
from pycardano.hash import SCRIPT_HASH_SIZE, DatumHash, ScriptHash

from src.on_chain.poc_lamp import MintRedeemer, UpdateRedeemer,  TrueRedeemer, metadata 
from src.utils import get_signing_info, get_address, network
from src.utils.network import get_chain_context
from src.utils.contracts import get_contract
from src.on_chain import poc_lamp
import cbor2



@click.command()
@click.argument("wallet_name")
# @click.argument("token_name")
@click.option(
    "--token_name",
    type=str,
    default=b"NFT1",
    help="Token Name",
)
@click.option(
    "--pocName",
    type=bytes,
    default=b"Nguyen Van Hieu",
    help="User Name.",
)

@click.option(
    "--pocPhone",
    type=bytes,
    default=b"0912066909",
    help="Phone Number.",
)
@click.option(
    "--pocLocation",
    type=bytes,
    default=b"105.000;21.0101",
    help="Location log/lat.",
)
@click.option(
    "--pocType",
    type=bytes,
    default=b"COVID-19",
    help="Test type ex. COVID-19, AIV, Afican.",
)
@click.option(
    "--pocSampleID",
    type=bytes,
    default=b"SampleID_0001",
    help="SampleID",
)
@click.option(
    "--pocResult",
    type=bytes,
    default=b"Pos",
    help="Result Negative/Positive",
)
@click.option(
    "--pocTtvalue",
    type=bytes,
    default=b'100',
    help="Result Negative/Positive",
)
@click.option(
    "--amount",
    type=int,
    default=1,
    help="Amount of tokens",
)
def main(wallet_name, token_name, pocname, pocphone, poclocation, poctype, pocsampleid, pocresult, pocttvalue, amount):

    print(f"Wallet Name: {wallet_name}")
    print(f"Token Name: {token_name}")
    print(f"Amount: {amount}")
    print(f"User Name: {pocname}")
    print(f"Phone Number: {pocphone}")
    print(f"Location: {poclocation}")
    print(f"Test Type: {poctype}")
    print(f"SampleID: {pocsampleid}")
    print(f"Test Result: {pocresult}")
    print(f"Test TT Value: {pocttvalue}")


    # Load chain context
    context = get_chain_context()

    #key=========================================================================================================================== 
    # Get payment address
    payment_vkey, payment_skey, payment_address = get_signing_info(wallet_name)
    vkey_owner_hash: VerificationKeyHash = payment_address.payment_part

    # get address smart contract
    script_cbor, script_hash, script_address = get_contract("poc_lamp")
    validator_hash=script_address.payment_part.to_primitive() #đưa vào datum
    datum_metadata = poc_lamp.metadata(
        pocOwner = bytes(vkey_owner_hash),
        pocName = bytes(pocname),
        pocPhone = bytes(pocphone),
        pocLocation =  bytes(poclocation),
        pocType = bytes(poctype),
        pocSampleID=bytes(pocsampleid),
        pocResult = bytes(pocresult),
        pocTtvalue = bytes(pocttvalue),
        validator_address=bytes(validator_hash)
    )
    
    #key===========================================================================================================================    

    #Thay đổi ==================================================================
    # Find a script UTxO
    script_utxos = context.utxos(str(script_address))
    sc_utxo = ""
    claimable_utxos = []
    utxo_to_spend = None

    for item in script_utxos:
        if item.output.script:
            sc_utxo = item
        elif item.output.datum:
            odatum  = cbor2.loads(item.output.datum.cbor)
            outputdatum=odatum.value[1]

            params = metadata(
                outputdatum[0],
                outputdatum[1],
                outputdatum[2],
                outputdatum[3],
                outputdatum[4],
                outputdatum[5],
                outputdatum[6],
                outputdatum[7],
                outputdatum[8],
            )
            if (
                params.pocOwner == bytes(payment_address.payment_part)
            ):
                pocOwner = Address(
                    VerificationKeyHash.from_primitive(params.pocOwner),
                    network=network,
                )
                """
                TODO: also check if the deadline has passed and if the oracle datum info is greater than the datum limit
                """
                claimable_utxos.append(
                    {
                    "utxo": item, 
                    "metadata": params
                    }
                )               
                # break
    # # assert isinstance(utxo_to_spend, UTxO), "No script UTxOs found!"

    if not sc_utxo:
        print("smart contract UTxO not found!")
        exit(1)

    if not len(claimable_utxos):
        print("no utxo to claim!")
        exit(1)

    # Find a collateral UTxO
    nft_utxo = []
    non_nft_utxo = None
    non_nft_utxo_spend = []
    # Get all UTxOs currently sitting at this address
    utxos = context.utxos(payment_address)
    for utxo in utxos:
        print(utxo)
        
        # multi_asset should be empty for collateral utxo
        if not utxo.output.amount.multi_asset and utxo.output.amount.coin >= 5000000 and utxo.output.amount.coin < 10000000:
            non_nft_utxo = utxo
        # multi_asset should be empty for collateral utxo
        elif not utxo.output.amount.multi_asset:
            non_nft_utxo_spend.append(
                {"utxo":utxo,
                }
            ) 
        else:
            nft_utxo.append(
                {"utxo":utxo,
                }
            )     
          
    assert isinstance(non_nft_utxo, UTxO), "No collateral UTxOs found!"  


    tn_bytes = bytes(token_name, encoding="utf-8")
    multi_assets= MultiAsset.from_primitive({bytes(script_hash): {tn_bytes: amount}})

    signatures = []
    lovelace_amount=3000000



    # Build the transaction==========================================================================================================   
    builder = TransactionBuilder(context)
    #builder.add_input_address(payment_address)
    # We can also tell the builder to include a specific UTxO in the transaction.
    # Similarly, "add_input" could be called multiple times.

    # builder.add_input(utxos[0])
   # reference_inputs smart contract
    builder.reference_inputs.add(sc_utxo)
    for utxo_to_input_spend in non_nft_utxo_spend: # Lovelace
        builder.add_input(utxo_to_input_spend["utxo"])
        # print(utxo_to_input_spend["utxo"])

    i=0
    for utxo_to_spend in claimable_utxos:

        builder.add_script_input(utxo_to_spend["utxo"], redeemer=Redeemer(TrueRedeemer())) #redeemer=Redeemer(RefundRedeemer())) # thay đổ khi dùng ref_scripts để refund 1 lần được tất cả
        # print(utxo_to_spend["utxo"])

        i+=1
        if i>15:
            break       
        # output for BatcherFee
        # print(utxo_to_spend["BatcherFee_addr"])
        # print(utxo_to_spend["fee"])

    # builder.add_script_input(sc_utxo, redeemer=Redeemer(TrueRedeemer()))  
   
    builder.collaterals.append(non_nft_utxo)
    # print(non_nft_utxo)
    # exit(1)
    # This tells pycardano to add vkey_hash to the witness set when calculating the transaction cost
    builder.required_signers = [vkey_owner_hash]
    # we must specify at least the start of the tx valid range in slots
    builder.validity_start = context.last_block_slot
    # This specifies the end of tx valid range in slots
    builder.ttl = builder.validity_start + 1000

    # Sign the transaction
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


  
#     # # assert isinstance(utxo_to_spend, UTxO), "No script UTxOs found!"

#     if not sc_utxo:
#         print("smart contract UTxO not found!")
#         exit(1)

#     # if not len(claimable_utxos):
#     #     print("no utxo to claim!")
#     #     exit(1)

#     # Find a collateral UTxO
#     nft_utxo = []
#     non_nft_utxo = None
#     non_nft_utxo_spend = []
#     # Get all UTxOs currently sitting at this address
#     utxos = context.utxos(payment_address)
#     for utxo in utxos:
#         # multi_asset should be empty for collateral utxo
#         if not utxo.output.amount.multi_asset and utxo.output.amount.coin >= 4000000 and utxo.output.amount.coin < 6000000:
#             non_nft_utxo = utxo
#         # multi_asset should be empty for collateral utxo
#         elif not utxo.output.amount.multi_asset:
#             non_nft_utxo_spend.append(
#                 {"utxo":utxo,
#                 }
#             ) 
#         else:
#             nft_utxo.append(
#                 {"utxo":utxo,
#                 }
#             )     
            
#     assert isinstance(non_nft_utxo, UTxO), "No collateral UTxOs found!"  


#     tn_bytes = bytes(token_name, encoding="utf-8")
#     multi_assets= MultiAsset.from_primitive({bytes(script_hash): {tn_bytes: amount}})

#     signatures = []
#     lovelace_amount=3000000
#     # Build the transaction==========================================================================================================   
#     builder = TransactionBuilder(context)
#     #builder.add_input_address(payment_address)
#     # We can also tell the builder to include a specific UTxO in the transaction.
#     # Similarly, "add_input" could be called multiple times.

#     # builder.add_input(utxos[0])
#     builder.add_minting_script(script=script_cbor, redeemer=Redeemer(MintRedeemer()))
#     builder.mint = multi_assets #MultiAsset.from_primitive({bytes(script_hash): {tn_bytes: amount}})
#     for utxo_to_input_spend in non_nft_utxo_spend: # Lovelace
#         builder.add_input(utxo_to_input_spend["utxo"])
#         # print(utxo_to_input_spend["utxo"])

#     # for utxo_to_input in nft_utxo: # Token
#     #     builder.add_input(utxo_to_input["utxo"])

#    # reference_inputs smart contract
#     builder.reference_inputs.add(sc_utxo)

#     builder.add_output(
#         TransactionOutput(address=script_address, amount=Value(lovelace_amount, multi_assets), datum=datum_metadata) #gửi token Trade vào SC
#     )

#     # signatures.append(VerificationKeyHash(payment_vkey))
#     builder.required_signers = signatures


    
#     builder.collaterals.append(non_nft_utxo)
#     # This tells pycardano to add vkey_hash to the witness set when calculating the transaction cost
#     builder.required_signers = [vkey_owner_hash]
#     # we must specify at least the start of the tx valid range in slots
#     builder.validity_start = context.last_block_slot
#     # This specifies the end of tx valid range in slots
#     builder.ttl = builder.validity_start + 1000

#     # Sign the transaction
#     signed_tx = builder.build_and_sign(
#         signing_keys=[payment_skey],
#         change_address=payment_address,
#     )
    

#     # Submit the transaction
#     context.submit_tx(signed_tx.to_cbor())

#     print(f"transaction id: {signed_tx.id}")
#     if network == Network.TESTNET:
#         print(f"Cexplorer: https://preview.cexplorer.io/tx/{signed_tx.id}")
#     else:
#         print(f"Cexplorer: https://cexplorer.io/tx/{signed_tx.id}")

 

# if __name__ == "__main__":
#     main()


  