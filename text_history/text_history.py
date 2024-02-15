from collections.abc import Iterator


class Action:
    def __init__(self, pos: int, from_version: int, to_version: int):
        self.pos = pos
        self.from_version = from_version
        self.to_version = to_version
        self.id = None


    def apply(self, string: str) -> str:
        if self.pos is None:
            self.pos = len(string)
        if self.pos > len(string) or self.pos < 0:
            raise ValueError

        return string


class InsertAction(Action):
    def __init__(self, pos: int, text: str, from_version: int, to_version: int):
        super().__init__(pos, from_version, to_version)
        self.text = text
        self.id = 'I'


    def apply(self, string: str) -> str:
        return f'{super().apply(string)[:self.pos]}{self.text}{string[self.pos:]}'


class ReplaceAction(Action):
    def __init__(self, pos: int, text: str, from_version: int, to_version: int):
        super().__init__(pos, from_version, to_version)
        self.text = text
        self.id = 'R'


    def apply(self, string: str) -> str:
        return f'{super().apply(string)[:self.pos]}{self.text}{string[self.pos + len(self.text):]}'


class DeleteAction(Action):
    def __init__(self, pos: int, length: int, from_version: int, to_version: int):
        super().__init__(pos, from_version, to_version)
        self.length = length
        self.id = 'D'


    def apply(self, string: str) -> str:
        if (self.pos + self.length) > len(string) or self.length < 0:
            raise ValueError
        return f'{super().apply(string)[:self.pos]}{string[self.pos + self.length:]}'


class TextHistory:
    def __init__(self, text: str=''):
        self._text = text
        self._version = 0
        self._actions = {}


    @property
    def text(self):
        return self._text


    @property
    def version(self):
        return self._version


    def __action(self, action: Action) -> int:
        self._text = action.apply(self._text)
        self._actions[self._version] = action
        self._version += 1


    def __optimization(self, actions: Iterator[Action]) -> list[Action]:
        '''Принимает на вход итератор состоящий из действий которые были совершены в период указанных версии,
           если несколько действии можно объеденить в одно - объединяет, возвращает оптимизированный список действии.'''

        def insert_actions(actions: Iterator[Action]) -> list[Action]:
            # text = ''
            # insert('q', pos=0), insert('w', pos=1), insert('erty', pos=2) -> insert('qwerty', pos=0)
            result_actions = []

            action, next_action = next(actions, None), next(actions, None)
            while next_action:
                if action.pos + len(action.text) == next_action.pos:
                    position = action.pos
                    from_version = action.from_version
                    list_text = [action.text, next_action.text]

                    action, next_action = next_action, next(actions, None)
                    while next_action and action.pos + len(action.text) == next_action.pos:
                        list_text.append(next_action.text)
                        action, next_action = next_action, next(actions, None)

                    result_actions.append(InsertAction(position, ''.join(list_text), from_version, action.to_version))
                    action, next_action = next_action, next(actions, None)
                    list_text.clear()
                else:
                    result_actions.append(action)
                    action, next_action = next_action, next(actions, None)

            last_action = action or next_action
            if last_action:
                result_actions.append(last_action)

            return result_actions


        def replace_actions(actions: Iterator[Action]) -> list[Action]:
            # text = 'qwerty'
            # replace('12', 1) > 'q12rty', replace('345', 2) > 'q1345y' -> replace('1345', 1)
            result_actions = []
            action, next_action = next(actions, None), next(actions, None)
            while next_action:
                if (len(action.text) - next_action.pos >= 0) and (next_action.pos <= action.pos + len(action.text)):
                    position = action.pos
                    from_version = action.from_version
                    list_text = [action.text[:next_action.pos - 1]]

                    action, next_action = next_action, next(actions, None)
                    while next_action and ((len(action.text) - next_action.pos >= 0) and (next_action.pos <= action.pos + len(action.text))):
                        list_text.append(action.text[:next_action.pos])
                        action, next_action = next_action, next(actions, None)

                    result_actions.append(ReplaceAction(position, ''.join(list_text), from_version, action.to_version))
                    action, next_action = next_action, next(actions, None)
                    list_text.clear()
                else:
                    result_actions.append(action)
                    action, next_action = next_action, next(actions, None)

            last_action = action or next_action
            if last_action:
                result_actions.append(last_action)

            return result_actions


        def delete_actions(actions: Iterator[Action]) -> list[Action]:
            # text = 'qwerty'
            # delete(0, 1), delete(0, 1), delete(0, 1) -> delete(0, 3)
            result_actions = []

            action, next_action = next(actions, None), next(actions, None)

            while next_action:
                if next_action.pos == action.pos:
                    position = action.pos
                    from_version = action.from_version
                    length = action.length + next_action.length
                    action, next_action = next_action, next(actions, None)

                    while next_action and next_action.pos == action.pos:
                        length += next_action.length
                        action, next_action = next_action, next(actions, None)

                    result_actions.append(DeleteAction(position, length, from_version, action.to_version))
                    action, next_action = next_action, next(actions, None)
                    length = 0
                else:
                    result_actions.extend([action, next_action])
                    action, next_action = next(actions, None), next(actions, None)

            last_action = action or next_action
            if last_action:
                result_actions.append(last_action)

            return result_actions

        funcs = {'I': insert_actions, 'R': replace_actions, 'D': delete_actions}

        result_actions = []
        action, next_action = next(actions, None), next(actions, None)

        while action and next_action:
            temp_actions = []
            if action.id == next_action.id:
                while next_action and action.id == next_action.id:
                    temp_actions.append(action)
                    action, next_action = next_action, next(actions, None)
                temp_actions.append(action)

                id = action.id
                action, next_action = next_action, next(actions, None)

                result_actions.extend(funcs[id](iter(temp_actions[:])))
                temp_actions.clear()
            else:
                result_actions.append(action)
                action, next_action = next_action, next(actions, None)

        action = action or next_action
        if action:
            result_actions.append(action)

        return result_actions


    def insert(self, text: str, pos: int=None) -> int:
        self.__action(InsertAction(pos, text, self._version, self._version + 1))
        return self._version


    def replace(self, text: str, pos: int=None) -> int:
        self.__action(ReplaceAction(pos, text, self._version, self._version + 1))
        return self._version


    def delete(self, pos: int, length: int=1) -> int:
        self.__action(DeleteAction(pos, length, self._version, self._version + 1))
        return self._version


    def action(self, action: Action) -> int:
        if action.from_version != self._version:
            raise ValueError
        else:
            self.__action(action)
            self._version = action.to_version
            return self._version


    def get_actions(self, from_version: int=None, to_version: int=None, optimization: bool=False) -> list[Action]:

        to_version = self._version if to_version is None else to_version
        from_version = 0 if from_version is None else from_version

        if ((from_version not in self._actions) and self._actions) or to_version > self._version or from_version > to_version:
            raise ValueError

        if optimization:
            return self.__optimization(iter([self._actions[version] for version in tuple(self._actions)[from_version:to_version]]))

        return [self._actions[version] for version in tuple(self._actions)[from_version:to_version]]
