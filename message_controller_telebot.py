from pyrogram import Client,filters
import time
import telebot
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from DB_controler import DB_controler
from pyromod import listen
from calendar_manager import calendar_obj
from datetime import date
from pyrogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

valid_days_of_week = ["Mon", "Tue", "Wed", "Thu",  "Fri", "Sat", "Sun"]

class message_controll():
	def __init__(self):
		self.app = telebot.TeleBot("6336485791:AAFUsEhb-Z_L67UqbtBPX7pnlV4wFIh90Gg")
		self.DB_controler = DB_controler("kaban.db")		
		self.set_commands_handler()
		self.add_vacation_status = "Not_started" #Not_started - ничего не задано, Started - задано начало отпуска
		self.vacation_start_data = ""
		self.app.infinity_polling()
	

	def set_commands_handler(self):
		@self.app.message_handler(commands=['help'])
		def handler_help(message):
			ID = message.from_user.id
			self.app.send_message(ID, "/add_users @iblinov @vihuhol_DV - добавить пользователей в список исключений")
			self.app.send_message(ID, "/delete_users @vihuhol_DV @orlan - удалить пользователей из список исключений")
			self.app.send_message(ID, "/show_user_list - вывести список исключений")
			self.app.send_message(ID, "/set_work_time 09:00 - 18:00 Mon Tue Wed Thu Fri Sat Sun - добавить рабочее время с 09:00 - 18:00 7 дней в неделю")
			self.app.send_message(ID, "/show_work_intervals - вывести все рабочие интервалы")
			self.app.send_message(ID, "/delete_work_interval_by_id 1 2 3 - удалить интервали в индексами 1 2 3 \n /delete_work_interval_by_id all - удалить все интервалы")
			self.app.send_message(ID, "/add_vacation - Выбрать дату начала и конца отпуска") 
			self.app.send_message(ID, "/show_vacations_list - Список отпусков")
			self.app.send_message(ID, "/delete_vacations_by_id 3 - Удалить отпуск с ID 3 \n /delete_vacations_by_id all -Удалить все отпуска")
			self.app.send_message(ID, "/set_non_work_time_answer Рабочий день закончился, я отвечу как только будет возможность и желание. - Установить ответ для нерабочего времени")
			self.app.send_message(ID, "/set_vacation_answer Я в отпуске. - Установить ответ для отпуска")
			#print(message)
			#for i in message.date.timetuple():     
			#	print(i)
			#print(date.fromisoformat(message.date))


		@self.app.message_handler(commands=["add_users"])
		def handler_add_user(message):
			try:
				for user in message.text.split()[1:]:
					self.DB_controler.add_user(user)
			except:
				pass

		@self.app.message_handler(commands=["delete_users"])
		def delete_user(message):
			try:
				for user in message.text.split()[1:]:
					self.DB_controler.delete_user(user)
			except:
				pass

		@self.app.message_handler(commands=["show_user_list"])
		def delete_user(message):
			users = self.DB_controler.return_user_list()
			ID = message.from_user.id
			result = ' '.join(users)
			self.app.send_message(ID, result)

		@self.app.message_handler(commands=["set_work_time"])
		def handler_set_work_time(message):
			try:
				start_time = message.text.split()[1]
				end_time = message.text.split()[3]
				for day_of_week in message.text.split()[4:]:
					self.DB_controler.set_work_interval(day_of_week, start_time, end_time)
			except:
				pass

		@self.app.message_handler(commands=["show_work_intervals"])
		def handler_show_work_intervals(message):
			intervals = self.DB_controler.return_work_intervals()
			ID = message.from_user.id
			for interval in intervals:
				self.app.send_message(ID, interval)

		@self.app.message_handler(commands=["delete_work_interval_by_id"])
		def handler_delete_work_interval_by_id(message):
			try:
				if len(message.text.split()) > 1:
					cmd = message.text.split()[1]
					if cmd == "all":
						self.DB_controler.delete_all_work_intervals()
					else:
						for ID in message.text.split()[1:]:
							self.DB_controler.delete_single_work_interval(ID)
			except:
				pass

		@self.app.message_handler(commands=["add_vacation"])
		def handler_add_vacation(message):
			calendar, step = DetailedTelegramCalendar().build()
			self.app.send_message(message.chat.id, f"Select {LSTEP[step]}", reply_markup=calendar)

		@self.app.callback_query_handler(func=DetailedTelegramCalendar.func())
		def cal(c):
		    result, key, step = DetailedTelegramCalendar().process(c.data)
		    if not result and key:
		        self.app.edit_message_text(f"Поля, выбери дату начала отпуска {LSTEP[step]}",
		                              c.message.chat.id,
		                              c.message.message_id,
		                              reply_markup=key)
		    elif result:
		        if self.add_vacation_status == "Not_started":
		            self.add_vacation_status = "Started"
		            self.vacation_start_data = result
		            self.app.edit_message_text(f"Начало отпуска {result}", c.message.chat.id, c.message.message_id)
		            calendar, step = DetailedTelegramCalendar().build()
		            self.app.send_message(c.message.chat.id, f"Поля, выбери дату окончания отпуска {LSTEP[step]}", reply_markup=calendar)
		        else:
		            self.add_vacation_status = "Not_started"
		            self.app.edit_message_text(f"Конец отпуска {result}", c.message.chat.id, c.message.message_id)
		            self.DB_controler.add_vacation(self.vacation_start_data, result)


		@self.app.message_handler(commands=["show_vacations_list"])
		def handler_show_vacations(message):
			vacations = self.DB_controler.return_vacations()
			ID = message.from_user.id
			for vacation in vacations:
				self.app.send_message(ID, vacation)

		@self.app.message_handler(commands=["delete_vacations_by_id"])
		def handler_delete_vacation(message):
			try:
				if len(message.text.split()) > 1:
					cmd = message.text.split()[1]
					if cmd == "all":
						self.DB_controler.delete_all_vacations()
					else:
						for ID in message.text.split()[1:]:
							self.DB_controler.delete_single_vacation(ID)
			except:
				pass


		@self.app.message_handler(commands=["set_non_work_time_answer"])
		def handler_set_non_work_time_answer(message):
			try:
				ans = ' '.join(message.text.split()[1:])
				self.DB_controler.set_non_work_time_answer(ans)
			except:
				pass


		@self.app.message_handler(commands=["set_vacation_answer"])
		def handler_set_vacation_answer(message):
			try:
				ans = ' '.join(message.text.split()[1:])
				self.DB_controler.set_vacation_answer(ans)
			except:
				pass