import redis
import pymysql
import json
import time
from datetime import datetime

# 将数据库任务清单推到redis
class TaskSync:
    def __init__(self):
        # self.logger = self.setup_logger()
        # self.redis_conn = redis.RedisCluster(
        #     startup_nodes=[{"host": "redis1", "port": 6379}, ...],
        #     password="your_password",
        #     decode_responses=False
        # )
        self.redis_conn = redis.Redis(host='localhost', port=6379, db=0)
        self.mysql_conn = pymysql.connect(
            host="127.0.0.1",
            user="root",
            password="123456",
            database="xxxx",
            charset='utf8mb4',
        )
        self.batch_size = 500
        self.queue_key = "crawl_queue:urls"

    # def setup_logger(self):
    #     logger = logging.getLogger('task_sync')
    #     logger.setLevel(logging.INFO)
    #     handler = logging.FileHandler('/logs/task_sync.log')
    #     formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    #     handler.setFormatter(formatter)
    #     logger.addHandler(handler)
    #     return logger

    def fetch_tasks(self):
        with self.mysql_conn.cursor() as cursor:
            cursor.execute("""
                SELECT t.*, s.request_interval, s.concurrent_limit 
                FROM crawl_tasks t
                JOIN site_config s ON t.site_id = s.site_id
                WHERE t.status = 'pending'
                ORDER BY t.priority DESC, t.create_time ASC
                LIMIT %s FOR UPDATE SKIP LOCKED
            """, (self.batch_size,))
            query_data = cursor.fetchall()

            result = []
            for row in query_data:
                task = {
                    "id": row[0],
                    "url": row[2],
                    "method": row[3],
                    "payload": row[4],
                    "site_id": row[1],
                    "use_selenium": row[5],
                    "parser_module": row[6],
                    "meta_data": row[9],
                    "priority": row[7],
                    "request_interval": row[13],
                    "concurrent_limit": row[14],
                }
                result.append(task)

            return result


    def push_to_redis(self, tasks):
        with self.redis_conn.pipeline() as pipe:
            for task in tasks:
                task_data = {
                    "task_id": task['id'],
                    "url": task['url'],
                    "method": task['method'],
                    "payload": task['payload'],
                    "site_id": task['site_id'],
                    "use_selenium": task['use_selenium'],
                    "parser": task['parser_module'],
                    "meta": json.loads(task['meta_data']) if task['meta_data'] else {},
                    "priority": task['priority'],
                    "request_interval": task['request_interval'],
                    "concurrent_limit": task['concurrent_limit']
                }
                # 使用有序集合按优先级排序
                pipe.rpush(self.queue_key, json.dumps(task_data))

            pipe.execute()

    def update_db_status(self, task_ids):
        with self.mysql_conn.cursor() as cursor:
            cursor.execute("""
                UPDATE crawl_tasks 
                SET status = 'processing', update_time = %s 
                WHERE id IN %s
            """, (datetime.now(), tuple(task_ids)))
            self.mysql_conn.commit()

    def run(self):
        # self.logger.info("Task Sync Started")
        while True:
            try:
                tasks = self.fetch_tasks()
                if tasks:
                    task_ids = [t['id'] for t in tasks]
                    self.push_to_redis(tasks)
                    print("添加完成")
                    # self.update_db_status(task_ids)
                    # self.logger.info(f"Synced {len(tasks)} tasks to Redis")
                    time.sleep(15)
            except Exception as e:
                # self.logger.error(f"Sync error: {str(e)}", exc_info=True)
                time.sleep(60)

if __name__ == "__main__":
    daemon = TaskSync()
    daemon.run()
