###Chat Bot

import sqlite3 as lite
database = lite.connect('user.db')
def main():
    list = database.execute("SELECT * FROM User")
    # list = list.fetchall()
    # print(list)
    # Example SQL print











if __name__ == '__main__':
    main()