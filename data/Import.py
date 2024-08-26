import csv
import sqlite3

con = sqlite3.connect('backend/db.sqlite3')
cur = con.cursor()

with open('data/ingredients.csv', 'r', encoding='utf8') as fin:
    dr = csv.DictReader(fin, delimiter=',')
    to_db = [(i['id'], i['name'], i['measurement_unit']) for i in dr]

cur.executemany(
    '''INSERT INTO recipes_ingredients(id, name, measurement_unit)
    VALUES (?, ?, ?);''',
    to_db)
con.commit()
con.close()
