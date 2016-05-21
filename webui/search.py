connect_string = "dbname={} user={} host={} password={}".format("grepr", "spider", "tuamadre.net", DATABASE['password'])
self._conn = psycopg2.connect(connect_string)

