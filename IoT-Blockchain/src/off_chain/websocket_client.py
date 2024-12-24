import asyncio
import websockets
import json

async def communicate(wallet_name, token_name, pocname, pocphone, poclocation, poctype,
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
    uri = "ws://cardano2vn.duckdns.org:8765"  
    async with websockets.connect(uri) as websocket:
        # Tạo metadata dạng JSON
        metadata = {
            "walletName" : str(wallet_name),
            "tokenName" : str(token_name),
            "pocName" : str(pocname),
            "pocPhone" : str(pocphone),
            "pocLocation" :  str(poclocation),
            "pocType" : str(poctype),
            "pocs1": str(pocs1),
            "pocs1result" : str(pocs1result),
            "pocs2": str(pocs2),
            "pocs2result" : str(pocs2result),
            "pocs3": str(pocs3),
            "pocs3result" : str(pocs3result),
            "pocs4": str(pocs4),
            "pocs4result" : str(pocs4result),
            "pocs5": str(pocs5),
            "pocs5result" : str(pocs5result),
            "pocs6": str(pocs6),
            "pocs6result" : str(pocs6result),
            "pocs7": str(pocs7),
            "pocs7result" : str(pocs7result),
            "pocs8": str(pocs8),
            "pocs8result" : str(pocs8result),
            "pocs9": str(pocs9),
            "pocs9result" : str(pocs9result),
            "pocs10": str(pocs10),
            "pocs10result" : str(pocs10result),
            "pocs11": str(pocs11),
            "pocs11result" : str(pocs11result),
            "pocs12": str(pocs12),
            "pocs12result" : str(pocs12result),
        }
        metadata_json = json.dumps(metadata)
        print(f"Sending JSON to server: {metadata}")

        # Gửi JSON đến server
        await websocket.send(metadata_json)

        # Nhận phản hồi từ server
        response = await websocket.recv()
        response_data = json.loads(response)
        print("Received JSON from server:")
        for key, value in response_data.items():
            print(f"{key}: {value}")

        # Nhận phản hồi từ server txhash
        response = await websocket.recv()
        response_data = json.loads(response)
        print("Received JSON from server:")
        for key, value in response_data.items():
            print(f"{key}: {value}")
# Ngọc đư các tham số vào đây và gọi hàm 
# asyncio.run(communicate(wallet_name, token_name, pocname, pocphone, poclocation, poctype, pocsampleid, pocresult, pocttvalue, amount))


wallet_name = "owner1"
token_name = "POC-LAMP01"
pocname = "Nguyen Van Hieu"
pocphone = "0912xxx" 
poclocation = "105.122 : 21.123" 
poctype = "COVID-19" 
pocsampleid = "001" 
pocresult = "P" 
pocttvalue ="1"  
amount = "1"
pocs1=pocsampleid
pocs2=pocsampleid
pocs3=pocsampleid
pocs4=pocsampleid
pocs5=pocsampleid
pocs6=pocsampleid
pocs7=pocsampleid
pocs8=pocsampleid
pocs9=pocsampleid
pocs10=pocsampleid
pocs11=pocsampleid
pocs12=pocsampleid

pocs1result=pocresult
pocs2result=pocresult
pocs3result=pocresult
pocs4result=pocresult
pocs5result=pocresult
pocs6result=pocresult
pocs7result=pocresult
pocs8result=pocresult
pocs9result=pocresult
pocs10result=pocresult
pocs11result=pocresult
pocs12result=pocresult



asyncio.run(communicate(wallet_name, token_name, pocname, pocphone, poclocation, poctype,
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
                        )
            
            )