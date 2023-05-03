import mysql.connector
from datetime import datetime, timezone, timedelta


class InviteCodeCounter:
    def __init__(self, conn_str, table='InviteCode'):
        """
        初始化 InviteCodeCounter 类
        :param conn_str: MySQL 数据库连接字符串
        :param table: 存储邀请码的表名
        """
        self.conn_str = conn_str
        self.table = table
        self.codes = {} # 存储邀请码和对应的最大次数、剩余次数和日期
        self.update_today() # 更新当前日期
        self.load_data() # 从数据库加载数据

    def update_today(self):
        """
        更新当天日期
        """
        tz = timezone(timedelta(hours=8)) # 设置时区为北京时区
        self.today = datetime.now(tz).strftime('%Y-%m-%d') # 获取当前日期

    def load_data(self):
        """
        从数据库加载邀请码数据
        """
        cnx = mysql.connector.connect(**self.conn_str)
        cursor = cnx.cursor()
        query = "SELECT code, max_times, remain_times, date FROM {}".format(self.table)
        cursor.execute(query)
        for code, max_times, remain_times, date in cursor:
            if code not in self.codes:
                self.codes[code] = {}
            date = date.strftime('%Y-%m-%d')
            self.codes[code][date] = {'max_times': max_times, 'remain_times': remain_times}
        cursor.close()
        cnx.close()

    def get_remain_times(self, code):
        """
        获取邀请码的剩余次数
        :param code: 邀请码
        :return: 剩余次数，如果邀请码不存在则返回 -1
        """
        if code not in self.codes:
            return -1
        self.update_today() # 更新当前日期
        if self.today not in self.codes[code]:
            # 如果今天还没有记录，从之前的记录中去取(但是不更新状态)
            if len(self.codes[code]) > 0:
                last_date = sorted(self.codes[code].keys())[-1]
                return self.codes[code][last_date]['max_times']
                # self.codes[code][self.today] = {'max_times': self.codes[code][last_date]['max_times'], 'remain_times': self.codes[code][last_date]['max_times']}
            else:
                return 100 #  self.codes[code]['max_times']
        return self.codes[code][self.today]['remain_times']

    def add_code(self, code, max_times):
        """
        添加邀请码
        :param code: 邀请码
        :param max_times: 最大使用次数
        """
        cnx = mysql.connector.connect(**self.conn_str)
        cursor = cnx.cursor()
        query = "INSERT INTO {} (code, max_times, remain_times, date) VALUES (%s, %s, %s, %s)".format(self.table)
        cursor.execute(query, (code, max_times, max_times, self.today))
        cnx.commit()
        cursor.close()
        cnx.close()
        if code not in self.codes:
            self.codes[code] = {}
        self.codes[code][self.today] = {'max_times': max_times, 'remain_times': max_times}

    def use_code(self, code):
        """
        使用邀请码
        :param code: 邀请码
        :return: 如果使用成功则返回 True，否则返回 False
        """
        self.update_today() # 更新当前日期
        if code in self.codes and self.today in self.codes[code]:
            remain_times = self.codes[code][self.today]['remain_times']
            if remain_times > 0:
                cnx = mysql.connector.connect(**self.conn_str)
                cursor = cnx.cursor()
                query = "UPDATE {} SET remain_times = remain_times - 1 WHERE code = %s AND date = %s".format(self.table)
                cursor.execute(query, (code, self.today))
                cnx.commit()
                cursor.close()
                cnx.close()
                self.codes[code][self.today]['remain_times'] = remain_times - 1
                return True
        else:
            print('Enter branch')
            max_times = self.get_remain_times(code)
            if max_times >= 0:
                print('Enter sub branch')
                self.add_code(code, max_times)
                return self.use_code(code)
        return False

"""
CREATE TABLE `InviteCode` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `code` varchar(255) NOT NULL,
  `max_times` int(11) NOT NULL,
  `remain_times` int(11) NOT NULL,
  `date` date NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code_date` (`code`,`date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"""
