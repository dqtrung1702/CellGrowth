import cx_Oracle
import concurrent.futures

# Thông tin kết nối Oracle
dns = '10.15.68.46:1521/orclpdb1'
username = 'inv'
password = '12345678'
# Số lượng kết nối trong pool
pool_size = 5

# Tạo connection pool
connection_pool = cx_Oracle.SessionPool(username, password, dns, encoding="UTF-8", min=2, max=pool_size, increment=1, threaded=True)

# Hàm thực hiện truy vấn Oracle
def execute_query(query):
    connection = connection_pool.acquire()
    cursor = connection.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    return result

# Ví dụ sử dụng connection pool
query = "SELECT tin,ind_sector FROM mv_tin"
with concurrent.futures.ThreadPoolExecutor() as executor:
    # Gửi các tác vụ thực thi truy vấn
    results = executor.submit(execute_query, query).result()

# In kết quả
for row in results:
    print(row)