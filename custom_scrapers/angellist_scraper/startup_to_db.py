import psycopg2
import glob

from bs4 import BeautifulSoup

connect_string = "dbname={} user={} host={} password={}".format("grepr", "spider", "localhost", "write_only")
_conn = psycopg2.connect(connect_string)

def execSqlQuery(_conn, sql_str, sql_data):
    with _conn.cursor() as curr:
        try:
            curr.execute(sql_str, sql_data)
        except psycopg2.IntegrityError:
            _conn.rollback()
            raise Exception("sql fail")
        else:
            _conn.commit()
            return


for file_name in glob.glob("data/angel.co/*"):
    with open(file_name) as business:
        bs = BeautifulSoup(business.read(), 'lxml')
    anchor = bs.select(".startup-link")[0]
    data = {
            'angel_link': anchor.get("href"),
            'angel_id': anchor.get("data-id"),
            'common_name': anchor.getText(),
            }
    sql_str = 'INSERT INTO "Businesses" (angel_link, angel_id, common_name) VALUES (%(angel_link)s, %(angel_id)s, %(common_name)s);'

    execSqlQuery(_conn, sql_str, data)
