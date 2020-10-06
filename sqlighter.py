import sqlite3

standart_filters = {
    'Стандарт' : {
        'year[from]' : None,
        'year[to]' : None,
        'price[from]' : None,
        'price[to]' : None,
        'region' : None,
        'bodywork' : None,
        'car' : None,
        'model' : None,
        'auto-run[to]' : None,
        'auto-car-volume[from]' : None,
        'auto-car-volume[to]' : None,
        'auto-car-transm' : None
    }
}

class SQLighter:

    def __init__(self, database):
        """Подключаемся к БД и сохраняем курсор соединения"""
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()

    def get_subscriptions(self, status=True):
        """Получаем всех активных подписчиков бота"""
        with self.connection:
            return self.cursor.execute("SELECT * FROM `subscriptions` WHERE `status` = ?", (status,)).fetchall()

    def subscriber_exists(self, user_id):
        """Проверяем, есть ли уже юзер в базе"""
        with self.connection:
            result = self.cursor.execute('SELECT * FROM `subscriptions` WHERE `user_id` = ?', (user_id,)).fetchall()
            return bool(len(result))

    def get_subscriber(self, user_id):
        """Получаем данные подписчика по айди"""
        with self.connection:
            return self.cursor.execute('SELECT * FROM `subscriptions` WHERE `user_id` = ?', (user_id,)).fetchall()

    def add_subscriber(self, user_id, status=True, filters=standart_filters):
        """Добавляем нового подписчика"""
        with self.connection:
            return self.cursor.execute("INSERT INTO `subscriptions` (`user_id`, `status`, `filters`) VALUES(?,?,?)", (user_id, status, str(filters)))

    def update_subscription(self, user_id, status, filters=standart_filters):
        """Обновляем статус подписки пользователя"""
        with self.connection:
            self.cursor.execute("UPDATE `subscriptions` SET `status` = ? WHERE `user_id` = ?", (status, user_id))
            self.cursor.execute("UPDATE `subscriptions` SET `filters` = ? WHERE `user_id` = ?", (str(filters), user_id))

    def reset_filters(self, user_id, car):
        with self.connection:
            filters = eval(self.get_subscriber(user_id)[0][2])
            filters[car] = {
                'year[from]' : None,
                'year[to]' : None,
                'price[from]' : None,
                'price[to]' : None,
                'region' : None,
                'bodywork' : None,
                'car' : None,
                'model' : None,
                'auto-run[to]' : None,
                'auto-car-volume[from]' : None,
                'auto-car-volume[to]' : None,
                'auto-car-transm' : None
            }
            return self.cursor.execute("UPDATE `subscriptions` SET `filters` = ? WHERE `user_id` = ?", (str(standart_filters), user_id))

    def add_car(self, user_id, car):
        with self.connection:
            filters = eval(self.get_subscriber(user_id)[0][2])
            filters[car] = {}
            filters[car] = {
                'year[from]' : None,
                'year[to]' : None,
                'price[from]' : None,
                'price[to]' : None,
                'region' : None,
                'bodywork' : None,
                'car' : None,
                'model' : None,
                'auto-run[to]' : None,
                'auto-car-volume[from]' : None,
                'auto-car-volume[to]' : None,
                'auto-car-transm' : None
            }

            return self.cursor.execute("UPDATE `subscriptions` SET `filters` = ? WHERE `user_id` = ?", (str(filters), user_id))

    def delete_car(self, user_id, car):
        with self.connection:
            filters = eval(self.get_subscriber(user_id)[0][2])
            filters.pop(car)

            return self.cursor.execute("UPDATE `subscriptions` SET `filters` = ? WHERE `user_id` = ?", (str(filters), user_id))

    def close(self):
        """Закрываем соединение с БД"""
        self.connection.close()