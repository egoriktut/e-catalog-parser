import requests
from bs4 import BeautifulSoup as bs
import sqlite3

class Parser:

    items_my = {}
    category = ''

    def __init__(self, link):
        self.link = link
        self.cite = requests.get(link)

    def add_this(self, item_key, item_value):
        self.items_my[item_key] = item_value

    def show_items(self):
        for key, value in self.items_my.items():
            print(f"{key} : {value}")

    def create_tables(self):
        try:
            my_bd = sqlite3.connect('info.db')
            cursor = my_bd.cursor()
            table = f'''CREATE TABLE category(
                                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                                            tittle TEXT
                                            );'''
            cursor.execute(table)

            table = f'''CREATE TABLE parameter(
                                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                                            id_category INTEGER,
                                            tittle TEXT,
                                            FOREIGN KEY (id_category)  REFERENCES category (id)
                                            );'''
            cursor.execute(table)

            table = f'''CREATE TABLE product(
                                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                                            name TEXT,
                                            price TEXT,
                                            id_category INTEGER,
                                            FOREIGN KEY (id_category)  REFERENCES category (id)
                                            );'''
            cursor.execute(table)

            table = f'''CREATE TABLE parameter_prod_value(
                                            id_parameter INTEGER,
                                            id_category INTEGER,
                                            id_product INTEGER,
                                            value TEXT,
                                            FOREIGN KEY (id_parameter)  REFERENCES parameter (id),
                                            FOREIGN KEY (id_category)  REFERENCES category (id),
                                            FOREIGN KEY (id_product)  REFERENCES product (id)
                                            );'''
            cursor.execute(table)

            my_bd.commit()
            cursor.close()
        except sqlite3.Error as error:
            # print("Error to connect sqlite", error)
            pass
        finally:
            if my_bd:
                my_bd.close()
                print("Successful create!")

    def storge_info(self):
        try:
            my_bd = sqlite3.connect('info.db')
            cursor = my_bd.cursor()
            cursor.execute("SELECT * FROM category WHERE tittle = ?", (self.category,))
            data = cursor.fetchall()
            id_cat = ''
            if len(data) == 0:
                add_category = f"""INSERT INTO category
                                              (id, tittle)  VALUES  (NULL, '{self.category}')"""
                cursor.execute(add_category)
                id_cat = cursor.lastrowid
            else:
                id_cat = data[0][0]
            for name, cost in self.items_my.items():
                add_prod = f"""INSERT INTO product
                                    (id, name, price, id_category)  VALUES  (NULL, '{name}', {cost[0]}, {id_cat})"""
                cursor.execute(add_prod)
                id_prod = cursor.lastrowid
                for i in range(1, len(cost)):
                    for j in cost[1][0]:
                        cursor.execute("SELECT * FROM parameter WHERE tittle = ?", (j[0],))
                        data = cursor.fetchall()
                        if len(data) == 0:
                            add_param = f"""INSERT INTO parameter
                                                    (id, id_category, tittle)  VALUES  (NULL, '{id_cat}', '{j[0]}')"""
                            cursor.execute(add_param)
                        for k in j[1]:
                            cursor.execute("SELECT * FROM parameter WHERE tittle = ?", (j[0],))
                            data = cursor.fetchall()
                            id_param = data[0][0]
                            add_param_value = f"""INSERT INTO parameter_prod_value
                (id_parameter, id_category, id_product, value)  VALUES  ('{id_param}', '{id_cat}', '{id_prod}', '{k}')"""
                            cursor.execute(add_param_value)
            my_bd.commit()
            cursor.close()

        except sqlite3.Error as error:
            print("Error to connect sqlite", error)
        finally:
            if my_bd:
                my_bd.close()
                print("Successful storge!")
                exit(0)

    def get_text(self):
        with open('main.html', 'w') as output_file:
            output_file.write(self.cite.text)
        soup = bs(self.cite.text, "html.parser")
        names = soup.find_all('div', class_='model-short-title')
        costs = soup.find_all('div', class_='model-price-range')
        tags = soup.find_all('div', class_='m-s-f2')
        self.category = soup.find_all('h1', class_='t2')[0].text.replace(' ', '_')
        for name, cost, tag in zip(names, costs, tags):
            key = separate_string(str(name))
            value = separate_string(str(cost.span))
            brief_info = []
            temp = tag.find_all('div')
            temp_brief_info = []
            for characteristics in temp:
                if characteristics.text.strip() != '':
                    temp_brief_info.append(separate_tag(characteristics.text))
            brief_info.append(temp_brief_info)
            self.add_this(key.strip(), [int(value.replace(' ', '')), brief_info])
        self.create_tables()
        self.storge_info()


def separate_string(item):  # получение нужных данных
    return item.split('>')[1].split('<')[0]


def separate_tag(tag):
    arr = []
    tag = tag.split(':')
    arr.append(tag[0])
    arr.append(tag[1].split(','))
    return tuple(arr)


def main():
    print("Enter a link")
    link = input()
    try:
        my_class = Parser(link)
        if my_class.cite.status_code == 200:
            print("Successful connect!")
            my_class.get_text()
        else:
            print("Something went wrong!\n", my_class.cite.status_code)
            main()
    except Exception:
        print("\n!!!\nSomething went wrong!\nCheck the link!\n!!!\n")
        main()


if __name__ == '__main__':
    main()
