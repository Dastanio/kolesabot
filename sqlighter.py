import psycopg2

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

    def __init__(self):
        """Подключаемся к БД и сохраняем курсор соединения"""
        self.connection = psycopg2.connect(dbname='dbh72hr25i5v8u', user='ckuncxrtjnqkcc',
            password='8b3cb42e4b499e5697ae6040c84e92544cc86821d66ce14dc2328ac2a2fdd95f',
            host='ec2-54-224-124-241.compute-1.amazonaws.com')
        self.cursor = self.connection.cursor()

    def create_table(self):
        with self.connection:
            """Создаем таблицу subscriptions"""
            return self.cursor.execute("""CREATE TABLE IF NOT EXISTS subscriptions(
                user_id INT,
                status BOOLEAN,
                filters TEXT
                )""")

    def get_subscriptions(self, status=True):
        """Получаем всех активных подписчиков бота"""
        with self.connection:
            self.cursor.execute("SELECT * FROM subscriptions WHERE status = (%s)", (status,))
            return self.cursor.fetchall()

    def subscriber_exists(self, user_id):
        """Проверяем, есть ли уже юзер в базе"""
        with self.connection:
            self.cursor.execute("SELECT * FROM subscriptions WHERE user_id = (%s)", (user_id,))
            result = self.cursor.fetchall()
            return bool(len(result))

    def get_subscriber(self, user_id):
        """Получаем данные подписчика по айди"""
        with self.connection:
            self.cursor.execute('SELECT * FROM subscriptions WHERE user_id = (%s)', (user_id,))
            return self.cursor.fetchall()

    def add_subscriber(self, user_id, status=True, filters=standart_filters):
        """Добавляем нового подписчика"""
        with self.connection:
            return self.cursor.execute("INSERT INTO subscriptions (user_id, status, filters) VALUES((%s),(%s),(%s))", (user_id, status, str(filters)))

    def update_subscription(self, user_id, status, filters=standart_filters):
        """Обновляем статус подписки пользователя"""
        with self.connection:
            self.cursor.execute("UPDATE subscriptions SET status = (%s) WHERE user_id = (%s)", (status, user_id))
            self.cursor.execute("UPDATE subscriptions SET filters = (%s) WHERE user_id = (%s)", (str(filters), user_id))

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

            return self.cursor.execute("UPDATE subscriptions SET filters = (%s) WHERE user_id = (%s)", (str(standart_filters), user_id))

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

            return self.cursor.execute("UPDATE subscriptions SET filters = (%s) WHERE user_id = (%s)", (str(filters), user_id))

    def delete_car(self, user_id, car):
        with self.connection:
            filters = eval(self.get_subscriber(user_id)[0][2])
            filters.pop(car)

            return self.cursor.execute("UPDATE subscriptions SET filters = (%s) WHERE user_id = (%s)", (str(filters), user_id))

    def close(self):
        """Закрываем соединение с БД"""
        self.connection.close()