from sqlite3 import connect


class DbProvider(object):

    def __init__(self):
        self._db = 'SimpleSMTP_DATA.db'
        self._conn = connect(self._db)
        self._cursor = self._conn.cursor()
        self._groups = []
        self._receivers = []

    def create_group(self, name):
        self._cursor.execute(f"INSERT INTO Groups (title) VALUES ('{name}')")
        self._conn.commit()

    def create_receiver(self, email, group):
        self._cursor.execute(f"INSERT INTO Receiver (email, group_id) VALUES ('{email}', '{self.get_group_id(group)}')")
        self._conn.commit()

    def create_history(self, time, message, receiver, group_id=None):
        if receiver is None:
            query = f"INSERT INTO History (time, message, group_id) VALUES ('{time}', '{message}', '{group_id}')"
        else:
            query = f"INSERT INTO History (time, message, receiver) VALUES ('{time}', '{message}', '{receiver}')"
        self._cursor.execute(query)
        self._conn.commit()

    def get_groups(self) -> list:
        query = """
            SELECT a.title
            FROM Groups a            
        """
        self._cursor.execute(query)
        self._groups = self._cursor.fetchall()
        return [group[0] for group in self._groups]

    def get_receivers(self, group) -> list:
        self._cursor.execute(f"SELECT email FROM Receiver WHERE group_id=('{self.get_group_id(group)}')")
        self._receivers = self._cursor.fetchall()
        return [receiver[0] for receiver in self._receivers]

    def get_history(self):
        self._cursor.execute(f"SELECT * FROM History")
        return self._cursor.fetchall()

    def get_title(self, group_id):
        self._cursor.execute(f"SELECT title FROM Groups WHERE id=('{group_id}')")
        return self._cursor.fetchone()[0] if group_id is not None else None

    def get_group_id(self, title):
        self._cursor.execute(f"SELECT id FROM Groups WHERE title=('{title}')")
        return self._cursor.fetchone()[0]

    def del_group(self, title):
        self._cursor.execute(f"DELETE FROM Receiver WHERE group_id=('{self.get_group_id(title)}')")
        self._cursor.execute(f"UPDATE History SET group_id=(NULL) WHERE group_id=('{self.get_group_id(title)}')")
        self._cursor.execute(f"DELETE FROM Groups WHERE title=('{title}')")
        self._conn.commit()

    def del_receiver(self, email, group):
        self._cursor.execute(f"DELETE FROM Receiver WHERE email=('{email}') AND group_id=('{self.get_group_id(group)}')")
        self._conn.commit()

