import cx_Oracle

class db:
	def __init__(self, user, pw, tns):
		self.pool = cx_Oracle.SessionPool(user, pw, tns, min=2, max=20, increment=1, encoding="UTF-8")

	def read(self, command, flat=True):
		con = self.pool.acquire()
		cur = con.cursor()
		f = cur.execute(command).fetchall()
		self.pool.release(con)
		if not f or not flat:
			return f
		else:
			if len(f[0]) == 1:
				f = [i[0] for i in f]
				if len(f) == 1:
					f = f[0]
			return f

	def read1(self, command):
		con = self.pool.acquire()
		cur = con.cursor()
		f = cur.execute(command).fetchone()
		self.pool.release(con)
		if len(f) == 1:
			f = f[0]
		return f

	def write(self, command):
		con = self.pool.acquire()
		cur = con.cursor()
		cur.execute(command)
		con.commit()
		self.pool.release(con)

	def __del__(self):
		self.pool.close()

