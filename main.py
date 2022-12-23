import datetime
import html
import json
import random
import threading
import time

import bs4
import requests
import vk

VK_API_TOKEN: str
GROUP: int
ADMINS: tuple
PEERS = [2000000001, 2000000002]
COMING_DEADLINES = dict()
with open("TOKEN.json", 'r') as file:
    VK_API_TOKEN = json.load(file)
with open("GROUP.json", 'r') as file:
    GROUP = json.load(file)
with open("ADMINS.json", 'r') as file:
    ADMINS = json.load(file)

STICKER_IDS = {'/ogre': '457239022', '/bebrou': '457239023', '/bigbrain': '457239024', '/sleeping': '457239025',
               '/xd': '457239026', '/fire': '457239027', '/walrus': '457239028', '/bruh': '457239029',
               '/based': '457239030', '/vsempoh': '457239031', '/starosta1': '457239037',
               '/starosta2': '457239032', '/char': '457239033', '/genius': '457239034', '/pickle': '457239035',
               '/vlad': '457239036', '/ryan': '457239038', '/noname': '457239039'}

api = vk.API(access_token=VK_API_TOKEN, v='5.95')

long_poll = api.groups.getLongPollServer(group_id=GROUP)
server, key, ts = long_poll['server'], long_poll['key'], long_poll['ts']


def start_msg(msg):
    start_messages = ["Я пришел с миром!", "Какие люди и без охраны!",
                      "Сколько лет, сколько зим!", "Отличное выглядишь!", "Салют!", "Мы знакомы?",
                      "Здравствуйте, товарищи!",
                      "Как настроение?", "Не верю своим глазам! Ты ли это?", "Гоп-стоп, мы подошли из-за угла.",
                      "Мне кажется или я где-то вас видел?", "Какие планы на вечер?", "Привет, чуваки!",
                      "Какие люди нарисовались!"]
    msg_text = random.choice(start_messages)

    api.messages.send(peer_id=msg['peer_id'],
                      random_id=random.randint(1, 2 ** 31),
                      message=msg_text)


def help_msg(msg):
    api.messages.send(peer_id=msg['peer_id'],
                      random_id=random.randint(1, 2 ** 31),
                      message=
                      """/start - приветствие
/help - справка
/gelich - Андрей Гелиевич
/spin - You spin me right round
/pohuy
/deadlines - список дедлайнов
/add_deadline <предмет> - <время> - +дедлайн, только админам
/remove_deadline <предмет> - -дедлайн, только админам
/nothing
/sourcecode - ссыль на исходники
/bash - рандомная цитата с башорга
/upya4ka - ...
/stickers - список команд для отправки "стикеров"
Дата и время в формате ДД.ММ.ГГГГ_ЧЧ:ММ:СС""")


def sticker_list(msg):
    text = ''
    for sticker in STICKER_IDS:
        text += sticker + ', '
    text = text.rstrip(', ')
    api.messages.send(peer_id=msg['peer_id'],
                      random_id=random.randint(1, 2 ** 31),
                      message=text)


def send_sticker(msg):
    attach = 'photo-217867161_'
    attach += STICKER_IDS[msg['text']]
    api.messages.send(peer_id=msg['peer_id'],
                      random_id=random.randint(1, 2 ** 31),
                      attachment=attach)


def gelich_msg(msg):
    api.messages.send(peer_id=msg['peer_id'],
                      random_id=random.randint(1, 2 ** 31),
                      attachment='wall-217867161_3')


def spin_msg(msg):
    api.messages.send(peer_id=msg['peer_id'],
                      random_id=random.randint(1, 2 ** 31),
                      attachment='wall-217867161_1')


def up4k_msg(msg):
    api.messages.send(peer_id=msg['peer_id'],
                      random_id=random.randint(1, 2 ** 31),
                      attachment='wall-217867161_4')


def poh_msg(msg):
    api.messages.send(peer_id=msg['peer_id'],
                      random_id=random.randint(1, 2 ** 31),
                      attachment=random.choice(
                          ['photo-217867161_457239017', 'photo-217867161_457239018', 'photo-217867161_457239019']))


def deadlines_msg(msg):
    text = ""
    with open("deadlines.json", "r") as fin:
        data = json.load(fin)
        if len(data) != 0:
            for subj in data:
                text += str(subj) + ' - ' + data[subj] + '\n'
        else:
            text = "Пока дедлайнов нет!"
    api.messages.send(peer_id=msg['peer_id'],
                      random_id=random.randint(1, 2 ** 31),
                      message=text)


def add_deadline(msg):
    try:
        fin = open("deadlines.json", "r")
        data = json.load(fin)
        if len(data) == 0:
            data = {'': ''}
        fin.close()
        new_deadline = msg['text'].split(" ", maxsplit=1)[1].split(' - ')
        subj = new_deadline[0]
        time = datetime.datetime.strptime(new_deadline[1], '%d.%m.%Y_%H:%M:%S')
        data[subj] = time.strftime('%d.%m.%Y_%H:%M:%S')
        data.pop('')
        with open("deadlines.json", "w") as fout:
            json.dump(data, fout)
        api.messages.send(peer_id=msg['peer_id'],
                          random_id=random.randint(1, 2 ** 31),
                          message="Добавил")
    except Exception as e:
        api.messages.send(peer_id=msg['peer_id'],
                          random_id=random.randint(1, 2 ** 31),
                          message="Ошибка: " + str(e))


def rem_deadline(msg):
    try:
        fin = open("deadlines.json", "r")
        data = json.load(fin)
        if len(data) == 0:
            api.messages.send(peer_id=msg['peer_id'],
                              random_id=random.randint(1, 2 ** 31),
                              message="Ошибка: Дедлайнов нет")
            return
        fin.close()
        deadline = msg['text'].split(" ", maxsplit=1)[1]
        data.pop(deadline)
        with open("deadlines.json", "w") as fout:
            json.dump(data, fout)
        api.messages.send(peer_id=msg['peer_id'],
                          random_id=random.randint(1, 2 ** 31),
                          message="Удалил")
    except Exception as e:
        api.messages.send(peer_id=msg['peer_id'],
                          random_id=random.randint(1, 2 ** 31),
                          message="Ошибка: " + str(e))


def notadmin_msg(msg):
    name = api.users.get(user_id=msg['from_id'])
    name = name[0]
    name = name['first_name']
    api.messages.send(peer_id=msg['peer_id'],
                      random_id=random.randint(1, 2 ** 31),
                      message=name + " is an impostor")


def nothing_msg(msg):
    api.messages.send(peer_id=msg['peer_id'],
                      random_id=random.randint(1, 2 ** 31),
                      message='&#13;')


def source_msg(msg):
    api.messages.send(peer_id=msg['peer_id'],
                      random_id=random.randint(1, 2 ** 31),
                      message='https://github.com/Andrien777/VKBot/')


def get_bash_quote():
    web = requests.get('https://башорг.рф/rss/')
    soup = bs4.BeautifulSoup(web.text, 'xml')
    results = soup.find_all(name='item')
    return html.unescape(
        random.choice(results).description.text.replace('&lt;', '<').replace('&rt;', '>').replace("<br>", '\n'))


def quote_msg(msg):
    api.messages.send(peer_id=msg['peer_id'],
                      random_id=random.randint(1, 2 ** 31),
                      message=get_bash_quote())


def check_deadlines():
    fin = open("deadlines.json", "r")
    data = json.load(fin)
    fin.close()
    curr = datetime.datetime.now()
    deadlines_to_delete = []
    for deadline in data:
        line = datetime.datetime.strptime(data[deadline], '%d.%m.%Y_%H:%M:%S')
        if line <= curr:
            deadlines_to_delete.append(deadline)
            continue
        delta = line - curr
        if delta.days == 1 and delta.seconds < 100:
            COMING_DEADLINES[deadline] = 'DAY'
        elif delta.days == 0 and delta.seconds in range(3500, 3700):
            COMING_DEADLINES[deadline] = 'HOUR'
    for deadline in deadlines_to_delete:
        data.pop(deadline)
    with open("deadlines.json", "w") as fout:
        json.dump(data, fout)


def inform_deadline(deadline, delta: str):
    text = 'Дедлайн ' + deadline + ' скоро истекает.\nОсталось времени: '
    print(text)
    if delta == 'DAY':
        text += '1 день'
    elif delta == 'HOUR':
        text += '1 час'
    print(text)
    for peer in PEERS:
        api.messages.send(peer_id=peer,
                          random_id=random.randint(1, 2 ** 31),
                          message=text)


def thread_task():
    while True:
        check_deadlines()
        time.sleep(60)


thread = threading.Thread(target=thread_task)
thread.start()

while True:
    long_poll = requests.post('%s' % server, data={'act': 'a_check',
                                                   'key': key,
                                                   'ts': ts,
                                                   'wait': 25}).json()
    try:
        if long_poll['updates'] and len(long_poll['updates']) != 0:
            for update in long_poll['updates']:
                if update['type'] == 'message_new':
                    if update['object']['peer_id'] not in PEERS:
                        PEERS.append(update['object']['peer_id'])
                    if update['object']['text'] == '/start':
                        start_msg(update['object'])
                    elif update['object']['text'] == '/help':
                        help_msg(update['object'])
                    elif update['object']['text'] == '/gelich':
                        gelich_msg(update['object'])
                    elif update['object']['text'] == '/spin':
                        spin_msg(update['object'])
                    elif update['object']['text'] == '/pohuy':
                        poh_msg(update['object'])
                    elif update['object']['text'] == '/deadlines':
                        deadlines_msg(update['object'])
                    elif update['object']['text'].startswith('/add_deadline '):
                        add_deadline(update['object']) if update['object']['from_id'] in ADMINS else notadmin_msg(
                            update['object'])
                    elif update['object']['text'].startswith('/remove_deadline '):
                        rem_deadline(update['object']) if update['object']['from_id'] in ADMINS else notadmin_msg(
                            update['object'])
                    elif update['object']['text'] == '/nothing':
                        nothing_msg(update['object'])
                    elif update['object']['text'] == '/sourcecode':
                        source_msg(update['object'])
                    elif update['object']['text'] == '/bash':
                        quote_msg(update['object'])
                    elif update['object']['text'] == '/upya4ka':
                        up4k_msg(update['object'])
                    elif update['object']['text'] == '/stickers':
                        sticker_list(update['object'])
                    elif update['object']['text'] in STICKER_IDS:
                        send_sticker(update['object'])
    except KeyError:
        api = vk.API(access_token=VK_API_TOKEN, v='5.95')
        long_poll = api.groups.getLongPollServer(group_id=GROUP)
        server, key, ts = long_poll['server'], long_poll['key'], long_poll['ts']
        continue
    for deadline in COMING_DEADLINES:
        inform_deadline(deadline, COMING_DEADLINES[deadline])
    COMING_DEADLINES.clear()
    ts = long_poll['ts']
