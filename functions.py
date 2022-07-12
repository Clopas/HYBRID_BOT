import json
from json import JSONDecodeError

import requests
import hmac
import hashlib
import time
from requests import Request, session
from credentials import *


# credentials
account_id_3commas = '' #a
api_key_3commas = '' #b
api_secret_3commas = '' #c
api_key_ftx = '' #d
api_secret_ftx = '' #e


def request_ftx(request_type, ftx_endpoint='', request_json=None):
    if request_json is None:
        request_json = {}
    ts = int(time.time() * 1000)
    position_request = Request(request_type, f"https://ftx.com/api{ftx_endpoint}", json=request_json)
    prepared = position_request.prepare()
    signature_payload = f'{ts}{prepared.method}{prepared.path_url}'.encode()
    if prepared.body:
        signature_payload += prepared.body
    signature_request_ftx = hmac.new(api_secret_ftx.encode(), signature_payload, 'sha256').hexdigest()
    prepared.headers['FTX-KEY'] = api_key_ftx
    prepared.headers['FTX-SIGN'] = signature_request_ftx
    prepared.headers['FTX-TS'] = str(ts)
    response = session().send(prepared)
    try:
        loaded_response = json.loads(response.content)
    except JSONDecodeError as e:
        print("Forgot VPN? ;)")
        raise (e)

    # print(f"response is {loaded_response}")
    return loaded_response


# print("log: start")
# ##################### Get price from FTX #################################
pair_ftx = "EOS-PERP"


def price():
    loaded_response_markets = request_ftx('GET', '/markets')
    for i in loaded_response_markets["result"]:
        if i['name'] == pair_ftx:
            pp = i['price']
            return pp
            # break


price_pair = price()
# print(f"{pair_ftx} price is {price_pair}")

# ##################### Get position details from FTX ######################
balance = 500
leverage = 5


def position():
    ftx_position_endpoint = '/positions?showAvgPrice=True'
    position_response = request_ftx('GET', ftx_position_endpoint)
    # print(position_response)
    try:
        for i in position_response['result']:
            if i["future"] == pair_ftx:
                if i["size"] == 0.0:
                    # print(i['size'])
                    print('You do not have an open', pair_ftx, 'position!')
                    return None
                else:
                    profit = (i['recentPnl'] / balance) * 100
                    avg = i['recentBreakEvenPrice']
                    size = i['size']
                    quote = i['cost']
                    pnl = i['recentPnl']
                    side = i['side']
                    print(
                        f"Your profit: {round(profit, 3)}%, position size: {size} {pair_ftx} ~ {round(quote, 2)}$, unrealized P&L: {round(pnl, 2)}$, break even price: {avg}.")
                    return [profit, avg, size, quote, pnl, side]
    except KeyError:
        raise KeyError("API Credentials must be missing.")
        # break


# ###################### 3commas endpoints ###########################
create_dca_url = '/ver1/bots/create_bot'  # POST
disable_dca_url = '/ver1/bots/{bot_id}/disable'  # POST
enable_dca_url = '/ver1/bots/{bot_id}/enable'  # POST
delete_dca_url = '/ver1/bots/{bot_id}/delete'  # POST
edit_dca_url = '/ver1/bots/{bot_id}/update'  # PATCH
asap_dca_url = '/ver1/bots/{bot_id}/start_new_deal'  # POST
dca_list_url = '/ver1/bots'  # GET
panic_sell_dca_url = '/ver1/bots/{bot_id}/panic_sell_all_deals'  # POST
dca_deals_stats_url = '/ver1/bots/{bot_id}/deals_stats'  # GET
dca_info_url = '/ver1/bots/{bot_id}/show'  # GET
cancel_dca_deals_url = '/ver1/bots/{bot_id}/cancel_all_deals'  # POST

create_grid_url = '/ver1/grid_bots/manual'  # POST
disable_grid_url = '/ver1/grid_bots/{id}/disable'  # POST
enable_grid_url = '/ver1/grid_bots/{id}/enable'  # POST
edit_grid_url = '/ver1/grid_bots/{id}/manual'  # PATCH
delete_grid_url = '/ver1/grid_bots/{id}'  # DELETE
id_grid_url = '/ver1/grid_bots'  # GET

create_smart_trade_url = '/v2/smart_trades'  # POST
close_smart_trade_url = '/v2/smart_trades/{id}/close_by_market'  # POST
enable_smart_trade_url = ''  # POST
# edit_smart_trade_url=''
delete_smart_trade_url = '/v2/smart_trades/{id}'  # DELETE
id_smart_trade_url = '/v2/smart_trades'  # GET


# ##################### 3commas requests function #############################

def request_3commas(request_type, endpoint_url, data_url=''):
    base_url = 'https://api.3commas.io/public/api'
    key_url = f'?api_key={api_key_3commas}&secret={api_secret_3commas}'

    signature_request_3commas = hmac.new(
        bytes(api_secret_3commas, 'latin-1'),
        msg=bytes('/public/api' + endpoint_url + key_url + (('&' + data_url) if data_url != '' else ''), 'latin-1'),
        digestmod=hashlib.sha256).hexdigest().upper()

    url_request_3commas = base_url + endpoint_url + key_url + (('&' + data_url) if data_url != '' else '')
    headers_request_3commas = {'APIKEY': f'{api_key_3commas}', 'Signature': signature_request_3commas}
    # print(url_request_3commas)  #test
    if request_type == 'GET':
        send_request_3commas = requests.get(url_request_3commas, headers=headers_request_3commas)
    elif request_type == 'POST':
        send_request_3commas = requests.post(url_request_3commas, headers=headers_request_3commas)
    elif request_type == 'DELETE':
        send_request_3commas = requests.delete(url_request_3commas, headers=headers_request_3commas)
    elif request_type == 'PATCH':
        send_request_3commas = requests.patch(url_request_3commas, headers=headers_request_3commas)
    else:
        raise TypeError("Request types should be one of the 'GET', 'POST', 'DELETE', 'PATCH' options! bro...")
    return json.loads(send_request_3commas.content)


# print(request_3commas('GET', id_grid_url))  # test
# print("log: 3commas function")
# ##################### Get DCA info ##############################

def dca_id():
    dca_list_dca_id = request_3commas('GET', dca_list_url)
    # print(dca_list_dca_id)
    for i in dca_list_dca_id:
        try:
            if i['pairs'][0] == pair_3commas:
                return i['id']
        except TypeError:
            raise TypeError('API Credentials must be missing.')

    print(f'Cannot get the DCA id. Sounds like there is no {pair_ftx} DCA.')
    return None


def dca_info():
    request_dca_info = request_3commas('GET', dca_info_url.format(bot_id=dca_id()))
    # print('DCA info:')
    # print(request_dca_info)
    entry_price = float(request_dca_info['active_deals'][0]['base_order_average_price'])
    safety_orders = float(request_dca_info['max_safety_orders'])
    step_percentage = float(request_dca_info['safety_order_step_percentage'])
    dca_low = entry_price * (1 - (safety_orders * (step_percentage / 100)))
    return [dca_low, entry_price, safety_orders, step_percentage]


# ##################### 3commas bot inputs for 50% D.D #######################

pair_3commas = f"USD_{pair_ftx}"

# ##################### 3commas bot inputs for 40% D.D ########################

# BOH = entry_price + (entry_price * (0.04))
# BOL = entry_price + (entry_price * (-0.05))

# SO1H = entry_price + (entry_price * (-0.05))
# SO1L = entry_price + (entry_price * (-0.12))

# SO2H = entry_price + (entry_price * (-0.12))
# SO2L = entry_price + (entry_price * (-0.19))

# SO3H = entry_price + (entry_price * (-0.19))
# SO3L = entry_price + (entry_price * (-0.26))

# SO4H = entry_price + (entry_price * (-0.26))
# SO4L = entry_price + (entry_price * (-0.33))

# SO5H = entry_price + (entry_price * (-0.33))
# SO5L = entry_price + (entry_price * (-0.4))

# ##################### Settings for 50% D.D ########################

# balance=500
# BO=37
SCALE50 = 1.481
# v_{0}=24.54
SO1V50 = 36.34
# r=0.236
# d_{m}=0.405
# ##################### Settings for 40% D.D ########################

# balance=500
# BOV=37
SCALE40 = 1.584
# v_{0}=19
SO1V40 = 30.1


# r=0.236
# d_{m}=0.32364


# ##################### Grids quantities #############################

def grids_quantity(grid_volume):
    a = [13, 14, 15, 16, 17, 18, 19, 20]
    for i in a[:]:
        if abs((grid_volume / i) - round(grid_volume / i, 1)) <= 0.1:
            return [round(grid_volume / i, 1), i]
    else:
        raise ValueError("Damn it!!! I Couldn't find a good grid quantity!")


# ###################### #Print % of steps in every grid ###################

# print('\n% of steps in every grid:')
# print(round(((BOH - BOL) / (BOH * (BO_qty[1]))) * 100, 3))
# print(round(((SO1H - SO1L) / (SO1H * (SO1_qty[1]))) * 100, 3))
# print(round(((SO2H - SO2L) / (SO2H * (SO2_qty[1]))) * 100, 3))
# print(round(((SO3H - SO3L) / (SO3H * (SO3_qty[1]))) * 100, 3))
# print(round(((SO4H - SO4L) / (SO4H * (SO4_qty[1]))) * 100, 3))
# print(round(((SO5H - SO5L) / (SO5H * (SO5_qty[1]))) * 100, 3))
# print("log: Printed inputs")


# ##################### Bot lists ##########################################
grid_list = request_3commas('GET', id_grid_url, '&limit=1000')
enabled_grid_list_new = []


# smart_trade_list = request_3commas('GET', id_smart_trade_url, '&status=active')


# ##################### Clean up useless grid bots ##############################
def cleanup():
    grid_list_cleanup = request_3commas('GET', id_grid_url, '&limit=1000')
    # print(grid_list_cleanup)
    for i in grid_list_cleanup:
        if (i['is_enabled'] == False) and i['total_profits_count'] == '0':
            request_3commas('DELETE', delete_grid_url.format(id=i['id']))
            print('\n' + str(i['id']) + ' ' + str(i['pair']) + ' is deleted.')
    print('Clean up is completed!')


# print("log: cleanup() function")


# #################### close all bots ########################################
def close_ftx():
    try:
        position_close_ftx = position()

        # print(position_close_ftx[2])

        side_close_ftx = 'buy' if position_close_ftx[5] == 'sell' else 'sell'
        json_close_ftx = {
            "market": pair_ftx,
            "side": side_close_ftx,
            "price": None,
            "type": "market",
            "size": position_close_ftx[2],
            "reduceOnly": True,
            "ioc": True,
        }
        a = request_ftx('POST', '/orders', json_close_ftx)
        print('\nClose FTX position request sent.\nResponse:')
        print(a)
    except TypeError as e:
        print(e)
        pass
    except AttributeError:
        print('Probably there is no open ftx position to close.')
        pass


def close_all():
    print("Close all started...\n")
    grid_list_stop = request_3commas('GET', id_grid_url, '&limit=1000')
    for i in grid_list_stop:
        if i['is_enabled'] == True and i['pair'] == pair_3commas:
            disable_grid_stop = request_3commas('POST', disable_grid_url.format(id=i['id']))
            print(f"\nGrid {i['id']} is disabled.\n" + str(disable_grid_stop))

    dca_id_close_all = dca_id()
    # print('bot id:' + str(dca_id_close_all))
    print('Disable DCA request sent.\nResponse:')
    print(request_3commas('POST', disable_dca_url.format(bot_id=dca_id_close_all)))
    # Note: panic sell + close_ftx() causes opening position in the opposite direction.
    # panic_sell_close_all = request_3commas('POST', panic_sell_dca_url.format(bot_id=dca_id_close_all))
    # print('\nPanic sell DCA deal request sent.\nResponse:\n' + str(panic_sell_close_all))
    print('\nCancel DCA deal request sent.\nResponse:')
    print(request_3commas('POST', cancel_dca_deals_url.format(bot_id=dca_id_close_all)))
    close_ftx()
    cleanup()
    #    except KeyError as e:
    #        print('error:' + str(e))
    #        # Note: even when there is no deals, it doesn't return error.
    #        print(
    #            'Exception occured. Closing the position from ftx. Likely there is no active DCA deal...\n closing position...')
    #        close_ftx()
    #        cleanup()

    print("Close all is done.")


# print("log: close_all() function")
# ################### start the bots ############################################


def start():
    # ############ DCA bot ##############

    # dca_json = "{\"strategy_list\": [{\"strategy\": \"nonstop\"}]}"
    # dca_data_url = f"&account_id={account_id_3commas}&pair={pair_3commas}&base_order_volume=50&take_profit='2.5'&safety_order_volume=4.32&martingale_volume_coefficient=1&martingale_step_coefficient=1&max_safety_orders=20&active_safety_orders_count=20&safety_order_step_percentage=0.675&take_profit_type=total&leverage_type=cross" + "&strategy_list=[{'strategy:nonstop'}]"

    # close_all()
    enabled_grid_list_new.clear()
    dca_id_start_2 = dca_id()
    if dca_id_start_2 is None:
        raise Exception("You Don't have a DCA bot. Create one first!")
        # dca_create = request_3commas('POST', create_dca_url, dca_data_url, dca_json)
        # enabled_grid_list_new.append('dca:' + dca_create['id'])
        # print('\nDCA created:\n' + str(dca_create))
        # time.sleep(0.1)

    dca_enable = request_3commas('POST', enable_dca_url.format(bot_id=dca_id()))
    print('\nDCA enabled.\nResponse:\n' + str(dca_enable))
    enabled_grid_list_new.append('dca:' + str(dca_enable['id']))
    time.sleep(0.1)

    # ########### Grid bots ############

    entry_price = dca_info()[1]

    # todo: BO and SO1 volumes are redundant but are still needed to calculate the balance. Should find a better way to calculate the balance.
    BOH = entry_price + (entry_price * 0.04)
    BOL = entry_price + (entry_price * (-0.05))

    SO1H = entry_price + (entry_price * (-0.05))
    SO1L = entry_price + (entry_price * (-0.14))

    SO2H = entry_price + (entry_price * (-0.14))
    SO2L = entry_price + (entry_price * (-0.23))

    SO3H = entry_price + (entry_price * (-0.23))
    SO3L = entry_price + (entry_price * (-0.32))

    SO4H = entry_price + (entry_price * (-0.32))
    SO4L = entry_price + (entry_price * (-0.41))

    SO5H = entry_price + (entry_price * (-0.41))
    SO5L = entry_price + (entry_price * (-0.5))

    BO_qty = grids_quantity(BO)
    # print(BO_qty)
    SO1_qty = grids_quantity(SO1)
    # print(SO1_qty)
    SO2_qty = grids_quantity(SO2)
    # print(SO2_qty)
    SO3_qty = grids_quantity(SO3)
    # print(SO3_qty)
    SO4_qty = grids_quantity(SO4)
    # print(SO4_qty)
    SO5_qty = grids_quantity(SO5)
    # print(SO5_qty)

    BO = (37 / price_pair)
    BOO = 37
    # print('\nBase currency volumes:\n' + str(round(BO)) + ' ' + pair_ftx)
    SO1 = (SO1V50 / (0.5 * (SO1H + SO1L)))
    SO1O = SO1V50
    # print(str(round(SO1, 2)) + ' ' + pair_ftx)
    SO2 = (SO1V50 * SCALE50) / (0.5 * (SO2H + SO2L))
    SO2O = SO1V50 * SCALE50
    # print(str(round(SO2, 2)) + ' ' + pair_ftx)
    SO3 = (SO1V50 * SCALE50 ** 2) / (0.5 * (SO3H + SO3L))
    SO3O = SO1V50 * SCALE50 ** 2
    # print(str(round(SO3, 2)) + ' ' + pair_ftx)
    SO4 = (SO1V50 * SCALE50 ** 3) / (0.5 * (SO4H + SO4L))
    SO4O = SO1V50 * SCALE50 ** 3
    # print(str(round(SO4, 2)) + ' ' + pair_ftx)
    SO5 = (SO1V50 * SCALE50 ** 4) / (0.5 * (SO5H + SO5L))
    SO5O = SO1V50 * SCALE50 ** 4
    # print(str(round(SO5, 2)) + ' ' + pair_ftx)

    # print(f"Total base currency size: {round((BO + SO1 + SO2 + SO3 + SO4 + SO5), 2)}")
    # print('BOO+SO1O+SO2O+SO3O+SO4O+SO5O)/price:' + str(round((BOO + SO1O + SO2O + SO3O + SO4O + SO5O) / price_pair, 2)))
    # ##################### #Print $$$ volume (quote currency volume) ####################
    # print('\nQuote currency volumes:\n' + str(BOO) + "$")
    # print(str(round(SO1O, 2)) + "$")
    # print(str(round(SO2O, 2)) + "$")
    # print(str(round(SO3O, 2)) + "$")
    # print(str(round(SO4O, 2)) + "$")
    # print(str(round(SO5O, 2)) + "$")

    balance = BOO + SO1O + SO2O + SO3O + SO4O + SO5O

    # print('Total balance: ' + str(round(balance, 2)) + '$\n')

    SO2_data_url = f"&account_id={account_id_3commas}&pair={pair_3commas}&upper_price={SO2H}&lower_price={SO2L}&quantity_per_grid={SO2_qty[0]}&grids_quantity={SO2_qty[1]}&leverage_type=cross&leverage_custom_value={leverage}&is_enabled=true"
    SO3_data_url = f"&account_id={account_id_3commas}&pair={pair_3commas}&upper_price={SO3H}&lower_price={SO3L}&quantity_per_grid={SO3_qty[0]}&grids_quantity={SO3_qty[1]}&leverage_type=cross&leverage_custom_value={leverage}&is_enabled=true"
    SO4_data_url = f"&account_id={account_id_3commas}&pair={pair_3commas}&upper_price={SO4H}&lower_price={SO4L}&quantity_per_grid={SO4_qty[0]}&grids_quantity={SO4_qty[1]}&leverage_type=cross&leverage_custom_value={leverage}&is_enabled=true"
    SO5_data_url = f"&account_id={account_id_3commas}&pair={pair_3commas}&upper_price={SO5H}&lower_price={SO5L}&quantity_per_grid={SO5_qty[0]}&grids_quantity={SO5_qty[1]}&leverage_type=cross&leverage_custom_value={leverage}&is_enabled=true"

    so2_create = request_3commas('POST', create_grid_url, SO2_data_url)
    print(so2_create)
    enabled_grid_list_new.append([so2_create['id'], so2_create['lower_price'], so2_create['upper_price']])
    print('\nso2_create:\n' + str(so2_create))
    time.sleep(0.1)

    so3_create = request_3commas('POST', create_grid_url, SO3_data_url)
    enabled_grid_list_new.append([so3_create['id'], so3_create['lower_price'], so3_create['upper_price']])
    print('\nso3_create:\n' + str(so3_create))
    time.sleep(0.1)

    so4_create = request_3commas('POST', create_grid_url, SO4_data_url)
    enabled_grid_list_new.append([so4_create['id'], so4_create['lower_price'], so4_create['upper_price']])
    print('\nso4_create:\n' + str(so4_create))
    time.sleep(0.1)

    so5_create = request_3commas('POST', create_grid_url, SO5_data_url)
    enabled_grid_list_new.append([so5_create['id'], so5_create['lower_price'], so5_create['upper_price']])
    print('\nso5_create:\n' + str(so5_create))

    print('\nNew bots are created.\n')


# print("log: start() function")


# #################### Take profit and enter as soon as possible ########################################
def tp(profit_tp):
    while position() is None:
        print("Waiting for an open position.")
        time.sleep(10)

    while price() >= dca_info()[0]:
        print("Price hasn't entered the grids yet.")
        time.sleep(10)

    print("Price entered the grids...\nDisable DCA request sent.\nResponse:")
    print(request_3commas('POST', disable_dca_url.format(bot_id=dca_id())))
    time.sleep(0.1)

    while position()[0] < profit_tp:
        price_tp = price()
        if len(enabled_grid_list_new) == 5:
            for i in enabled_grid_list_new[1:]:
                if price_tp <= float(i[1]):
                    request_3commas('POST', disable_grid_url.format(id=i[0]))
                    print(f"The higher grid {i} is disabled.")
            time.sleep(10)
            continue
        else:
            grid_list_tp = request_3commas('GET', id_grid_url, '&limit=1000')
            for i in grid_list_tp:
                if i['is_enabled'] == True and i['pair'] == pair_3commas:
                    disable_grid_tp = request_3commas('POST', disable_grid_url.format(id=i['id']))
                    print(f"\nGrid {i['id']} is disabled.\n" + str(disable_grid_tp))
            start()
            tp(profit_tp)
            # raise ValueError("There isn't 5 bots in the list! tp() cannot continue.")
    print("\nTake profit is executing. With specs as [profit, avg, size, quote, pnl]:\n" + str(position()))
    close_all()
    start()
    time.sleep(10)
    tp(profit_tp)


# print("log: tp() function")

# #################### main function ########################################
def run():
    close_all()
    start()
    tp(0.25)
    pass
