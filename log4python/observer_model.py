# -*- coding: utf-8 -*-


class Subject(object):
    def __init__(self):
        self.__observer_list = []
        self.data = 0

    def add_observer(self, observer):
        self.__observer_list.append(observer)

    def delete_observer(self, observer):
        if observer in self.__observer_list:
            self.__observer_list.remove(observer)

    def notify_observers(self):
        for observer in self.__observer_list:
            observer.update(self.data)

    def set_value(self, data_important):
        self.data = data_important
        self.notify_observers()


class Observer(object):
    data = ""

    def __init__(self, subject):
        self.subject = subject
        self.subject.add_observer(self)
        self.data = self.subject.data

    def update(self, data):
        self.data = data
        self.display()

    def display(self):
        print(self.data)
