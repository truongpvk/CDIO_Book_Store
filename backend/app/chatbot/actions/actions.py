# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions
import random
# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import mysql.connector

connection = mysql.connector.connect(
    host='127.0.0.1',
    user='root',
    passwd='truong181004',
    database='bookstore'
)
cur = connection.cursor()


class ActionSearchBook(Action):

    def name(self) -> Text:
        return "action_search_book"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        title = tracker.get_slot('name')
        author = tracker.get_slot('author')
        category = tracker.get_slot('category')
        check = bool(tracker.get_slot('check'))

        print((title, author, category))

        if title != '':
            cur.execute(f'select * from book where title="{title}";')
            book_finded = cur.fetchone()

            if book_finded:
                dispatcher.utter_message(
                    text=f"Bạn đang tìm cuốn sách {book_finded['title']} của tác giả {book_finded['author']}, nó thuộc thể loại {book_finded['category']}. Dưới đây là liên kết đến sản phẩm:\n <domain_name>/{book_finded['sku']}")
            else:
                dispatcher.utter_message(text="Có vẻ trong cửa hàng không có sách bạn muốn tìm?")
        elif title == '' or not check:
            sql = f'select * from book where '

            if author and not category:
                sql += f'author="{author}"'
            elif category and not author:
                sql += f'category="{category}"'
            elif author and category:
                sql += f'author="{author}" or category="{category}"'

            cur.execute(sql + ';')
            book_data = cur.fetchall()
            choice = random.choice(book_data)
            dispatcher.utter_message(text=f"Tôi đề cử cuốn sách {choice['title']}: <domain_name>/{choice['sku']}")
        else:
            dispatcher.utter_message(text="Có vẻ thông tin bạn đưa ra chưa đủ hoặc khó nhận diện, xin hãy thử lại!")

        return []


class ActionInstructBook(Action):

    def name(self) -> Text:
        return "action_instruct_book"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        title = tracker.get_slot('name')

        print(title)

        dispatcher.utter_message(text=f"Nội dung của {title}")

        return []

class ActionFindBookByName(Action):

    def name(self) -> Text:
        return "action_find_book_by_name"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        title = tracker.get_slot('name')

        if title != '':
            sql = f"select sku from book where title='{title}'"
            cur.execute(sql)

            sku = cur.fetchall()

            if len(sku) > 0:
                dispatcher.utter_message(text=f'Đây là quyển sách bạn muốn tìm kiếm: /{random.choice(sku)}')
            else:
                dispatcher.utter_message(text='Có vẻ như cuốn sách này không tồn tại trong cửa hàng, hoặc bạn có thể đã đưa sai thông tin?')

        return []