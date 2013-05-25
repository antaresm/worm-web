
from django.conf import settings
import MySQLdb


def password():
    return settings.DB_PASSWORD


def get_db():
    return MySQLdb.connect(host="localhost", user="root", passwd=password(), db="worm", charset='utf8')


def get_table_schema(table_name):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("describe " + table_name)
    result = cursor.fetchall()
    db.close()
    return result


def dbdata_tojson(t_name, db_data, allData=True):
    result_data = []
    schema = get_table_schema(t_name)
    field_num = 0
    for row in db_data:
        result_row = dict()
        for value in row:
            if value.__class__.__name__ == 'datetime':
                value = str(value)
            field_name = schema[field_num][0]
            field_num += 1
            result_row[field_name] = value
        if not allData:
            return result_row
        else:
            result_data.append(result_row)
            field_num = 0
    return result_data