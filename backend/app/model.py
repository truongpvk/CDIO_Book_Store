import mysql.connector
from sqlalchemy import create_engine
from typing import List, Tuple

HOST = '127.0.0.1'
USER = 'root'
PASSWORD = 'truong181004'
DATABASE = 'bookstore'

class DatabaseConnection:
    def __init__(self, host=HOST, user=USER, password=PASSWORD, database=DATABASE) -> None:
        self.connection = mysql.connector.connect(host=host, user=user, passwd=password, database=database)
        self.cur = self.connection.cursor()
    
    def getTableColumn(self, table_name):
        self.cur.execute(f'show columns from {table_name}')
        columns = (self.cur.fetchall())

        result = []
        for col in columns:
            result.append(col[0])
        
        return result[1:]

    def insertTable(self, table_name, value: List[Tuple]) -> None:
        columns = self.getTableColumn(table_name)
        col_str = ", ".join(map(str, columns))

        value_x = ["%s" for _ in range(len(columns))]
        val_str = ", ".join(map(str, value_x))

        sql = f"insert into {table_name} ({col_str}) values ({val_str})"
        print(sql)
        print(value)
        self.cur.executemany(sql, value)
        self.connection.commit()
    
    def searchInTable(self, table_name, column_name: list, value: tuple):
        sql = f"select * from {table_name} where "
        for i in range(len(column_name)):
            if i != len(column_name) - 1:
                sql += f"{column_name[i]} = %s and "
            else:
                sql += f"{column_name[i]} = %s"
                break
        
        self.cur.execute(sql, value)
        result = self.cur.fetchall()

        return result

    def getTableData(self, table_name, columns: list):
        column_sql = ", ".join(map(str, columns))
        sql = f"select {column_sql} from {table_name}"
        self.cur.execute(sql)
        result = self.cur.fetchall()
        return result

