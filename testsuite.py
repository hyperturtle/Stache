import os
import string
import sys
try:
    import unittest2 as unittest
except ImportError:
    import unittest


import stache
from stache import render, Stache


# start generated code
class BaseTest(unittest.TestCase):
    def stache_verify(self, output, template, data):
        #print("%s with %s" % (template, data))
        result = render(template, data)
        result_iter = ''.join(Stache().render_iter(template, data))
        #print("Output: %s\n" % output)
        #print("Result: %s\n" % result)
        #assert result == output
        self.assertEqual(result, output)
        #assert result == result_iter
        self.assertEqual(result, result_iter)


class verify(BaseTest):

    # test tag lookup
    def test_verify_01(self):
        self.stache_verify('a10c', 'a{{b}}c', {'b': 10})


    def test_verify_02(self):
        self.stache_verify('a10c', 'a{{b}}c', {'b': 10})


    def test_verify_03(self):
        self.stache_verify('ac', 'a{{b}}c', {'c': 10})


    def test_verify_04(self):
        self.stache_verify('a10c', 'a{{b}}c', {'b': '10'})


    def test_verify_05(self):
        self.stache_verify('acde', 'a{{!b}}cde', {'b': '10'})


    def test_verify_06(self):
        self.stache_verify('aTrue', 'a{{b}}', {'b': True})


    def test_verify_07(self):
        self.stache_verify('a123', 'a{{b}}{{c}}{{d}}', {'c': 2, 'b': 1, 'd': 3})


    # test falsy #sections
    def test_verify_08(self):
        self.stache_verify('ab', 'a{{#b}}b{{/b}}', {'b': True})


    def test_verify_09(self):
        self.stache_verify('a', 'a{{^b}}b{{/b}}', {'b': True})


    def test_verify_10(self):
        self.stache_verify('a', 'a{{#b}}b{{/}}', {'b': False})


    def test_verify_11(self):
        self.stache_verify('ab', 'a{{^b}}b{{/b}}', {'b': False})


    # test invert sections
    def test_verify_12(self):
        self.stache_verify('ab', 'a{{#b}}ignore me{{/b}}{{^b}}b{{/}}', {'b': []})


    def test_verify_13(self):
        self.stache_verify('ab', 'a{{#b}}b{{/b}}{{^b}}ignore me{{/}}', {'b': [1]})


    def test_verify_14(self):
        self.stache_verify('ab', 'a{{#b}}b{{/b}}{{^b}}ignore me{{/}}', {'b': True})


    # test ?sections
    def test_verify_15(self):
        self.stache_verify('a- 1 2 3 4', 'a{{?b}}-{{#b}} {{.}}{{/}}{{/}}', {'b': [1, 2, 3, 4]})


    def test_verify_16(self):
        self.stache_verify('a', 'a{{?b}}ignoreme{{/}}', {'b': False})


    def test_verify_17(self):
        self.stache_verify('a', 'a{{?b}}ignoreme{{/}}', {'b': []})


    def test_verify_18(self):
        self.stache_verify('a', 'a{{?b}}ignoreme{{/}}', {})


    def test_verify_19(self):
        self.stache_verify('abb', 'a{{?b}}b{{/}}{{?b}}b{{/}}', {'b': [1, 2, 3]})


    def test_verify_20(self):
        self.stache_verify('ab123d', 'a{{?b}}b{{#b}}{{.}}{{/}}d{{/}}', {'b': [1, 2, 3]})


    # test #section scope
    def test_verify_21(self):
        self.stache_verify('abbbb', 'a{{#b}}b{{/b}}', {'b': [1, 2, 3, 4]})


    def test_verify_22(self):
        self.stache_verify('a1234', 'a{{#b}}{{.}}{{/b}}', {'b': [1, 2, 3, 4]})


    def test_verify_23(self):
        self.stache_verify('aa=1 a=2 a=0 a', 'a {{#b}}a={{a}} {{/b}}a', {'a': 0, 'b': [{'a': 1}, {'a': 2}, {'c': 1}]})

    def test_verify_23_a(self):
        self.stache_verify('a a=1 a=2 a=0 a', 'a {{#b}} a={{a}}{{/b}} a', {'a': 0, 'b': [{'a': 1}, {'a': 2}, {'c': 1}]})


    def test_verify_24(self):
        self.stache_verify('1', '{{#a}}{{#b}}{{c}}{{/b}}{{/a}}', {'a': {'b': {'c': 1}}})


    def test_verify_25(self):
        self.stache_verify('12', '{{#a}}{{#b}}{{c}}{{/}}{{/a}}', {'a': {'b': [{'c': 1}, {'c': 2}]}})


    def test_verify_26(self):
        self.stache_verify('12', '{{#a}}{{#b}}{{c}}{{/b}}{{/}}', {'a': [{'b': {'c': 1}}, {'b': {'c': 2}}]})


    def test_verify_27(self):
        self.stache_verify('132', '{{#a}}{{#b}}{{c}}{{/}}{{/}}', {'a': [{'b': [{'c': 1}, {'c': 3}]}, {'b': {'c': 2}}]})


    def test_verify_28(self):
        self.stache_verify('132456', '{{#a}}{{#b}}{{c}}{{/b}}{{/a}}', {'a': [{'b': [{'c': 1}, {'c': 3}]}, {'b': {'c': 2}}, {'b': [{'c': 4}, {'c': 5}]}, {'b': {'c': 6}}]})


    def test_verify_29(self):
        self.stache_verify('1', '{{#a}}{{#a}}{{c}}{{/a}}{{/a}}', {'a': {'a': {'c': 1}}})


    def test_verify_30(self):
        self.stache_verify('<3><3><3>', '<{{id}}><{{# a? }}{{id}}{{/ a? }}><{{# b? }}{{id}}{{/ b? }}>', {'b?': True, 'id': 3, 'a?': True})


    # test delim
    def test_verify_31(self):
        self.stache_verify('delim{{a}}', '{{=<% %>=}}<%a%>{{a}}', {'a': 'delim'})


    def test_verify_32(self):
        self.stache_verify('delim{{a}}delim<%a%>', '{{=<% %>=}}<%a%>{{a}}<%={{ }}=%>{{a}}<%a%>', {'a': 'delim'})


    # test :
    def test_verify_33(self):
        self.stache_verify('123test', '123{{:hi}}abc{{/}}', {'hi': 'test'})


    def test_verify_34(self):
        self.stache_verify('123test', '123{{:hi}}{{:hi}}abc{{/}}{{/}}', {'hi': 'test'})


    def test_verify_35(self):
        self.stache_verify('123abc', '123{{:hi}}{{:hi2}}abc{{/}}{{/}}', {})


    def test_verify_36(self):
        self.stache_verify('123cba', '123{{:hi}}{{:hi2}}abc{{/}}{{/}}', {'hi2': 'cba'})


    def test_verify_37(self):
        self.stache_verify('123abc', '123{{:hi}}abc{{/}}', {})


    def test_verify_38(self):
        self.stache_verify('123abc', '123{{:hi}}abc{{/}}', {'hi': False})


    def test_verify_39(self):
        self.stache_verify('123abc', '123{{:hi}}abc{{/}}', {'hi': []})


    def test_verify_40(self):
        self.stache_verify('123test', '{{<hi}}test{{/}}123{{:hi}}abc{{/}}', {})


    # iterators
    def test_verify_41(self):
        self.stache_verify('0123456789', '{{#a}}{{.}}{{/a}}', {'a': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]})


    def test_verify_42(self):
        self.stache_verify('02468', '{{#a}}{{.}}{{/a}}', {'a': [0, 2, 4, 6, 8]})


    # escaping
    def test_verify_43(self):
        self.stache_verify('&gt;&lt;', '{{a}}', {'a': '><'})


    def test_verify_44(self):
        self.stache_verify('><', '{{&a}}', {'a': '><'})


    def test_verify_45(self):
        self.stache_verify('><', '{{{a}}}', {'a': '><'})


s = Stache()
s.add_template('a', '1')
s.add_template('b', '{{>a}}')
s.add_template('c', '{{>a}}{{>b}}')
s.add_template('d', '{{#a}}{{b}}{{/a}}')
s.add_template('e', '{{>d}}')
s.add_template('f', '{{>e}}')
s.add_template('g', '{{<e}}123{{/e}}{{e}}')
s.add_template('h', '{{<e}}123{{/e}}{{>i}}')
s.add_template('i', 'i={{e}}')
s.add_template('j', 'show{{!ignoreme}}me')
s.add_template('k', '{{:e}}default{{/}}')
s.add_template('l', '<{{id}}><{{# a }}{{id}}{{/ a }}><{{# b }}{{id}}{{/ b }}>')
s.add_template('m', '<{{id}}><{{# a? }}{{id}}{{/ a? }}><{{# b? }}{{id}}{{/ b? }}>')
s.add_template('n', 'a{{?b}}b{{/}}{{?b}}b{{/}}')
s.add_template('o', 'a{{?b}}b{{#b}}{{.}}{{/}}d{{/}}')


class verify_partial(BaseTest):

    def stache_verify_partial(self, output, template, data={}):
        stachio = s
        #print("%s with %s" % (template, data))
        result = stachio.render_template(template, data)
        #print("Result: %s\n" % result)
        #assert output == result
        self.assertEqual(result, output)



    def test_verify_partial_01(self):
        self.stache_verify_partial('1', 'a', {})


    def test_verify_partial_02(self):
        self.stache_verify_partial('1', 'b', {})


    def test_verify_partial_03(self):
        self.stache_verify_partial('11', 'c', {})


    def test_verify_partial_04(self):
        self.stache_verify_partial('', 'd', {})


    def test_verify_partial_05(self):
        self.stache_verify_partial('555', 'd', {'a': {'b': 555}})


    def test_verify_partial_06(self):
        self.stache_verify_partial('123', 'g', {'a': {}})


    def test_verify_partial_07(self):
        self.stache_verify_partial('555', 'e', {'a': {'b': 555}})


    def test_verify_partial_08(self):
        self.stache_verify_partial('555', 'f', {'a': {'b': 555}})


    def test_verify_partial_09(self):
        self.stache_verify_partial('i=123', 'h', {})


    def test_verify_partial_10(self):
        self.stache_verify_partial('i=', 'i', {})


    def test_verify_partial_11(self):
        self.stache_verify_partial('showme', 'j', {})


    def test_verify_partial_12(self):
        self.stache_verify_partial('default', 'k', {})


    def test_verify_partial_13(self):
        self.stache_verify_partial('custom', 'k', {'e': 'custom'})


    def test_verify_partial_14(self):
        self.stache_verify_partial('<3><3><3>', 'l', {'a': True, 'b': True, 'id': 3})


    def test_verify_partial_15(self):
        self.stache_verify_partial('<3><3><3>', 'm', {'b?': True, 'id': 3, 'a?': True})


    def test_verify_partial_16(self):
        self.stache_verify_partial('abb', 'n', {'b': [1, 2, 3]})


    def test_verify_partial_17(self):
        self.stache_verify_partial('ab123d', 'o', {'b': [1, 2, 3]})


class RaisesErrors(BaseTest):

    def test_good_tags(self):
        self.stache_verify('1', '{{#a}}{{b}}{{/a}}', {'a': {'b': '1'}})

    def test_mismatched_tags(self):  # compare with test_good_tags()
        #self.stache_verify('1', '{{#a}}{{b}}{{/b}}', {'a': {'b': '1'}})  # 'a' not closed, attempts to close 'b' instead
        self.assertRaises(AssertionError, self.stache_verify, '1', '{{#a}}{{b}}{{/b}}', {'a': {'b': '1'}})  # 'a' not closed, attempts to close 'b' instead
        # TODO check error/exception documents correct tags in error

def main(argv=None):
    if argv is None:
        argv = sys.argv

    print('Python %s on %s' %(sys.version, sys.platform))
    unittest.main()

    return 0


if __name__ == "__main__":
    sys.exit(main())

# end generated code
