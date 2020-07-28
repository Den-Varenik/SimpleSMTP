from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5.uic import loadUi
from lib.message import Message
from lib.provider import DbProvider
from time import strftime
import re


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self._ui = loadUi('MainWindow.ui')
        self._provider = DbProvider()
        self._groups = self._provider.get_groups()
        self._receivers = []
        self._select_group = None
        self._select_receiver = None
        self.connect()
        self.show_groups()
        self.history()

    def connect(self):
        self._ui.sendButton.clicked.connect(self.send_message)
        self._ui.clearButton.clicked.connect(self.clear_fields)
        self._ui.groupButton.clicked.connect(self.add_group)
        self._ui.emailButton.clicked.connect(self.add_email)
        self._ui.groupList.clicked.connect(self.show_receivers)
        self._ui.groupReceivers.clicked.connect(self.selected_to_del)
        self._ui.delButton.clicked.connect(self.del_receiver)
        self._ui.delButton_2.clicked.connect(self.del_group)

    def open(self):
        self._ui.show()

    def send_message(self):
        server = self._ui.servetField.text()
        login = self._ui.sendField.text()
        password = self._ui.passwordField.text()
        if server != '' and login != '' and password != '':
            msg = Message(server, login, password)
            receiver = self._ui.reciverField.text()
            subject = self._ui.subjectField.text()
            message = self._ui.messageField.toPlainText()
            if message != '':
                if receiver == '' and self._select_group is not None:
                    for rec in self._provider.get_receivers(self._select_group.text()):
                        msg.create(rec, subject, message)
                        msg.send()
                    self._provider.create_history(strftime('%d.%m.%Y %H:%M:%S'), message, None,
                                                  self._provider.get_group_id(self._select_group.text()))
                    self.history()
                elif receiver != '':
                    msg.create(receiver, subject, message)
                    msg.send()
                    self._provider.create_history(strftime('%d.%m.%Y %H:%M:%S'), message, receiver)
                    self.history()
                else:
                    QMessageBox.warning(self, 'Предупреждение', 'Не указан получатель!')
            else:
                QMessageBox.warning(self, 'Предупреждение', 'Не указан текст сообщения!')
        else:
            QMessageBox.warning(self, 'Предупреждение', 'Первые три поля должны быть заполнены!')

    def clear_fields(self):
        self._ui.reciverField.clear()
        self._ui.subjectField.clear()
        self._ui.messageField.clear()

    def add_group(self):
        name = self._ui.groupField.text()
        if name != '' and name not in self._groups:
            self._provider.create_group(name)
            self._ui.groupField.clear()
            self._ui.groupList.clear()
            self._groups = self._provider.get_groups()
            self.show_groups()
        else:
            QMessageBox.warning(self, 'Ошибка', 'Введите название группы!')
            self._ui.groupField.setText('')

    def show_groups(self):
        self._ui.groupList.clear()
        for group in self._groups:
            self._ui.groupList.addItem(group)

    def show_receivers(self):
        self._ui.groupReceivers.clear()
        self._ui.reciverField.clear()
        self._select_group = self._ui.groupList.currentItem()
        self._ui.delField_2.setText(self._select_group.text())
        self._receivers = self._provider.get_receivers(self._select_group.text())
        for receiver in self._provider.get_receivers(self._select_group.text()):
            self._ui.groupReceivers.addItem(receiver)

    def add_email(self):
        if self._select_group is not None:
            email = re.match(r'.*\.*.+@.+\..+', self._ui.emailField.text())
            self._provider.create_receiver(email.group(), self._select_group.text()) if email is not None\
                else QMessageBox.warning(self, 'Ошибка', 'Не верный формат!')
            self._ui.emailField.clear()
            self.show_receivers()
        else:
            QMessageBox.warning(self, 'Ошибка', 'Выберете группу рассылки!')

    def selected_to_del(self):
        self._select_receiver = self._ui.groupReceivers.currentItem()
        self._ui.delField.setText(self._select_receiver.text())

    def del_receiver(self):
        if self._select_receiver is not None:
            self._provider.del_receiver(self._select_receiver.text(), self._select_group.text())
            self._select_receiver = None
            self.show_receivers()
            self._ui.delField.clear()
        else:
            QMessageBox.warning(self, 'Ошибка', 'Получатель не выбран!')

    def del_group(self):
        if self._select_group is not None:
            self._provider.del_group(self._select_group.text())
            self._groups = self._provider.get_groups()
            self._select_group = None
            self.show_groups()
            self._ui.delField_2.clear()
            self._ui.groupReceivers.clear()
            self.history()
        else:
            QMessageBox.warning(self, 'Ошибка', 'Группа не выбрана!')

    def history(self):
        self._ui.historyList.clear()
        history = self._provider.get_history()[-11:]
        for i in history:
            query = f'time - {i[1]} -> receiver - {i[3] if i[3] is not None else self._provider.get_title(i[4])}'
            self._ui.historyList.addItem(query)
