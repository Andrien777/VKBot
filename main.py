import datetime
import html
import json
import random
import threading
import time
import bs4
import requests
import vk
import wolframalpha
from queue import Queue
import re


similar_letters = {'а': ['а', 'a', '@'],
                   'б': ['б', '6', 'b'],
                   'в': ['в', 'b', 'v'],
                   'г': ['г', 'r', 'g'],
                   'д': ['д', 'd'],
                   'е': ['е', 'e'],
                   'ё': ['ё', 'e'],
                   'ж': ['ж', 'zh', '*'],
                   'з': ['з', '3', 'z'],
                   'и': ['и', 'u', 'i'],
                   'й': ['й', 'u', 'i'],
                   'к': ['к', 'k', 'i{', '|{'],
                   'л': ['л', 'l', 'ji'],
                   'м': ['м', 'm'],
                   'н': ['н', 'h', 'n'],
                   'о': ['о', 'o', '0'],
                   'п': ['п', 'n', 'p'],
                   'р': ['р', 'r', 'p'],
                   'с': ['с', 'c', 's'],
                   'т': ['т', 'm', 't'],
                   'у': ['у', 'y', 'u'],
                   'ф': ['ф', 'f'],
                   'х': ['х', 'x', 'h', '}{'],
                   'ц': ['ц', 'c', 'u,'],
                   'ч': ['ч', 'ch'],
                   'ш': ['ш', 'sh'],
                   'щ': ['щ', 'sch'],
                   'ь': ['ь', 'b'],
                   'ы': ['ы', 'bi'],
                   'ъ': ['ъ'],
                   'э': ['э', 'e'],
                   'ю': ['ю', 'io'],
                   'я': ['я', 'ya']
                   }


VK_API_TOKEN: str
WA_TOKEN: str
GROUP: int
ADMINS: tuple
PEERS = [2000000001, 2000000002]
COMING_DEADLINES = dict()
COMMAND_QUEUE = Queue()
STICKER_IDS = {'/ogre': '457239022', '/bebrou': '457239023', '/bigbrain': '457239024', '/sleeping': '457239025',
               '/xd': '457239026', '/fire': '457239027', '/walrus': '457239028', '/bruh': '457239029',
               '/based': '457239030', '/vsempoh': '457239031', '/starosta1': '457239037',
               '/starosta2': '457239032', '/char': '457239033', '/genius': '457239034', '/pickle': '457239035',
               '/vlad': '457239036', '/ryan': '457239038', '/noname': '457239039'}
ARG_COMMANDS = ["/add_deadline", "/remove_deadline", "/wolfram", "/brainfuck"]
EXIT = False

with open("TOKEN.json", 'r') as file:
    VK_API_TOKEN = json.load(file)
with open("WA_TOKEN.json", 'r') as file:
    WA_TOKEN = json.load(file)
with open("GROUP.json", 'r') as file:
    GROUP = json.load(file)
with open("ADMINS.json", 'r') as file:
    ADMINS = json.load(file)
wolfram = wolframalpha.Client(WA_TOKEN)

api = vk.API(access_token=VK_API_TOKEN, v='5.95')

long_poll = api.groups.getLongPollServer(group_id=GROUP)
server, key, ts = long_poll['server'], long_poll['key'], long_poll['ts']


def swear_check(message):
    PATTERN_1 = r''.join((
        r'\w{0,5}[хx]([хx\s\!@#\$%\^&*+-\|\/]{0,6})',
        r'[уy]([уy\s\!@#\$%\^&*+-\|\/]{0,6})[ёiлeеюийя]\w{0,7}|\w{0,6}[пp]',
        r'([пp\s\!@#\$%\^&*+-\|\/]{0,6})[iие]([iие\s\!@#\$%\^&*+-\|\/]{0,6})',
        r'[3зс]([3зс\s\!@#\$%\^&*+-\|\/]{0,6})[дd]\w{0,10}|[сcs][уy]',
        r'([уy\!@#\$%\^&*+-\|\/]{0,6})[4чkк]\w{1,3}|\w{0,4}[bб]',
        r'([bб\s\!@#\$%\^&*+-\|\/]{0,6})[lл]([lл\s\!@#\$%\^&*+-\|\/]{0,6})',
        r'[yя]\w{0,10}|\w{0,8}[её][bб][лске@eыиаa][наи@йвл]\w{0,8}|\w{0,4}[еe]',
        r'([еe\s\!@#\$%\^&*+-\|\/]{0,6})[бb]([бb\s\!@#\$%\^&*+-\|\/]{0,6})',
        r'[uу]([uу\s\!@#\$%\^&*+-\|\/]{0,6})[н4ч]\w{0,4}|\w{0,4}[еeё]',
        r'([еeё\s\!@#\$%\^&*+-\|\/]{0,6})[бb]([бb\s\!@#\$%\^&*+-\|\/]{0,6})',
        r'[нn]([нn\s\!@#\$%\^&*+-\|\/]{0,6})[уy]\w{0,4}|\w{0,4}[еe]',
        r'([еe\s\!@#\$%\^&*+-\|\/]{0,6})[бb]([бb\s\!@#\$%\^&*+-\|\/]{0,6})',
        r'[оoаa@]([оoаa@\s\!@#\$%\^&*+-\|\/]{0,6})[тnнt]\w{0,4}|\w{0,10}[ё]',
        r'([ё\!@#\$%\^&*+-\|\/]{0,6})[б]\w{0,6}|\w{0,4}[pп]',
        r'([pп\s\!@#\$%\^&*+-\|\/]{0,6})[иeеi]([иeеi\s\!@#\$%\^&*+-\|\/]{0,6})',
        r'[дd]([дd\s\!@#\$%\^&*+-\|\/]{0,6})[oоаa@еeиi]',
        r'([oоаa@еeиi\s\!@#\$%\^&*+-\|\/]{0,6})[рr]\w{0,12}',
    ))

    PATTERN_2 = r'|'.join((
        r"(\b[сs]{1}[сsц]{0,1}[uуy](?:[ч4]{0,1}[иаakк][^ц])\w*\b)",
        r"(\b(?!пло|стра|[тл]и)(\w(?!(у|пло)))*[хx][уy](й|йа|[еeё]|и|я|ли|ю)(?!га)\w*\b)",
        r"(\b(п[oо]|[нз][аa])*[хx][eе][рp]\w*\b)",
        r"(\b[мm][уy][дd]([аa][кk]|[oо]|и)\w*\b)",
        r"(\b\w*д[рp](?:[oо][ч4]|[аa][ч4])(?!л)\w*\b)",
        r"(\b(?!(?:кило)?[тм]ет)(?!смо)[а-яa-z]*(?<!с)т[рp][аa][хx]\w*\b)",
        r"(\b[к|k][аaoо][з3z]+[eе]?ё?л\w*\b)",
        r"(\b(?!со)\w*п[еeё]р[нд](и|иc|ы|у|н|е|ы)\w*\b)",
        r"(\b\w*[бп][ссз]д\w+\b)",
        r"(\b([нnп][аa]?[оo]?[xх])\b)",
        r"(\b([аa]?[оo]?[нnпбз][аa]?[оo]?)?([cс][pр][аa][^зжбсвм])\w*\b)",
        r"(\b\w*([оo]т|вы|[рp]и|[оo]|и|[уy]){0,1}([пnрp][iиеeё]{0,1}[3zзсcs][дd])\w*\b)",
        r"(\b(вы)?у?[еeё]?би?ля[дт]?[юоo]?\w*\b)",
        r"(\b(?!вело|ски|эн)\w*[пpp][eеиi][дd][oaоаеeирp](?![цянгюсмйчв])[рp]?(?![лт])\w*\b)",
        r"(\b(?!в?[ст]{1,2}еб)(?:(?:в?[сcз3о][тяaа]?[ьъ]?|вы|п[рp][иоo]|[уy]|р[aа][з3z][ьъ]?|к[оo]н[оo])?[её]б[а-яa-z]*)|(?:[а-яa-z]*[^хлрдв][еeё]б)\b)",
        r"(\b[з3z][аaоo]л[уy]п[аaeеин]\w*\b)",
    ))

    regexp = re.compile(PATTERN_1, re.U | re.I)

    text = message['text'].lower().replace(" ", "")
    for key, value in similar_letters.items():
        for letter in value:
            for phr in text:
                if letter == phr:
                    text = text.replace(phr, key)
    return bool(regexp.findall(text))


def start_message(message):
    start_messages = ["Я пришел с миром!", "Какие люди и без охраны!",
                      "Сколько лет, сколько зим!", "Отличное выглядишь!", "Салют!", "Мы знакомы?",
                      "Здравствуйте, товарищи!",
                      "Как настроение?", "Не верю своим глазам! Ты ли это?", "Гоп-стоп, мы подошли из-за угла.",
                      "Мне кажется или я где-то вас видел?", "Какие планы на вечер?", "Привет, чуваки!",
                      "Какие люди нарисовались!"]
    message_text = random.choice(start_messages)

    api.messages.send(peer_id=message['peer_id'],
                      random_id=random.randint(1, 2 ** 31),
                      message=message_text)


def help_message(message):
    api.messages.send(peer_id=message['peer_id'],
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
/wolfram <запрос> - запрос сервису Wolfram|Alpha
/brainfuck <код> [<ввод>] - выполнить код на Brainfuck. А почему бы и да?
Дата и время в формате ДД.ММ.ГГГГ_ЧЧ:ММ:СС""")


def sticker_list(message):
    text = ''
    for sticker in STICKER_IDS:
        text += sticker + ', '
    text = text.rstrip(', ')
    api.messages.send(peer_id=message['peer_id'],
                      random_id=random.randint(1, 2 ** 31),
                      message=text)


def send_sticker(message):
    attach = 'photo-217867161_'
    attach += STICKER_IDS[message['text']]
    api.messages.send(peer_id=message['peer_id'],
                      random_id=random.randint(1, 2 ** 31),
                      attachment=attach)


def gelich_message(message):
    api.messages.send(peer_id=message['peer_id'],
                      random_id=random.randint(1, 2 ** 31),
                      attachment='wall-217867161_3')


def spin_message(message):
    api.messages.send(peer_id=message['peer_id'],
                      random_id=random.randint(1, 2 ** 31),
                      attachment='wall-217867161_1')


def up4k_message(message):
    api.messages.send(peer_id=message['peer_id'],
                      random_id=random.randint(1, 2 ** 31),
                      attachment='wall-217867161_4')


def poh_message(message):
    api.messages.send(peer_id=message['peer_id'],
                      random_id=random.randint(1, 2 ** 31),
                      attachment=random.choice(
                          ['photo-217867161_457239017', 'photo-217867161_457239018', 'photo-217867161_457239019']))


def deadlines_message(message):
    text = ""
    with open("deadlines.json", "r") as fin:
        data = json.load(fin)
        if len(data) != 0:
            for subj in data:
                text += str(subj) + ' - ' + data[subj] + '\n'
        else:
            text = "Пока дедлайнов нет!"
    api.messages.send(peer_id=message['peer_id'],
                      random_id=random.randint(1, 2 ** 31),
                      message=text)


def add_deadline(message):
    try:
        fin = open("deadlines.json", "r")
        data = json.load(fin)
        if len(data) == 0:
            data = {'': ''}
        fin.close()
        new_deadline = message['text'].split(" ", maxsplit=1)[1].split(' - ')
        subj = new_deadline[0]
        time = datetime.datetime.strptime(new_deadline[1], '%d.%m.%Y_%H:%M:%S')
        data[subj] = time.strftime('%d.%m.%Y_%H:%M:%S')
        data.pop('')
        with open("deadlines.json", "w") as fout:
            json.dump(data, fout)
        api.messages.send(peer_id=message['peer_id'],
                          random_id=random.randint(1, 2 ** 31),
                          message="Добавил")
    except Exception as e:
        api.messages.send(peer_id=message['peer_id'],
                          random_id=random.randint(1, 2 ** 31),
                          message="Ошибка: " + str(e))


def rem_deadline(message):
    try:
        fin = open("deadlines.json", "r")
        data = json.load(fin)
        if len(data) == 0:
            api.messages.send(peer_id=message['peer_id'],
                              random_id=random.randint(1, 2 ** 31),
                              message="Ошибка: Дедлайнов нет")
            return
        fin.close()
        deadline = message['text'].split(" ", maxsplit=1)[1]
        data.pop(deadline)
        with open("deadlines.json", "w") as fout:
            json.dump(data, fout)
        api.messages.send(peer_id=message['peer_id'],
                          random_id=random.randint(1, 2 ** 31),
                          message="Удалил")
    except Exception as e:
        api.messages.send(peer_id=message['peer_id'],
                          random_id=random.randint(1, 2 ** 31),
                          message="Ошибка: " + str(e))


def notadmin_message(message):
    name = api.users.get(user_id=message['from_id'])
    name = name[0]
    name = name['first_name']
    api.messages.send(peer_id=message['peer_id'],
                      random_id=random.randint(1, 2 ** 31),
                      message=name + " is an impostor")


def nothing_message(message):
    api.messages.send(peer_id=message['peer_id'],
                      random_id=random.randint(1, 2 ** 31),
                      message='&#13;')


def source_message(message):
    api.messages.send(peer_id=message['peer_id'],
                      random_id=random.randint(1, 2 ** 31),
                      message='https://github.com/Andrien777/VKBot/')


def get_bash_quote():
    web = requests.get('https://башорг.рф/rss/')
    soup = bs4.BeautifulSoup(web.text, 'xml')
    results = soup.find_all(name='item')
    return html.unescape(
        random.choice(results).description.text.replace('&lt;', '<').replace('&rt;', '>').replace("<br>", '\n'))


def quote_message(message):
    api.messages.send(peer_id=message['peer_id'],
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


def wolfram_message(message):
    question = message['text'].split(' ', maxsplit=1)[1]
    res = wolfram.query(question)
    text = next(res.results).text
    api.messages.send(peer_id=message['peer_id'],
                      random_id=random.randint(1, 2 ** 31),
                      message=text)


def brainfuck_parser(code, input=''):
    tape = [0] * 30000
    pos = 0
    height = 0
    input_index = 0
    output = ''
    for char in code:
        if char == '[':
            height += 1
        elif char == ']':
            height -= 1
        if height < 0:
            raise SyntaxError("Invalid bracket placement")
    if height != 0:
        raise SyntaxError("Unclosed brackets")
    timer = time.time()
    code_index = 0
    while code_index < len(code):
        if code[code_index] == '+':
            tape[pos] += 1
            tape[pos] %= 256
        elif code[code_index] == '-':
            tape[pos] -= 1
            tape[pos] %= 256
        elif code[code_index] == '>':
            pos += 1
            pos %= 30000
        elif code[code_index] == '<':
            pos -= 1
            pos %= 30000
        elif code[code_index] == '.':
            output += chr(tape[pos])
        elif code[code_index] == ',':
            tape[pos] = ord(input[input_index])
            input_index += 1
        elif code[code_index] == '[':
            if tape[pos] == 0:
                height += 1
                while height != 0:
                    code_index += 1
                    if code[code_index] == '[':
                        height += 1
                    elif code[code_index] == ']':
                        height -= 1
        elif code[code_index] == ']':
            if tape[pos] != 0:
                height += 1
                while height != 0:
                    code_index -= 1
                    if code[code_index] == '[':
                        height -= 1
                    elif code[code_index] == ']':
                        height += 1
        code_index += 1
        if time.time() - timer > 20:
            raise TimeoutError(output)
    return output


def brainfuck_message(message):
    args = message['text'].split(' ', maxsplit=2)
    code = args[1]
    out: str
    text: str
    try:
        if len(args) > 2:
            out = brainfuck_parser(code, args[2])
        else:
            out = brainfuck_parser(code)
        text = f"Output: {out}"
    except TimeoutError as e:
        text = f"Output: {e.args}\nException: TimeoutError()"
    except BaseException as e:
        text = f"Exception: {e.__class__}"
    api.messages.send(peer_id=message['peer_id'],
                      random_id=random.randint(1, 2 ** 31),
                      message=text)


COMMANDS = {"/start": start_message, "/help": help_message, "/spin": spin_message, "/gelich": gelich_message, "/pohuy": poh_message,
            "/deadlines": deadlines_message, "/nothing": nothing_message, "/upya4ka": up4k_message, "/sourcecode": source_message,
            "/bash": quote_message, "/stickers": sticker_list}


def bg_deadlines_check():
    while True:
        check_deadlines()
        time.sleep(60)
        if EXIT:
            break


def message_parser(message):
    if message['text'] in COMMANDS:
        COMMANDS[message['text']](message)
    elif message['text'] in STICKER_IDS:
        send_sticker(message)
    elif message['text'].startswith('/add_deadline '):
        add_deadline(message) if message['from_id'] in ADMINS else notadmin_message(
            message)
    elif message['text'].startswith('/remove_deadline '):
        rem_deadline(message) if message['from_id'] in ADMINS else notadmin_message(
            message)
    elif message['text'].startswith('/wolfram '):
        wolfram_message(message)
    elif message['text'].startswith('/brainfuck '):
        brainfuck_message(message)


def message_sink():
    while True:
        if not COMMAND_QUEUE.empty():
            message_parser(COMMAND_QUEUE.get())
        if EXIT:
            break


deadline_thread = threading.Thread(target=bg_deadlines_check)
deadline_thread.start()

message_thread = threading.Thread(target=message_sink)
message_thread.start()


while True:
    try:
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
                        if update['object']['text'] in STICKER_IDS or \
                                update['object']['text'] in COMMANDS or \
                                any(update['object']['text'].startswith(i) for i in ARG_COMMANDS):
                            COMMAND_QUEUE.put(update['object'])
                        if swear_check(update['object']):
                            api.messages.send(peer_id=update['object']['peer_id'],
                                              random_id=random.randint(1, 2 ** 31),
                                              message="Не материться!")

        except KeyError:
            api = vk.API(access_token=VK_API_TOKEN, v='5.95')
            long_poll = api.groups.getLongPollServer(group_id=GROUP)
            server, key, ts = long_poll['server'], long_poll['key'], long_poll['ts']
            continue
        for deadline in COMING_DEADLINES:
            inform_deadline(deadline, COMING_DEADLINES[deadline])
        COMING_DEADLINES.clear()
        ts = long_poll['ts']
    except BaseException:
        EXIT = True
        deadline_thread.join()
        message_thread.join()
        while deadline_thread.is_alive() or message_thread.is_alive():
            continue
        api.session.close()
        break
