from time import sleep
from tokenize import group
from flask import Flask, make_response, render_template, redirect, url_for, request,jsonify
import json, requests
from datetime import datetime, timedelta
import os

TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
# Flask - библиотека для запуска нашего приложения Flask - app
# render_template - нужен для то чтобы ваша страница html отобразилась корреткно
# redirect - нам понадобится для обработки запросы формы где мы перенаприм пользователя на страницу админ панели
# url_for - вспомогательна библиотека для того чтобы сделать правильный переход по ссылке в нашем случеш мы будем ссылаться на adm_panel
# request - обработчик запросов GET/POST и дргуих 


time_now = datetime.now() + timedelta(hours=2)

lesson_price_usd = {
    'individual': '20/28/33',
    'individual_time':'30/45/60',
    'group':125,
    'pair':44
    }



product_price_usd = {
    'elementary': 9,
    'pre_inter': 11,
    'inter': 10
    }


def tg_sendMsg(msg: str = "no message",TOKEN=TOKEN,chat_id=CHAT_ID,
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


def form_backup(name, email, message):
    with open('form_usage.txt', 'a') as f:
        msg = f'[{time_now.strftime("%Y-%m-%d %H:%M:%S")}] {email} {name}:"{message}"\n'+'-'*150+'\n\n'
        f.write(msg)  
    
    tg_sendMsg(f'[{time_now.strftime("%Y-%m-%d %H:%M:%S")}] Contact Form\n{email} \n{name}: "{message}"')

def form_order(name, email, product, payment_method, message):
    if message == '':
        message = 'none'
    with open('orders.txt', 'a') as f:
        msg = f'[{time_now.strftime("%Y-%m-%d %H:%M:%S")}] Order \nmail:{email} \nname:{name}\nProduct:"{product}"\nPaymentMethod:{payment_method}\n'+f'comment:{message}\n\n'+'-'*150+'\n\n'
        f.write(msg)  
    
    tg_sendMsg(f'[{time_now.strftime("%Y-%m-%d %H:%M:%S")}] Order\nEmail:{email}\nName:{name}\nProduct:\n"{product}"\nComment:{message}')

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

        form_backup(name, email, message) 
        
        print(name)
        return redirect('/contact')


    # Загрузка и отображение главной страницы (landing page)
    return render_template('index.html', 
    individual_price=lesson_price_usd['individual'],
    individual_time=lesson_price_usd['individual_time'],
    group_price=lesson_price_usd['group'],
    pair_price=lesson_price_usd['pair'],
    elementary_price=product_price_usd['elementary'], #TODO add varial to order html
    pre_inter_price=product_price_usd['pre_inter'],
    inter_price=product_price_usd['inter']
) 


@app.route('/ua', methods=['GET','POST'])
@limiter.limit('20/minute')
def home_ua():
    if request.method == 'POST':
        # Здесь должна быть логика аутентификации
        name = request.form['name']
        email = request.form['email'] 
        message = request.form['message']
        form_backup(name, email, message) 
        
        print(name)
        return redirect('/contact_ua')
    # Загрузка и отображение главной страницы (landing page)
    return render_template('index_ukr.html') 

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


@app.route('/order/<product>', methods=['POST', 'GET'])
@limiter.limit('20/minute')
def make_order(product):

    if request.method == 'POST':
        # Здесь должна быть логика аутентификации
        name = request.form['name'] 
        email = request.form['email']
        message = request.form['message']
        payment_method = request.form['paymentMethod']
        
        form_order(name, email, product, payment_method, message)
        return redirect(url_for('order_sent'))
    # Загрузка и отображение главной страницы (landing page)
    url = f'order_{product}.html'
    return render_template(url)
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
    # app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
    
    