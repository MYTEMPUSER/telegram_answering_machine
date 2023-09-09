from pyrogram import Client,filters
import time
from datetime import datetime
import telebot
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP
from DB_controler import DB_controler
from pyromod import listen
from calendar_manager import calendar_obj
from datetime import date
from pyrogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP

from pyrogram.types import (ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton)

days_of_week = ["Mon", "Tue", "Wed", "Thu",  "Fri", "Sat", "Sun"]

def parce_time(time):
	H, M = time.split(":")
	return int(H), int(M)

class message_controll():
	def __init__(self):
		self.api_id = 21770637
		self.api_hash = "9b941df2caee5b823de80d4af7b8fb10" 
		self.app = Client("account", api_hash=self.api_hash, api_id=self.api_id)
		self.set_message_handler()
		self.DB_controler = DB_controler("kaban.db")
		self.answered_users = []
		self.app.run()


	def generate_answer_status(self, msg):
		if self.check_vacation(msg.date):
			return self.DB_controler.get_vacation_answer()
		if not self.check_work_time(msg.date):
			return self.DB_controler.get_non_work_time_answer()
		return False

	def check_user_exclusions(self, user_name, user_phone_number):
		users = self.DB_controler.return_user_list()
		return (("@" + str(user_name)) in users) or (("+" + str(user_phone_number)) in users)

	def check_vacation(self, date):
		vacations = self.DB_controler.return_vacations()
		for vacation in vacations:
			vacation_info = vacation.split(' ')
			start = datetime.strptime(vacation_info[2], "%Y-%m-%d")
			end = datetime.strptime(vacation_info[4], "%Y-%m-%d")
			if (date >= start and date <= end):
				return True

		return False

	def check_work_time(self, date):
		try:
			work_intervals = self.DB_controler.return_work_intervals()
			for work_interval in work_intervals:
				work_interval_info = work_interval.split(' ') 
				day_of_week = work_interval_info[2]
				start = work_interval_info[3]
				end = work_interval_info[5]
				if days_of_week[date.weekday()].lower() == day_of_week.lower():
					now = datetime.now()
					time_to_check = now.replace(hour=date.timetuple().tm_hour, minute=date.timetuple().tm_min, second=0, microsecond=0)

					H, M = parce_time(start)
					start_time = now.replace(hour=H, minute=M, second=0, microsecond=0)
					H, M = parce_time(end)
					end_time = now.replace(hour=H, minute=M, second=0, microsecond=0)
					if (start_time <= time_to_check and time_to_check <= end_time):
						return True
		except:
			pass
		return False


	def is_user_answered_today(self, username, date):
		day = date.timetuple().tm_yday
		if ([username, day] in self.answered_users):
			return True
		else:
			self.answered_users.append([username, day])
			return False 

	def set_message_handler(self):
		@self.app.on_message(filters.private & filters.incoming)
		async def type(_, msg):
			sp_p=[]
			ID = msg.chat.id 
			if not self.check_user_exclusions(msg.from_user.username, msg.from_user.phone_number):
				answer = self.generate_answer_status(msg)
				if answer:
					if not self.is_user_answered_today(msg.from_user.username, msg.date):
						await self.app.send_message(ID, answer)