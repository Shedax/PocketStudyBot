import telebot
import random
import datetime
from telebot import types
from config import *

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat .id, 'Привет, {0.first_name}! ✋\nДобро пожаловать на платформу для дистанционного обучения'
                                       ' <b>{1.first_name}</b>!'.format(message.from_user, bot.get_me()), parse_mode='html')
    bot.send_message(message.chat.id, 'Прежде всего, давай авторизуем тебя в системе!\n ')
    mes = bot.send_message(message.chat.id, 'Введи 8-значный пароль, выданный для авторизации.')
    bot.register_next_step_handler(mes, validation)

def validation(message):
    keyboard = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton(text='Перейти в личный кабинет', callback_data='home')
    keyboard.add(btn)
    database = DB('users.db')
    students = database.get_codes('students')
    teachers = database.get_codes('teachers')
    admins = database.get_admins()
    admin_list = []
    for i in range(len(admins)):
        admin_list.append(admins[i][3])
    if message.text in students and message.text in teachers:
        bot.send_message(message.chat.id, 'Обнаружен одинаковый код в базе данных преподавателей и учеников, обратитесь к администратору.')
    else:
        if message.text in students:
            database.insert_value('Статус', 'Авторизован', message.text, 'students')
            database.insert_value('chat_id', message.chat.id, message.text, 'students')
            full_name = database.get_student_fio('chat_id',message.chat.id)[0]
            name = full_name[full_name.find(" ")+1:]
            bot.send_message(message.chat.id, 'Вы авторизованы, {0}!'.format(name), reply_markup=keyboard)
        elif message.text in teachers:
            database.insert_value('Статус', 'Авторизован', message.text, 'teachers')
            database.insert_value('chat_id', message.chat.id, message.text, 'teachers')
            full_name = database.get_teacher_fio(message.chat.id)[0]
            name = full_name[full_name.find(" ")+1:]
            bot.send_message(message.chat.id, 'Вы авторизованы, {0}!'.format(name), reply_markup=keyboard)
        elif message.text in admin_list:
            bot.send_message(message.chat.id, 'Вы авторизованы, администратор!', reply_markup=keyboard)
        else:
            if len(message.text)!=8:
                mes = bot.send_message(message.chat.id, 'Ошибка авторизации. Пароль должен состоять из 8 символов.')
            else:
                mes = bot.send_message(message.chat.id, 'Ошибка авторизации. Введён неверный пароль.')
            bot.register_next_step_handler(mes, validation)
    database.close()

@bot.message_handler(commands=['home'])
def home(message):
    student = False
    admin = False
    database = DB('users.db')
    keyboard = types.InlineKeyboardMarkup()
    mes = '<b>ЛИЧНЫЕ ДАННЫЕ</b>'
    user_info = database.get_user_info('teachers', message.chat.id)
    if user_info is None:
        user_info = database.get_user_info('students', message.chat.id)
        if user_info is None:
            admin = True
        else:
            student = True
    if student is True and admin is False:
        n=5
        mes += ' <b>СТУДЕНТА</b>\n'
        btn1 = types.InlineKeyboardButton(text='Успеваемость', callback_data='statistic')
        btn2 = types.InlineKeyboardButton(text='Текущие задания', callback_data='tasks')
        btn3 = types.InlineKeyboardButton(text='Связаться с преподавателем', callback_data='teacher_con')
        btn4 = types.InlineKeyboardButton(text='Связаться с администрацией', callback_data='admin_con')
        btn5 = types.InlineKeyboardButton(text='Материалы', callback_data='material')
        courses = database.get_curses('Группы', user_info[6])
        pos = 0
        group = user_info[6]
        if ',' in group:
            z = group.split(', ')
            pos = z.index(group)
        text = '\n<b>Предметы</b>\n'
        for i in range(len(courses)):
            text+= courses[i][1] + ' - ' + courses[i][3].split(', ')[pos] + '\n'
        keyboard.add(btn5, btn2)
        keyboard.add(btn1)
        keyboard.add(btn3)
        keyboard.add(btn4)
    elif student is False and admin is False:
        n=4
        mes += ' <b>ПРЕПОДАВАТЕЛЯ</b>\n'
        btn1 = types.InlineKeyboardButton(text='Отправить материал', callback_data='send_material')
        btn2 = types.InlineKeyboardButton(text='Задания, ожидающие проверки', callback_data='tasks_2')
        btn3 = types.InlineKeyboardButton(text='Связаться со студентами', callback_data='student_con')
        btn4 = types.InlineKeyboardButton(text='Связаться с администрацией', callback_data='admin_con')
        keyboard.add(btn1)
        keyboard.add(btn2)
        keyboard.add(btn3)
        keyboard.add(btn4)
        courses = database.get_curses('Преподаватель', user_info[3])
        text = 'Вы ведёте следующие предметы: \n'
        for i in range(len(courses)):
            text+= courses[i][1] + ' - ' + courses[i][2] + '\n'
    if admin is True:
        btn1 = types.InlineKeyboardButton(text='Статистика', callback_data='admin_stat')
        btn2 = types.InlineKeyboardButton(text='Обратная связь', callback_data='user_con')
        keyboard.add(btn1)
        keyboard.add(btn2)
        bot.send_message(message.chat.id, 'Главное меню', reply_markup=keyboard)
    else:
        for i in range(len(user_info)-n):
            if student is True:
                if i == 1:
                    mes += '<b>Уровень подготовки</b>: '
                elif i == 2:
                    mes += '<b>Факультет</b>: '
                elif i == 3:
                    mes += '<b>Группа</b>: '
                elif i == 4:
                    mes += '<b>№ Зачетной книжки</b>: '
                elif i == 5:
                    mes += '<b>Дата рождения</b>: '
            else:
                if i == 1:
                    mes += '<b>Учёная степень</b>: '
                elif i == 2:
                    mes += '<b>Учёное звание</b>: '
                elif i == 3:
                    mes += '<b>Стаж работы</b>: '
                elif i == 4:
                    mes += '<b>Дата рождения</b>: '
            mes += str(user_info[i+3]) + '\n'
        mes += text
        bot.send_message(message.chat.id, mes, parse_mode='html', reply_markup=keyboard)
        database.close()

def pick_lesson(message):
    keyboard = types.ReplyKeyboardMarkup(True, True)
    database = DB('users.db')
    teacher = database.get_teacher_fio(message.chat.id)
    courses = database.get_curses('Преподаватель', teacher[0])
    for i in range(len(courses)):
        keyboard.row(courses[i][1])
    keyboard.row('Назад')
    mes = bot.send_message(message.chat.id, 'Выберите предмет, по которому собираетесь отправить материал.', reply_markup=keyboard)
    bot.register_next_step_handler(mes, current_lesson)
    database.close()

def current_lesson(message):
    func = funcs(message)
    if func == 2:
        database = DB('users.db')
        teacher = database.get_teacher_fio(message.chat.id)
        courses = database.get_curses('Преподаватель', teacher[0])
        lessons = []
        for i in range(len(courses)):
            lessons.append(courses[i][1])
        if message.text not in lessons and message.text != 'Назад':
            mes=bot.send_message(message.chat.id, 'Ошибка в названии предмета. Укажите название повторно.')
            bot.register_next_step_handler(mes, current_lesson)
        else:
            if message.text != 'Назад':
                send(message, None, message.text)
            else:
                home(message)

def send(message, current_groups, lesson):
    func = funcs(message)
    if func == 2:
        keyboard = types.ReplyKeyboardMarkup(True, True)
        database = DB('users.db')
        courses = database.get_curses('Предмет', lesson)
        groups = []
        for i in range(len(courses)):
            if ',' in courses[i][2]:
                for j in range(len(courses[i][2].split(', '))):
                    groups.append(courses[i][2].split(', ')[j])
            else:
                groups.append(courses[i][2])
        if current_groups is not None:
            for i in range(len(current_groups.split(', '))):
                try:
                    groups.remove(current_groups.split(', ')[i])
                except ValueError:
                    pass
            for i in range(len(groups)):
                keyboard.row(current_groups + ', ' + groups[i])
        else:
            for i in range(len(groups)):
                keyboard.row(groups[i])
        keyboard.row('Выбрать всё')
        database.close()
        mes = bot.send_message(message.chat.id, 'Укажите группы, которым вы хотите отправить материал.', reply_markup=keyboard)
        bot.register_next_step_handler(mes, current_gr, lesson)

def current_gr(message, lesson):
    func = funcs(message)
    if func == 2:
        database = DB('users.db')
        courses = database.get_curses('Предмет', lesson)
        groups = []
        for i in range(len(courses)):
            if ',' in courses[i][2]:
                for j in range(len(courses[i][2].split(', '))):
                    groups.append(courses[i][2].split(', ')[j])
            else:
                groups.append(courses[i][2])
        if message.text != 'Назад' and message.text != 'Выбрать всё':
            a = 0
            for i in groups:
                if i not in message.text:
                    a+=1
            if a == len(groups):
                mes=bot.send_message(message.chat.id, 'Ошибка в названии группы. Укажите название повторно.')
                bot.register_next_step_handler(mes, current_gr, lesson)
            else:
                send2(message, lesson, None)
        else:
            if message.text != 'Назад':
                send2(message, lesson, None)
            else:
                home(message)

def send2(message, lesson, grs):
    database = DB('users.db')
    courses = database.get_curses('Предмет', lesson)
    groups = []
    for i in range(len(courses)):
        if ',' in courses[i][2]:
            for j in range(len(courses[i][2].split(', '))):
                groups.append(courses[i][2].split(', ')[j])
        else:
            groups.append(courses[i][2])
    if message.text == 'Выбрать всё':
        text = ', '.join(groups)
    else:
        if grs is None:
            text = message.text
        else:
            text = grs
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text='Перейти к следующему шагу',
                                      callback_data='send_next_{0}_{1}'.format(text, lesson[:5]))
    btn3 = types.InlineKeyboardButton(text='Назад', callback_data='send_material')
    btn4 = types.InlineKeyboardButton(text='Вернуться в личный кабинет', callback_data='home')
    markup.add(btn1)
    if set(text.split(', ')) != set(groups):
        btn2 = types.InlineKeyboardButton(text='Выбрать ещё одну группу',
                                          callback_data='a_a_{0}'.format(lesson[:10]))
        markup.add(btn2)
    markup.add(btn3)
    markup.add(btn4)
    bot.send_message(message.chat.id, 'Предмет: ' + courses[0][1] + '\nГруппы для отправки: ' + text,
                     reply_markup=markup)
    database.close()

def sending_info(message, groups , lesson):
    keyb = types.ReplyKeyboardMarkup(True, True)
    btn1 = 'Назад'
    keyb.row('Теоретический материал')
    keyb.row('Практический материал')
    keyb.row(btn1)
    mes = bot.send_message(message.chat.id, 'Вы собираетесь отправить практический материал или теоретический?', reply_markup=keyb)
    bot.register_next_step_handler(mes, mat_type, groups, lesson, 1)

def mat_type(message, groups, lesson, var):
    func = funcs(message)
    if func == 2:
        if message.text != 'Назад':
            if message.text != 'Практический материал' and message.text != 'Теоретический материал' and var !=2:
                mes = bot.send_message(message.chat.id, 'Ошибка, укажите корректно тип отправляемого материала.')
                bot.register_next_step_handler(mes, mat_type, groups, lesson, var)
            else:
                keyb = types.ReplyKeyboardMarkup(True, True)
                btn1 = 'Назад'
                keyb.row(btn1)
                if var == 1:
                    mes = bot.send_message(message.chat.id, 'Теперь отправьте материал. \nЕсли материал практический, то описание к файлу оформляется следующим образом:\n'
                                                            '<b>Название работы</b> + <b>№ работы</b> + <b>дата сдачи работы</b> в формате дд.мм.гг.', reply_markup=keyb, parse_mode='html')
                    bot.send_message(message.chat.id, 'Пример 1:\nЛабораторная работа №1, сдать до 25.05.2021\n'
                                                      'Пример 2:\nПрактическая работа №3, дата сдачи 11.03.2021')
                elif var == 2:
                    mes = bot.send_message(message.chat.id,
                                           'Отправьте сообщение группам '+ groups, reply_markup=keyb)
                bot.register_next_step_handler(mes, final_send, groups, lesson, message.text, var)
        else:
            send2(message, lesson, groups)

def final_send(message, groups, lesson, type, var):
    func = funcs(message)
    if func == 2:
        if var == 1 and  message.content_type != 'document' and message.content_type != 'video' and message.content_type != 'photo' and message.text != 'Назад':
            mes = bot.send_message(message.chat.id, 'Некорректный формат файла. Ожидается повторная отправка.')
            bot.register_next_step_handler(mes, final_send, groups, lesson, type, var)
        else:
            if message.text != 'Назад':
                markup = types.InlineKeyboardMarkup()
                btn = types.InlineKeyboardButton(text='Отправить сообщение данным группам', callback_data='sendmes_{0}_{1}'.format(groups, lesson[:5]))
                btn2 = types.InlineKeyboardButton(text='Отправить ещё один файл', callback_data='send_more_{0}_{1}'.format(groups, lesson[:5]))
                btn3 = types.InlineKeyboardButton(text='Вернуться в личный кабинет', callback_data='home')
                markup.add(btn)
                markup.add(btn2)
                markup.add(btn3)
                database = DB('users.db')
                gr_list = []
                chat_ids = []
                les = database.get_curses('Предмет', lesson)[0][1]
                if ', ' in groups:
                    gr_list = groups.split(', ')
                else:
                    gr_list.append(groups)
                for i in range(len(gr_list)):
                    chat_ids+=(database.get_student_ids('Авторизован', gr_list[i]))
                if len(chat_ids)!= 0:
                    for i in range(len(chat_ids)):
                        current_id = chat_ids[i]
                        #Если нет пользователей в выбранной группе
                        if current_id is not None:
                            if 'Практический' in type:
                                if message.caption is None:
                                    mes = bot.send_message(message.chat.id,'Отсутствует описание файла! Отправьте повторно '
                                                                           'файл и укажите название и номер работы, а также дату сдачи.')
                                    bot.register_next_step_handler(mes, final_send, groups, lesson, type, var)
                                else:
                                    text = message.caption.split()
                                    iterator = 0
                                    for b in range(len(text)):
                                        try:
                                            if datetime.datetime.strptime(text[b], "%d.%m.%Y"):
                                                iterator = b
                                        except:
                                            pass
                                    if iterator == 0:
                                        mes = bot.send_message(message.chat.id, 'Неверно указан формат времени! Отправьте повторно файл и укажите корректно дату.')
                                        bot.register_next_step_handler(mes, final_send, groups, lesson, type, var)
                                    else:
                                        bot.send_message(current_id[0], 'Поступило новое задание по предмету\n' + '<b>'+les+'</b>' + '.', parse_mode='html')
                                        bot.forward_message(current_id[0], message.chat.id, message.id)
                                        bot.send_message(message.chat.id, 'Материал успешно отправлен!\n', reply_markup=markup)
                                        if message.content_type == 'document':
                                            if message.document.file_name.endswith(
                                                    '.jpg') or message.document.file_name.endswith(
                                                    '.png') or message.document.file_name.endswith('.jpeg'):
                                                mes = bot.send_message(message.chat.id,
                                                                       'При отправке фотографий необходимо нажать на галочку напротив пункта "Сжать изображения"')
                                                bot.register_next_step_handler(mes, final_send, groups, lesson, type, var)
                                            else:
                                                database.new_material(les, type, message.document.file_name.split('.')[0], groups, message.id, message.chat.id, message.document.file_id, 'document')
                                        elif message.content_type == 'photo':
                                            capt = message.caption +'\n(изображение)'
                                            database.new_material(les, type, capt, groups, message.id,
                                                                  message.chat.id, message.photo[2].file_id, 'photo')
                                        elif message.content_type == 'video':
                                            capt = message.video.file_name.split('.')[0] + '\n(видео)'
                                            database.new_material(les, type, capt, groups, message.id,
                                                                  message.chat.id, message.video.file_id, 'video')
                            elif 'Теоретический' in type:
                                if message.content_type != 'document':
                                    bot.send_message(current_id[0],
                                                     'Поступил новый материал по предмету\n' + '<b>' + les + '</b>' + '.',
                                                     parse_mode='html')
                                    bot.forward_message(current_id[0], message.chat.id, message.id)
                                    bot.send_message(message.chat.id, 'Материал успешно отправлен!\n', reply_markup=markup)
                                if message.content_type == 'document':
                                    if message.document.file_name.endswith('.jpg') or message.document.file_name.endswith('.png') or message.document.file_name.endswith('.jpeg'):
                                        mes = bot.send_message(message.chat.id, 'При отправке фотографий необходимо нажать на галочку напротив пункта "Сжать изображения"!')
                                        bot.register_next_step_handler(mes, final_send, groups, lesson, type, var )
                                    else:
                                        database.new_material(les, type, message.document.file_name.split('.')[0], groups, message.id, message.chat.id, message.document.file_id, 'document')
                                        bot.send_message(current_id[0],
                                                         'Поступил новый материал по предмету\n' + '<b>' + les + '</b>' + '.',
                                                         parse_mode='html')
                                        bot.forward_message(current_id[0], message.chat.id, message.id)
                                        bot.send_message(message.chat.id, 'Материал успешно отправлен!\n',
                                                         reply_markup=markup)
                                elif message.content_type == 'photo':
                                    if message.caption is None:
                                        mes = bot.send_message(message.chat.id,
                                                               'При отправке изображений необходимо указывать их описание!')
                                        bot.register_next_step_handler(mes, final_send, groups, lesson, type, var)
                                    else:
                                        capt = message.caption + '\n(изображение)'
                                        database.new_material(les, type, capt, groups, message.id,
                                                              message.chat.id, message.photo[2].file_id, 'photo')
                                elif message.content_type == 'video':
                                    capt = message.json['video']['file_name'].split('.')[0] + '\n(видео)'
                                    database.new_material(les, type, capt, groups, message.id,
                                                          message.chat.id, message.video.file_id, 'video')
                            else:
                                bot.send_message(current_id[0],
                                                 'Пришло сообщение от преподавателя по поводу предмета\n' + '<b>' + les + '</b>' + '.',
                                                 parse_mode='html')
                                bot.forward_message(current_id[0], message.chat.id, message.id)
                                bot.send_message(message.chat.id, 'Сообщение успешно отправлено!\n',reply_markup=markup)
                database.close()
            else:
                send2(message, lesson, groups)

def student_con(message):
    keyboard = types.ReplyKeyboardMarkup(True, True)
    keyboard.row('Связаться с группой', 'Связаться с конкретным учеником')
    keyboard.row('Назад')
    mes = bot.send_message(message.chat.id, 'Вы хотите связаться с группой или с конкретным учеником?', reply_markup=keyboard)
    bot.register_next_step_handler(mes, con_choice)

def con_choice(message):
    func = funcs(message)
    if func == 2:
        keyb = types.ReplyKeyboardMarkup(True, True)
        keyb.add('Назад')
        if message.text == 'Связаться с группой':
            mes = bot.send_message(message.chat.id, 'Напишите, какой группе вы хотите отправить сообщение.\nЕсли групп несколько, то укажите их через запятую.', reply_markup=keyb)
            bot.register_next_step_handler(mes, group_choice, 1)
        elif message.text == 'Связаться с конкретным учеником':
            mes = bot.send_message(message.chat.id, 'Напишите, студенту какой группы вы хотите отправить сообщение.', reply_markup=keyb)
            bot.register_next_step_handler(mes, group_choice, 2)
        elif message.text == 'Назад':
            home(message)
        else:
            mes = bot.send_message(message.chat.id, 'Некорректный выбор, ожидается повторный ввод информации.')
            bot.register_next_step_handler(mes, student_con)

def group_choice(message, var):
    func = funcs(message)
    if func == 2:
        if message.text != 'Назад':
            keyb = types.ReplyKeyboardMarkup(True, True)
            keyb.add('Назад')
            database = DB('users.db')
            groups = database.get_groups()
            gr_split = message.text.split(',')
            gr_split2 = message.text.split(', ')
            if gr_split[0] in groups:
                if var == 1:
                    a = 0
                    for i in range(len(gr_split)):
                        if gr_split[i] not in groups and gr_split2[i] not in groups:
                            a+=1
                    if a != 0:
                        mes = bot.send_message(message.chat.id,
                                               'Ошибка в названии группы, напишите название корректно.')
                        bot.register_next_step_handler(mes, group_choice, var)
                    else:
                        if len(gr_split) == 2:
                            mes = bot.send_message(message.chat.id, 'Напишите сообщение, которое хотите отправить группе ' + message.text+ '.', reply_markup=keyb)
                        else:
                            mes = bot.send_message(message.chat.id,
                                                   'Напишите сообщение, которое хотите отправить группам ' + message.text + '.',reply_markup=keyb)
                        bot.register_next_step_handler(mes, send_to_group, message.text)
                elif var == 2:
                    if message.text in groups:
                        stud_list=database.get_student_fio('Группа', message.text)
                        text = '<b>Список группы ' + message.text + '</b>\n'
                        for i in range(len(stud_list)):
                            text+=stud_list[i] + '\n'
                        bot.send_message(message.chat.id, text, parse_mode='html')
                        mes = bot.send_message(message.chat.id, 'Напишите фамилию и имя ученика, с которым хотите связаться.',reply_markup=keyb)
                        bot.register_next_step_handler(mes, student_choice)
                    else:
                        mes = bot.send_message(message.chat.id, 'Ошибка в названии группы, напишите название корректно.')
                        bot.register_next_step_handler(mes, group_choice, var)
            else:
                mes = bot.send_message(message.chat.id, 'Ошибка в названии группы, напишите название корректно.')
                bot.register_next_step_handler(mes, group_choice, var)
            database.close()
        else:
            student_con(message)

def student_choice(message):
    func = funcs(message)
    if func == 2:
        if message.text!= 'Назад':
            database = DB('users.db')
            if len(message.text.split(' ')) != 2:
                mes = bot.send_message(message.chat.id,
                                       'Необходимо указать и имя и фамилию, ожидается повторная отправка ФИО.')
                bot.register_next_step_handler(mes, student_choice)
            else:
                try:
                    id = database.get_id_by_fio('Авторизован', message.text)[0]
                    fio = database.get_student_fio('chat_id', id)[0]
                except:
                    mes = bot.send_message(message.chat.id,
                                           'Некорректно указано имя или фамилия студента, ожидается повторная отправка ФИО.')
                    bot.register_next_step_handler(mes, student_choice)
                else:
                    if message.text.split(' ')[0] not in fio.split(' ') or message.text.split(' ')[1] not in fio.split(' '):
                        mes = bot.send_message(message.chat.id,
                                               'Некорректно указано имя или фамилия студента, ожидается повторная отправка ФИО.')
                        bot.register_next_step_handler(mes, student_choice)
                    else:
                        keyb = types.ReplyKeyboardMarkup(True,True)
                        keyb.add('Назад')
                        mes = bot.send_message(message.chat.id, 'Напишите сообщение, которое хотите отправить.', reply_markup=keyb)
                        bot.register_next_step_handler(mes, send_to_stud, message.text)
            database.close()
        else:
            student_con(message)

def send_to_stud(message, student):
    func = funcs(message)
    if func == 2:
        if message.text != 'Назад':
            database = DB('users.db')
            id = database.get_id_by_fio('Авторизован', student)[0]
            bot.send_message(id, 'Вам пришло личное сообщение от преподавателя!\nЧтобы открыть диалог с преподавателем, нажмите '
                                 'на его имя в пересланном сообщении, после чего нажмите на кнопку  "Отправить сообщение".')
            bot.send_message(message.chat.id, 'Ваше сообщение отправлено!')
            bot.forward_message(id, message.chat.id, message.id)
            database.close()
            home(message)
        else:
            student_con(message)

def send_to_group(message, groups):
    func = funcs(message)
    if func == 2:
        if message.text != 'Назад':
            database = DB('users.db')
            groups_list = []
            if ', ' in groups:
                groups_list += groups.split(', ')
            elif ',' in groups:
                groups_list += groups.split(',')
            else:
                groups_list.append(groups)
            ids = []
            for i in range(len(groups_list)):
                ids += database.get_student_ids('Авторизован', groups_list[i])
            if len(ids) != 0:
                for i in range(len(ids)):
                    current_id = ids[i]
                    # Если нет пользователей в выбранной группе
                    if current_id is not None:
                        bot.send_message(current_id[0], 'Пришло сообщение от преподавателя.')
                        bot.forward_message(current_id[0], message.chat.id, message.id)
                bot.send_message(message.chat.id, 'Ваше сообщение успешно отправлено!')
                home(message)
            database.close()
        else:
            student_con(message)

def grade(message):
    database = DB('users.db')
    gr_tasks = database.grade_tasks(message.chat.id, 0)
    if len(gr_tasks) == 0:
        bot.send_message(message.chat.id, 'У вас нет непроверенных работ!')
    else:
        lessons = []
        for i in range(len(gr_tasks)):
            lessons.append(gr_tasks[i][1])
        les_list = list(set(lessons))
        keyb = types.ReplyKeyboardMarkup(True,True)
        for i in range(len(les_list)):
            keyb.row(les_list[i])
        keyb.row('Назад')
        mes = bot.send_message(message.chat.id, 'Выберите предмет по которому хотите оценить работы.', reply_markup=keyb)
        bot.register_next_step_handler(mes, les_choice, les_list)
    database.close()

def les_choice(message, lessons):
    func = funcs(message)
    if func == 2:
        if message.text != 'Назад':
            database = DB('users.db')
            if message.text not in lessons:
                mes = bot.send_message(message.chat.id, 'Некорректное название предмета, повторно укажите название.')
                bot.register_next_step_handler(mes, les_choice, lessons)
            else:
                gr_tasks = database.grade_tasks(message.chat.id, 0)
                z = []
                for i in range(len(gr_tasks)):
                    z.append(gr_tasks[i][4])
                newz = list(set(z))
                keyb = types.ReplyKeyboardMarkup(True, True)
                for i in range(len(newz)):
                    keyb.row(newz[i])
                keyb.row('Назад')
                mes = bot.send_message(message.chat.id, 'Укажите, работы какой группы вы хотите оценить.', reply_markup=keyb)
                bot.register_next_step_handler(mes, grade_group, message.text, 0, 0, None)
            database.close()
        else:
            home(message)

def grade_group(message, lesson, n, mat, groups):
    func = funcs(message)
    if func == 2:
        if message.text != 'Назад':
            n=int(n)
            database = DB('users.db')
            gr_tasks = database.grade_tasks(message.chat.id, 0)
            z = []
            for i in range(len(gr_tasks)):
                z.append(gr_tasks[i][4])
            newz = list(set(z))
            if mat == 0:
                grs = message.text
            else:
                grs = groups
            if grs not in newz and mat !=1:
                mes = bot.send_message(message.chat.id, 'Некорректное название группы, повторно укажите название.')
                bot.register_next_step_handler(mes, grade_group, lesson, int(n))
            else:
                markup = types.InlineKeyboardMarkup()
                btn2 = types.InlineKeyboardButton(text='Вернуться в личный кабинет', callback_data='home')
                tasklist = database.grade_tasks_2(message.chat.id, grs, lesson, 0)
                if len(tasklist)<=5:
                    for i in range(len(tasklist)):
                        try:
                            mark2 = types.InlineKeyboardMarkup()
                            mark2.add(types.InlineKeyboardButton(text='Оценить работу', callback_data='grade_{0}_{1}_{2}_{3}'.
                                                                 format(tasklist[i][2], lesson[:6], 'doc', tasklist[i][3])))
                            bot.send_document(message.chat.id, tasklist[i][6], caption='Отправитель - '+
                            str(database.get_student_fio('chat_id', tasklist[i][2])[0]), reply_markup=mark2)
                        except:
                            mark2 = types.InlineKeyboardMarkup()
                            mark2.add(types.InlineKeyboardButton(text='Оценить работу', callback_data='grade_{0}_{1}_{2}_{3}'.
                                                                 format(tasklist[i][2], lesson[:6], 'video', tasklist[i][3])))
                            bot.send_video(message.chat.id, tasklist[i][6], caption='Отправитель - '+
                            str(database.get_student_fio('chat_id', tasklist[i][2])[0]), reply_markup=mark2)
                    markup.add(btn2)
                    bot.send_message(message.chat.id, 'Были отправлены все решения.', reply_markup=markup)
                else:
                    for i in range(5):
                        try:
                            if int(n) == len(tasklist):
                                markup = types.InlineKeyboardMarkup()
                                markup.add(btn2)
                                bot.send_message(message.chat.id,'Были отправлены все решения.', reply_markup=markup)
                                break
                            else:
                                mark2 = types.InlineKeyboardMarkup()
                                mark2.add(types.InlineKeyboardButton(text='Оценить работу', callback_data='grade_{0}_{1}_{2}_{3}'.
                                                                     format(tasklist[n][2], lesson[:6], 'doc', tasklist[n][3])))
                                bot.send_document(message.chat.id, tasklist[n][6], caption='Отправитель - ' +
                                str(database.get_student_fio('chat_id', tasklist[n][2])[0]),reply_markup=mark2)
                        except:
                            mark2 = types.InlineKeyboardMarkup()
                            mark2.add(types.InlineKeyboardButton(text='Оценить работу', callback_data='grade_{0}_{1}_{2}_{3}'.
                                                                 format(tasklist[n][2], lesson[:6], 'video', tasklist[n][3])))
                            bot.send_video(message.chat.id, tasklist[n][6], caption='Отправитель - ' +
                            str(database.get_student_fio('chat_id', tasklist[n][2])[0]), reply_markup=mark2)
                            n+=1
                        else:
                            n+=1
                    btn1 = types.InlineKeyboardButton(text='Отправить', callback_data='next5_{0}_{1}_{2}'.format(str(n), lesson[:6], grs))
                    markup.add(btn1)
                    markup.add(btn2)
                    if len(tasklist)-n > 5:
                        bot.send_message(message.chat.id, 'Были отправлены первые 5 решений.\nОтправить следущие 5 решений?', reply_markup=markup)
                    elif len(tasklist)-n <= 5 and len(tasklist)-n > 0:
                        bot.send_message(message.chat.id,
                                         'Были отправлены первые 5 решений.\nОтправить последние ' +str(len(tasklist)-n) + '?', reply_markup=markup)

            database.close()
        else:
            grade(message)

def grading(message, student, lesson, work, tsk):
    database = DB('users.db')
    fio = database.get_student_fio('chat_id', student)
    mes =bot.send_message(message.chat.id, 'Укажите оценку за работу студента ' + fio[0] + '.')
    bot.register_next_step_handler(mes, grading_doc, lesson, student, work, tsk)
    database.close()

def grading_doc(message, lesson, student, work, tsk):
    func = funcs(message)
    if func == 2:
        if message.text.isdigit():
            mes = bot.send_message(message.chat.id, 'Ожидается отправка файла или сообщения с разъяснениями для студента.\n'
                                              'Если вы хотите пропустить этот шаг, то нажмите на /home')
            bot.register_next_step_handler(mes, final_grade, lesson, student, message.text, work, tsk)
        else:
            mes = bot.send_message(message.chat.id, 'Неверно указана оценка. Отправьте оценку повторно.')
            bot.register_next_step_handler(mes, grading_doc, lesson, student, message.text, work, tsk)

def final_grade(message, lesson, student, grade, work, tsk):
    func = funcs(message)
    if func == 2 or message.text == '/home':
        database = DB('users.db')
        stat = database.get_stat(student)
        if stat is None:
            dictionary = {lesson: [grade]}
            database.insert_dict(dictionary, student)
        else:
            dictionary = json.loads(stat)
            if lesson not in dictionary.keys():
                dictionary.update({lesson:[grade]})
            else:
                grade_list = dictionary[lesson]
                grade_list.append(grade)
                dictionary.update({lesson: grade_list})
            database.insert_dict(dictionary, student)
        database.insert_grade(grade, tsk, lesson, student)
        if grade.endswith('4') or grade.endswith('3') or grade.endswith('2'):
            lit = 'а.'
        elif grade.endswith('1') and grade != '11':
            lit = '.'
        else:
            lit = 'ов.'
        bot.send_message(student,'Вы получили оценку по предмету\n' + '<b>' +lesson + '</b> за работу '+ work +'\nРабота оценена в ' + grade + ' балл' + lit, parse_mode='html')
        if message.text != '/home':
            if message.content_type == 'video':
                bot.send_message(student, 'Комментарии преподаваателя указаны в видео.')
            elif message.content_type == 'document':
                bot.send_message(student, 'Комментарии преподавателя указаны в документе.')
            else:
                bot.send_message(student, 'Комментарии преподаваателя о работе:')
            bot.forward_message(student, message.chat.id, message.id)
        database.close()

def get_mat(message):
    database = DB('users.db')
    group = database.get_user_info('students', message.chat.id)[6]
    courses = database.get_curses('Группы', group)
    keyb = types.ReplyKeyboardMarkup(True, True)
    for i in range(len(courses)):
        keyb.row(courses[i][1])
    mes = bot.send_message(message.chat.id, 'Выберите интересующий вас предмет.', reply_markup=keyb)
    bot.register_next_step_handler(mes, mat_n)
    database.close()

def mat_n(message):
    func = funcs(message)
    if func == 2:
        database = DB('users.db')
        group = database.get_user_info('students', message.chat.id)[6]
        courses = database.get_curses('Группы', group)
        lessons = []
        for i in range(len(courses)):
            lessons.append(courses[i][1])
        keyb = types.ReplyKeyboardMarkup(True, True)
        keyb.row('Конкретный материал')
        keyb.row('Все материалы по предмету')
        keyb.row('Назад')
        if message.text in lessons:
            mes = bot.send_message(message.chat.id, 'Выберите количество материала.', reply_markup=keyb)
            bot.register_next_step_handler(mes, mat_choice, message.text, 0, 0)
        elif message.text == 'Назад':
            get_mat(message)
        else:
            mes = bot.send_message(message.chat.id, 'Ошибка в названии предмета.')
            bot.register_next_step_handler(mes, mat_n)
        database.close()

def mat_choice(message, lesson, pos, mat):
    func = funcs(message)
    if func == 2:
        database = DB('users.db')
        group = database.get_user_info('students', message.chat.id)[6]
        keyb = types.ReplyKeyboardMarkup(True, True)
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton(text='Вернуться в личный кабинет', callback_data='home')
        markup.add(btn)
        if message.text == 'Конкретный материал' or mat == 1:
            materials = database.get_material('Группы', group, lesson, 'Теоретический материал')
            if len(materials) != 0:
                names = []
                for i in range(len(materials)):
                    if '.' not in materials[i][3]:
                        if 'Практ' not in str(materials[i][2]):
                            names.append(materials[i][3])
                    else:
                        if 'Практ' not in str(materials[i][2]):
                            names.append(materials[i][3].split('.')[0])
                if len(materials) != 0:
                    if pos == len(names):
                        pos = 0
                    for i in range(2):
                        try:
                            keyb.row(names[pos], names[pos + 1])
                        except:
                            try:
                                keyb.row(names[pos])
                            except:
                                pass
                            else:
                                pos += 1
                        else:
                            pos += 2
                    keyb.row('Дальше➡')
                    keyb.row('Назад')
                mes = bot.send_message(message.chat.id, 'Выберите интересующую вас тему.', reply_markup=keyb)
                bot.register_next_step_handler(mes, mat_theme, lesson, pos)
            else:
                bot.send_message(message.chat.id, 'Материалов по данному предмету ещё не поступало от преподавателя.', reply_markup=markup)
        elif message.text == 'Все материалы по предмету':
            materials = database.get_material('Группы', group, lesson, 'Теоретический материал')
            if len(materials) != 0:
                for i in range(len(materials)):
                    if 'Практический' not in materials[i][2]:
                        if i!=len(materials)-1:
                            bot.forward_message(message.chat.id, materials[i][6], materials[i][5])
                        else:
                            bot.forward_message(message.chat.id, materials[i][6], materials[i][5])
                    else:
                        continue
                bot.send_message(message.chat.id, 'Все материалы по предмету <b>' + lesson + '</b> были отправлены!',
                                 reply_markup=markup, parse_mode='html')
            else:
                bot.send_message(message.chat.id, 'Материалов по данному предмету ещё не поступало от преподавателя.', reply_markup=markup)
        elif message.text == 'Назад':
            mat_n(message)
        else:
            mes = bot.send_message(message.chat.id, 'Ошибка в указании количества материала.')
            bot.register_next_step_handler(mes, mat_choice, lesson, pos, mat)
        database.close()

def mat_theme(message, lesson, pos):
    func = funcs(message)
    if func == 2:
        database = DB('users.db')
        if message.text == 'Дальше➡':
            mat_choice(message, lesson, pos, 1)
        elif message.text == 'Назад':
            mat_choice(message, lesson, pos, 0)
        else:
            group = database.get_user_info('students', message.chat.id)[6]
            materials = database.get_material2(lesson, 'Теоретический материал',message.text)
            if len(materials) != 0:
                for i in range(len(materials)):
                    if group not in materials[i][4]:
                        pass
                    else:
                        markup = types.InlineKeyboardMarkup()
                        btn = types.InlineKeyboardButton(text='Вернуться в личный кабинет', callback_data='home')
                        markup.add(btn)
                        bot.forward_message(message.chat.id, materials[i][6], materials[i][5])
                        if i == len(materials)-1:
                            bot.send_message(message.chat.id, 'Материал по предмету <b>' + lesson + '</b> был отправлен!',
                                             reply_markup=markup, parse_mode='html')
            else:
                mes = bot.send_message(message.chat.id, 'Неверно указано название темы. Отправьте название повторно.')
                bot.register_next_step_handler(mes, mat_theme, lesson, pos)
        database.close()

def tasks(message):
    database = DB('users.db')
    markup = types.InlineKeyboardMarkup()
    keyb = types.ReplyKeyboardMarkup(True, True)
    btn = types.InlineKeyboardButton(text='Вернуться в личный кабинет', callback_data='home')
    markup.add(btn)
    group = database.get_user_info('students', message.chat.id)[6]
    materials = database.get_task(group, 'Практический материал')
    #
    done = database.find_tasks(message.chat.id)
    mat3 = []
    for i in range(len(materials)):
        for j in range(len(done)):
            if str(materials[i][5]) in done[j] and str(materials[i][6] in done[j]):
                mat3.append(materials[i])
    for i in range(len(mat3)):
        del materials[materials.index(mat3[i])]
    if len(materials)!=0:
        if len(materials)>=5:
            letter = 'й'
        elif 2<=len(materials)<5:
            letter = 'я'
        else:
            letter = 'е'
        lessons = []
        for i in range(len(materials)):
            lessons.append(materials[i][1])
        all_lessons = list(set(lessons))
        text = ''
        for i in range(len(all_lessons)):
            text += all_lessons[i] + ' - ' + str(count(materials, all_lessons[i])) + '\n'
            keyb.row(all_lessons[i])
        keyb.row('Назад')
        bot.send_message(message.chat.id, 'У вас не выполнено ' + str(len(materials)) +' задани' +letter+ ' по следующим предметам:\n'
                                      +text)
        mes = bot.send_message(message.chat.id, 'Выберите предмет, по которому хотите просмотреть задание.', reply_markup=keyb)
        bot.register_next_step_handler(mes, task_send)
    else:
        bot.send_message(message.chat.id, 'У вас нет невыполненных заданий!', reply_markup=markup)
    database.close()

def task_send(message):
    func = funcs(message)
    if func == 2:
        if message.text != 'Назад':
            database = DB('users.db')
            group = database.get_user_info('students', message.chat.id)[6]
            materials = database.get_task(group, 'Практический материал')
            lessons = []
            for i in range(len(materials)):
                lessons.append(materials[i][1])
            if message.text in lessons:
                btn2 = types.InlineKeyboardButton(text='Вернуться в личный кабинет', callback_data='home')
                done = database.find_tasks(message.chat.id)
                mat3 = []
                for i in range(len(materials)):
                    for j in range(len(done)):
                        if str(materials[i][5]) in done[j] and str(materials[i][6] in done[j]):
                            mat3.append(materials[i])
                for i in range(len(mat3)):
                    del materials[materials.index(mat3[i])]
                mat2 = []
                for i in range(len(materials)):
                    if materials[i][1] == message.text:
                        mat2.append(materials[i])
                for i in range(count(materials, message.text)):
                    if i != len(mat2)-1:
                        markup = types.InlineKeyboardMarkup()
                        markup.add(types.InlineKeyboardButton(text='Отправить решение',
                                                  callback_data='send_sol_{0}_{1}_{2}'.format(mat2[i][5], mat2[i][6], message.text[:6])))
                    else:
                        markup = types.InlineKeyboardMarkup()
                        markup.add(types.InlineKeyboardButton(text='Отправить решение',
                                                              callback_data='send_sol_{0}_{1}_{2}'.format(mat2[i][5],
                                                                                                      mat2[i][6], message.text[:6])))
                        markup.add(btn2)
                    if mat2[i][8] == 'document':
                        bot.send_document(message.chat.id, str(mat2[i][7]), reply_markup=markup)
                    elif mat2[i][8] == 'photo':
                        bot.send_photo(message.chat.id, str(mat2[i][7]), reply_markup=markup)
                    elif mat2[i][8] == 'video':
                        bot.send_video(message.chat.id, str(mat2[i][7]), reply_markup=markup)
            else:
                mes = bot.send_message(message.chat.id, 'Ошибка в названии предмета, отправьте повторно название.')
                bot.register_next_step_handler(mes, task_send)
            database.close()
        else:
            home(message)

def send_solution(message, task, t_id, lesson):
    keyb = types.ReplyKeyboardMarkup(True, True)
    keyb.row('Назад')
    mes = bot.send_message(message.chat.id, 'Отправьте документ или видео с решением.', reply_markup=keyb)
    bot.register_next_step_handler(mes, final_send_sol, task, t_id, lesson)

def final_send_sol(message, task, t_id, lesson):
    func = funcs(message)
    if func == 2:
        if message.text != 'Назад':
            if message.content_type == 'document' or message.content_type == 'video':
                markup = types.InlineKeyboardMarkup()
                btn1 = types.InlineKeyboardButton(text='Вернуться в личный кабинет', callback_data='home')
                markup.add(btn1)
                database = DB('users.db')
                info = database.get_user_info('students', message.chat.id)
                if message.content_type == 'document':
                    f_id = message.document.file_id
                else:
                    f_id = message.video.file_id
                database.insert_task(str(lesson), str(message.chat.id), str(task), str(info[6]), str(t_id), str(f_id))
                bot.send_message(message.chat.id, 'Ваше решение отправлено преподавателю!', reply_markup=markup)
                database.close()
            else:
                mes =bot.send_message(message.chat.id, 'Некорректный формат файла. Отправьте файл с разрешением .doc или .mp4')
                bot.register_next_step_handler(mes, final_send_sol, task, t_id)
        else:
            task_send(message)

@bot.message_handler(commands=['statistics'])
def statistics(message):
    database = DB('users.db')
    stat = database.get_stat(message.chat.id)
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text='Вернуться в личный кабинет', callback_data='home')
    markup.add(btn1)
    if stat is None:
        bot.send_message(message.chat.id, 'У вас пока нет оценок', reply_markup=markup)
    else:
        dictionary = json.loads(stat)
        ln = dictionary.keys()
        text = '<b>Успеваемость</b>\n'
        for i in ln:
            text += '•' + i + '\n'
            for j in range(len(dictionary[i])):
                text += '\t\t\t\t\t\t' + 'Лабораторная работа № ' + str(j+1) + ' — ' + dictionary[i][j]+ '\n'
        bot.send_message(message.chat.id, text, parse_mode='html', reply_markup=markup)
    database.close()

@bot.message_handler(commands=['help'])
def admin_con(message):
    keyb = types.ReplyKeyboardMarkup(True, True)
    keyb.add('Назад')
    mes = bot.send_message(message.chat.id, 'Отправьте сообщение для администратора.', reply_markup=keyb)
    bot.register_next_step_handler(mes, a_con_2)

def a_con_2(message):
    func = funcs(message)
    if func == 2:
        if message.text != 'Назад':
            bot.send_message(message.chat.id, 'Ваше сообщение было отправлено администрации!'
                                              ' После ознакомления с ним с вами свяжутся в случае необходимости.')
            database = DB('users.db')
            admins = database.get_admins()
            req = admins[0][2]
            newlist = []
            for i in range(len(admins)):
                if req > admins[i][2]:
                    req = admins[i][2]
            for i in range(len(admins)):
                if admins[i][2] == req:
                    newlist.append(admins[i])
            random.shuffle(newlist)
            chat_id = newlist[0][1]
            bot.forward_message(chat_id, message.chat.id, message.id)
            database.insert_request(req+1, chat_id)
            database.close()
        else:
            home(message)

def teacher_con(message):
    func = funcs(message)
    if func == 2:
        if len(message.text.split(' ')) < 2:
            mes = bot.send_message(message.chat.id, 'Необходимо указать и имя и фамилию. Ожидается повторная отправка ФИО')
            bot.register_next_step_handler(mes, teacher_con)
        else:
            database = DB('users.db')
            try:
                idt = database.get_id_by_fio2('Авторизован', message.text)[0]
                fio = database.get_teacher_fio(idt)[0]
            except:
                mes = bot.send_message(message.chat.id,
                                       '1Некорректно указано имя или фамилия преподавателя, ожидается повторная отправка ФИО.')
                bot.register_next_step_handler(mes, teacher_con)
            else:
                if message.text.split(' ')[0] not in fio.split(' ') or message.text.split(' ')[1] not in fio.split(' '):
                    mes = bot.send_message(message.chat.id,
                                           '2Некорректно указано имя или фамилия преподавателя, ожидается повторная отправка ФИО.')
                    bot.register_next_step_handler(mes, teacher_con)
                else:
                    keyb = types.ReplyKeyboardMarkup(True, True)
                    keyb.add('Назад')
                    mes = bot.send_message(message.chat.id, 'Напишите сообщение, которое хотите отправить.',
                                           reply_markup=keyb)
                    bot.register_next_step_handler(mes, send_to_teacher, idt)
            database.close()
        bot.send_message(message.chat.id, message.text)

def send_to_teacher(message, idt):
    bot.send_message(idt, 'Вам пришло личное сообщение от студента!')
    bot.forward_message(idt, message.chat.id, message.id)
    bot.send_message(message.chat.id, 'Ваше сообщение успешно отправлено!')

def user_con(message):
    keyb = types.ReplyKeyboardMarkup(True, True)
    keyb.row('Все пользователи')
    keyb.row('Конкретный пользователь')
    keyb.row('Назад')
    mes = bot.send_message(message.chat.id, 'С кем вы хотите связаться?', reply_markup=keyb)
    bot.register_next_step_handler(mes, user_choice)

def user_choice(message):
    func = funcs(message)
    if func == 2:
        keyb = types.ReplyKeyboardMarkup(True, True)
        keyb.row('Назад')
        if message.text == 'Все пользователи':
            mes = bot.send_message(message.chat.id, 'Отправьте сообщение, которое будет пересслано всем пользователям.', reply_markup=keyb)
            bot.register_next_step_handler(mes, user_send, 1)
        elif message.text == 'Конкретный пользователь':
            mes = bot.send_message(message.chat.id, 'Укажите chat_id пользователя, которому вы хотите отправить сооющение.', reply_markup=keyb)
            bot.register_next_step_handler(mes, user_send, 2)
        elif message.text == 'Назад':
            home(message)
        else:
            mes = bot.send_message(message.chat.id, 'Ошибка. Укажите повторно, с кем вы хотите связаться.')
            bot.register_next_step_handler(mes, user_choice)

def user_send(message, var):
    func = funcs(message)
    if func == 2:
        if message.text != 'Назад':
            database = DB('users.db')
            users = []
            keyb = types.ReplyKeyboardMarkup(True, True)
            keyb.row('Назад')
            students = database.select_all('students')
            teachers = database.select_all('teachers')
            for i in range(len(students)):
                if students[i][2] == 'Авторизован':
                    users.append(str(students[i][9]))
            for i in range(len(teachers)):
                if teachers[i][2] == 'Авторизован':
                    users.append(str(teachers[i][8]))
            if var == 2:
                if str(message.text) in users:
                    fio = database.get_teacher_fio(str(message.text))
                    if fio is None:
                        fio = database.get_student_fio('chat_id', str(message.text))
                    mes = bot.send_message(message.chat.id, 'Отправьте сообщение, которое хотите отправить пользователю ' + str(fio[0]) + '.', reply_markup=keyb)
                    bot.register_next_step_handler(mes, user_send2, message.text)
                else:
                    mes = bot.send_message(message.chat.id,
                                           'Неверный chat_id, ожидается повторная отправка.',
                                           reply_markup=keyb)
                    bot.register_next_step_handler(mes, user_send, var)
            else:
                for i in range(len(users)):
                    bot.send_message(users[i], '<b>Сообщение от администрации.</b>', parse_mode='html')
                    bot.send_message(users[i], message.text)
                bot.send_message(message.chat.id, 'Ваше сообщение было отправлено всем пользователям!')
                home(message)
            database.close()
        else:
            home(message)

def user_send2(message, id):
    func = funcs(message)
    if func == 2:
        if message.text != 'Назад':
            bot.send_message(id, '<b>Сообщение от администрации.</b>', parse_mode='html')
            bot.send_message(id, message.text)
            bot.send_message(message.chat.id, 'Ваше сообщение было отправлено!')
            home(message)
        else:
            home(message)

def admin_stat(message):
    database = DB('users.db')
    users = []
    users1 = []
    users2 = []
    keyb = types.InlineKeyboardMarkup()
    keyb.row(types.InlineKeyboardButton(text='Вернуться в меню', callback_data='home'))
    students = database.select_all('students')
    teachers = database.select_all('teachers')
    for i in range(len(students)):
        if students[i][2] == 'Авторизован':
            users.append(str(students[i][9]))
            users1.append(str(students[i][9]))
    for i in range(len(teachers)):
        if teachers[i][2] == 'Авторизован':
            users.append(str(teachers[i][8]))
            users2.append(str(teachers[i][8]))
    bot.send_message(message.chat.id, 'В системе зарегистрировано ' + str(len(users)) + ' пользователей.\n'
                                    'Из них ' + str(len(users1)) + ' студентов и ' + str(len(users2)) + ' преподавателей.', reply_markup=keyb)
    database.close()

@bot.callback_query_handler(func=lambda call:True)
def ans(call):
    try:
        database = DB('users.db')
        if call.data == 'home':
            home(call.message)
        if call.data == 'material':
            get_mat(call.message)
        if call.data == 'statistic':
            statistics(call.message)
        if 'send_more' in call.data:
            groups = call.data.split('_')[2]
            lesson = database.get_curses('Предмет', call.data.split('_')[3])[0][1]
            sending_info(call.message, groups, lesson)
        if call.data == 'send_material':
            pick_lesson(call.message)
        if 'a_a_' in call.data:
            lesson = database.get_curses('Предмет', call.data.split('a_a_')[1])[0][1]
            send(call.message, call.message.text.split('отправки: ')[1], lesson)
        if 'send_next' in call.data:
            groups = call.data.split('_')[2]
            lesson = call.data.split('_')[3]
            sending_info(call.message, groups, lesson)
        if call.data == 'student_con':
            student_con(call.message)
        if 'sendmes' in call.data:
            groups = call.data.split('_')[1]
            lesson = call.data.split('_')[2]
            courses = database.get_curses('Предмет', lesson)
            mat_type(call.message, groups, courses[0][1], 2)
        if call.data == 'tasks':
            tasks(call.message)
        if call.data == 'tasks_2':
            grade(call.message)
        if 'send_sol' in call.data:
            task = call.data.split('_')[2]
            t_id = call.data.split('_')[3]
            les = call.data.split('_')[4]
            courses = database.get_curses('Предмет', les)
            send_solution(call.message, task, t_id, courses[0][1])
        if 'next5' in call.data:
            n = call.data.split('_')[1]
            les = call.data.split('_')[2]
            courses = database.get_curses('Предмет', les)
            grs = call.data.split('_')[3]
            grade_group(call.message, courses[0][1], n, 1, grs)
        if 'grade' in call.data:
            student = call.data.split('_')[1]
            lesson = call.data.split('_')[2]
            courses = database.get_curses('Предмет', lesson)
            form = call.data.split('_')[3]
            tsk = call.data.split('_')[4]
            if form == 'video':
                work = call.message.json['video']['file_name'].split('.')[0]
            elif form == 'doc':
                work = call.message.document.file_name.split('.')[0]
            grading(call.message, student, courses[0][1], work, tsk)
        if call.data == 'admin_con':
            admin_con(call.message)
        if call.data == 'teacher_con':
            mes = bot.send_message(call.message.chat.id, 'Напишите фамилию и имя преподавателя, с которым хотите связаться.')
            bot.register_next_step_handler(mes, teacher_con)
        if call.data == 'user_con':
            user_con(call.message)
        if call.data == 'admin_stat':
            admin_stat(call.message)
        database.close()
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id)
    except:
        pass

def funcs(message):
    if message.text == '/start':
        start_message(message)
    elif message.text == '/statistics':
        statistics(message)
    elif message.text == '/home':
        home(message)
    elif message.text == '/help':
        admin_con(message)
    else:
        return 2

def count(tasks, b):
    c = 0
    for i in range(len(tasks)):
        if tasks[i][1] == b:
            c+=1
    return c


@bot.message_handler(content_types=['text', 'video', 'photo', 'document'])
def words(message):
    bot.send_message(message.chat.id, 'Извините, но я не понимаю вас.')

if __name__ == '__main__':
    bot.polling(none_stop=True)