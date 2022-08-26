import sqlite3
import pandas as pd

conn = sqlite3.connect('SQLDatabase.db', check_same_thread=False)

states_list = conn.execute("SELECT STATE FROM STATES").fetchall()
states_list = sorted([i[0] for i in states_list])



categories = conn.execute("SELECT CATEGORY FROM CATEGORIES").fetchall()
categories = sorted([i[0] for i in categories])