import time
import json
# import ogmios
import click
from pycardano import (
    OgmiosV6ChainContext,
    KupoOgmiosV6ChainContext,
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
    PlutusData
)

from pycardano.hash import SCRIPT_HASH_SIZE, DatumHash, ScriptHash

from src.on_chain.poc_lamp import MintRedeemer, UpdateRedeemer,  TrueRedeemer, metadata, metadata_poc
from src.utils import get_signing_info, get_address, network
from src.utils.network import get_chain_context, ogmios_url, kupo_url
from src.utils.contracts import get_contract
from src.on_chain import poc_lamp
import cbor2
from src.off_chain.convert_metadata import create_metadatum_json


# Tạo lớp PlutusData với tên trường trực tiếp
class MetadataExample(PlutusData):
    def __init__(self, name, description, image, mediaType):
        # Gọi hàm khởi tạo của lớp cha (PlutusData) nếu cần
        super().__init__()
        
        # Khởi tạo các thuộc tính
        self.name = name
        self.description = description
        self.image = image
        self.mediaType = mediaType

    # Phương thức khác nếu cần (nếu muốn sử dụng to_dict hoặc serialize)
    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "image": self.image,
            "mediaType": self.mediaType,
        }



@click.command()
@click.argument("wallet_name")
@click.argument("token_name")
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
    default=b"S01",
    help="SampleID",
)
@click.option(
    "--pocResult",
    type=bytes,
    default=b"P",
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

    # context = KupoOgmiosV6ChainContext(ws_url=ogmios_url, network=network, kupo_url=kupo_url)
    # context = ogmios.OgmiosChainContext("localhost", 1337)
    # context = OgmiosV6ChainContext("localhost", 1337)
    # context = KupoOgmiosV6ChainContext("localhost", 1337, kupo_url)
    
    #key=========================================================================================================================== 
    # Get payment address
    payment_vkey, payment_skey, payment_address = get_signing_info(wallet_name)
    vkey_owner_hash: VerificationKeyHash = payment_address.payment_part

    # get address smart contract
    script_cbor, script_hash, script_address = get_contract("poc_lamp")
    validator_hash=script_address.payment_part.to_primitive() #đưa vào datum

    
    #key===========================================================================================================================    



    signatures = []
    lovelace_amount=2000000
    # Find a script UTxO
    script_utxos = context.utxos(str(script_address))
    sc_utxo = ""
    claimable_utxos = []
    utxo_to_spend = None

    for item in script_utxos:
        if item.output.script:
            sc_utxo = item
    #     elif item.output.datum:
    #         outputdatum = cbor2.loads(item.output.datum.cbor)
            
    #         params = metadata(
    #             outputdatum.value[0],
    #             outputdatum.value[1],
    #             outputdatum.value[2],
    #             outputdatum.value[3],
    #             outputdatum.value[4],
    #             outputdatum.value[5],
    #             outputdatum.value[6],
    #             outputdatum.value[7],
    #             outputdatum.value[8],
    #         )
    #         if (
    #             params.pocOwner == bytes(payment_address.payment_part)
    #         ):
    #             pocOwner = Address(
    #                 VerificationKeyHash.from_primitive(params.pocOwner),
    #                 network=network,
    #             )
    #             """
    #             TODO: also check if the deadline has passed and if the oracle datum info is greater than the datum limit
    #             """
    #             claimable_utxos.append(
    #                 {
    #                 "utxo": item, 
    #                 "metadata": params
    #                 }
    #             )               
    #             break
    # # assert isinstance(utxo_to_spend, UTxO), "No script UTxOs found!"

    if not sc_utxo:
        print("smart contract UTxO not found!")
        exit(1)

    # if not len(claimable_utxos):
    #     print("no utxo to claim!")
    #     exit(1)

    # Find a collateral UTxO
    nft_utxo = []
    non_nft_utxo = None
    non_nft_utxo_spend = []
    # Get input utxo
    utxo_to_spend = None
    # Get all UTxOs currently sitting at this address
    utxos = context.utxos(payment_address)
    for utxo in utxos:
        # multi_asset should be empty for collateral utxo
        if not utxo.output.amount.multi_asset and utxo.output.amount.coin >= 4000000 and utxo.output.amount.coin < 6000000:
            non_nft_utxo = utxo
        # multi_asset should be empty for collateral utxo
        elif not utxo.output.amount.multi_asset:
            non_nft_utxo_spend.append(
                {"utxo":utxo,
                }
            )
            
        elif utxo.output.amount.coin > 10000000:
            utxo_to_spend = utxo

        else:
            nft_utxo.append(
                {"utxo":utxo,
                }
            )     
            
    # assert isinstance(non_nft_utxo, UTxO), "No collateral UTxOs found!"  
    assert utxo_to_spend is not None, "UTxO not found to spend!" 


    
    refprefix = '000643b0'  # (100)
    usrprefix = '000de140'  # (222))
    reftn_bytes = bytes.fromhex(refprefix) + bytes(token_name, encoding="utf-8")
    usrtn_bytes = bytes.fromhex(usrprefix )+ bytes(token_name, encoding="utf-8")
    multi_assets_ref= MultiAsset.from_primitive({bytes(script_hash): {reftn_bytes: amount}})
    multi_assets_usr= MultiAsset.from_primitive({bytes(script_hash): {usrtn_bytes: amount}})
    multi_asset= MultiAsset.from_primitive({
        bytes(script_hash): {
        reftn_bytes: amount,
        usrtn_bytes: amount,
        }
    })
    

    # datum_metadata = poc_lamp.metadata(
    #     pocName = bytes(pocname),
    #     pocPhone = bytes(pocphone),
    #     pocLocation =  bytes(poclocation),
    #     pocType = bytes(poctype),
    #     pocSampleID=bytes(pocsampleid),
    #     pocResult = bytes(pocresult),
    #     pocTtvalue = bytes(pocttvalue),
    #     validator_address=bytes(validator_hash),
    #     pocOwner = bytes(vkey_owner_hash)
    # )
    datum_metadata = metadata(
        pocOwner = bytes(vkey_owner_hash),
        validator_address=bytes(validator_hash),
        pocName = bytes(pocname),
        pocPhone = bytes(pocphone),
        pocLocation =  bytes(poclocation),
        pocType = bytes(poctype)
    )
    print(datum_metadata)
    


    # Build the transaction==========================================================================================================   
    builder = TransactionBuilder(context)
    #builder.add_input_address(payment_address)
    # We can also tell the builder to include a specific UTxO in the transaction.
    # Similarly, "add_input" could be called multiple times.

    # builder.add_input(utxos[0])
    builder.add_minting_script(script=script_cbor, redeemer=Redeemer(MintRedeemer()))
    builder.mint = multi_asset
    # builder.mint = multi_assets_usr 

    builder.add_input(utxo_to_spend)
    builder.add_output(
        TransactionOutput(address=script_address, amount=Value(lovelace_amount, multi_assets_ref), datum=datum_metadata) #datum_metadata) #gửi token Trade vào SC
    )
    builder.add_output(
        TransactionOutput(address=payment_address, amount=Value(lovelace_amount, multi_assets_usr))
    )

    # signatures.append(VerificationKeyHash(payment_vkey))
    builder.required_signers = signatures


    
    # builder.collaterals.append(non_nft_utxo)

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


  