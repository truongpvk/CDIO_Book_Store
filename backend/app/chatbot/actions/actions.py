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

import os
import google.generativeai as genai

import difflib

os.environ["API_KEY"] = "KEY"
genai.configure(api_key=os.environ["API_KEY"])

# Create the model
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
  model_name="gemini-1.5-flash",
  generation_config=generation_config,
)

chat_session = model.start_chat(
  history=[
  ]
)

connection = mysql.connector.connect(
    host='127.0.0.1',
    user='root',
    passwd='truong181004',
    database='bookstore'
)
cur = connection.cursor()

cur.execute("select title, author, category, description, sku from book")
full_book = cur.fetchall()

class ActionSearchBook(Action):
    def name(self) -> Text:
        return "action_search_book"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        title = tracker.get_slot('name')
        author = tracker.get_slot('author')
        category = tracker.get_slot('category')

        if title is not None:
            book_title = [book[0] for book in full_book]
            search_result = difflib.get_close_matches(title, book_title, n=5, cutoff=0.6)
            book_chosen = random.choice(search_result) if len(search_result) > 0 else None
            if book_chosen:
                dispatcher.utter_message(text=f"Đây là cuốn sách {book_chosen[0]} mà tôi tìm được.")
                dispatcher.utter_message(text=f"Link sản phẩm: /{book_chosen[-1]}")
                return []

        if author is not None:
            book_by_author = [book for book in full_book if author.lower() in book[1].lower()]
            book_chosen = random.choice(book_by_author) if len(book_by_author) else None
            if book_chosen:
                dispatcher.utter_message(text=f"Đây là cuốn sách {book_chosen[0]} của tác giả {author}")
                dispatcher.utter_message(text=f"Link sản phẩm: /{book_chosen[-1]}")
                return []

        if category is not None:
            book_by_category = [book for book in full_book if category.lower() in book[2].lower()]
            book_chosen = random.choice(book_by_category) if len(book_by_category) else None
            if book_chosen:
                dispatcher.utter_message(text=f"Đây là cuốn sách {book_chosen[0]} thuộc thể loại {category}")
                dispatcher.utter_message(text=f"Link sản phẩm: /{book_chosen[-1]}")
                return []

        dispatcher.utter_message(text="Có vẻ trong cửa hàng không có sách bạn muốn tìm, bạn có thể thử các cuốn sách khác!")

        return []


class ActionInstructBook(Action):

    def name(self) -> Text:
        return "action_instruct_book"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        title = tracker.get_slot('name')

        if title is not None:
            response = chat_session.send_message(f"Tóm tắt nội dung sơ lược của cuốn sách {title} trong một đoạn văn")
            dispatcher.utter_message(text=response.text)
            return []

        dispatcher.utter_message(text="Có vẻ chúng tôi không tìm thấy cuốn sách mà bạn đề cập tới.")

        return []
