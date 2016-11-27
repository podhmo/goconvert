import unittest


class PreGencodeTests(unittest.TestCase):
    def _getTargetClass(self):
        from goconvert.minicode import MinicodeNormalizer
        return MinicodeNormalizer

    def _makeOne(self):
        items = [
            ("string", "X"),
            ("string", "Y"),
            ("string", "strfmt.Email"),
        ]
        from goconvert.typeresolver import TypeMappingResolver
        return self._getTargetClass()(TypeMappingResolver(items))

    def test_it(self):
        path = [
            ('coerce', ('string', ), ('strfmt.Email', )),
            ('coerce', ('strfmt.Email', ), ('pointer', 'strfmt.Email'))
        ]
        target = self._makeOne()
        actual = target.pre_gencode(path)
        self.assertEqual(path, actual)

    def test_array(self):
        path = [
            ("coerce", ("array", "X"), ("array", "Y")),
        ]
        target = self._makeOne()
        actual = target.pre_gencode(path)
        expected = [
            ("coerce", ("array", "X"), ("X", )),
            ("coerce", ("X", ), ("Y", )),
            ("coerce", ("Y", ), ("array", "Y")),
        ]
        self.assertEqual(expected, actual)

    def test_array_pointer(self):
        path = [
            ("coerce", ("pointer", "array", "X"), ("pointer", "array", "Y")),
        ]
        target = self._makeOne()
        actual = target.pre_gencode(path)
        expected = [
            ("coerce", ("pointer", "array", "X"), ("array", "X", )),
            ("coerce", ("array", "X"), ("X", )),
            ("coerce", ("X", ), ("Y", )),
            ("coerce", ("Y", ), ("array", "Y")),
            ("coerce", ("array", "Y", ), ("pointer", "array", "Y")),
        ]
        self.assertEqual(expected, actual)

    def test_pointer_array(self):
        path = [
            ("coerce", ("array", "pointer", "X"), ("array", "pointer", "Y")),
        ]
        target = self._makeOne()
        actual = target.pre_gencode(path)
        expected = [
            ('coerce', ('array', 'pointer', 'X'), ('pointer', 'X')),
            ('coerce', ('pointer', 'X'), ('pointer', 'Y')),
            ('coerce', ('pointer', 'Y'), ('array', 'pointer', 'Y')),
        ]
        self.assertEqual(expected, actual)

    def test_array_array(self):
        path = [
            ("coerce", ("array", "array", "X"), ("array", "array", "Y")),
        ]
        target = self._makeOne()
        actual = target.pre_gencode(path)
        expected = [
            ("coerce", ("array", "array", "X"), ("array", "X", )),
            ("coerce", ("array", "X"), ("X", )),
            ("coerce", ("X", ), ("Y", )),
            ("coerce", ("Y", ), ("array", "Y")),
            ("coerce", ("array", "Y", ), ("array", "array", "Y")),
        ]
        self.assertEqual(expected, actual)

    def test_guessing_pointer_arary(self):
        # correct: ("coerce", ("array", "pointer", "x"), ("array", "pointer", "y"))
        path = [
            ('coerce', ('array', 'pointer', 'X'), ('array', 'X')),
            ('coerce', ('array', 'X'), ('array', 'Y')),
            ('coerce', ('array', 'Y'), ('array', 'pointer', 'Y')),
        ]
        target = self._makeOne()
        actual = target.pre_gencode(path)
        from goconvert.typeresolver import Action
        expected = [
            Action(action='coerce', src=('array', 'pointer', 'X'), dst=('pointer', 'X')),  # dearray
            Action(action='coerce', src=('pointer', 'X'), dst=('X',)),  # deref
            Action(action='coerce', src=('X',), dst=('array', 'X')),  # array
            Action(action='coerce', src=('array', 'X'), dst=('X',)),  # dearray
            Action(action='coerce', src=('X',), dst=('Y',)),  # coerce
            Action(action='coerce', src=('Y',), dst=('array', 'Y')),  # array
            Action(action='coerce', src=('array', 'Y'), dst=('Y',)),  # dearray
            Action(action='coerce', src=('Y',), dst=('pointer', 'Y')),  # ref
            Action(action='coerce', src=('pointer', 'Y'), dst=('array', 'pointer', 'Y'))  # array
        ]
        self.assertEqual(expected, actual)
        # # after optimized
        # expected = [
        #     Action(action='coerce', src=('array', 'pointer', 'X'), dst=('pointer', 'X')),  # dearray
        #     Action(action='coerce', src=('pointer', 'X'), dst=('X',)),  # deref
        #     Action(action='coerce', src=('X',), dst=('Y',)),  # coerce
        #     Action(action='coerce', src=('Y',), dst=('pointer', 'Y')),  # ref
        #     Action(action='coerce', src=('pointer', 'Y'), dst=('array', 'pointer', 'Y'))  # array
        # ]
