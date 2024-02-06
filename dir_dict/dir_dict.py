import os

class DirDict():
    def __init__(self, path: str):
        self.path = os.path.join(*path.split('/'))
        os.makedirs(self.path)


    def __setitem__(self, key: str, value: type) -> None:
        with open(f'{self.path}\{key}.txt', 'w') as file:
            file.write(repr(value))


    def __delitem__(self, key: str) -> None:
        if os.path.exists(f'{self.path}\{key}.txt'):
            os.remove(f'{self.path}\{key}.txt')
        else:
            raise KeyError(key)


    def __getitem__(self, key: str) -> str:
        if os.path.exists(f'{self.path}\{key}.txt'):
            return next(open(f'{self.path}\{key}.txt', 'r'))
        raise KeyError(key)


    def keys(self) -> list[str]:
        return list(map(lambda key: key.replace('.txt', ''), os.listdir(self.path)))


    def values(self) -> list[str]:
        return [next(open(f'{self.path}\{key}', 'r')) for key in os.listdir(self.path)]


    def items(self) -> list[tuple]:
        return [(key.replace('.txt', ''), next(open(f'{self.path}\{key}', 'r'))) for key in os.listdir(self.path)]


    def get(self, key: str, default: type) -> str:
        try:
            return self.__getitem__(key)
        except KeyError:
            return repr(default)


    def __iter__(self):
        for key in os.listdir(self.path):
            yield key.replace('.txt', '')
