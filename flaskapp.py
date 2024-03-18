from time import sleep
from tokenize import group
from flask import Flask, make_response, render_template, redirect, url_for, request,jsonify
import json, requests
from datetime import datetime, timedelta
import os
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
import math


#GET USD RATE INITIAL ATTEMP
url = "https://api.monobank.ua/bank/currency"
try:
    res = requests.get(url) 
    if res.status_code == 200:
        print('MonoRate')
        usd_price_intial = res.json()[0]['rateSell']
        product_price_uah = {
            'elementary': math.ceil(9 * usd_price_intial),
            'pre_intermediate': math.ceil(11 * usd_price_intial),
            'intermediate': math.ceil(10 * usd_price_intial)
            }
        # print(product_price_uah['elementary'])
        print(f'INITIAL PRICE: {usd_price_intial}')
        bank = 'Монобанк'
    else:
        print('Privat24 Rate')
        url = 'https://api.privatbank.ua/p24api/pubinfo?exchange&json&coursid=11'
        try:
            res = requests.get(url) 
            if res.status_code == 200:
                usd_price_intial = float(res.json()[1]['sale'])
                product_price_uah = {
                    'elementary': math.ceil(9 * usd_price_intial),
                    'pre_intermediate': math.ceil(11 * usd_price_intial),
                    'intermediate': math.ceil(10 * usd_price_intial)
                    }
                # print(product_price_uah['elementary'])
                print(f'INITIAL PRICE: {usd_price_intial}')
                bank = 'Приват24'
            else:
                usd_price_intial = 39.75
        except Exception as e:
            raise e
except Exception as e:
    raise e

usd_price = usd_price_intial

lesson_price_usd = {
    'individual': '35/50/60',
    'individual_time':'30/45/60',
    'group':150,
    'pair':75
    }

product_price_usd = { 
    'elementary': 8,
    'pre_intermediate': 9,
    'intermediate': 10
    }


product_price_uah = {
    'elementary': math.ceil(product_price_usd['elementary'] * usd_price),
    'pre_intermediate': math.ceil(product_price_usd['pre_intermediate'] * usd_price),
    'intermediate': math.ceil(product_price_usd['intermediate'] * usd_price)
    }


# TOKEN = os.getenv('BOT_TOKEN')
# CHAT_ID = os.getenv('CHAT_ID')


from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
# Flask - библиотека для запуска нашего приложения Flask - app
# render_template - нужен для то чтобы ваша страница html отобразилась корреткно
# redirect - нам понадобится для обработки запросы формы где мы перенаприм пользователя на страницу админ панели
# url_for - вспомогательна библиотека для того чтобы сделать правильный переход по ссылке в нашем случеш мы будем ссылаться на adm_panel
# request - обработчик запросов GET/POST и дргуих 


time_now = datetime.now() + timedelta(hours=2)


def get_usd_price():
    
    global usd_price, product_price_uah, bank
    url = "https://api.monobank.ua/bank/currency"
    try:
        res = requests.get(url) 
        if res.status_code == 200:
            usd_price = res.json()[0]['rateSell']
            product_price_uah = {
                'elementary': math.ceil(9 * usd_price),
                'pre_intermediate': math.ceil(11 * usd_price),
                'intermediate': math.ceil(10 * usd_price)
                }
            print(product_price_uah['elementary'])
            print(usd_price)
            bank = 'Монобанк'
            return usd_price
    except Exception as e:
        tg_sendMsg_report(f'[{time_now.strftime("%Y-%m-%d %H:%M:%S")}] Exeption\nPashaVPS\nshozaenglish.pp.ua\n\n def get_usd_price()\n\n{e}')
        raise e
    
    url = 'https://api.privatbank.ua/p24api/pubinfo?exchange&json&coursid=11'
    try:
        res = requests.get(url) 
        if res.status_code == 200:
            usd_price = float(res.json()[0]['sale'])
            product_price_uah = {
                'elementary': math.ceil(9 * usd_price),
                'pre_intermediate': math.ceil(11 * usd_price),
                'intermediate': math.ceil(10 * usd_price)
                }
            print(product_price_uah['elementary'])
            print(f'INITIAL PRICE: {usd_price}')
            bank = 'Приват24'
        else:
            usd_price = 39.75
    except Exception as e:
        tg_sendMsg_report(f'[{time_now.strftime("%Y-%m-%d %H:%M:%S")}] Exeption\nPashaVPS\nshozaenglish.pp.ua\n\n def get_usd_price(PrivatBank)\n\n{e}')
        raise e
    
    return usd_price


scheduler = BackgroundScheduler()
scheduler.add_job(func=get_usd_price, trigger="interval", seconds=360)
scheduler.start()

def get_location(ip_address):
    # https://ip-api.com/docs/api:json
    req = requests.get(f'http://ip-api.com/json/{ip_address}').json()
    # print(req)
    country,city = (req["country"], req["city"])
    return country,city

def tg_sendMsg_report(msg: str = "no message",TOKEN='7032094699:AAFlN7PBqH6LJKR-K-YpFhnanGop9MnYv2Q',chat_id=752683417,
    ps = "\n",
    *,
    sep_msg: bool = False,
):

    """send message via telegram api(url)\n
    url = (
        f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={msg}"
    )"""
    # TOKEN = TOKEN
    # chat_id = chat_id
    _ps = ps
    isStr = type(msg) is str
    if isStr:
        msg = msg + _ps
    # if sep_msg and type(msg) == list:
    #     for m in msg:
    #         url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={m + _ps}"
    #         requests.get(url).json()
    # elif not sep_msg and type(msg) != str:
    #     msg = " \n".join([m for m in msg]) + _ps
    url = (
        f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={msg}"
    )
    requests.get(url).json()

def tg_sendMsg(msg: str = "no message",TOKEN='7032094699:AAFlN7PBqH6LJKR-K-YpFhnanGop9MnYv2Q',chat_id=643621106,
    ps = "\n",
    *,
    sep_msg: bool = False,
):

    """send message via telegram api(url)\n
    url = (
        f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={msg}"
    )"""
    # TOKEN = TOKEN
    # chat_id = chat_id
    _ps = ps
    isStr = type(msg) is str
    if isStr:
        msg = msg + _ps
    # if sep_msg and type(msg) == list:
    #     for m in msg:
    #         url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={m + _ps}"
    #         requests.get(url).json()
    # elif not sep_msg and type(msg) != str:
    #     msg = " \n".join([m for m in msg]) + _ps
    url = (
        f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={msg}"
    )
    requests.get(url).json()


def form_backup(name, email, message,ip_address):
    
    country,city = get_location(ip_address)

    with open('form_usage.txt', 'a') as f:
        msg = f'[{time_now.strftime("%Y-%m-%d %H:%M:%S")}] Contact Form\n{email}\n{country}({city})\n{name}\n\n"{message}"\n'+'-'*150+'\n\n'
        f.write(msg)  
    
    tg_sendMsg(f'[{time_now.strftime("%Y-%m-%d %H:%M:%S")}] Contact Form\n{email}\n{country}({city})\n{name}\n\n"{message}"')

def form_order(name, email, product, payment_method, payment_amount, message,ip_address):
    country,city = get_location(ip_address)
    if message == '':
        message = 'none'
    with open('orders.txt', 'a') as f:
        msg = f'[{time_now.strftime("%Y-%m-%d %H:%M:%S")}] Order \nmail:{email}\nlocation:{country}({city})\nname:{name}\nProduct:"{product}"\nPaymentMethod:{payment_method}\nAmount:{payment_amount}'+f'comment:{message}\n\n'+'-'*150+'\n\n'
        f.write(msg)  
    
    tg_sendMsg(f'[{time_now.strftime("%Y-%m-%d %H:%M:%S")}] Order\nEmail:{email}\nLocation:{country}({city})\nName:{name}\nProduct:"{product}"\nPaymentMethod:{payment_method}\nAmount:{payment_amount}\nComment:{message}')

app = Flask(__name__)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["500 per day", "200 per hour"],
    storage_uri="memory://",
)

app.config['STATIC_FOLDER'] = 'static'
app.config['STATIC_URL_PATH'] = 'static'


# @app.route("/", methods=["GET", 'POST'])
# def redirect_internal():
#     return redirect("/ru", code=302)

#  наша корневая страиницу лендинда 
@app.route('/', methods=['GET','POST'])
@limiter.limit('20/minute')
def home_ru():
    if request.method == 'POST':
        # Здесь должна быть логика аутентификации
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        # ip_address = request.environ['REMOTE_ADDR']
        # ip_address = request.remote_addr
        ip_address = request.environ['HTTP_X_FORWARDED_FOR']

        print(ip_address)
        
        form_backup(name, email, message,ip_address) 
        
        return redirect('/contact')


    # Загрузка и отображение главной страницы (landing page)
    return render_template('index.html', 
    individual_price=lesson_price_usd['individual'],
    individual_time=lesson_price_usd['individual_time'],
    group_price=lesson_price_usd['group'],
    pair_price=lesson_price_usd['pair'],
    elementary_price=product_price_usd['elementary'], #TODO add varial to order html
    pre_inter_price=product_price_usd['pre_intermediate'],
    inter_price=product_price_usd['intermediate']
) 


@app.route('/ua', methods=['GET','POST'])
@limiter.limit('20/minute')
def home_ua():
    if request.method == 'POST':
        # Здесь должна быть логика аутентификации
        name = request.form['name']
        email = request.form['email'] 
        message = request.form['message']
        ip_address = request.environ['HTTP_X_FORWARDED_FOR']
        print(ip_address)
        
        form_backup(name, email, message, ip_address) 
        
        
        return redirect('/contact_ua')
    # Загрузка и отображение главной страницы (landing page)
    return render_template('index_ukr.html',
    individual_price=lesson_price_usd['individual'],
    individual_time=lesson_price_usd['individual_time'],
    group_price=lesson_price_usd['group'],
    pair_price=lesson_price_usd['pair'],
    elementary_price=product_price_usd['elementary'], #TODO add varial to order html
    pre_inter_price=product_price_usd['pre_intermediate'],
    inter_price=product_price_usd['intermediate']
    ) 

@app.route('/contact', methods=['GET'])
@limiter.limit('20/minute')
def contact():
    return render_template('index_message_sent.html') 

@app.route('/contact_ua', methods=['GET'])
@limiter.limit('20/minute')
def contact_ua():
    # Загрузка и отображение главной страницы (landing page)
    return render_template('index_message_sent_ua.html') 
    # return f'welcome {user}'

@app.route('/order_sent', methods=['GET'])
@limiter.limit('20/minute')
def order_sent():
    # Загрузка и отображение главной страницы (landing page)
    return render_template('order_sent.html') 

@app.route('/order_sent_ua', methods=['GET'])
@limiter.limit('20/minute')
def order_sent_ua():
    # Загрузка и отображение главной страницы (landing page)
    return render_template('order_sent_ua.html')


@app.route('/order/<product>/', methods=['POST', 'GET'])
@limiter.limit('20/minute')
def make_order(product):

    if request.method == 'POST':
        # Здесь должна быть логика аутентификации
        name = request.form['name'] 
        email = request.form['email']
        message = request.form['message']
        payment_method = request.form['paymentMethod']
        suffix_list = ['(USD)', 'pal']
        suffix_list1 = ['(TRC20)', '(ID)']
        payment_amount = 0

        if payment_method.endswith(tuple(suffix_list)):
            payment_amount = str(product_price_usd[f'{product}']) + ' USD'
        elif payment_method.endswith(tuple(suffix_list1)):
            payment_amount = str(product_price_usd[f'{product}']) + ' USDT'
        elif payment_method.endswith('(UAH)'):
            payment_amount = str(product_price_uah[f'{product}']) + ' UAH'

        ip_address = request.environ['HTTP_X_FORWARDED_FOR']

        form_order(name, email, product, payment_method, payment_amount, message, ip_address)
        return redirect(url_for('order_sent'))
    # Загрузка и отображение главной страницы (landing page)
    url = f'order_{product}.html'
    return render_template(url, usd_price=usd_price,
    product_price_uah=product_price_uah[f'{product}'],
    product_price_usd=product_price_usd[f'{product}'],
    bank=bank)


@app.route('/order/<product>/ua', methods=['POST', 'GET'])
@limiter.limit('20/minute')
def make_order_ua(product):

    if request.method == 'POST':
        # Здесь должна быть логика аутентификации
        name = request.form['name'] 
        email = request.form['email']
        message = request.form['message']
        payment_method = request.form['paymentMethod']

        suffix_list = ['(USD)', 'pal']
        suffix_list1 = ['(TRC20)', '(ID)']
        payment_amount = 0

        if payment_method.endswith(tuple(suffix_list)):
            payment_amount = str(product_price_usd[f'{product}']) + ' USD'
        elif payment_method.endswith(tuple(suffix_list1)):
            payment_amount = str(product_price_usd[f'{product}']) + ' USDT'
        elif payment_method.endswith('(UAH)'):
            payment_amount = str(product_price_uah[f'{product}']) + ' UAH'
        
        ip_address = request.environ['HTTP_X_FORWARDED_FOR']
        form_order(name, email, product, payment_method, payment_amount, message,ip_address)
        return redirect(url_for('order_sent_ua'))
    # Загрузка и отображение главной страницы (landing page)
    url = f'order_{product}_ua.html'
    return render_template(url, usd_price=usd_price,
    product_price_uah=product_price_uah[f'{product}'],
    product_price_usd=product_price_usd[f'{product}'],
    bank=bank
    )
# @app.route('/visit', methods=['GET','POST'])
# @limiter.limit('20/minute')  
# def visit():
#     vc=request.cookies.get('user_visit', "1")
#     resp = make_response(f"This is visit number {int(vc)}")
#     vscount=int(vc)+1
#     resp.set_cookie('user_visit',str(vscount), max_age=5*60*60, secure=True)
#     return resp


# # форма отправки сообщения
# @app.route('/', methods=['POST'])
# def send_message():
#     if request.method == 'POST':
#         return redirect(url_for('contact'))
#     else:
#         return redirect('/')

# форма отправки сообщения
# @app.route('/ua', methods=['POST'])
# def send_message_ua():
#     if request.method == 'POST':
#         return redirect(url_for('contact_ua'))
#     else:
#         return redirect('/ua')



if __name__ == '__main__':
    app.run(debug=True)
    # Shut down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())
    # app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
    
    