AppName="5P50101877"
AppSource=21885
UserID="B8I7uoAKrTv"
Password="v20Crs1503k"
UserKey="BqlWZe4zncP6S2WKTHRDw7yUz8L7tCZP"
EncryptionKey="ZAsxzvvnWK6sj3qxkfsUBYYhievD0Jbq"
Validupto="3/30/2050 12:00:00 PM"
Redirect_URL="Null"
totpstr="GUYDCMBRHA3TOXZVKBDUWRKZ"

from py5paisa import FivePaisaClient
import pyotp
client=None
def login():
    global client
    cred={
        "APP_NAME":AppName,
        "APP_SOURCE":AppSource,
        "USER_ID":UserID,
        "PASSWORD":Password,
        "USER_KEY":UserKey,
        "ENCRYPTION_KEY":EncryptionKey
        }

    twofa = pyotp.TOTP(totpstr)
    twofa = twofa.now()
    client = FivePaisaClient(cred=cred)
    client.get_totp_session(client_code=50101877,totp=twofa,pin=654321)
    client.get_oauth_session('Your Response Token')
    print(client.get_access_token())

def get_historical_data():
    global client
    df=client.historical_data('N','C',1660,'1d','2024-03-01','2024-03-03')
    print(df)


def get_live_market_feed():
    global client
    req_list_ = [{"Exch": "N", "ExchType": "C", "ScripData": "ITC"},
    {"Exch": "N", "ExchType": "C", "ScripCode": "2885"}]

    print(client.fetch_market_feed_scrip(req_list_))

def previousdayclose(code):
    global client
    req_list_ = [{"Exch": "N", "ExchType": "C", "ScripCode": code}]
    responce=client.fetch_market_feed_scrip(req_list_)
    pclose_value = float(responce['Data'][0]['PClose'])
    return pclose_value


def get_ltp(code):
    global client
    req_list_ = [{"Exch": "N", "ExchType": "C", "ScripCode": code}]
    responce=client.fetch_market_feed_scrip(req_list_)
    last_rate = float(responce['Data'][0].get('LastRate', 0))
    print(last_rate)

    return last_rate

def buy( ScripCode , Qty, Price,OrderType='B',Exchange='N',ExchangeType='C'):
    global client
    client.place_order(OrderType=OrderType,
                       Exchange=Exchange,
                       ExchangeType=ExchangeType,
                       ScripCode = ScripCode,
                       Qty=Qty,
                       Price=Price)

def sell( ScripCode , Qty, Price,OrderType='S',Exchange='N',ExchangeType='C'):
    global client
    client.place_order(OrderType=OrderType,
                       Exchange=Exchange,
                       ExchangeType=ExchangeType,
                       ScripCode = ScripCode,
                       Qty=Qty,
                       Price=Price)
def short( ScripCode , Qty, Price,OrderType='S',Exchange='N',ExchangeType='C'):
    global client
    client.place_order(OrderType=OrderType,
                       Exchange=Exchange,
                       ExchangeType=ExchangeType,
                       ScripCode = ScripCode,
                       Qty=Qty,
                       Price=Price)

def cover( ScripCode , Qty, Price,OrderType='B',Exchange='N',ExchangeType='C'):
    global client
    client.place_order(OrderType=OrderType,
                       Exchange=Exchange,
                       ExchangeType=ExchangeType,
                       ScripCode = ScripCode,
                       Qty=Qty,
                       Price=Price)

def get_position():
    global client
    responce = client.positions()

    return responce

def get_margin():
    global client
    responce= client.margin()
    if responce:
        net_available_margin =float (responce[0]['NetAvailableMargin'])
        return net_available_margin
    else:
        print("Error: Unable to get NetAvailableMargin")
        return None





















