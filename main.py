import FivePaisaIntegration
import time as sleep_time
import pandas as pd
from datetime import datetime
import threading
lock = threading.Lock()

FivePaisaIntegration.login()


def write_to_order_logs(message):
    with open('OrderLog.txt', 'a') as file:  # Open the file in append mode
        file.write(message + '\n')

def calculate_percentage_values(value, percentage):
    final = (float(percentage) / 100) * float(value)
    return final


def delete_file_contents(file_name):
    try:
        # Open the file in write mode, which truncates it (deletes contents)
        with open(file_name, 'w') as file:
            file.truncate(0)
        print(f"Contents of {file_name} have been deleted.")
    except FileNotFoundError:
        print(f"File {file_name} not found.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

def get_zerodha_credentials():
    delete_file_contents("OrderLog.txt")
    credentials = {}
    try:
        df = pd.read_csv('TradeSetting.csv')
        for index, row in df.iterrows():
            title = row['Title']
            value = row['Value']
            credentials[title] = value
    except pd.errors.EmptyDataError:
        print("The CSV file is empty or has no data.")
    except FileNotFoundError:
        print("The CSV file was not found.")
    except Exception as e:
        print("An error occurred while reading the CSV file:", str(e))

    return credentials

credentials_dict = get_zerodha_credentials()
BuyBufferPercentage = float(credentials_dict.get('BuyBufferPercentage'))
SellBufferPercentage = float(credentials_dict.get('SellBufferPercentage'))
StoplossPercentage = float(credentials_dict.get('StoplossPercentage'))
Target1Percentage =float( credentials_dict.get('Target1Percentage'))
Target2Percentage =float( credentials_dict.get('Target2Percentage'))
Target3Percentage =float( credentials_dict.get('Target3Percentage'))
TSLPercentage =float( credentials_dict.get('TSLPercentage'))
TotalAmountQty=float( credentials_dict.get('TotalAmountQty'))
Lot1_percentage=float( credentials_dict.get('Lot1_percentage'))
Lot2_percentage=float( credentials_dict.get('Lot2_percentage'))
Lot3_percentage=float( credentials_dict.get('Lot3_percentage'))
Leverage_multiplier=float( credentials_dict.get('Leverage_multiplier'))
StartTime=credentials_dict.get('StartTime')
Stoptime=credentials_dict.get('Stoptime')
symbol_dict={}
priority_dict={}
formatted_symbols=None

def my_trade_universe():
    global BuyBufferPercentage ,SellBufferPercentage , Leverage_multiplier, Lot3_percentage,Lot2_percentage, Lot1_percentage,TotalAmountQty, symbol_dict, formatted_symbols,StoplossPercentage,Target1Percentage,Target2Percentage,Target3Percentage,TSLPercentage
    try:
        df = pd.read_csv('MYINSTRUMENTS.csv')
        pf = pd.read_csv('ScripMaster.csv')
        cashdf=pf[(pf['Exch']=="N")&(pf['ExchType']=="C")&(pf['Series']=="EQ")]
        cashdf['Name']=cashdf['Name'].str.strip()
        cashdf = cashdf[['ScripCode', 'Name']]
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        for symbol in df['Symbol']:
            try:
                matching_row = cashdf[cashdf['Name'].str.strip() == symbol.strip()]
                if not matching_row.empty:
                    # Get the 'ScripCode' value
                    spcode = matching_row.iloc[0]['ScripCode']

                else:
                    print(f"No matching row found for symbol {symbol}")

                previousclose=FivePaisaIntegration.previousdayclose(code=str(spcode))

                buyval=calculate_percentage_values(previousclose,BuyBufferPercentage)
                buyval=previousclose+buyval

                sellval=calculate_percentage_values(previousclose,SellBufferPercentage)
                sellval=previousclose-sellval

                symbol_dict[symbol] = {
                    "scriptcode": spcode,
                    "previousclose": previousclose,
                    "buyval": buyval,
                    "sellval": sellval,
                    "stoplossval": 0,
                    "tp1": 0,
                    "tp2": 0,
                    "tp3": 0,
                    "tp1qty": 0,
                    "tp2qty": 0,
                    "tp3qty": 0,
                    "slqty": 0,
                    "totalqty":0,
                    "stoplos_bool": False,
                    "tp1_bool": False,
                    "tp2_bool": False,
                    "tp3_bool": False,
                    "tradetype": None,
                    "tslstep":0,
                    "tslmove":0,
                    "tslval":0,
                    "slpts":0,
                }
                formatted_symbols = [f'NSE: {symbol}' for symbol in symbol_dict.keys()]
            except Exception as e:
                print(f"An error occurred for symbol {symbol}: {str(e)}")

        # print(symbol_dict)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        print(symbol_dict)
    except Exception as e:
        print("An error occurred while reading the MYINSTRUMENTS.CSV file:", str(e))


def check_orders(symbol_dict):
    global Leverage_multiplier, Lot3_percentage, Lot2_percentage, Lot1_percentage, TotalAmountQty, formatted_symbols, TradeBufferPercentage, StoplossPercentage, Target1Percentage, Target2Percentage, Target3Percentage, TSLPercentage

    for symbol, data in symbol_dict.items():
        try:
            StartTime = credentials_dict.get('StartTime')
            Stoptime = credentials_dict.get('Stoptime')
            StartTime = datetime.strptime(StartTime, '%H:%M').time()
            Stoptime = datetime.strptime(Stoptime, '%H:%M').time()

            now = datetime.now().time()
            timestamp = datetime.now()
            timestamp = timestamp.strftime("%d/%m/%Y %H:%M:%S")
            ltp = float(FivePaisaIntegration.get_ltp(code=str(data['scriptcode'])))

            print(f"symbol: {symbol},ltp:{ltp}")
            print(f"symbol: {symbol},data['buyval']:{data['buyval']}")
            if data['tradetype'] is None and float(data['buyval'] ) > 0 and float(ltp) > float(data['buyval']) and now>=StartTime and now < Stoptime:
                ltp = ltp
                data['tradetype']="BUY"
                data["stoplos_bool"]=True
                data["tp1_bool"]=True
                data["tp2_bool"]=True
                data["tp3_bool"]=True
                brokermargin = FivePaisaIntegration.get_margin()
                print("present broker margin : ",brokermargin)


                amounttotrade= calculate_percentage_values(brokermargin,TotalAmountQty)
                print("amounttotrade: ",amounttotrade)
                print("ltp", ltp)
                totalqty= int(amounttotrade/ltp)


                print("totalqty1: ",totalqty)

                totalqty= totalqty * Leverage_multiplier
                print("totalqty2: ", totalqty)



                data["slqty"]=totalqty
                data["totalqty"]= totalqty
                tp1qty=calculate_percentage_values(totalqty,Lot1_percentage)
                tp1qty=int(tp1qty)
                data["tp1qty"] = tp1qty

                tp2qty = calculate_percentage_values(totalqty, Lot2_percentage)
                tp2qty = int(tp2qty)
                data["tp2qty"] = tp2qty

                tp3qty= totalqty-tp1qty
                tp3qty=tp3qty-tp2qty
                tp3qty=int(tp2qty)
                data["tp3qty"] = tp3qty

                tp1 =calculate_percentage_values(ltp,Target1Percentage)
                tp1 = ltp + tp1
                data['tp1']= tp1

                tp2 =calculate_percentage_values(ltp,Target2Percentage)
                tp2 = ltp + tp2
                data['tp2']= tp2

                tp3 = calculate_percentage_values(ltp, Target3Percentage)
                tp3 =ltp + tp3
                data['tp3'] = tp3

                stoplossval=calculate_percentage_values(ltp, StoplossPercentage)
                data["slpts"] =  stoplossval
                stoplossval = ltp - stoplossval
                data['stoplossval'] = stoplossval

                data["tslval"] = calculate_percentage_values(ltp, TSLPercentage)

                data["tslstep"] = ltp + data["tslval"]

                orderlog = f"{timestamp} Buy order executed for {symbol} for lotsize= {totalqty}  @ {ltp} ,Target1 ={tp1},Target2 ={tp2},Target3 ={tp3}, TslStep= {data['tslstep']}  And Stoploss ={stoplossval}"
                print(orderlog)
                write_to_order_logs(orderlog)
                FivePaisaIntegration.buy(ScripCode=str(data['scriptcode']) , Qty=int(totalqty), Price=float(FivePaisaIntegration.get_ltp(code=str(data['scriptcode']))))


            if data['tradetype'] is None and float(data['sellval']) > 0 and float(ltp) < float(data['sellval']) and now>=StartTime and now < Stoptime:
                data['tradetype'] = "SHORT"
                data["stoplos_bool"] = True
                data["tp1_bool"] = True
                data["tp2_bool"] = True
                data["tp3_bool"] = True
                brokermargin = FivePaisaIntegration.get_margin()
                print("present broker margin : ", brokermargin)
                amounttotrade = calculate_percentage_values(brokermargin, TotalAmountQty)
                totalqty = int(amounttotrade / ltp)
                totalqty = totalqty * Leverage_multiplier
                data["slqty"] = totalqty
                data["totalqty"] = totalqty

                tp1qty = calculate_percentage_values(totalqty, Lot1_percentage)
                tp1qty = int(tp1qty)
                data["tp1qty"] = tp1qty

                tp2qty = calculate_percentage_values(totalqty, Lot2_percentage)
                tp2qty = int(tp2qty)
                data["tp2qty"] = tp2qty

                tp3qty = totalqty - tp1qty
                tp3qty = tp3qty - tp2qty
                tp3qty = int(tp2qty)
                data["tp3qty"] = tp3qty


                tp1 = calculate_percentage_values(ltp, Target1Percentage)
                tp1 = ltp - tp1
                data['tp1'] = tp1

                tp2 = calculate_percentage_values(ltp, Target2Percentage)
                tp2 = ltp - tp2
                data['tp2'] = tp2

                tp3 = calculate_percentage_values(ltp, Target3Percentage)
                tp3 = ltp - tp3
                data['tp3'] = tp3

                stoplossval = calculate_percentage_values(ltp, StoplossPercentage)
                data["slpts"] = stoplossval
                stoplossval = ltp + stoplossval
                data['stoplossval'] = stoplossval

                data["tslval"] = calculate_percentage_values(ltp, TSLPercentage)
                data["tslstep"] = ltp - data["tslval"]


                FivePaisaIntegration.short(ScripCode=str(data['scriptcode']) , Qty=int(totalqty), Price=float(FivePaisaIntegration.get_ltp(code=str(data['scriptcode']))))
                orderlog = f"{timestamp} sell order executed for {symbol} for lotsize= {totalqty} @ {ltp} ,Target1 ={tp1},Target2 ={tp2},Target3 ={tp3}, TslStep= {data['tslstep']} And Stoploss ={stoplossval} "
                print(orderlog)
                write_to_order_logs(orderlog)

                net_positions = FivePaisaIntegration.get_position()
                if any(pos['ScripName'] == symbol for pos in net_positions):
                    # Find the position for the symbol
                    position = next((pos for pos in net_positions if pos['ScripName'] == symbol), None)
                    if position and 'NetQty' in position:
                        quantity = position['NetQty']
                        print(f"Net Quantity for {symbol}: {quantity}")

                        # Now you can use 'quantity' as needed in your logic

                    if quantity > 0 and data['tradetype'] == "BUY" and float(ltp) >= float(data["tslstep"]):
                        data["tslstep"] = ltp + data["tslval"]
                        data['stoplossval'] = ltp - data["slpts"]
                        orderlog = f"{timestamp} Tsl executed {symbol} for lotsize=  @ {ltp} new  Stoploss ={data['stoplossval']}"
                        print(orderlog)
                        write_to_order_logs(orderlog)

                    if quantity > 0 and data['tradetype'] == "SHORT" and float(ltp) <= float(data["tslstep"]):
                        data["tslstep"] = ltp - data["tslval"]
                        data['stoplossval'] = ltp + data["slpts"]
                        orderlog = f"{timestamp} Tsl executed {symbol} for lotsize=  @ {ltp} new  Stoploss ={data['stoplossval']}"
                        print(orderlog)
                        write_to_order_logs(orderlog)

                    if quantity > 0 and data['tradetype'] == "BUY" and float(ltp) >= float(data['tp1']) and float(
                            data['tp1']) > 0 and data["tp1_bool"] == True:
                        data["tp1_bool"] = False
                        data["slqty"] = int(data["slqty"]) - int(data["tp1qty"])

                        FivePaisaIntegration.sell(ScripCode=str(data['scriptcode']) , Qty= int(data["tp1qty"]),Price=float(FivePaisaIntegration.get_ltp(code=str(data['scriptcode']))))
                        orderlog = f"{timestamp} Buy Target 1 executed {symbol} @ {data['tp1']}"
                        data['tp1'] = 0
                        write_to_order_logs(orderlog)

                    if quantity < 0 and data['tradetype'] == "SHORT" and float(ltp) <= float(data['tp1']) and float(
                            data['tp1']) > 0 and data["tp1_bool"] == True:
                        data["tp1_bool"] = False
                        data["slqty"] = int(data["slqty"]) - int(data["tp1qty"])
                        FivePaisaIntegration.cover(ScripCode=str(data['scriptcode']) ,Qty= int(data["tp1qty"]), Price=float(FivePaisaIntegration.get_ltp(code=str(data['scriptcode']))))
                        orderlog = f"{timestamp} Sell Target 1 executed {symbol} @ {data['tp1']}"
                        data['tp1'] = 0
                        write_to_order_logs(orderlog)

                    if quantity > 0 and data['tradetype'] == "BUY" and float(ltp) >= float(data['tp2']) and float(
                            data['tp2']) > 0 and data["tp2_bool"] == True:
                        data["tp2_bool"] = False
                        data["slqty"] = int(data["slqty"]) - int(data["tp2qty"])
                        FivePaisaIntegration.sell(ScripCode=str(data['scriptcode']), Qty= int(data["tp2qty"]), Price=float(FivePaisaIntegration.get_ltp(code=str(data['scriptcode']))))
                        orderlog = f"{timestamp} Buy Target 2 executed {symbol} @ {data['tp2']}"
                        data['tp2'] = 0
                        write_to_order_logs(orderlog)

                    if quantity < 0 and data['tradetype'] == "SHORT" and float(ltp) <= float(data['tp2']) and float(
                            data['tp2']) > 0 and data["tp2_bool"] == True:
                        data["tp2_bool"] = False
                        data["slqty"] = int(data["slqty"]) - int(data["tp2qty"])
                        FivePaisaIntegration.cover(ScripCode=str(data['scriptcode']), Qty=int(data["tp2qty"]), Price=float(FivePaisaIntegration.get_ltp(code=str(data['scriptcode']))))
                        orderlog = f"{timestamp} Sell Target 2 executed {symbol} @ {data['tp2']}"
                        data['tp2'] = 0
                        write_to_order_logs(orderlog)

                    if quantity > 0 and data['tradetype'] == "BUY" and float(ltp) >= float(data['tp3']) and float(
                            data['tp3']) > 0 and data["tp3_bool"] == True:
                        data["tp3_bool"] = False
                        data["slqty"] = 0
                        FivePaisaIntegration.sell(ScripCode=str(data['scriptcode']),Qty= int(data["tp3qty"]), Price=float(FivePaisaIntegration.get_ltp(code=str(data['scriptcode']))))
                        orderlog = f"{timestamp} Buy Target 3 executed {symbol} @ {data['tp3']}"
                        data['tp3'] = 0
                        write_to_order_logs(orderlog)
                        data['tradetype'] = "TradeDone"

                    if quantity < 0 and data['tradetype'] == "SHORT" and float(ltp) <= float(data['tp3']) and float(
                            data['tp3']) > 0 and data["tp3_bool"] == True:
                        data["tp3_bool"] = False
                        data["slqty"] = 0
                        FivePaisaIntegration.cover(ScripCode=str(data['scriptcode']),Qty= int(data["tp3qty"]), Price=float(FivePaisaIntegration.get_ltp(code=str(data['scriptcode']))))
                        orderlog = f"{timestamp} Short Target 3 executed {symbol} @ {data['tp3']}"
                        data['tp3'] = 0
                        write_to_order_logs(orderlog)
                        data['tradetype'] = "TradeDone"

                    if quantity > 0 and data['tradetype'] == "BUY" and float(ltp) <= float(
                            data['stoplossval']) and float(data['stoplossval']) > 0 and data["stoplos_bool"] == True:
                        data["stoplos_bool"] = False
                        FivePaisaIntegration.sell(ScripCode=str(data['scriptcode']),Qty= int(data["slqty"]), Price=float(FivePaisaIntegration.get_ltp(code=str(data['scriptcode']))))
                        orderlog = f"{timestamp} Buy Stoploss executed {symbol} @ {ltp} , qty traded: {data['slqty']}"
                        data['tp3'] = 0
                        write_to_order_logs(orderlog)
                        data['tradetype'] = "TradeDone"

                    if quantity < 0 and data['tradetype'] == "SHORT" and float(ltp) >= float(
                            data['stoplossval']) and float(data['stoplossval']) > 0 and data["stoplos_bool"] == True:
                        data["stoplos_bool"] = False
                        FivePaisaIntegration.cover(ScripCode=str(data['scriptcode']), Qty=int(data["slqty"]), Price=float(FivePaisaIntegration.get_ltp(code=str(data['scriptcode']))))
                        orderlog = f"{timestamp} Short Stoploss executed {symbol} @ {ltp}, qty traded: {data['slqty']}"
                        data['tp3'] = 0
                        write_to_order_logs(orderlog)
                        data['tradetype'] = "TradeDone"

        except Exception as e:
            print(f"error happened in order placement  {symbol}: {str(e)}")



# FivePaisaIntegration.get_margin()
# FivePaisaIntegration.get_ltp(code=2023678)
# FivePaisaIntegration.buy(ScripCode="1660" , Qty=int(1), Price=float(FivePaisaIntegration.get_ltp(code="1660")))



def mainstrategy():
    global Leverage_multiplier
    strattime = credentials_dict.get('StartTime')
    stoptime = credentials_dict.get('Stoptime')
    start_time = datetime.strptime(strattime, '%H:%M').time()
    stop_time = datetime.strptime(stoptime, '%H:%M').time()
    while True:
        now = datetime.now().time()
        if now >= start_time :
            check_orders(symbol_dict)
            sleep_time.sleep(1)


my_trade_universe()
mainstrategy()