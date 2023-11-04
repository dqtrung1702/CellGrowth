import cx_Oracle
import concurrent.futures

# Thông tin kết nối Oracle
dns = '10.15.68.46:1521/orclpdb1'
username = 'inv'
password = '12345678'
dns2 = '10.15.68.46:1521/orclpdb1'
username2 = 'trns2tpr'
password2 = 'trns2tpr'
# Số lượng kết nối trong pool
pool_size = 60
# Số lượng luồng
num_threads = 50
xgets = [
        "SELECT tin,ind_sector FROM mv_tin order by tin OFFSET 0  ROWS FETCH NEXT 2 ROWS ONLY",
        "SELECT tin,ind_sector FROM mv_tin order by tin OFFSET 1  ROWS FETCH NEXT 2 ROWS ONLY"
        ]
xpush = "INSERT INTO testx (tin, ind_sector) VALUES (:1, :2)"
# Biến đếm số lượng kết nối tới connectionpool
num_conn2pool = [0]
num_conn2pool2 = [0]
# Hàm callback được gọi khi kết nối được giải phóng
def cnt_conn2pool(connection,requested_tag):
    # print(connection)
    # print(requested_tag)
    num_conn2pool[0] += 1
def cnt_conn2pool2(connection,requested_tag):
    # print(connection)
    # print(requested_tag)
    num_conn2pool2[0] += 1
i = 0
def xdata():
    # Kết nối vào 2 Database và sử dụng connection pool
    connection_pool = cx_Oracle.SessionPool( username, password, dns, encoding="UTF-8", min=1, max=pool_size, increment=1, threaded=True, getmode=cx_Oracle.SPOOL_ATTRVAL_WAIT, session_callback=cnt_conn2pool)
    connection_pool2= cx_Oracle.SessionPool( username2, password2, dns2, encoding="UTF-8", min=1, max=pool_size, increment=1, threaded=True, getmode=cx_Oracle.SPOOL_ATTRVAL_WAIT, session_callback=cnt_conn2pool2)
    # Tạo danh sách chứa kết quả
    result = []
    # Hàm con để thực hiện select theo chunk
    
    def select_chunk_from_dbs_n_insert_db2(xget,xpush):
        connection = connection_pool.acquire()
        connection2 = connection_pool2.acquire()
        cursor = connection.cursor()
        cursor2 = connection2.cursor()
        # xget trả ra số cột và thứ tự cột phải tương ứng với xpush
        cursor.execute(xget)
        rows = cursor.fetchall()
        for row in rows:
            # line = {}
            # for key,val in row.items():
            #     if isinstance(val, date):
            #         value = val.replace(tzinfo=pytz.UTC).astimezone(local_zone).strftime('%d/%m/%Y,%H:%M:%S')  
            #     elif isinstance(val, bytes):
            #         value = str(val,'utf-8')
            #     elif isinstance(val, list):
            #         value = transf(val).jsonflobject()
            #     elif isinstance(val, dict):
            #         value = transf(val).jsonfdobject()
            #     else:
            #         value = val
            #     line.update({key:value}) 
            cursor2.execute(xpush,row)
            connection2.commit()

    # Tạo executor với số luồng đã chỉ định
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        # Thực hiện các select trên các luồng
        futures = []
        for xget in xgets:
            # Tạo chunk và gửi tác vụ select tới luồng
            future = executor.submit(select_chunk_from_dbs_n_insert_db2, xget,xpush)
            futures.append(future)
        # Đợi cho tất cả các luồng hoàn thành
        concurrent.futures.wait(futures)
    # Trả về kết quả đã select
    return result
# Gọi hàm select_data và lấy kết quả
xdataed = xdata()
# In kết quả
# for row in xdataed:
#     print(row)
# print(xdataed)