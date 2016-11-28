import unittest


class Tests(unittest.TestCase):
    def _getTargetClass(self):
        from goconvert.convertor import ConvertorFromMinicode
        return ConvertorFromMinicode

    def _makeOne(self, items):
        from goconvert.typeresolver import TypeMappingResolver
        from goconvert.convertor import CoerceMap
        return self._getTargetClass()(CoerceMap(TypeMappingResolver(items)))

    def _makeContext(self):
        from goconvert.convertor import Context
        from prestring.go import GoModule
        return Context(GoModule())

    def test_convert_ref(self):
        target = self._makeOne([])
        request = self._makeContext()
        value = "v"
        code = [("ref",)]
        _, value = target.code_from_minicode(request, code, value)
        self.assertEqual("", str(request.m))
        self.assertEqual("&(v)", value)

    def test_convert_deref(self):
        target = self._makeOne([])
        request = self._makeContext()
        value = "v"
        code = [("deref",)]
        _, value = target.code_from_minicode(request, code, value)
        expected = """\
if v != nil  {
\ttmp1 := *(v)
}\
"""
        self.assertEqual(expected, str(request.m))
        self.assertEqual("tmp1", value)

    def test_convert_coerce(self):
        from goconvert.typeresolver import Action
        target = self._makeOne([("string", "X")])
        request = self._makeContext()
        value = "v"
        code = [Action(action="coerce", src=("string",), dst=("X", ))]
        _, value = target.code_from_minicode(request, code, value)
        self.assertEqual("tmp1 := X(v)", str(request.m))
        self.assertEqual("tmp1", value)

    def test_convert_coerce_ref(self):
        from goconvert.typeresolver import Action
        target = self._makeOne([("string", "X")])
        request = self._makeContext()
        value = "v"
        code = [("ref",), Action(action="coerce", src=("string",), dst=("X", ))]
        _, value = target.code_from_minicode(request, code, value)
        expected = """\
tmp1 := &(v)
tmp2 := X(tmp1)\
"""

        self.assertEqual(expected, str(request.m))
        self.assertEqual("tmp2", value)

    def test_convert_deref_coerce(self):
        from goconvert.typeresolver import Action
        target = self._makeOne([("string", "X")])
        request = self._makeContext()
        value = "v"
        code = [("deref",), Action(action="coerce", src=("string",), dst=("X", ))]
        _, value = target.code_from_minicode(request, code, value)
        expected = """\
if v != nil  {
\ttmp1 := *(v)
\ttmp2 := X(tmp1)
}\
"""
        self.assertEqual(expected, str(request.m))
        self.assertEqual("tmp2", value)
