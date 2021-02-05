import telebot
import time
from threading import Thread
import requests
import string
import random


bot = telebot.TeleBot('1699048434:AAGgyh-TS-QLOYF56cH-IBsCf4-Lf2bM0Go')
keyboard1 = telebot.types.ReplyKeyboardMarkup(True, True)
keyboard1.row('Create mail', 'Help')
keyboard2 = telebot.types.ReplyKeyboardMarkup(True, True)
keyboard2.row('Create mail', 'Restart bot')
keyboard3 = telebot.types.ReplyKeyboardMarkup(True)
keyboard3.row('Check mail')

url = 'https://api.mail.tm/'

response_domain = requests.get(f'{url}domains').json()
data = {
        'address': f'{"".join(random.sample(string.ascii_lowercase + string.digits, 15))}'
                   f'@{response_domain["hydra:member"][0]["domain"]}',
        'password': f'{"".join(random.sample(string.ascii_letters + string.digits, 10))}'
}


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Welcome to the FakeMailBot. Here you can create a temporary mail for all of '
                                      'your needs.', reply_markup=keyboard1)


@bot.message_handler(commands=['help'])
def help_message(message):
    bot.send_message(message.chat.id, 'This bot creates a temporary mail address. Why you should use it? '
                                      'Maybe you want to sign up for a site which requires that you provide'
                                      ' an e-mail address to send validation e-mail to. And maybe you don\'t '
                                      'want to give up your real e-mail address and end up on a bunch of spam lists.'
                                      ' This is nice and disposable. And it\'s free. Enjoy!.'
                                      ' Also you can restart the bot by pressing the button below.',
                     reply_markup=keyboard2)


@bot.message_handler(content_types=['text'])
def response(message):

    def delete_acc(id1, token):
        time.sleep(600)
        requests.delete(f'{url}accounts/{id1}', headers={'Authorization': f'Bearer {token}'})
        bot.send_message(message.chat.id, 'Your mail account has been successfully deleted.', reply_markup=keyboard1,
                         disable_notification=True)

    if message.text.lower() == 'help':
        help_message(message)
    elif message.text.lower() == 'create mail':
        requests.post(f'{url}accounts', json=data).json()
        bot.send_message(message.chat.id, text=data["address"])
        bot.send_message(message.chat.id, f'Here is your mail address. It will be automatically deleted after 10'
                                          f' minutes. To check for new messages press the button below.',
                         reply_markup=keyboard3)
        response_token = requests.post(f'{url}authentication_token', json=data).json()
        th = Thread(target=delete_acc, args=(response_token['id'], response_token['token']))
        th.start()
    elif message.text.lower() == 'check mail':
        try:
            response_token = requests.post(f'{url}authentication_token', json=data).json()
            response_msg = requests.get(f'{url}messages',
                                        headers={'Authorization': f'Bearer {response_token["token"]}'}).json()

            if len(response_msg['hydra:member']) == 0:
                bot.send_message(message.chat.id, 'No new mail yet.')
            else:
                response_msg_text = requests.get(
                    f'{url}messages/{response_msg["hydra:member"][0]["id"]}',
                    headers={'Authorization': f'Bearer {response_token["token"]}'}).json()
                bot.send_message(
                    message.chat.id,
                    f'From: {response_msg_text["from"]["name"]}'
                    f' ({response_msg_text["from"]["address"]})\n'
                    f'Subject: {response_msg_text["subject"]}\n'
                    f'  {response_msg_text["text"]}')
                requests.delete(f'{url}messages/{response_msg["hydra:member"][0]["id"]}', json=data,
                                headers={'Authorization': f'Bearer {response_token["token"]}'})
        except KeyError:
            bot.send_message(message.chat.id, 'You need to create a mail first.', reply_markup=keyboard1)
    elif message.text.lower() == 'restart bot':
        start_message(message)


bot.polling(none_stop=True)
