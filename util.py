# Decorator for singleton classes.
# Modified from https://gist.github.com/goutomroy/c925b1316bd9e7ec2cf9b1e4c183f5f4#file-singleton-py
# Why is this not in some standard library? ¯\_(ツ)_/¯
class Singleton:
    def __init__(self, cls, *args, **kwargs):
        self.cls = cls
        self.args = args
        self.kwargs = kwargs

    def get(self):
        try:
            return self.instance
        except AttributeError:
            self.instance = self.cls(*self.args, **self.kwargs)
            return self.instance

    def __call__(self):
        raise TypeError('Singletons must be accessed through `get()`.')

    def __instancecheck__(self, inst):
        return isinstance(inst, self.cls)
