import time
import vk
import requests
import random
import json
import datetime
import threading

VK_API_TOKEN: str
with open("TOKEN.json", 'r') as file:
    VK_API_TOKEN = json.load(file)
GROUP = 217867161
ADMINS = (559617832, 307644172)
PEERS = [2000000001, 2000000002]
COMING_DEADLINES = dict()


api = vk.API(access_token=VK_API_TOKEN, v='5.95')

longPoll = api.groups.getLongPollServer(group_id=GROUP)
server, key, ts = longPoll['server'], longPoll['key'], longPoll['ts']


def start_msg(msg):
    startMessages = ["Я пришел с миром!", "Какие люди и без охраны!",
                     "Сколько лет, сколько зим!", "Отличное выглядишь!", "Салют!", "Мы знакомы?",
                     "Здравствуйте, товарищи!",
                     "Как настроение?", "Не верю своим глазам! Ты ли это?", "Гоп-стоп, мы подошли из-за угла.",
                     "Мне кажется или я где-то вас видел?", "Какие планы на вечер?", "Привет, чуваки!",
                     "Какие люди нарисовались!"]
    msgText = random.choice(startMessages)

    api.messages.send(peer_id=msg['peer_id'],
                      random_id=random.randint(1, 2 ** 31),
                      message=msgText)


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
Дата и время в формате ДД.ММ.ГГГГ_ЧЧ:ММ:СС""")


def gelich_msg(msg):
    api.messages.send(peer_id=msg['peer_id'],
                      random_id=random.randint(1, 2 ** 31),
                      attachment='wall-217867161_3')


def spin_msg(msg):
    api.messages.send(peer_id=msg['peer_id'],
                      random_id=random.randint(1, 2 ** 31),
                      attachment='wall-217867161_1')


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
    longPoll = requests.post('%s' % server, data={'act': 'a_check',
                                                  'key': key,
                                                  'ts': ts,
                                                  'wait': 25}).json()

    if longPoll['updates'] and len(longPoll['updates']) != 0:
        for update in longPoll['updates']:
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
    for deadline in COMING_DEADLINES:
        inform_deadline(deadline, COMING_DEADLINES[deadline])
    ts = longPoll['ts']