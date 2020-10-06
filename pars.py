import os
import requests
from bs4 import BeautifulSoup as BS

bodywork = {'Седан' : 'sedan','Универсал' : 'station-wagon','Хэтчбек' : 'hatchback','Лимузин' : 'limousine','Купе' : 'body-coupe','Родстер' : 'body-roadster','Кабриолет' : 'cabriolet','Внедорожник' : 'suv','Кроссовер' : 'crossover-suv','Микровэн' : 'microvan','Минивэн' : 'minivan','Микроавтобус' : 'van','Фургон' : 'wagon','Пикап' : 'body-pickup','Тарга' : 'targa','Фастбек' : 'fastback','Лифтбек' : 'liftback','Хардтоп' : 'hardtop'}
KKP = {'Механика' : '1','АКПП' : '2345','Автомат' : '2','Типтроник' : '3','Вариатор' : '4','Робот' : '5'}

def get_marks():
	response = requests.get('https://kolesa.kz/cars/')
	html = BS(response.content, 'html.parser')
	marks = {}

	items = html.find('ul', class_='cross-links-list cross-links__columns cross-links__columns--3 js__links-list')
	
	for i in items.findAll('li'):
		marks[i.a.getText()] = i.a.attrs['href'].split('/')[2]

	return marks

def get_regions():
	response = requests.get('https://kolesa.kz/cars/')
	html = BS(response.content, 'html.parser')
	regions = {}

	items = html.find('ul', class_='cross-links-list cross-links__columns cross-links__columns--2')
	
	for i in items.findAll('li'):
		regions[i.a.getText()] = i.a.attrs['href'].split('/')[2]

	return regions

def get_models(car):
	response = requests.get('https://kolesa.kz/cars/' + car)
	html = BS(response.content, 'html.parser')
	models = {}

	items = html.findAll('div', class_='cross-links')

	for i in items:
		if 'Модельный ряд' in i.h2.getText(strip=True):
			for j in i.ul.findAll('li'):
				models[j.a.getText()] = j.a.attrs['href'].split('/')[3]

	return models

class KolesaKz:
	host = 'https://kolesa.kz'
	url = 'https://kolesa.kz/cars/'
	list_car_id = []
	list_car_id_file = ''

	def __init__(self, list_car_id_file, filters=None):
		self.list_car_id_file = list_car_id_file

		if(os.path.exists(list_car_id_file)):
			self.list_car_id = list(map(lambda x: x.strip(), open(list_car_id_file, 'r').readlines()))
		else:
			open(list_car_id_file, 'w').write('')

		if filters != None:
			self.filters = filters
			part1 = ['', '', '', '']
			filters_array = []

			for i, j in filters.items():
				if i == 'bodywork' and j != None:
					part1[0] = j + '/'
				elif i == 'car' and j != None:
					part1[1] = j + '/'
				elif i == 'model' and j != None:
					part1[2] = j + '/'
				elif i == 'region' and j != None:
					part1[3] = j + '/'
				elif j != None:
					filters_array.append(str(i) + '=' + str(j))

			self.url += ''.join(part1)
			if filters_array != []:
				self.url += '?' + '&'.join(filters_array)

	def new_cars(self):
		response = requests.get(self.url)
		html = BS(response.content, 'html.parser')

		cars = []
		items = html.findAll('div', class_='row vw-item list-item a-elem')

		for i in items:
			id_car = i['data-id']

			if id_car not in self.list_car_id:
				self.list_car_id.append(id_car)
				self.update_cars()

				cars.append('%s/a/show/%s' % (self.host, id_car))

		return cars

	def update_cars(self):
		with open(self.list_car_id_file, "w") as f:
			f.write('\n'.join(self.list_car_id))
