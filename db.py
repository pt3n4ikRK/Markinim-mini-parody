import sqlite3
import threading
import random

def mix_messages_together(message1, message2):
    words1 = message1.split()
    words2 = message2.split()

    # Обираємо випадкове слово для обміну
    index1 = random.randint(0, len(words1) - 1)
    index2 = random.randint(0, len(words2) - 1)

    # Міняємо слова між собою
    words1[index1], words2[index2] = words2[index2], words1[index1]

    # Формуємо нові повідомлення
    mixed_message1 = ' '.join(words1)
    mixed_message2 = ' '.join(words2)

    return mixed_message1, mixed_message2

class Database:
    def __init__(self, name):
        self.name = name
        self.conn = sqlite3.connect(self.name)
        self.cur = self.conn.cursor()
        self.thread_local = threading.local()

    def get_connection(self):
        # Перевіряємо, чи існує вже з'єднання для поточного потоку
        if not hasattr(self.thread_local, 'connection'):
            # Якщо немає, створюємо нове з'єднання
            self.thread_local.connection = sqlite3.connect(self.name)
        return self.thread_local.connection

    def create_table(self, table_name, statistic: bool):
        connection = self.get_connection()
        cursor = connection.cursor()
        if statistic:
            cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} (chat_id STRING, user_id STRING, message_count INT);")
            connection.commit()
        else:
            cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} (chat_id STRING, message STRING);")
            connection.commit()

    def add_count_messages(self, table_name, chat_id, user_id):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute(f"SELECT message_count FROM {table_name} WHERE chat_id = ? AND user_id = ?", (chat_id, user_id))
        result = cursor.fetchone()

        if result is None:
            cursor.execute(f"INSERT INTO {table_name} (chat_id, user_id, message_count) VALUES (?, ?, 1)",
                           (chat_id, user_id))
        else:
            cursor.execute(
                f'UPDATE {table_name} SET message_count = message_count + 1 WHERE chat_id = ? AND user_id = ?;',
                (chat_id, user_id))
        connection.commit()
    def add_message(self, table_name, chat_id, message):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute(f"INSERT INTO {table_name} (chat_id, message) VALUES (?, ?);", (chat_id, message))
        connection.commit()

    def get_random_message(self, table_name, chat_id):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute(f"SELECT message FROM {table_name} WHERE chat_id = ? ORDER BY RANDOM() LIMIT 2;", (chat_id,))
        results = cursor.fetchall()

        if len(results) == 2:
            # Перевіряємо, чи результати не є None
            if results[0][0] is not None and results[1][0] is not None:
                message1, message2 = mix_messages_together(results[0][0], results[1][0])
                result_main = message1 + ", " + message2 + "."
                return result_main
            else:
                return None
        else:
            return None

    def get_statistic(self, table_name, chat_id, user_id):
        connection = self.get_connection()
        cursor = connection.cursor()
        cursor.execute(f"SELECT message_count FROM {table_name} WHERE chat_id = ? AND user_id = ?", (chat_id, user_id))
        result = cursor.fetchone()

        if result is not None:
            return result[0]
        else:
            self.add_count_messages(table_name, chat_id, user_id)
