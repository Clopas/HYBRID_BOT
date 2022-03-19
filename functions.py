import json
import requests
import hmac
import hashlib
import time
from requests import Request, session
from credentials import *
# ##################### FTX request function ###############################


def request_ftx(request_type, ftx_endpoint):
    ts = int(time.time() * 1000)
    position_request = Request(request_type, f"https://ftx.com/api{ftx_endpoint}")
    prepared = position_request.prepare()
    signature_payload = f'{ts}{prepared.method}{prepared.path_url}'.encode()
    signature_request_ftx = hmac.new(api_secret_ftx.encode(), signature_payload, 'sha256').hexdigest()
    prepared.headers['FTX-KEY'] = api_key_ftx
    prepared.headers['FTX-SIGN'] = signature_request_ftx
    prepared.headers['FTX-TS'] = str(ts)
    response = session().send(prepared)
    loaded_response = json.loads(response.content)
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
            break


price_pair = price()
print(f"{pair_ftx} price is {price_pair}")

# ##################### Get position details from FTX ######################
balance = 0
leverage = 2


def position():
    ftx_position_endpoint = '/positions?showAvgPrice=True'
    position_response = request_ftx('GET', ftx_position_endpoint)
    for i in position_response['result']:
        if i["future"] == pair_ftx:
            if i["size"] == 0.0:
                print('You do not have an open', pair_ftx, 'position!')
                return None
            else:
                p = (i['recentPnl'] / balance) * 100
                avg = i['recentBreakEvenPrice']
                size = i['size']
                quote = i['cost']
                pnl = i['recentPnl']
                print(
                    f"Your profit is {round(p, 4)}%, position size is {size} {pair_ftx} ~ {quote}$, unrealized p&l is {pnl}$, average price to break even is {avg}.")
                return [p, avg, size, quote, pnl]
            break


# ##################### 3commas bot inputs for 50% D.D #######################

pair_3commas = f"USD_{pair_ftx}"

BOH = price_pair + (price_pair * (0.04))
BOL = price_pair + (price_pair * (-0.05))

SO1H = price_pair + (price_pair * (-0.05))
SO1L = price_pair + (price_pair * (-0.14))

SO2H = price_pair + (price_pair * (-0.14))
SO2L = price_pair + (price_pair * (-0.23))

SO3H = price_pair + (price_pair * (-0.23))
SO3L = price_pair + (price_pair * (-0.32))

SO4H = price_pair + (price_pair * (-0.32))
SO4L = price_pair + (price_pair * (-0.41))

SO5H = price_pair + (price_pair * (-0.41))
SO5L = price_pair + (price_pair * (-0.5))

print(SO2H)
print(SO2H/price_pair)
# ##################### 3commas bot inputs for 40% D.D ########################

# BOH = price_pair + (price_pair * (0.04))
# BOL = price_pair + (price_pair * (-0.05))

# SO1H = price_pair + (price_pair * (-0.05))
# SO1L = price_pair + (price_pair * (-0.12))

# SO2H = price_pair + (price_pair * (-0.12))
# SO2L = price_pair + (price_pair * (-0.19))

# SO3H = price_pair + (price_pair * (-0.19))
# SO3L = price_pair + (price_pair * (-0.26))

# SO4H = price_pair + (price_pair * (-0.26))
# SO4L = price_pair + (price_pair * (-0.33))

# SO5H = price_pair + (price_pair * (-0.33))
# SO5L = price_pair + (price_pair * (-0.4))

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
# ##################### Print pair quantity & volume (per D.D) (base currency volume) ####################

BO = (37 / price_pair)
BOO = 37
print('\nBase currency volumes:\n' + str(round(BO)) + ' ' + pair_ftx)
SO1 = (SO1V50 / (0.5 * (SO1H + SO1L)))
SO1O = SO1V50
print(str(round(SO1, 2)) + ' ' + pair_ftx)
SO2 = (SO1V50 * SCALE50) / (0.5 * (SO2H + SO2L))
SO2O = SO1V50 * SCALE50
print(str(round(SO2, 2)) + ' ' + pair_ftx)
SO3 = (SO1V50 * SCALE50 ** 2) / (0.5 * (SO3H + SO3L))
SO3O = SO1V50 * SCALE50 ** 2
print(str(round(SO3, 2)) + ' ' + pair_ftx)
SO4 = (SO1V50 * SCALE50 ** 3) / (0.5 * (SO4H + SO4L))
SO4O = SO1V50 * SCALE50 ** 3
print(str(round(SO4, 2)) + ' ' + pair_ftx)
SO5 = (SO1V50 * SCALE50 ** 4) / (0.5 * (SO5H + SO5L))
SO5O = SO1V50 * SCALE50 ** 4
print(str(round(SO5, 2)) + ' ' + pair_ftx)

print(f"Total base currency size: {round((BO + SO1 + SO2 + SO3 + SO4 + SO5), 2)}")
print('BOO+SO1O+SO2O+SO3O+SO4O+SO5O)/price:' + str(round((BOO + SO1O + SO2O + SO3O + SO4O + SO5O) / price_pair, 2)))
# ##################### Print $$$ volume (quote currency volume) ####################
print('\nQuote currency volumes:\n' + str(BOO) + "$")
print(str(round(SO1O, 2)) + "$")
print(str(round(SO2O, 2)) + "$")
print(str(round(SO3O, 2)) + "$")
print(str(round(SO4O, 2)) + "$")
print(str(round(SO5O, 2)) + "$")

balance = BOO + SO1O + SO2O + SO3O + SO4O + SO5O
print('Total balance: ' + str(round(balance, 2)) + '$\n')


# ##################### Grids quantities #############################

def grids_quantity(grid_volume):
    a = [14, 15, 16, 17, 18, 19, 20]
    for i in a[:]:
        if abs((grid_volume / i) - round(grid_volume / i, 1)) <= 0.1:
            return [round(grid_volume / i, 1), i]
    else:
        raise ValueError("Damn it!!! I Couldn't find a good grid quantity!")


BO_qty = grids_quantity(BO)
print(BO_qty)
SO1_qty = grids_quantity(SO1)
print(SO1_qty)
SO2_qty = grids_quantity(SO2)
print(SO2_qty)
SO3_qty = grids_quantity(SO3)
print(SO3_qty)
SO4_qty = grids_quantity(SO4)
print(SO4_qty)
SO5_qty = grids_quantity(SO5)
print(SO5_qty)
# ###################### Print % of steps in every grid ###################

print('\n% of steps in every grid:')
print(round(((BOH - BOL) / (BOH * (BO_qty[1]))) * 100, 3))
print(round(((SO1H - SO1L) / (SO1H * (SO1_qty[1]))) * 100, 3))
print(round(((SO2H - SO2L) / (SO2H * (SO2_qty[1]))) * 100, 3))
print(round(((SO3H - SO3L) / (SO3H * (SO3_qty[1]))) * 100, 3))
print(round(((SO4H - SO4L) / (SO4H * (SO4_qty[1]))) * 100, 3))
print(round(((SO5H - SO5L) / (SO5H * (SO5_qty[1]))) * 100, 3))
# print("log: Printed inputs")

# ###################### 3commas endpoints ###########################
create_dca_url = '/ver1/bots/create_bot'  # POST
disable_dca_url = '/ver1/bots/{bot_id}/disable'   #POST
enable_dca_url = '/ver1/bots/{bot_id}/enable'   #POST
delete_dca_url = '/ver1/bots/{bot_id}/delete' #POST
edit_dca_url = '/ver1/bots/{bot_id}/update'  # PATCH
#id_dca_url = '/ver1/grid_bots'  # GET
asap_dca_url = '/ver1/bots/{bot_id}/start_new_deal'  #POST


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
# ##################### 3commas data_urls #########################

BO_dca_data_url = f"&account_id={account_id_3commas}&pair={pair_3commas}&base_order_volume=50&take_profit='5'&safety_order_volume=4.32&martingale_volume_coefficient=1&martingale_step_coefficient=1&max_safety_orders=20&active_safety_orders_count=20&safety_order_step_percentage=0.675&take_profit_type=total&leverage_type=cross"

SO2_data_url = f"&account_id={account_id_3commas}&pair={pair_3commas}&upper_price={SO2H}&lower_price={SO2L}&quantity_per_grid={SO2_qty[0]}&grids_quantity={SO2_qty[1]}&leverage_type=cross&leverage_custom_value={leverage}&is_enabled=true"
SO3_data_url = f"&account_id={account_id_3commas}&pair={pair_3commas}&upper_price={SO3H}&lower_price={SO3L}&quantity_per_grid={SO3_qty[0]}&grids_quantity={SO3_qty[1]}&leverage_type=cross&leverage_custom_value={leverage}&is_enabled=true"
SO4_data_url = f"&account_id={account_id_3commas}&pair={pair_3commas}&upper_price={SO4H}&lower_price={SO4L}&quantity_per_grid={SO4_qty[0]}&grids_quantity={SO4_qty[1]}&leverage_type=cross&leverage_custom_value={leverage}&is_enabled=true"
SO5_data_url = f"&account_id={account_id_3commas}&pair={pair_3commas}&upper_price={SO5H}&lower_price={SO5L}&quantity_per_grid={SO5_qty[0]}&grids_quantity={SO5_qty[1]}&leverage_type=cross&leverage_custom_value={leverage}&is_enabled=true"


# ##################### 3commas requests function #############################

def request_3commas(request_type, endpoint_url, data_url):
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


# print(request_3commas('GET', id_grid_url, ''))  # test
# print("log: 3commas function")

# ##################### Bot lists ##########################################
grid_list = request_3commas('GET', id_grid_url, '&limit=1000')
enabled_grid_list_new = []
# for i in grid_list:
#    if i['is_enabled'] == True and i['pair'] == pair_3commas:
#        enabled_grid_list_new.append([i['id'], i['upper_price'], i['updated_at']])
#        enabled_grid_list_new.sort(key=lambda x: x[1], reverse=True)
#        # print(enabled_grid_list_new) #test

smart_trade_list = request_3commas('GET', id_smart_trade_url, '&status=active')


# ##################### Clean up useless grid bots ##############################
async def cleanup():
    for i in grid_list:
        if (i['is_enabled'] == False) and i['total_profits_count'] == '0':
            request_3commas('DELETE', delete_grid_url.format(id=i['id']), '')
            print('\n' + str(i['id']) + ' ' + str(i['pair']) + ' is deleted.')
    print('Bots clean up is completed!')


# print("log: cleanup() function")
def create_dca():
    request_3commas('POST', create_dca_url, BO_dca_data_url)


# ################### Run the bots ############################################
def run():
    if len(enabled_grid_list_new) == 6:
        print('List before editing: ' + str(enabled_grid_list_new))

        for i in smart_trade_list:
            if i['pair'] == pair_3commas:
                smart_trade_close = request_3commas('POST', close_smart_trade_url.format(id=i['id']), '')
                print("\nA smart trade is closed:\n" + str(smart_trade_close))

        request_3commas('POST', create_dca_url, BO_dca_data_url)

        so2_edit = request_3commas('PATCH', edit_grid_url.format(id=enabled_grid_list_new[2][0]),
                                   SO2_data_url)
        request_3commas('POST', enable_grid_url.format(id=enabled_grid_list_new[2][0]), '')
        print('\nso2_edited:\n' + str(so2_edit))

        so3_edit = request_3commas('PATCH', edit_grid_url.format(id=enabled_grid_list_new[3][0]),
                                   SO3_data_url)
        request_3commas('POST', enable_grid_url.format(id=enabled_grid_list_new[3][0]), '')
        print('\nso3_edited:\n' + str(so3_edit))

        so4_edit = request_3commas('PATCH', edit_grid_url.format(id=enabled_grid_list_new[4][0]),
                                   SO4_data_url)
        request_3commas('POST', enable_grid_url.format(id=enabled_grid_list_new[4][0]), '')
        print('\nso4_edited:\n' + str(so4_edit))

        so5_edit = request_3commas('PATCH', edit_grid_url.format(id=enabled_grid_list_new[5][0]),
                                   SO5_data_url)
        request_3commas('POST', enable_grid_url.format(id=enabled_grid_list_new[5][0]), '')
        print('\nso5_edited:\n' + str(so5_edit))

        print("\nThe previously enabled bots are edited.")

    else:
        if len(enabled_grid_list_new) > 0:
            print("I couldn't find 6 grids to edit them. So I am creating new ones.")
        enabled_grid_list_new.clear()
        request_3commas('POST', create_dca_url, BO_dca_data_url)
        so2_create = request_3commas('POST', create_grid_url, SO2_data_url)
        enabled_grid_list_new.append([so2_create['id'], so2_create['lower_price']])
        print('\nso2_create:\n' + str(so2_create))

        so3_create = request_3commas('POST', create_grid_url, SO3_data_url)
        enabled_grid_list_new.append([so3_create['id'], so3_create['lower_price']])
        print('\nso3_create:\n' + str(so3_create))

        so4_create = request_3commas('POST', create_grid_url, SO4_data_url)
        enabled_grid_list_new.append([so4_create['id'], so4_create['lower_price']])
        print('\nso4_create:\n' + str(so4_create))

        so5_create = request_3commas('POST', create_grid_url, SO5_data_url)
        enabled_grid_list_new.append([so5_create['id'], so5_create['lower_price']])
        print('\nso5_create:\n' + str(so5_create))

        print('\nNew bots are created.')


# print("log: run() function")


# #################### Take profit and enter as soon as possible ########################################
def tp(profit_tp):
    while position() is None:
        time.sleep(10)
        print("Waiting for an open position.")
        continue

    while not (position()[0] >= profit_tp):
        price_tp = price()
        for i in enabled_grid_list_new[1:]:
            if price_tp <= float(i[1]):
                request_3commas('POST', disable_grid_url.format(id=i[0]), '')
                print(f"The higher grid {i} is disabled.")
        time.sleep(10)
        continue
    print("\nTake profit is executed. With specs as [p, avg, size, quote, pnl]:\n" + str(position()))
    run()
    tp()


# print("log: tp() function")


# #################### stop bots ########################################
async def close_all():
    grid_list_stop = request_3commas('GET', id_grid_url, '&limit=1000')
    for i in grid_list_stop:
        if i['is_enabled'] == True and i['pair'] == pair_3commas:
            disable_grid_stop = request_3commas('POST', disable_grid_url.format(id=i['id']), '')
            print(f"\nGrid {i['id']} is disabled.\n" + str(disable_grid_stop))

    for i in request_3commas('GET', '/ver1/bots/account_trade_info', f'&account_id={account_id_3commas}'):
        if i['pairs'] == [pair_3commas]:
            smart_trade_close_stop = request_3commas('POST', close_smart_trade_url.format(id=i['id']), '')
            print("\nA DCA is closed:\n" + str(smart_trade_close_stop))
    print("Close all done.")

print()
# print("log: close_all() function")

