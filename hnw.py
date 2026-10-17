import sys
from pathlib import Path
import json
from pprint import pprint
import requests
import math
import random
import time
import hashlib
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import sqlite3
import mysql.connect
import redis


class Spider():
    session = requests.Session()
    session.headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
        'cache-control': 'no-cache',
        'content-type': 'application/json',
        'origin': 'https://www.cnhnb.com',
        'pragma': 'no-cache',
        'priority': 'u=1, i',
        'referer': 'https://www.cnhnb.com/',
        'sec-ch-ua': '"Chromium";v="154", "Microsoft Edge";v="154", "Not A(Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36 Edg/154.0.0.0',
        'x-b3-traceid': '0MV0B65WLMXFX5KC',
        'x-client-appid': '4',
        'x-client-environment': 'pro',
        'x-client-id': '87f01c9-d838-4976-ae14-996ea9c1e',
        'x-client-nonce': '27730fe8e5f7d9ed99ad6bcaf994654c',
        'x-client-page': '/purchase/',
        'x-client-sid': 'S_0MV0B63RWAXSYYZI',
        'x-client-sign': '7a270672aac9b7d53e7349a97ab4c164fe88e5b83fa43959ec419b8d4ba8d709403e283e289dc07b1bbb3d82191cb05d',
        'x-client-time': '1791510625893',
        'x-hn-job': 'If you see these message, I hope you dont hack us, I hope you can join us! Please visit https://www.cnhnkj.com/job.html',
    }
    # session.proxies = {
    #     "http": "http://127.0.0.1:7890",
    #     "https": "http://127.0.0.1:7890",
    # }
    
    
    def get_traceId(self):
        _BASE36 = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        def to_base36(value, width):
            chars = ""
            while value:
                value, remainder = divmod(value, 36)
                chars = _BASE36[remainder] + chars
            return chars[-width:].rjust(width, "0")
        
        timestamp = int(time.time() * 1000)
        random_part = random.randint(0, 78_364_164_095)
        return to_base36(timestamp, 9) + to_base36(random_part, 7)

    def get_nonce(self, e=True):
        t = int(time.time() * 1000)
        template = (
            "xxxxxxxxxxxxxyxxxxyxxxxxxxxxxxxx"
            if e
            else "xxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxx"
        )
        result = []
        for ch in template:
            if ch not in ("x", "y"):
                result.append(ch)
                continue
            n = math.floor((t + 16 * random.random()) % 16)
            t = math.floor(t / 16)
            value = n if ch == "x" else ((3 & n) | 8)
            result.append(format(value, "x"))
        return "".join(result)

    def build_headers(self):
        x_client_nonce = self.get_nonce()
        x_client_traceid = self.get_traceId()
        x_client_id = '87f01c9-d838-4976-ae14-996ea9c1e'
        x_client_time = str(int(time.time() * 1000))
        F = hashlib.sha256(x_client_nonce.encode('utf-8')).hexdigest()
        # print(F)
        A = hashlib.sha384(x_client_time.encode('utf-8')).hexdigest()
        # print(A)
        string = x_client_nonce + '(lo__ol)' + x_client_id
        B = hashlib.md5(string.encode('utf-8')).hexdigest()
        # print(B)
        string = f'{x_client_time}_hnw_+_--_123_)!@iiD5R4Mljlk4JWYk*YOiub2RnKkahR'
        W = hashlib.sha1(f'{x_client_time}_hnw_+_--_123_)!@iiD5R4Mljlk4JWYk*YOiub2RnKkahR'.encode('utf-8')).hexdigest()
        W = W[-16:-1]       # 15 位十六进制字符
        T = str(int(W, 16)) # 按十六进制解析，再转为十进制字符串
        # print(T)
        P = [F, A, B, T]
        I = "(o1o)".join(P)
        # print(I)
        x_client_sign = hashlib.sha384(I.encode('utf-8')).hexdigest()
        self.session.headers['x-client-nonce'] = x_client_nonce
        self.session.headers['x-client-time'] = x_client_time
        self.session.headers['x-b3-traceid'] = x_client_traceid
        self.session.headers['x-client-sign'] = x_client_sign
        return self.session.headers.copy()
    
    # def build_db(self):
    #     conn = sqlite3.connect('hnw.db')
    #     sql = """
    #         CREATE TABLE IF NOT EXISTS purchase (
    #             id INTEGER PRIMARY KEY AUTOINCREMENT,
    #             uid TEXT NOT NULL,
    #             purchase_id TEXT NOT NULL,
    #             buy_title TEXT NOT NULL,
    #             cate_name TEXT NOT NULL,
    #             authentication TEXT NOT NULL,
    #             qty_unit TEXT NOT NULL,
    #             link_name TEXT NOT NULL,
    #             explanation TEXT 
    #         )
    #     """
    #     conn.execute(sql)
    #     return conn
    
    def build_db(self):
        conn = mysql.connector.connect(
            host="localhost",
            port=3306,
            user="root",
            password="你的密码",
            database="hnw",       # 相当于原来的 hnw.db
            charset="utf8mb4",    # 中文不乱码
        )
        sql = """
            CREATE TABLE IF NOT EXISTS purchase (
                id INT PRIMARY KEY AUTO_INCREMENT,
                uid VARCHAR(64) NOT NULL,
                purchase_id VARCHAR(64) NOT NULL,
                buy_title VARCHAR(255) NOT NULL,
                cate_name VARCHAR(128) NOT NULL,
                authentication VARCHAR(128) NOT NULL,
                qty_unit VARCHAR(64) NOT NULL,
                link_name VARCHAR(255) NOT NULL,
                explanation TEXT
            ) DEFAULT CHARSET=utf8mb4
        """
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
        cur.close()
        return conn
    
    def generate_urls(self):
        for i in range(1, 100):
            page_num = i

    def get_data(self, page_num, page_size: int =10):
        headers = self.build_headers()
        conn = self.build_db()
        json_data = {
            'pageNumber': page_num,
            'pageSize': page_size,
        }
        response = self.session.post('https://pcapi.cnhnb.com/esearch-pc/api/transform/purchase/list', headers=headers, json=json_data)
        json_str = response.text
        json_dict = json.loads(json_str)
        # pprint(json_dict)
        for index, item in enumerate(json_dict['data']['datas'], start=1):
            buy_title = item['buyTitle']
            cate_name = item['cateName']
            uid = item['hnUserId']
            purchase_id = item['purchaseId']
            authentication = "已认证" if item["isAuthentication"] == 1 else "未认证"
            qty_unit = str(item['qty']) + item['unit']
            link_name = item['linkName']
            explanation = item.get('explanation', None)
            sql = """
                INSERT INTO purchase (
                    uid, purchase_id, buy_title, cate_name,
                    authentication, qty_unit, link_name, explanation
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """

            conn.execute(sql, (
                uid, purchase_id, buy_title, cate_name,
                authentication, qty_unit, link_name, explanation
            ))    
        conn.commit()
            
            
            
    def run(self):
        s = Spider()
        with ThreadPoolExecutor(max_workers=1) as pool:
            futures = {pool.submit(s.get_data, page_num): page_num for page_num in range(1, 2)}
            for future in as_completed(futures):
                page_num = futures[future]
                try:
                    result = future.result()
                    print(f"第 {page_num} 页完成")
                    # 在这里处理 result
                except Exception as e:
                    print(f"第 {page_num} 页失败：{e}")
                
                
if __name__ == "__main__":
    s = Spider()
    s.run()
    
