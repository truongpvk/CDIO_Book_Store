# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import mysql.connector

HOST = '127.0.0.1'
USER = 'root'
PASSWORD = 'truong181004'
DATABASE = 'bookstore'

connection = mysql.connector.connect(host=HOST, user=USER, passwd=PASSWORD, database=DATABASE)
cur = connection.cursor()

class ActionSearchBook(Action):

    def name(self) -> Text:
        return "action_hello_world"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        book_name = tracker.get_slot('book_name')
        author = tracker.get_slot('author')
        genre = tracker.get_slot('genre')
        cur.execute(f'select title, author, category from book where title={book_name} or author={author} or category={genre}')

        result = cur.fetchone()

        if result:
            title, author, genre = result
            dispatcher.utter_message(f"Sách '{book_name}' được viết bởi {author} và thuộc thể loại {genre}.")
        else:
            dispatcher.utter_message(f"Không tìm thấy thông tin cho cuốn sách '{book_name}'.")

        return []
