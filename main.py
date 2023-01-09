import telebot
from telebot import types
import psycopg2
import datetime
import re

conn = psycopg2.connect(dbname='windowcorp', user='postgres', password='123123', host='localhost')
cursor = conn.cursor()
bot = telebot.TeleBot('5931490397:AAHTruRa5X4wl5ZN_Y33FuhYPnkbt9YawO8')


@bot.message_handler(commands=['start'])
def start_message(msg):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    items = types.KeyboardButton('Авторизация')
    markup.add(items)

    bot.send_message(msg.chat.id, 'Пожалуйста авторизуйтесь', reply_markup=markup)


dict_all = {'login': False, 'password': False, 'login_data': '', 'password_data': '',
            'manager-online': False, 'winmaster-online': False, 'Authorization_successful': False, 'worker_id': 0,
            'incorrect_log_pass': False}

dict_manager_options = {'show_all_tasks': False, 'change_priority_manager': False, 'add_user': False}

dict_bd_work = {'change_priority': False, 'priority_id': False}

dict_priority = {'id': 0}

dict_add_user = {'login': False, 'password': False, 'role': False,
                 'full_name': False, 'phone_number': False, 'email': False, 'passport': False}
dict_add_user_data = {'login': '', 'password': '', 'role': '',
                      'full_name': '', 'phone_number': '', 'email': '', 'passport': ''}
dict_add_task = {'description': False, 'deadline': False, 'priority': False, 'executor': False}
dict_add_task_data = {'description': '', 'deadline': '', 'priority': 0, 'executor': 0}

dict_finish_task = {'id_task': 0, 'inp_id': False}


@bot.message_handler(content_types='text')
def reply(input_message):

    def manager_markup(id, msg):
        markup_manager = types.ReplyKeyboardMarkup(resize_keyboard=True)
        items_button_executable = types.KeyboardButton('Просмотр всех заданий')
        items_button_status = types.KeyboardButton('Изменить приоритет задания')
        items_button_new_user = types.KeyboardButton('Добавление нового пользователя')
        items_button_new_task = types.KeyboardButton('Добавление нового задания')
        markup_manager.add(items_button_executable, items_button_status, items_button_new_user, items_button_new_task)
        bot.send_message(id, msg, reply_markup=markup_manager)

    def winmaster_markup(id, msg):
        markup_manager = types.ReplyKeyboardMarkup(resize_keyboard=True)
        items_button_executable = types.KeyboardButton('Просмотр всех заданий')
        items_button_done = types.KeyboardButton('Завершение задания')
        markup_manager.add(items_button_executable, items_button_done)
        bot.send_message(id, msg, reply_markup=markup_manager)

    if (input_message.text =='Авторизация' and dict_all['Authorization_successful'] is False) or\
            dict_all['incorrect_log_pass'] is True:
        dict_all['incorrect_log_pass'] = False
        bot.send_message(input_message.chat.id, 'Введите логин:')
        dict_all['login'] = True
    elif dict_all['Authorization_successful'] is False and dict_all['login'] == True:
        dict_all['login_data'] = input_message.text
        dict_all['login'] = False
        dict_all['password'] = True
        bot.send_message(input_message.chat.id, 'Введите пароль:')
    elif dict_all['Authorization_successful'] is False and dict_all['password'] is True:
        dict_all['password'] = False
        dict_all['password_data'] = input_message.text
        cursor.execute(f"SELECT role FROM account WHERE login = '{dict_all['login_data']}'"
                       f" AND password = '{dict_all['password_data']}'")
        records = cursor.fetchall()
        if len(records) != 0:
            get_role = str(records[0][0])
        if len(records) == 0:
            bot.send_message(input_message.chat.id, 'Неверный логин или пароль. Повторите попытку авторизации.\n')
            dict_all['login'] = True
            bot.send_message(input_message.chat.id, 'Введите логин:')
        elif get_role == 'role-manager':
            dict_all['incorrect_log_pass'] = False
            dict_all['Authorization_successful'] = True
            dict_all['manager-online'] = True
            manager_markup(input_message.chat.id, 'Авторизация успешна. Ваша роль: Менеджер')
            cursor.execute(f"SELECT id_worker FROM account WHERE login = '{dict_all['login_data']}'")
            id_worker = cursor.fetchall()
            dict_all['worker_id'] = id_worker[0][0]
        elif get_role == 'role-winmaster':
            cursor.execute(f"SELECT id_worker FROM account WHERE login = '{dict_all['login_data']}'")
            id_worker = cursor.fetchall()
            dict_all['worker_id'] = id_worker[0][0]
            winmaster_markup(input_message.chat.id, 'Авторизация успешна. Ваша роль: Оконный мастер')
            dict_all['incorrect_log_pass'] = False
            dict_all['Authorization_successful'] = True
            dict_all['winmaster-online'] = True



    elif input_message.text == 'Просмотр всех заданий' and dict_all['manager-online'] == True:
        cursor.execute(f"SELECT * FROM task ORDER BY id_task")
        record_all_task = cursor.fetchall()
        for rec in record_all_task:
            a = (
                f'id: {rec[0]}\nДата создания: {rec[1]}\nДедлайн: {rec[2]}\nДата завершения: {rec[3]}\nОписание:'
                f' {rec[8]}\nПриоритет: {rec[6]}')
            bot.send_message(input_message.chat.id, f'{a}')
    elif input_message.text == 'Изменить приоритет задания' and dict_all['manager-online'] == True:
        cursor.execute(f"SELECT * FROM task ORDER BY id_task")
        record_all_task = cursor.fetchall()
        for rec in record_all_task:
            a = (
                f'id: {rec[0]}\nДата создания: {rec[1]}\nДедлайн: {rec[2]}\nДата завершения: {rec[3]}\nОписание: '
                f'{rec[8]}\nПриоритет: {rec[6]}')
            bot.send_message(input_message.chat.id, f'{a}')
        bot.send_message(input_message.chat.id, 'Введите id задания, у которого хотите изменить приоритет:')
        dict_bd_work['change_priority'] = True
    elif dict_bd_work['change_priority'] is True and dict_all['manager-online'] is True:
        dict_priority['id'] = input_message.text
        dict_bd_work['change_priority'] = False
        bot.send_message(input_message.chat.id, 'Введите новый приоритет в диапазоне 1-3:')
        dict_bd_work['priority_id'] = True
    elif dict_bd_work['priority_id'] is True and dict_all['manager-online'] is True:
        new_priority = input_message.text
        dict_bd_work['priority_id'] = False
        cursor.execute(f"UPDATE task SET id_priority = {new_priority}WHERE id_task = {dict_priority['id']}")
        dict_bd_work['change_priority'] = False
        conn.commit()
        manager_markup(input_message.chat.id, 'Приоритет успешно изменен')
    elif input_message.text == 'Добавление нового пользователя' and dict_all['manager-online'] == True:
        dict_manager_options['add_user'] = True
        dict_add_user['login'] = True
        bot.send_message(input_message.chat.id, 'Введите логин пользователя:')
    elif dict_add_user['login'] is True and dict_manager_options['add_user'] is True:
        dict_add_user_data['login'] = input_message.text
        dict_add_user['login'] = False
        dict_add_user['password'] = True
        bot.send_message(input_message.chat.id, 'Введите пароль пользователя:')
    elif dict_add_user['password'] is True and dict_manager_options['add_user'] is True:
        dict_add_user_data['password'] = input_message.text
        dict_add_user['password'] = False
        markup_role_user = types.ReplyKeyboardMarkup(resize_keyboard=True)
        items_button_manager = types.KeyboardButton('Менеджер')
        items_button_winmaster = types.KeyboardButton('Оконный мастер')
        markup_role_user.add(items_button_winmaster, items_button_manager)
        bot.send_message(input_message.chat.id, 'Выберите роль пользователя:', reply_markup=markup_role_user)
        dict_add_user['role'] = True
    elif dict_add_user['role'] is True and dict_manager_options['add_user'] is True:
        add_user_role = input_message.text
        if add_user_role == 'Менеджер':
            dict_add_user_data['role'] = 'role-manager'
        elif add_user_role == 'Оконный мастер':
            dict_add_user_data['role'] = 'role-winmaster'
        dict_add_user['role'] = False
        bot.send_message(input_message.chat.id, 'Введите ФИО пользователя:')
        dict_add_user['full_name'] = True
    elif dict_add_user['full_name'] is True and dict_manager_options['add_user'] is True:
        dict_add_user_data['full_name'] = input_message.text
        dict_add_user['full_name'] = False
        bot.send_message(input_message.chat.id, 'Введите телефонный номер пользователя в формате +7...:')
        dict_add_user['phone_number'] = True
    elif dict_add_user['phone_number'] is True and dict_manager_options['add_user'] is True:
        dict_add_user['phone_number'] = False
        check_phone_number = input_message.text
        match = re.fullmatch(r'[+][7]\d{10}', check_phone_number)
        if match is not None:
            dict_add_user_data['phone_number'] = input_message.text
            bot.send_message(input_message.chat.id, 'Введите e-mail пользователя:')
            dict_add_user['email'] = True
        else:
            dict_add_user['phone_number'] = True
            bot.send_message(input_message.chat.id, 'Введенный номер не соответствует формату номера! '
                                                    'повторите попытку ввода!')
    elif dict_add_user['email'] is True and dict_manager_options['add_user'] is True:
        dict_add_user_data['email'] = input_message.text
        dict_add_user['email'] = False
        bot.send_message(input_message.chat.id, 'Введите номер паспорта пользователя. 10 цифр без пробела:')
        dict_add_user['passport'] = True
    elif dict_add_user['passport'] is True and dict_manager_options['add_user'] is True:
        check_passport = input_message.text
        dict_add_user['passport'] = False
        match_passport = re.fullmatch(r'\d{10}', check_passport)
        if match_passport is not None:
            dict_add_user_data['passport'] = input_message.text
            dict_add_user['passport'] = False
            dict_manager_options['add_user'] = False
            manager_markup(input_message.chat.id, 'Пользователь успешно добавлен')
            if dict_add_user_data['role'] == 'role-manager':
                user_role_id = 1
            elif dict_add_user_data['role'] == 'role-winmaster':
                user_role_id = 2
            cursor.execute(f"INSERT INTO Worker(full_name_worker, number_phone_worker,"
                           f"email_worker,passport_number, id_position) "
                           f"VALUES ('{dict_add_user_data['full_name']}', '{dict_add_user_data['phone_number']}',"
                           f"'{dict_add_user_data['email']}', '{dict_add_user_data['passport']}',{user_role_id})")
            conn.commit()
            cursor.execute(f"SELECT id_worker FROM worker WHERE email_worker = '{dict_add_user_data['email']}'")
            record_id_worker_account = cursor.fetchall()
            cursor.execute(f"INSERT INTO account(login,password,role,id_worker) VALUES "
                           f"('{dict_add_user_data['login']}',"
                           f" '{dict_add_user_data['password']}', '{dict_add_user_data['role']}',"
                           f" {record_id_worker_account[0][0]})")
            conn.commit()
        else:
            bot.send_message(input_message.chat.id, 'Паспорт введен в неверном формате! Повторите ввод!')
            dict_add_user['passport'] = True
    elif input_message.text == 'Добавление нового задания' and dict_all['manager-online'] is True:
        dict_add_task['description'] = True
        bot.send_message(input_message.chat.id, 'Ввведите описание задания:')
    elif dict_add_task['description'] is True and dict_all['manager-online'] is True:
        dict_add_task['description'] = False
        dict_add_task_data['description'] = input_message.text
        dict_add_task['deadline'] = True
        bot.send_message(input_message.chat.id, f'Ввведите дедлайн задачи: \n формат YYYY-MM-DD HH:MM:SS')
    elif dict_add_task['deadline'] is True and dict_all['manager-online'] is True:
        dict_add_task['deadline'] = False
        check_deadline = input_message.text
        match_deadline = re.fullmatch(r'\d{4}[-]\d{2}[-]\d{2}[ ]\d{2}[:]\d{2}[:]\d{2}', check_deadline)
        if match_deadline is not None:
            dict_add_task_data['deadline'] = datetime.datetime.strptime(input_message.text, '%Y-%m-%d %H:%M:%S')
            dict_add_task['priority'] = True
            bot.send_message(input_message.chat.id, 'Ввведите приоритет задачи в диапазоне 1-3:')
        else:
            dict_add_task['deadline'] = True
            bot.send_message(input_message.chat.id, 'Введенная дата имеет неверный формат! Повторите попытку ввода:')
    elif dict_add_task['priority'] is True and dict_all['manager-online'] is True:
        dict_add_task['priority'] = False
        dict_add_task_data['priority'] = int(input_message.text)
        dict_add_task['executor'] = True
        cursor.execute(f"SELECT id_worker, full_name_worker FROM worker")
        chosen_worker = cursor.fetchall()
        for worker in chosen_worker:
            bot.send_message(input_message.chat.id, f"id: {worker[0]}\n ФИО: {worker[1]}")
        bot.send_message(input_message.chat.id, 'Введите id работника, который будет исполнять задачу:')
    elif dict_add_task['executor'] is True and dict_all['manager-online'] is True:
        dict_add_task['executor'] = False
        dict_add_task_data['executor'] = input_message.text
        now = datetime.datetime.now()
        time_format = "%Y-%m-%d %H:%M:%S"
        now_format = f"{now:{time_format}}"
        cursor.execute(f"INSERT INTO task(descr_task, data_create, deadline, data_end, id_contract,"
                       f" id_priority, id_task_type, id_author, id_executor) "
                       f"VALUES ('{dict_add_task_data['description']}', '{now_format}', "
                       f"'{dict_add_task_data['deadline']}', null, 1,{dict_add_task_data['priority']},1,"
                       f"{dict_all['worker_id']},"
                       f"{dict_add_task_data['executor']} )")
        conn.commit()
        manager_markup(input_message.chat.id, 'Задание добавлено')

    elif input_message.text == 'Просмотр всех заданий' and dict_all['winmaster-online'] is True:
        cursor.execute(f"SELECT * FROM task WHERE id_executor = {dict_all['worker_id']} and data_end is null")
        worker_tasks = cursor.fetchall()
        if len(worker_tasks) == 0:
            bot.send_message(input_message.chat.id, 'Для вас задания отсутствуют')
        else:
            for tasks in worker_tasks:
                a = (
                    f'id: {tasks[0]}\nДата создания: {tasks[1]}\nДедлайн: {tasks[2]}\nДата завершения: '
                    f'{tasks[3]}\nОписание: {tasks[8]}\nПриоритет: {tasks[6]}')
                bot.send_message(input_message.chat.id, f'{a}')
    elif input_message.text == 'Завершение задания' and dict_all['winmaster-online'] == True:
        dict_finish_task['inp_id'] = True
        cursor.execute(f"SELECT * FROM task WHERE id_executor = {dict_all['worker_id']} and data_end is null")
        worker_tasks = cursor.fetchall()
        if len(worker_tasks) == 0:
            bot.send_message(input_message.chat.id, 'Завершить задание невозможно - задания отсутствуют')
        else:
            for tasks in worker_tasks:
                a = (
                    f'id: {tasks[0]}\nДата создания: {tasks[1]}\nДедлайн: {tasks[2]}\nДата завершения: '
                    f'{tasks[3]}\nОписание: {tasks[8]}\nПриоритет: {tasks[6]}')
                bot.send_message(input_message.chat.id, f'{a}')
            bot.send_message(input_message.chat.id, 'Введите id задания, которое завершили:')
    elif dict_finish_task['inp_id'] is True and dict_all['winmaster-online'] is True:
        dict_finish_task['inp_id'] = False
        dict_finish_task['id_task'] = input_message.text
        now = datetime.datetime.now()
        time_format = "%Y-%m-%d %H:%M:%S"
        now_format = f"{now:{time_format}}"
        cursor.execute(f"UPDATE task SET data_end = '{now_format}' WHERE id_task = {dict_finish_task['id_task']}")
        conn.commit()
        winmaster_markup(input_message.chat.id, 'Выбранное задание завершено')


bot.infinity_polling()
