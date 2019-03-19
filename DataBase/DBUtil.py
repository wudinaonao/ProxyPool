import os
import sys
sys.path.append(os.path.split(os.path.dirname(os.path.abspath(__file__)))[0])

from DBUtils.PooledDB import PooledDB
import pymysql
from Config import DataBase as DataBaseConfig
from Tools.Log import Log as logger

class DBUtil():
    
    # create link pool
    pool = PooledDB(creator=pymysql,
                    mincached=16,
                    maxcached=32,
                    maxconnections=32,
                    host=DataBaseConfig.HOST,
                    port=int(DataBaseConfig.PORT),
                    user=DataBaseConfig.USERNAME,
                    passwd=DataBaseConfig.PASSWORD,
                    db=DataBaseConfig.DATABASE_NAME,
                    charset="utf8")

    def insert(self, tableName, info):
        '''
        insert data to tabel
        :param tableName:
        :param info: a dictionary
        :return:
        '''
        conn = self.pool.connection()
        cursor = conn.cursor()
        try:
            # set columns
            columns = ""
            for column in info.keys():
                columns +=  str(column) + ", "
            columns = columns[:-2]
            # set values
            values = ""
            for value in info.values():
                values += "'" + str(value) + "'"+ ", "
            values = values[:-2]
            # set sql string
            sql = "INSERT INTO {0} ({1}) VALUES ({2})".format(
                tableName,
                columns,
                values
            )
            # set id = null
            sql = sql.replace("'null'", "null")
            sql = sql.replace('"null"', "null")
            cursor.execute(sql)
            conn.commit()
            return True
        except Exception:
            return False
        finally:
            cursor.close()
            conn.close()

    def delete(self, tableName, position=None):
        '''
        delete row from table, if position is None, clean table
        :param tableName:
        :param position:    position is a dictionary
        :return:
        '''
        conn = self.pool.connection()
        cursor = conn.cursor()
        try:
            if position is not None:
                if len(position) == 1:
                    key = [key for key in position.keys()][0]
                    sql = "DELETE FROM " + str(tableName) + " WHERE " + str(key) + " = " + "'" + position[key] + "'"
                else:
                    keys = [key for key in position.keys()]
                    sql = "DELETE FROM " + str(tableName) + " WHERE "
                    for key in keys:
                        sql += str(key) + " = " + "'" + position[key] + "'" + " and "
                    sql = sql[:len(sql) - 5]
            else:
                sql = "TRUNCATE TABLE {0}".format(tableName)
            cursor.execute(sql)
            conn.commit()
            return True
        except Exception:
            return False
        finally:
            cursor.close()
            conn.close()
    
    def update(self, tableName, info):
        '''
        指定表名,和更新数据更新表
        更新数据为一个字典,例如:
        {
            "key_values":{"key1":"value1","key2":"value2"...},
            "postions":{"key1":"value1","key2":"value2"...}
        }
        key_values接受多个参数,但是注意该表里是否有该keys
        postions接受多个参数,但是目前判断条件只用and,如果需要or请重写代码

        实例:
            info = {
            "key_values":{
                            "name":"naonao",
                            "age":"23",
                            "date":"940208",
                            "sex":"man"
                        },
            "postions":{
                            "sex":"man",
                            "date":"940208"
                        }
            }
        返回:     True
        '''
        conn = self.pool.connection()
        cursor = conn.cursor()
        try:
            # update values dict
            key_values_dict = info['key_values']
            # postions dict
            postions_dict = info['postions']
            sql = "UPDATE " + str(tableName) + " " + "SET" + " "
            # update values
            for key in key_values_dict.keys():
                sql += str(key) + "=" + "'" + str(key_values_dict[key]) + "'" + ","
            sql = sql[:len(sql) - 1]
            sql += " WHERE "
            # postion row
            if len(postions_dict) == 1:
                postion_key = [key for key in postions_dict][0]
                sql += postion_key
                sql += " = '{0}'".format(postions_dict[postion_key])
            else:
                postion_key_ls = [key for key in postions_dict]
                for key in postion_key_ls:
                    sql += key + " = " + "'" + postions_dict[key] + "'" + " and "
                sql = sql[:len(sql) - 5]
            cursor.execute(sql)
            conn.commit()
            return True
        except Exception:
            return False
        finally:
            cursor.close()
            conn.close()
            
    def query(self, tableName, position=None):
        '''
        输入表名和位置查询当前行,若位置为空则查询全部.
        如果postion存在key"query_col"则请求选择列
        例如:
        postions = {
                    "query_col":"name"
                    }
        请求name列所有内容

        postions = {
                    "name:"wen lyuzhao",
                    "age":"24"
                    }
        请求name=wen lyuzhao并且age=24的行

        返回格式为一个列表字典,例如:
        [
            {"name":"naonao","name":"mama"}
            ...
        ]
        '''
        conn = self.pool.connection()
        cursor = conn.cursor()
        try:
            # judge have or not positions key
            if position is not None:
                # has postion
                # get column all values if have "query_col" key
                if "query_col" in position.keys():
                    rows = position["query_col"]
                    sql = "SELECT " + str(rows) + " FROM " + str(tableName)
                else:
                    # has postion
                    sql = "SELECT * FROM " + str(tableName) + " WHERE "
                    for key in position.keys():
                        sql += key + " = " + "'" + position[key] + "'" + " and "
                    sql = sql[:len(sql) - 5]
            else:
                # get all
                sql = "SELECT * FROM " + str(tableName)
            cursor.execute(sql)
            conn.commit()
            resultTupleList = cursor.fetchall()
            resultDictList = []
            for result in resultTupleList:
                resultDict = {}
                resultDict.setdefault("id", result[0])
                resultDict.setdefault("ip", result[1])
                resultDict.setdefault("port", result[2])
                resultDict.setdefault("type", result[3])
                resultDict.setdefault("location", result[4])
                resultDict.setdefault("speed", result[5])
                resultDict.setdefault("lastUpdateTime", result[6])
                resultDict.setdefault("md5", result[7])
                resultDict.setdefault("weight", result[8])
                resultDictList.append(resultDict)
            return resultDictList
        except Exception:
            return []
        finally:
            cursor.close()
            conn.close()
            
    def queryIsExist(self, tableName, position):
        '''
        check is exist
        :param table_name:
        :param key:    position condition     --> MD5
        :param value:  position value         --> XXX....
        :return:
        '''
        conn = self.pool.connection()
        # conn.autocommit(1)
        cursor = conn.cursor()
        try:
            if len(position) == 1:
                key = [key for key in position.keys()][0]
                sql = "SELECT * FROM " + str(tableName) + " WHERE " + str(key) + " = " + "'" + position[key] + "'"
            else:
                keys = [key for key in position.keys()]
                sql = "SELECT * FROM " + str(tableName) + " WHERE "
                for key in keys:
                    sql += str(key) + " = " + "'" + position[key] + "'" + " and "
                sql = sql[:len(sql) - 5]
            # sql = "SELECT * FROM {0} WHERE {1} = '{2}'".format(table_name, key, value)
            cursor.execute(sql)
            conn.commit()
            resultList = cursor.fetchall()
            if len(resultList) != 0:
                return True
            else:
                return False
        except Exception:
            return False
        finally:
            cursor.close()
            conn.close()

if __name__ == '__main__':
    
    database = DBUtil()
    print(database.queryIsExist("Verified", {"md5": "AD27BF22D6F354137A2BE88AD314B475"}))
    pass