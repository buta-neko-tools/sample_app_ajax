import psycopg2
from psycopg2.extras import DictCursor

class postgres:
	def connection(self,host,user,password,dbname,port):
		self.conn=psycopg2.connect(host=host,dbname=dbname,user=user,password=password,port=port)
		self.conn.autocommit=True
		self.dictcur=self.conn.cursor(cursor_factory=DictCursor)

	def fetchall_dict(self,sql):
		self.dictcur.execute(sql)
		return [dict(r) for r in self.dictcur.fetchall()]

host='ec2-34-202-54-225.compute-1.amazonaws.com'
dbname='d1mm72kta8mglb'
port='5432'
user='bpldtuvfxuwtvc'
password='da41ca9d74c46db9ec8f61cf8d32cf15c4f1c3adeb11cbda314545ad2fd68bc6'

pg = postgres()
pg.connection(host=host,port=port,user=user,password=password,dbname=dbname)
sqm_dict = pg.fetchall_dict('SELECT * FROM applications_searchquerymodel')
print(sqm_dict)
udm_dict = pg.fetchall_dict('SELECT * FROM applications_userdatamodel')
print(udm_dict)