import sqlite3
import json
admin_chat_id=801093112
TOKEN=''

class DB:

    def __init__(self, database):
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    def select_all(self, table):
        """ Получаем все строки """
        with self.connection:
            return self.cursor.execute('SELECT * FROM {0}'.format(table)).fetchall()

    def select_groups(self, rownum):
        """ Получаем группы """
        with self.connection:
            return self.cursor.execute('SELECT Группа FROM students WHERE chat_id = ?', (rownum,)).fetchone()

    def get_codes(self, table):
        """ Получаем все коды из таблицы"""
        with self.connection:
            users=[]
            for i in range(self.count_rows(table)):
                users += self.cursor.execute('SELECT Код FROM {}'.format(table)).fetchall()[i]
            return users

    def get_teacher_fio(self, code):
        """ Получаем ФИО преподавателя"""
        with self.connection:
            return self.cursor.execute('SELECT ФИО FROM teachers WHERE chat_id = ?', (code,)).fetchone()

    def get_student_fio(self, field, code):
        """ Получаем ФИО студента"""
        with self.connection:
            return self.cursor.execute('SELECT ФИО FROM students WHERE {0} = ?'.format(field), (code,)).fetchone()

    def get_user_info(self, table, code):
        """ Получаем информацию о опльзователе"""
        with self.connection:
            return self.cursor.execute('SELECT * FROM {0} WHERE chat_id = ?'.format(table), (code,)).fetchone()

    def insert_value(self, column, value, uid, current_table):
        """ Вставляем значения в БД """
        with self.connection:
            sql = """
            UPDATE {0} 
            SET {1} = '%s'
            WHERE Код = '%s'
            """.format(current_table, column) % (value, uid)
            self.cursor.execute(sql)

    def get_curses(self, field, group):
        """ Получаем курсы"""
        with self.connection:
            return self.cursor.execute("SELECT * FROM courses WHERE {0} LIKE '%{1}%'".format(field, group)).fetchall()

    def count_rows(self, table):
        """ Считаем количество строк """
        with self.connection:
            result = self.cursor.execute('SELECT * FROM {}'.format(table)).fetchall()
            return len(result)

    def get_student_ids(self, status, code):
        """ Получаем chat_id студента"""
        with self.connection:
            return self.cursor.execute('SELECT chat_id FROM students WHERE Статус = ? AND Группа = ?', (status, code,)).fetchall()

    def get_id_by_fio(self, status, fio):
        """ Получаем chat_id студента через фамилию"""
        with self.connection:
            return self.cursor.execute('SELECT chat_id FROM students WHERE Статус = ? AND ФИО LIKE "%{0}%"'.format(fio), (status,)).fetchone()

    def get_id_by_fio2(self, status, fio):
        """ Получаем chat_id преподавателя через фамилию"""
        with self.connection:
            return self.cursor.execute('SELECT chat_id FROM teachers WHERE Статус = ? AND ФИО LIKE "%{0}%"'.format(fio), (status,)).fetchone()

    def get_groups(self):
        """ Получаем список групп"""
        with self.connection:
            z = []
            for i in range(self.count_rows('students')):
                z += (self.cursor.execute('SELECT Группа FROM students')).fetchall()[i]
            return list(set(z))

    def get_material(self, field, grs, les, form):
        """ Получаем материалы """
        with self.connection:
            return self.cursor.execute('SELECT * FROM materials WHERE Предмет = ? AND Тип = ? AND {0} LIKE "%{1}%" '.format(field, grs),(les, form)).fetchall()

    def get_material2(self, les, form, name):
        """ Материалы с другой выборкой """
        with self.connection:
            return self.cursor.execute('SELECT * FROM materials WHERE Предмет = ? AND Тип = ? AND Название = ?',(les, form, name)).fetchall()

    def get_task(self, grs, task):
        """ Получаем задания """
        with self.connection:
            return self.cursor.execute(
                'SELECT * FROM materials WHERE Тип = ? AND Группы LIKE "%{0}%" '.format(grs), (task,)).fetchall()

    def new_material(self, predm, type, name, grs, mes_id, teach_id, file_code, format):
        with self.connection:
            return self.cursor.execute('INSERT INTO materials (Предмет, Тип, Название, Группы, mes_id, teacher_id, file_code, Формат) '
                                       'VALUES (?, ?, ?, ?, ?, ?, ?, ?)', (predm, type, name, grs, mes_id, teach_id, file_code, format))
    def count_tasks(self, les, task):
        """ Считаем количество заданий """
        with self.connection:
            result = self.cursor.execute('SELECT * FROM materials WHERE Предмет = ? AND Тип = ?', (les, task)).fetchall()
            return len(result)

    def find_tasks(self, stud):
        """Получаем задания """
        with self.connection:
            return self.cursor.execute('SELECT * FROM tasks WHERE student_id = {0}'.format(stud)).fetchall()

    def insert_task(self, predm, stud_id, task, otz, t_id, mes_id):
        with self.connection:
            return self.cursor.execute(
                'INSERT INTO tasks (Предмет, student_id, Задание, Группа, teacher_id, mes_id) VALUES (?, ?, ?, ?, ?, ?)', (predm, stud_id, task, otz, t_id, mes_id))

    def grade_tasks(self, t_id, n):
        """ Получаем задания для оценки """
        with self.connection:
            return self.cursor.execute('SELECT * FROM tasks WHERE teacher_id = ? AND Оценка = ?', (t_id, n,)).fetchall()

    def grade_tasks_2(self, t_id, group, les, n):
        """ Задания для оценци с другой выборкой """
        with self.connection:
            return self.cursor.execute('SELECT * FROM tasks WHERE teacher_id = ? AND Группа = ? AND Предмет = ? AND Оценка = ?', (t_id, group, les, n)).fetchall()

    def insert_grade(self, value, uid, les, s_id):
        """ Вставляем значения в БД """
        with self.connection:
            sql = """
            UPDATE tasks 
            SET Оценка = '%s'
            WHERE Задание = '%s'
            AND Предмет = '%s'
            AND student_id = '%s'
            """ % (value, uid, les, s_id)
            self.cursor.execute(sql)

    def get_stat(self, s_id):
        """ Считаем статистику """
        with self.connection:
            return self.cursor.execute('SELECT stat FROM students WHERE chat_id = {0}'.format(s_id)).fetchone()[0]

    def insert_dict(self, dict, s_id):
        with self.connection:
            sql = """
            UPDATE students
            SET stat = '%s' 
            WHERE chat_id = '%s'
            """ % (json.dumps(dict), s_id)
            self.cursor.execute(sql)

    def close(self):
        """ Закрываем текущее соединение с БД """
        self.connection.close()

    def get_admins(self):
        """ Считаем информацию из таблицы администрации"""
        with self.connection:
            return self.cursor.execute('SELECT * FROM admins').fetchall()

    def insert_request(self, req, chat_id):
        with self.connection:
            sql = """
            UPDATE admins
            SET requests = '%s' 
            WHERE chat_id = '%s'
            """ % (req, chat_id)
            self.cursor.execute(sql)