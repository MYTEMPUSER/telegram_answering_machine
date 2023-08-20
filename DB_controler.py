import sqlite3


class DB_controler():
    def __init__(self, DB_name):
        try:
            self.DB_name = DB_name
            self.sqlite_connection = sqlite3.connect(self.DB_name, check_same_thread=False, timeout=30)
            self.cursor = self.sqlite_connection.cursor()
            self.cursor.execute("CREATE TABLE IF NOT EXISTS Users (tg_login)")
            self.cursor.execute("CREATE TABLE IF NOT EXISTS Vacations (interval_id INTEGER PRIMARY KEY, start, end)")
            self.cursor.execute("CREATE TABLE IF NOT EXISTS Work_times (interval_id INTEGER PRIMARY KEY, day, start, end)")
            self.cursor.execute("CREATE TABLE IF NOT EXISTS Non_work_time_answer (ans)")
            self.cursor.execute("CREATE TABLE IF NOT EXISTS Vacation_answer (ans)")
            self.cursor.close()
            if (self.sqlite_connection):
                self.sqlite_connection.commit()
                self.sqlite_connection.close()

        except sqlite3.Error as error:
            print("sqlite connection error", error)

    def __del__(self):
        if (self.sqlite_connection):
            self.sqlite_connection.commit()
            self.sqlite_connection.close()
            print("Соединение с SQLite закрыто")

    def open_DB(self):
        self.sqlite_connection = sqlite3.connect(self.DB_name, check_same_thread=False, timeout=30)
        self.cursor = self.sqlite_connection.cursor()

    def close_DB(self):
        self.cursor.close()
        self.sqlite_connection.commit()
        self.sqlite_connection.close()
        

    def add_user(self, tg_login):
        self.open_DB()
        self.cursor.execute('SELECT * FROM Users WHERE (tg_login=?)', (tg_login,))
        entry = self.cursor.fetchone()
        if entry is None:
            sqlite_insert_with_param = """INSERT INTO Users (tg_login) VALUES (?);"""
            data_tuple = (tg_login,)
            self.cursor.execute(sqlite_insert_with_param, data_tuple)
            self.sqlite_connection.commit()
        self.close_DB()
        

    def return_user_list(self):
        self.open_DB()
        sqlite_show_all_users = """SELECT * FROM Users"""
        self.cursor.execute(sqlite_show_all_users)
        rows = self.cursor.fetchall()
        user_list = []
        for row in rows:
            user_list.append(row[0])
        self.close_DB()
        return user_list
    

    def delete_user(self, tg_login):
        self.open_DB()
        self.cursor.execute('DELETE FROM Users WHERE (tg_login=?)', (tg_login,))
        self.close_DB()


    def add_vacation(self, start_data, end_data):
        self.open_DB()
        entry = self.cursor.fetchone()
        if entry is None:
            sqlite_insert_with_param = """INSERT INTO Vacations (start, end) VALUES (?,?);"""
            data_tuple = (start_data, end_data,)
            self.cursor.execute(sqlite_insert_with_param, data_tuple)
            self.sqlite_connection.commit()
        self.close_DB()

    def return_vacations(self):
        self.open_DB()
        sqlite_show_all_vacations = """SELECT * FROM Vacations"""
        self.cursor.execute(sqlite_show_all_vacations)
        rows = self.cursor.fetchall()
        vacations = []
        for row in rows:
            information_string = "ID: " + str(row[0]) + " " + str(row[1]) + " - " + str(row[2]) 
            vacations.append(information_string)
        self.close_DB()
        return vacations



    def delete_all_vacations(self):
        self.open_DB()
        self.cursor.execute("DROP TABLE Vacations")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS Vacations (interval_id INTEGER PRIMARY KEY, start, end)")
        self.close_DB()


    def delete_single_vacation(self, id):
        self.open_DB()
        self.cursor.execute('DELETE FROM Vacations WHERE (interval_id=?)', (id,))
        self.close_DB()


    def set_work_interval(self, day, start, end):
        self.open_DB()
        data_tuple = (day, start, end,)
        self.cursor.execute('INSERT INTO Work_times(day, start, end) VALUES (?,?,?)', data_tuple)
        self.close_DB()

    def return_work_intervals(self):
        self.open_DB()
        sqlite_show_all_work_intervals = """SELECT * FROM Work_times"""
        self.cursor.execute(sqlite_show_all_work_intervals)
        rows = self.cursor.fetchall()
        work_intervals = []
        for row in rows:
            information_string = "ID: " + str(row[0]) + " " + str(row[1]) + " " + str(row[2]) + " - " + str(row[3])
            work_intervals.append(information_string)
        self.close_DB()
        return work_intervals


    def delete_all_work_intervals(self):
        self.open_DB()
        self.cursor.execute("DROP TABLE Work_times")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS Work_times (interval_id INTEGER PRIMARY KEY, day, start, end)")
        self.close_DB()


    def delete_single_work_interval(self, id):
        self.open_DB()
        self.cursor.execute('DELETE FROM Work_times WHERE (interval_id=?)', (id,))
        self.close_DB()


    def set_non_work_time_answer(self, text):
        self.open_DB()
        self.cursor.execute("DELETE FROM Non_work_time_answer")
        data_tuple = (text,)
        self.cursor.execute('INSERT INTO Non_work_time_answer(ans) VALUES (?)', data_tuple)
        self.close_DB()

    def get_non_work_time_answer(self):
        self.open_DB()
        self.cursor.execute("SELECT * FROM Non_work_time_answer")
        rows = self.cursor.fetchall()
        self.close_DB()
        try:
            if rows[0][0] == "":
                return "Рабочий день закончился, я прочитаю ваше сообщение как только появится свободное время или начнётся следующий рабочий день."
            else:
                return str(rows[0][0])
        except:
            return "Рабочий день закончился, я прочитаю ваше сообщение как только появится свободное время или начнётся следующий рабочий день."

    def set_vacation_answer(self, text):
        self.open_DB()
        self.cursor.execute("DELETE FROM Vacation_answer")
        data_tuple = (text,)
        self.cursor.execute('INSERT INTO Vacation_answer(ans) VALUES (?)', data_tuple)
        rows = self.cursor.fetchall()
        self.close_DB()

    def get_vacation_answer(self):
        self.open_DB()
        self.cursor.execute("SELECT * FROM Vacation_answer")
        rows = self.cursor.fetchall()
        self.close_DB()
        try:
            if rows[0][0] == "":
                return "Я в отпуске, ваше сообщение будет обязательно прочитано как только у меня появится свободное время"
            else:
                return str(rows[0][0])
        except:
            return "Я в отпуске, ваше сообщение будет обязательно прочитано как только у меня появится свободное время."