from rq import Queue
import worker
import time
q = Queue(connection=worker.conn)

import task
# from utils import count_words_at_url
result = q.enqueue(task.count_words_at_url, 'https://www.google.com/')

print(result.id)
