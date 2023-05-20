import cx_Oracle
import concurrent.futures

# Thông tin kết nối Oracle - Database 1
dsn1 = cx_Oracle.makedsn(host='<hostname1>', port=<port1>, service_name='<service_name1>')
username1 = '<username1>'
password1 = '<password1>'

# Thông tin kết nối Oracle - Database 2
dsn2 = cx_Oracle.makedsn(host='<hostname2>', port=<port2>, service_name='<service_name2>')
username2 = '<username2>'
password2 = '<password2>'

# Kích thước chunk
chunk_size = 1000

# Hàm để tạo kết nối Oracle - Database 1
def create_connection1():
    return cx_Oracle.connect(username1, password1, dsn1)

# Hàm để tạo kết nối Oracle - Database 2
def create_connection2():
    return cx_Oracle.connect(username2, password2, dsn2)

# Hàm thực hiện chuyển dữ liệu từ chunk
def process_chunk(chunk, connection2):
    cursor2 = connection2.cursor()
    insert_query = "INSERT INTO table2 (column1, column2, column3) VALUES (:1, :2, :3)"
    cursor2.executemany(insert_query, chunk)
    cursor2.close()

# Tạo connection pool cho Database 2
connection_pool2 = cx_Oracle.SessionPool(create_connection2, min=2, max=10, increment=1, threaded=True)

# Kết nối vào Database 1
connection1 = cx_Oracle.connect(username1, password1, dsn1)
cursor1 = connection1.cursor()

# Truy vấn SELECT từ Database 1
query = "SELECT * FROM table1"
cursor1.execute(query)

# Lấy kết quả từ Database 1
results = cursor1.fetchmany(chunk_size)

# Kết nối vào Database 2 và sử dụng connection pool
with concurrent.futures.ThreadPoolExecutor() as executor:
    while results:
        # Tạo một danh sách các chunk từ kết quả
        chunks = [results[i:i+chunk_size] for i in range(0, len(results), chunk_size)]
        
        # Gửi các tác vụ xử lý chunk
        futures = []
        for chunk in chunks:
            # Lấy kết nối từ connection pool
            connection2 = connection_pool2.acquire()
            future = executor.submit(process_chunk, chunk, connection2)
            futures.append(future)

        # Chờ cho tất cả các tác vụ hoàn thành
        concurrent.futures.wait(futures)

        # Trả lại kết nối vào connection pool
        for future in futures:
            connection2 = future.result()
            connection_pool2.release(connection2)

        # Tiếp tục lấy kết quả tiếp theo từ Database 1
        results = cursor1.fetchmany(chunk_size)

# Đóng kết nối
cursor1.close()
connection1.close()
