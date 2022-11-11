import psycopg2
con = psycopg2.connect(
      database="dev"
      , user="admin"
      , password="admin"
      , host="127.0.0.1"
      , port="5436"
      , options="-c search_path=dbo,uaa"
      )

cur = con.cursor()
cur.execute('''CREATE TABLE uaa.STUDENT2
      (ADMISSION INT PRIMARY KEY     NOT NULL,
      NAME           TEXT    NOT NULL,
      AGE            INT     NOT NULL,
      COURSE        CHAR(50),
      DEPARTMENT        CHAR(50));''')
print("Table created successfully")

con.commit()
con.close()