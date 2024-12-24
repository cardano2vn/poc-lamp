import time
import json
import click
import asyncio
import websockets

from pycardano import (
    OgmiosV6ChainContext,
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
    # PubKeyHash, PlutusData, dataclass,

)
from pycardano.hash import SCRIPT_HASH_SIZE, DatumHash, ScriptHash

from src.on_chain.poc_lamp import MintRedeemer, UpdateRedeemer,  TrueRedeemer, metadata, metadata_poc
from src.utils import get_signing_info, get_address, network
from src.utils.network import get_chain_context
from src.utils.contracts import get_contract
from src.on_chain import poc_lamp
import cbor2


def update_datum(wallet_name, token_name, pocname, pocphone, poclocation, poctype,
                 pocs1, pocs1result, 
                 pocs2, pocs2result, 
                 pocs3, pocs3result, 
                 pocs4, pocs4result, 
                 pocs5, pocs5result, 
                 pocs6, pocs6result, 
                 pocs7, pocs7result, 
                 pocs8, pocs8result, 
                 pocs9, pocs9result, 
                 pocs10, pocs10result, 
                 pocs11, pocs11result,
                 pocs12, pocs12result,                   
                 ):
    amount=1
    print(f"Wallet Name: {wallet_name}")
    print(f"Token Name: {token_name}")
    #key=========================================================================================================================== 
    # Get payment address
    payment_vkey, payment_skey, payment_address = get_signing_info(wallet_name)
    vkey_owner_hash: VerificationKeyHash = payment_address.payment_part

    # get address smart contract
    script_cbor, script_hash, script_address = get_contract("poc_lamp")
    validator_hash=script_address.payment_part.to_primitive() #đưa vào datum

    refprefix = '000643b0'  # (100)
    usrprefix = '000de140'  # (222))
    reftn_bytes = bytes.fromhex(refprefix) + bytes(token_name, encoding="utf-8")
    asset_name_update=""
    usrtn_bytes = bytes.fromhex(usrprefix )+ bytes(token_name, encoding="utf-8")
    multi_assets_ref= MultiAsset.from_primitive({bytes(script_hash): {reftn_bytes: amount}})
    multi_assets_usr= MultiAsset.from_primitive({bytes(script_hash): {usrtn_bytes: amount}})
    multi_asset= MultiAsset.from_primitive({
        bytes(script_hash): {
        reftn_bytes: amount,
        }
    })

    # Load chain context
    context = get_chain_context()
    # context = OgmiosV6ChainContext("localhost", 1337)


    # datum_metadata = metadata(
    #     pocOwner = bytes(vkey_owner_hash),
    #     pocName = bytes(pocname),
    #     pocPhone = bytes(pocphone),
    #     pocLocation =  bytes(poclocation),
    #     pocType = bytes(poctype),
    #     pocSampleID=bytes(pocsampleid),
    #     pocResult = bytes(pocresult),
    #     pocTtvalue = bytes(pocttvalue),
    #     validator_address=bytes(validator_hash)
    # )
    
    datum_metadata = metadata_poc(
        pocOwner = bytes(vkey_owner_hash),
        validator_address=bytes(validator_hash),
        pocName = bytes(pocname, "utf-8"),
        pocPhone = bytes(pocphone, "utf-8"),
        pocLocation =  bytes(poclocation, "utf-8"),
        pocType = bytes(poctype, "utf-8"),
        pocS1 =bytes(pocs1, "utf-8"), 
        pocS1Result = bytes(pocs1result, "utf-8"), 
        pocS2 = bytes(pocs2, "utf-8"),
        pocS2Result = bytes(pocs2result, "utf-8"),
        pocS3 = bytes(pocs3, "utf-8"), 
        pocS3Result = bytes(pocs3result, "utf-8"),
        pocS4 = bytes(pocs4, "utf-8"), 
        pocS4Result = bytes(pocs4result, "utf-8"),
        pocS5 = bytes(pocs5, "utf-8"), 
        pocS5Result = bytes(pocs5result, "utf-8"),
        pocS6 = bytes(pocs6, "utf-8"), 
        pocS6Result = bytes(pocs6result, "utf-8"),
        pocS7 = bytes(pocs7, "utf-8"), 
        pocS7Result = bytes(pocs7result, "utf-8"),
        pocS8 = bytes(pocs8, "utf-8"), 
        pocS8Result = bytes(pocs8result, "utf-8"),
        pocS9 = bytes(pocs9, "utf-8"), 
        pocS9Result = bytes(pocs9result, "utf-8"),
        pocS10 = bytes(pocs10, "utf-8"), 
        pocS10Result = bytes(pocs10result, "utf-8"), 
        pocS11 = bytes(pocs11, "utf-8"), 
        pocS11Result = bytes(pocs11result, "utf-8"),
        pocS12 = bytes(pocs12, "utf-8"), 
        pocS12Result = bytes(pocs12result, "utf-8"),
    )
 

    print(datum_metadata)
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
            # print(sc_utxo)
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

            )
            multi_asset_NFT = item.output.amount.multi_asset

            # Duyệt qua các `AssetName`
            for script_hash, assets in multi_asset_NFT.items():
                print(f"Script Hash: {script_hash}")
                for asset_name, quantity in assets.items():
                    # Chuyển đổi AssetName thành chuỗi dễ đọc
                    print(f"asset_name: {reftn_bytes.hex()}")
                    asset_name_update=asset_name
                    print(f"Asset Name: {asset_name_update}, Quantity: {quantity}")
            
                    #print(f"Asset: {multi_assets2}")    
                    #print(f"Asset: {multi_assets1}")   

                    if (
                        params.pocOwner == bytes(payment_address.payment_part)   and str(reftn_bytes.hex())==str(asset_name_update)
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
                        break
    # assert isinstance(utxo_to_spend, UTxO), "No script UTxOs found!"

    if not sc_utxo:
        print("smart contract UTxO not found!")
        return "Error -> Smart contract UTxO not found!"

    if not len(claimable_utxos):
        print("no utxo to claim!")
        return "Error -> No NFT to update!"

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
            
        elif utxo.output.amount.coin > 30000000:
            utxo_to_spend = utxo

        else:
            nft_utxo.append(
                {"utxo":utxo,
                }
            )     
            
    assert isinstance(non_nft_utxo, UTxO), "No collateral UTxOs found!"  
    assert utxo_to_spend is not None, "UTxO not found to spend!" 


    # Cần đọc multi_assets1
    # tn_bytes= bytes(token_name, encoding="utf-8")
    # multi_assets1= MultiAsset.from_primitive({bytes(script_hash): {tn_bytes: amount}})


    lovelace_amount=2000000
    # Build the transaction==========================================================================================================   
    builder = TransactionBuilder(context)
    #builder.add_input_address(payment_address)
    # We can also tell the builder to include a specific UTxO in the transaction.
    # Similarly, "add_input" could be called multiple times.

    # builder.add_input(utxos[0])
    builder.add_input(utxo_to_spend)
    print(f"utxo_to_spend: {utxo_to_spend}")

    # for utxo_to_input_spend in non_nft_utxo_spend: # Lovelace
    #     builder.add_input(utxo_to_input_spend["utxo"])
    #     print(utxo_to_input_spend["utxo"])

    # for utxo_to_input in nft_utxo: # Token
    #     builder.add_input(utxo_to_input["utxo"])

   # reference_inputs smart contract
    builder.reference_inputs.add(sc_utxo)

    for utxo_to_spend in claimable_utxos:
        builder.add_script_input(utxo_to_spend["utxo"], redeemer=Redeemer(UpdateRedeemer()))
        print("utxo_spend_sc:")
        print(utxo_to_spend["utxo"])
        # builder.add_script_input(utxo_to_spend["utxo"], script=script_cbor, redeemer=Redeemer(UpdateRedeemer()))
        
        #print(f"Asset: {multi_assets2}")    
        #print(f"Asset: {multi_assets1}")   
        # Make datum


        #print(f"datum2.buyPrice= {datum2.buyPrice} params.buyPrice= {params.buyPrice}")

        builder.add_output(
            TransactionOutput(address=script_address, amount=Value(lovelace_amount, multi_assets_ref), datum=datum_metadata) #gửi token Trade vào SC
        )

        # break
     

    builder.collaterals.append(non_nft_utxo)
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
        print(f"Cexplorer: https://preprod.cexplorer.io/tx/{signed_tx.id}")
    else:
        print(f"Cexplorer: https://cexplorer.io/tx/{signed_tx.id}")
    return signed_tx.id

 

async def handle_client(websocket, path):
    print("Client connected")
    try:
        async for message in websocket:
            print(f"Received from client: {message}")
            
            # Giả sử client gửi metadata dưới dạng JSON
            try:
                client_data = json.loads(message)
                print("walletName:", client_data["walletName"])
                print(client_data["tokenName"]) 
                print(client_data["pocName"]) 
                print(client_data["pocs12result"])


                response_data = {
                    "Creating transaction update datum!": "...",                  # Giả sử là PubKeyHash dạng chuỗi
                }
                response_json = json.dumps(response_data) # gửi phản hồi.
                # Gửi phản hồi dạng JSON
                await websocket.send(response_json)
                
                # lấy từ client_data
                # response_tx="123OK"
                response_tx= update_datum(
                    client_data["walletName"],
                    client_data["tokenName"], 
                    client_data["pocName"], 
                    client_data["pocPhone"], 
                    client_data["pocLocation"], 
                    client_data["pocType"], 
                    client_data["pocs1"], 
                    client_data["pocs1result"], 
                    client_data["pocs2"], 
                    client_data["pocs2result"],
                    client_data["pocs3"], 
                    client_data["pocs3result"], 
                    client_data["pocs4"], 
                    client_data["pocs4result"],
                    client_data["pocs5"], 
                    client_data["pocs5result"], 
                    client_data["pocs6"], 
                    client_data["pocs6result"],
                    client_data["pocs7"], 
                    client_data["pocs7result"], 
                    client_data["pocs8"], 
                    client_data["pocs8result"],
                    client_data["pocs9"], 
                    client_data["pocs9result"], 
                    client_data["pocs10"], 
                    client_data["pocs10result"], 
                    client_data["pocs11"], 
                    client_data["pocs11result"], 
                    client_data["pocs12"], 
                    client_data["pocs12result"]
                    ) #Gửi lên Blockchain b


                # Tạo JSON phản hồi

                response_data = {
                    "Response":  str(response_tx),                  # Giả sử là PubKeyHash dạng chuỗi
                }
                response_json = json.dumps(response_data) # gửi phản hồi. 

                # Gửi phản hồi dạng JSON
                await websocket.send(response_json)
                print("Sent JSON to client:", response_data)
            except json.JSONDecodeError:
                await websocket.send(json.dumps({"error": "Invalid JSON format"}))
    except websockets.exceptions.ConnectionClosedOK:
        print("Client disconnected")

async def main():
    # Lắng nghe trên tất cả địa chỉ IP với cổng 8765
    async with websockets.serve(handle_client, "0.0.0.0", 8765):
        print("WebSocket server started on ws://0.0.0.0:8765")
        await asyncio.Future()  # Chạy vô hạn

asyncio.run(main())

  