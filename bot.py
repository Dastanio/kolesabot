from telebot import TeleBot, types
from sqlighter import SQLighter

from pars import KolesaKz, get_marks, get_regions, get_models, bodywork, KKP

from time import sleep
from multiprocessing import Process

bot = TeleBot('1198609069:AAFSfedIfR22MxNL63bprOqnxhPIYS7hwHo')



@bot.message_handler(commands= ['start'])
def main(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton('/subscribe')
    item2 = types.KeyboardButton('/unsubscribe')
    item3 = types.KeyboardButton('/edit_filters')
    item4 = types.KeyboardButton('/show_filters')
    item5 = types.KeyboardButton('/delete_car')
    item6 = types.KeyboardButton('/add_car')
    markup.add(item1,item2, item3, item4,item5, item6)

    bot.send_message(message.chat.id, 'Приветствую {0.first_name}!, \nsubscribe  - Подписка на рассылку\nunsubscribe  - Отписка от рассылок\nedit_filters - изменить фильтры\nshow_filters - посмотреть все текущие комплекты /фильтры\nadd_car - добавить комплект\ndelete_car - удалить комплект'.format(message.from_user, bot.get_me()),
        parse_mode='html', reply_markup=markup)


@bot.message_handler(commands=['subscribe'])
def subscribe(message):
	db = SQLighter('db.db')

	if not db.subscriber_exists(message.from_user.id):
		db.add_subscriber(message.from_user.id)
	else:
		db.update_subscription(message.from_user.id, True)

	bot.send_message(message.chat.id, "Вы успешно подписались на рассылку!\nПо умолчанию вам будут приходить все уведомление машин с сайта. =)")
	db.close()

@bot.message_handler(commands=['unsubscribe'])
def unsubscribe(message):
	db = SQLighter('db.db')

	if not db.subscriber_exists(message.from_user.id):
		db.add_subscriber(message.from_user.id, False)
		bot.send_message(message.chat.id, "Вы итак не подписаны.")
	else:
		db.update_subscription(message.from_user.id, False)
		bot.send_message(message.chat.id, "Вы успешно отписаны от рассылки.")

	db.close()

@bot.message_handler(commands=['edit_filters'])
def filters(message):
	db = SQLighter('db.db')

	if message.chat.id in [i[0] for i in db.get_subscriptions()]:
		keyboard = types.InlineKeyboardMarkup()
		subscriber = db.get_subscriber(message.chat.id)

		for i in eval(subscriber[0][2]).keys():
			keyboard.add(types.InlineKeyboardButton(i, callback_data='19.'+i))
		bot.send_message(message.chat.id, 'Выберите комплект фильтра:', reply_markup=keyboard)
	else:
		bot.send_message(message.chat.id, "Вы не подписаны.")

	db.close()

def save_filter(id, text, filter, car):
	db = SQLighter('db.db')

	filters = eval(db.get_subscriber(id)[0][2])

	if text.lower() == 'неважен':
		filters[car][filter] = None
	else:
		filters[car][filter] = text

	db.update_subscription(id, True, filters=filters)
	bot.send_message(id, "Фильтр применен.")

	db.close()

@bot.callback_query_handler(func=lambda query: True)
def handler_callback_query(query):
	if query.data.startswith('1.'):
		keyboard = types.InlineKeyboardMarkup()

		for i in bodywork.keys():
			keyboard.add(types.InlineKeyboardButton(i, callback_data='14.'+bodywork[i]+'.'+query.data.split('1.')[1]))
		keyboard.add(types.InlineKeyboardButton('Неважно', callback_data='14.0.'+query.data.split('1.')[1]))

		bot.edit_message_text(chat_id=query.from_user.id, message_id=query.message.message_id, text="Кузов:", reply_markup=keyboard)
	elif query.data.startswith('2.'):
		keyboard = types.InlineKeyboardMarkup()
		regions = get_regions()

		for i in regions.keys():
			keyboard.add(types.InlineKeyboardButton(i, callback_data='15.'+regions[i]+'.'+query.data.split('2.')[1]))
		keyboard.add(types.InlineKeyboardButton('Неважно', callback_data='15.0.'+query.data.split('2.')[1]))

		bot.edit_message_text(chat_id=query.from_user.id, message_id=query.message.message_id, text="Где искать (неважно):", reply_markup=keyboard)
	elif query.data.startswith('7.'):
		keyboard = types.InlineKeyboardMarkup()
		marks = get_marks()

		for i in marks.keys():
			keyboard.add(types.InlineKeyboardButton(i, callback_data='16.'+marks[i]+'.'+query.data.split('7.')[1]))
		keyboard.add(types.InlineKeyboardButton('Неважно', callback_data='16.0.'+query.data.split('7.')[1]))

		bot.edit_message_text(chat_id=query.from_user.id, message_id=query.message.message_id, text="Марка:", reply_markup=keyboard)
	elif query.data.startswith('8.'):
		db = SQLighter('db.db')
		subscriber = db.get_subscriber(message.from_user.id)
		db.close()

		if eval(subscriber[0][2])[query.data.split('8.')[1]]['car'] != None:
			keyboard = types.InlineKeyboardMarkup()
			models = get_models(eval(subscriber[0][2])[query.data.split('8.')[1]]['car'])

			for i in models.keys():
				keyboard.add(types.InlineKeyboardButton(i, callback_data='17.'+models[i]+'.'+query.data.split('8.')[1]))
			keyboard.add(types.InlineKeyboardButton('Неважно', callback_data='17.0.'+query.data.split('8.')[1]))

			bot.edit_message_text(chat_id=query.from_user.id, message_id=query.message.message_id, text="Модель:", reply_markup=keyboard)
		else:
			bot.send_message(query.from_user.id, "Выберите марку!")
	elif query.data.startswith('12.'):
		keyboard = types.InlineKeyboardMarkup()

		for i in KKP.keys():
			keyboard.add(types.InlineKeyboardButton(i, callback_data='18.'+KKP[i]+'.'+query.data.split('12.')[1]))
		keyboard.add(types.InlineKeyboardButton('Неважно', callback_data='18.0.'+query.data.split('12.')[1]))

		bot.edit_message_text(chat_id=query.from_user.id, message_id=query.message.message_id, text="КПП:", reply_markup=keyboard)
	elif query.data.startswith('3.'):
		bot.edit_message_text(chat_id=query.from_user.id, message_id=query.message.message_id, text="Введите год от (неважно):")
		bot.register_next_step_handler(query.message, lambda message: save_filter(message.chat.id, message.text, 'year[from]', query.data.split('3.')[1]))
	elif query.data.startswith('4.'):
		bot.edit_message_text(chat_id=query.from_user.id, message_id=query.message.message_id, text="Введите год до 2020 (неважно):")
		bot.register_next_step_handler(query.message, lambda message: save_filter(message.chat.id, message.text, 'year[to]', query.data.split('4.')[1]))
	elif query.data.startswith('5.'):
		bot.edit_message_text(chat_id=query.from_user.id, message_id=query.message.message_id, text="Цену от (неважно):")
		bot.register_next_step_handler(query.message, lambda message: save_filter(message.chat.id, message.text, 'price[from]', query.data.split('5.')[1]))
	elif query.data.startswith('6.'):
		bot.edit_message_text(chat_id=query.from_user.id, message_id=query.message.message_id, text="Цену до (неважно):")
		bot.register_next_step_handler(query.message, lambda message: save_filter(message.chat.id, message.text, 'price[to]', query.data.split('6.')[1]))
	elif query.data.startswith('9.'):
		bot.edit_message_text(chat_id=query.from_user.id, message_id=query.message.message_id, text="Введите пробег (неважно):")
		bot.register_next_step_handler(query.message, lambda message: save_filter(message.chat.id, message.text, 'auto-run[to]', query.data.split('9.')[1]))
	elif query.data.startswith('10.'):
		bot.edit_message_text(chat_id=query.from_user.id, message_id=query.message.message_id, text="Введите объем от (неважно):")
		bot.register_next_step_handler(query.message, lambda message: save_filter(message.chat.id, message.text, 'auto-car-volume[from]', query.data.split('10.')[1]))
	elif query.data.startswith('11.'):
		bot.edit_message_text(chat_id=query.from_user.id, message_id=query.message.message_id, text="Введите объем до (неважно):")
		bot.register_next_step_handler(query.message, lambda message: save_filter(message.chat.id, message.text, 'auto-car-volume[to]', query.data.split('11.')[1]))
	elif query.data.startswith('13.'):
		db = SQLighter('db.db')

		db.reset_filters(query.from_user.id, query.data.split('13.')[1])
		bot.edit_message_text(chat_id=query.from_user.id, message_id=query.message.message_id, text="Фильтры сброшены.")

		db.close()
	elif query.data.startswith('14.') or query.data.startswith('15.') or query.data.startswith('16.') or query.data.startswith('17.') or query.data.startswith('18.'):
		data = query.data.split('.')

		if query.data.startswith('14.'):
			name = 'bodywork'
		elif query.data.startswith('15.'):
			name = 'region'
		elif query.data.startswith('16.'):
			name = 'car'
		elif query.data.startswith('17.'):
			name = 'model'
		elif query.data.startswith('18.'):
			name = 'auto-car-transm'

		db = SQLighter('db.db')
		filters = eval(db.get_subscriber(query.from_user.id)[0][2])

		if data == '0':
			filters[data[2]][name] = None
		else:
			filters[data[2]][name] = data[1]

		db.update_subscription(query.from_user.id, True, filters=filters)
		db.close()
		bot.edit_message_text(chat_id=query.from_user.id, message_id=query.message.message_id, text='Фильтр применен.')
	elif query.data.startswith('19.'):
		data = query.data.split('19.')[1]
		filters_keyboard = types.InlineKeyboardMarkup()

		filters_keyboard.row(types.InlineKeyboardButton('Кузов', callback_data='1.'+data), types.InlineKeyboardButton('Где искать', callback_data='2.'+data), types.InlineKeyboardButton('Год ОТ', callback_data='3.'+data))
		filters_keyboard.row(types.InlineKeyboardButton('Год ДО', callback_data='4.'+data), types.InlineKeyboardButton('Цена ОТ', callback_data='5.'+data), types.InlineKeyboardButton('Цена ДО', callback_data='6.'+data))
		filters_keyboard.row(types.InlineKeyboardButton('Марка', callback_data='7.'+data), types.InlineKeyboardButton('Модель', callback_data='8.'+data), types.InlineKeyboardButton('Пробег', callback_data='9.'+data))
		filters_keyboard.row(types.InlineKeyboardButton('Объем ОТ', callback_data='10.'+data), types.InlineKeyboardButton('Объем ДО', callback_data='11.'+data), types.InlineKeyboardButton('КПП', callback_data='12.'+data))
		filters_keyboard.row(types.InlineKeyboardButton('Сброс', callback_data='13.'+data))

		bot.edit_message_text(chat_id=query.from_user.id, message_id=query.message.message_id, text='Выберите желаемый фильтр:', reply_markup=filters_keyboard)
	elif query.data.startswith('20.'):
		db = SQLighter('db.db')
		db.delete_car(query.from_user.id, query.data.split('20.')[1])
		db.close()

		bot.edit_message_text(chat_id=query.from_user.id, message_id=query.message.message_id, text="Комплект фильтра удален.")
	elif query.data.startswith('21.'):
		db = SQLighter('db.db')
		text = ''
		filters = eval(db.get_subscriber(query.from_user.id)[0][2])[query.data.split('21.')[1]]

		if filters['bodywork'] != None:
			text += 'Кузов: {}\n'.format(filters['bodywork'])
		else:
			text += 'Кузов: не важен\n'

		if filters['region'] != None:
			text += 'Где искать: {}\n'.format(filters['region'])
		else:
			text += 'Где искать: не важен\n'

		if filters['year[from]'] != None:
			text += 'Год ОТ: {}\n'.format(filters['year[from]'])
		else:
			text += 'Год ОТ: не важен\n'

		if filters['year[to]'] != None:
			text += 'Год ДО: {}\n'.format(filters['year[to]'])
		else:
			text += 'Год ДО: не важен\n'

		if filters['price[from]'] != None:
			text += 'Цена ОТ: {}\n'.format(filters['price[from]'])
		else:
			text += 'Цена ОТ: не важен\n'

		if filters['price[to]'] != None:
			text += 'Цена ДО: {}\n'.format(filters['price[to]'])
		else:
			text += 'Цена ДО: не важен\n'

		if filters['car'] != None:
			text += 'Марка: {}\n'.format(filters['car'])
		else:
			text += 'Марка: не важен\n'

		if filters['model'] != None:
			text += 'Модель: {}\n'.format(filters['model'])
		else:
			text += 'Модель: не важен\n'

		if filters['auto-run[to]'] != None:
			text += 'Пробег: {}\n'.format(filters['auto-run[to]'])
		else:
			text += 'Пробег: не важен\n'

		if filters['auto-car-volume[from]'] != None:
			text += 'Объём ОТ: {}\n'.format(filters['auto-car-volume[from]'])
		else:
			text += 'Объём ОТ: не важен\n'

		if filters['auto-car-volume[to]'] != None:
			text += 'Объём ДО: {}\n'.format(filters['auto-car-volume[to]'])
		else:
			text += 'Объём ДО: не важен\n'

		if filters['auto-car-transm'] != None:
			text += 'КПП: {}\n'.format(filters['auto-car-transm'])
		else:
			text += 'КПП: не важен\n'

		bot.edit_message_text(chat_id=query.from_user.id, message_id=query.message.message_id, text=text)
		db.close()

	bot.answer_callback_query(query.id)

def add_car(message):
	db = SQLighter('db.db')
	db.add_car(message.chat.id, message.text)
	db.close()

	bot.send_message(message.chat.id, "Комплект фильтра добавлен.")

@bot.message_handler(commands=['add_car'])
def add_car_command(message):
	db = SQLighter('db.db')

	if message.chat.id in [i[0] for i in db.get_subscriptions()]:
		bot.send_message(message.chat.id, 'Введите название комплекта фильтра:')
		bot.register_next_step_handler(message, add_car)
	else:
		bot.send_message(message.chat.id, "Вы не подписаны.")

	db.close()

@bot.message_handler(commands=['delete_car'])
def delete_car_command(message):
	db = SQLighter('db.db')

	if message.chat.id in [i[0] for i in db.get_subscriptions()]:
		keyboard = types.InlineKeyboardMarkup()
		subscriber = db.get_subscriber(message.chat.id)

		for i in eval(subscriber[0][2]).keys():
			keyboard.add(types.InlineKeyboardButton(i, callback_data='20.'+i))
		bot.send_message(message.chat.id, 'Выберите комплект фильтра:', reply_markup=keyboard)
	else:
		bot.send_message(message.chat.id, "Вы не подписаны.")

	db.close()

@bot.message_handler(commands=['show_filters'])
def show_filters(message):
	db = SQLighter('db.db')

	if message.chat.id in [i[0] for i in db.get_subscriptions()]:
		keyboard = types.InlineKeyboardMarkup()
		subscriber = db.get_subscriber(message.chat.id)

		for i in eval(subscriber[0][2]).keys():
			keyboard.add(types.InlineKeyboardButton(i, callback_data='21.'+i))
		bot.send_message(message.chat.id, 'Выберите комплект фильтра:', reply_markup=keyboard)
	else:
		bot.send_message(message.chat.id, "Вы не подписаны.")

	db.close()

def schedule(wait_for):
	while True:
		sleep(wait_for)

		db = SQLighter('db.db')

		for i in db.get_subscriptions():
			for j, k in eval(i[2]).items():
				sg = KolesaKz('users/'+str(i[0])+'.txt', filters=k)
				for l in sg.new_cars():
					bot.send_message(i[0], 'Новая объявление в %s: %s' % (j, l), disable_notification=True)

		db.close()

if __name__==  '__main__':
	Process(target=schedule, args=(250, )).start()
	bot.polling(none_stop=True)
