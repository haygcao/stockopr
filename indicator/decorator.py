
def computed(column_name=None):
    def decorate(func):
        def inner(*args, **kwargs):
            if column_name in (args[0]).columns:
                return args[0]
            return func(*args, **kwargs)
        return inner
    return decorate
