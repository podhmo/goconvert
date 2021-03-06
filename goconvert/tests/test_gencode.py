import unittest


class Tests(unittest.TestCase):
    def _getTargetClass(self):
        from goconvert.minicode import MinicodeGenerator
        return MinicodeGenerator

    def _makeOne(self, items=None):
        from goconvert.typeresolver import TypeMappingResolver
        return self._getTargetClass()(TypeMappingResolver(items or []), verify=False)

    def test_it(self):
        target = self._makeOne()
        actual = target.gencode(["string"], ["string"])
        expected = []
        self.assertEqual(expected, actual)

    def test_src_pointer(self):
        target = self._makeOne()
        actual = target.gencode(["pointer", "string"], ["string"])
        expected = [("deref",)]
        self.assertEqual(expected, actual)

    def test_dst_pointer(self):
        target = self._makeOne()
        actual = target.gencode(["string"], ["pointer", "string"])
        expected = [("ref",)]
        self.assertEqual(expected, actual)

    def test_same_with_pointer(self):
        target = self._makeOne()
        actual = target.gencode(["pointer", "string"], ["pointer", "string"])
        expected = []
        self.assertEqual(expected, actual)

    def test_src_pointer_pointer(self):
        target = self._makeOne()
        actual = target.gencode(["pointer", "pointer", "string"], ["pointer", "string"])
        expected = [("deref",)]
        self.assertEqual(expected, actual)

    def test_src_pointer_pointer2(self):
        target = self._makeOne()
        actual = target.gencode(["pointer", "pointer", "string"], ["string"])
        expected = [("deref",), ("deref",)]
        self.assertEqual(expected, actual)

    def test_cast(self):
        target = self._makeOne({"string": "X"}.items())
        actual = target.gencode(["string"], ["X"])
        expected = [("coerce", ("string",), ("X",))]
        self.assertEqual(expected, actual)

    def test_cast2(self):
        target = self._makeOne([("string", "X"), ("string", "Y")])
        actual = target.gencode(["Y"], ["X"])
        expected = [("coerce", ("Y", ), ("string", )), ("coerce", ("string",), ("X",))]
        self.assertEqual(expected, actual)

    def test_cast3(self):
        target = self._makeOne([("string", "X"), ("string", "Y")])
        actual = target.gencode(["pointer", "pointer", "Y"], ["pointer", "X"])
        expected = [("deref",), ("deref", ), ("coerce", ("Y",), ("string",)), ("coerce", ("string",), ("X",)), ("ref", )]
        self.assertEqual(expected, actual)

    def test_cast4(self):
        target = self._makeOne([(("pointer", "string"), "PX"), ("string", "Y")])
        actual = target.gencode("Y", "PX")
        expected = [('coerce', ('Y',), ('string',)), ('ref',), ('coerce', ('pointer', 'string'), ('PX',))]
        self.assertEqual(expected, actual)

    def test_cast5(self):
        target = self._makeOne([(("pointer", "string"), "PX"), ("string", "Y")])
        actual = target.gencode("PX", "Y")
        expected = [('coerce', ('PX',), ('pointer', 'string')), ('deref',), ('coerce', ('string',), ('Y',))]
        self.assertEqual(expected, actual)

    def test_array(self):
        target = self._makeOne([("string", "X"), ("string", "Y")])
        actual = target.gencode(("array", "X"), ("array", "pointer", "Y"))
        from goconvert.typeresolver import Action
        expected = [
            Action(action=('iterate',
                           Action(action='coerce', src=('X',), dst=('string',)),
                           Action(action='coerce', src=('string',), dst=('Y',)),
                           ('ref',)),
                   src=('array', 'X'), dst=['array', 'pointer', 'Y'])
        ]
        self.assertEqual(expected, actual)

    def test_array_pointer(self):
        target = self._makeOne([("string", "X"), ("string", "Y")])
        actual = target.gencode(("pointer", "array", "X"), ("array", "Y"))
        from goconvert.typeresolver import Action
        expected = [
            ('deref',),
            Action(action=('iterate',
                           Action(action='coerce', src=('X',), dst=('string',)),
                           Action(action='coerce', src=('string',), dst=('Y',))),
                   src=('array', 'X'), dst=['array', 'Y'])
        ]
        self.assertEqual(expected, actual)

    def test_pointer_array(self):
        target = self._makeOne([(("pointer", "X"), ("pointer", "Y"))])
        actual = target.gencode(("array", "X"), ("array", "Y"))
        from goconvert.typeresolver import Action
        expected = [
            Action(action=('iterate',
                           ('ref',),
                           Action(action='coerce', src=('pointer', 'X'), dst=('pointer', 'Y')), ('deref',)),
                   src=('array', 'X'), dst=['array', 'Y'])
        ]
        self.assertEqual(expected, actual)

    def test_array_array(self):
        target = self._makeOne([("string", "X"), ("string", "Y")])
        actual = target.gencode(("array", "array", "X"), ("array", "array", "pointer", "Y"))
        from goconvert.typeresolver import Action
        expected = [
            Action(action=('iterate',
                           Action(action=('iterate',
                                          Action(action='coerce', src=('X',), dst=('string',)),
                                          Action(action='coerce', src=('string',), dst=('Y',)),
                                          ('ref',)),
                                  src=('array', 'X'), dst=['array', 'pointer', 'Y'])),
                   src=('array', 'array', 'X'), dst=['array', 'array', 'pointer', 'Y'])
        ]
        self.assertEqual(expected, actual)
