# -*- coding: utf-8 -*-
import os
import pprint
import sys
import time

Module = type(sys)

from contextlib import contextmanager
is_py2 = True if sys.version_info.major == 2 else False
if not is_py2:
    from importlib import util


@contextmanager
def add_to_path(p):
    import sys
    old_path = sys.path
    sys.path = sys.path[:]
    sys.path.insert(0, p)
    try:
        yield
    finally:
        sys.path = old_path


class ModulesDynamicLoad:
    def __init__(self):
        self.__modules = {}
        self.is_py2 = True if sys.version_info.major == 2 else False

    def code_demo(self, py_absolute_path):
        m = self.load(py_absolute_path)
        data = pprint.pformat(m.config)
        print(data)

        while True:
            m = self.reload(m)
            data = pprint.pformat(m.config)
            print(data)
            time.sleep(2)

    def load(self, path):
        if self.is_py2:
            tmp_module = self.__load_py2(path)
        else:
            tmp_module = self.__load_py3(path)
        return tmp_module

    def reload(self, module):
        if self.is_py2:
            tmp_module = self.__reload_py2(module)
        else:
            tmp_module = self.__reload_py3(module)
        return tmp_module

    def __load_py3(self, absolute_path):
        """implementation taken from
        https://docs.python.org/3/library/importlib.html#importing-a-source-file-directly"""
        filename = os.path.basename(absolute_path)
        try:
            return self.__modules[filename]
        except KeyError:
            pass

        with add_to_path(os.path.dirname(absolute_path)):
            spec = util.spec_from_file_location(absolute_path, absolute_path)
            module = util.module_from_spec(spec)
            spec.loader.exec_module(module)

            self.__modules[filename] = module
            return module

    def __reload_py3(self, module):
        absolute_path = module.__file__
        filename = os.path.basename(absolute_path)

        with add_to_path(os.path.dirname(absolute_path)):
            spec = util.spec_from_file_location(absolute_path, absolute_path)
            module = util.module_from_spec(spec)
            spec.loader.exec_module(module)

            self.__modules[filename] = module
            return module

    def __load_py2(self, full_path, env={}, module=Module):
        """
        load python modules
        :param full_path:
        :param env:
        :param module:
        :return:
        """
        try:
            code = open(full_path).read()
        except IOError:
            raise ImportError('No module named  %s' % full_path)

        filename = os.path.basename(full_path)
        try:
            return self.__modules[filename]
        except KeyError:
            pass

        m = module(filename)
        m.__module_class__ = module
        m.__file__ = full_path
        m.__dict__.update(env)

        exec(compile(code, filename, 'exec'), m.__dict__, m.__dict__)
        self.__modules[filename] = m

        return m

    def __unload_py2(self, m):
        """
        remove py2 module
        :param m:
        :return:
        """
        filename = os.path.basename(m.__file__)
        del self.__modules[filename]
        return None

    def __reload_py2(self, m):
        """
        reload modules
        :param m:
        :return:
        """
        full_path = m.__file__

        try:
            code = open(full_path).read()
        except IOError:
            raise ImportError('No module named  %s' % full_path)

        env = m.__dict__
        module_class = m.__module_class__

        filename = os.path.basename(full_path)
        m = module_class(filename)

        m.__file__ = full_path
        m.__dict__.update(env)
        m.__module_class__ = module_class

        exec(compile(code, filename, 'exec'), m.__dict__, m.__dict__)
        self.__modules[filename] = m

        return m


if __name__ == '__main__':
    pass
