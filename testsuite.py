from __future__ import generators
import sys
import warnings
try:
    import timeit
except ImportError:
    # TODO fake it?
    timeit = None
try:
    import subprocess
except ImportError:
    subprocess = None

try:
    import json
except ImportError:
    # TODO import simplejson, etc.
    json = None

from stache import Stache, render, render_js


skip_bool = False
if sys.version_info < (2, 3):
    skip_bool = True

def mydict(*args, **kwargs):
    """Emulate Python 2.3 dict keyword support
    """
    if args:
        raise NotImplementedError('args not supported')
    if kwargs:
        return kwargs
    else:
        return {}

def verify(output, template, data):
    print("%s with %s" % (template, data))
    result = render(template, data)
    result_iter = ''.join(Stache().render_iter(template, data))
    print("Output: %s\n" % output)
    print("Result: %s\n" % result)
    assert result == output
    assert result == result_iter

def verify_js(output, template, data):
    if json is None:
        warnings.warn('json module missing, skipping this js test')
        return
    script = render_js(template)
    print("%s with %s" % (template, data))
    result = subprocess.check_output(["node", "-e", "console.log({0}({1}))".format(script,  json.dumps(data))]).strip()
    print("Result: %s\n" % result)
    assert output.lower() == result

def verify_js_partial(stachio, output, template, data={}):
    if json is None:
        warnings.warn('json module missing, skipping this js test')
        return
    print("%s with %s" % (template, data))
    script = stachio.render_js_template(template)
    result = subprocess.check_output(["node", "-e", "console.log({0}({1}))".format(script,  json.dumps(data))]).strip()
    print("Result: %s\n" % result)
    assert output.lower() == result

def bare_js_partial(stachio, output, template, data={}):
    if json is None:
        warnings.warn('json module missing, skipping this js test')
        return
    return stachio.render_js_template(template)

def verify_partial(stachio, output, template, data={}):
    print("%s with %s" % (template, data))
    result = stachio.render_template(template, data)
    print("Result: %s\n" % result)
    assert output == result

def bench(output, template, data):
    if timeit is None:
        warnings.warn('timeit module missing, skipping this test')
        return
    t = timeit.Timer("render('%s', %s)" % (template, data), "from __main__ import render")
    print("%.2f\tusec/test > python %s with %s" % (1000000 * t.timeit(number=10000)/10000, template, data))

def bench_js(output, template, data):
    if timeit is None:
        warnings.warn('timeit module missing, skipping this test')
        return
    t = timeit.Timer("render_js('%s')" % (template), "from __main__ import render_js")
    print("%.2f\tusec/test > js %s with %s" % (1000000 * t.timeit(number=10000)/10000, template, data))

def bench_partial(stachio, output, template, data={}):
    if timeit is None:
        warnings.warn('timeit module missing, skipping this test')
        return
    t = timeit.Timer("s.render_template('%s', %s)" % (template, data),  "from __main__ import test_partials, s")
    print("%.2f\tusec/test > python partial %s with %s" % (1000000 * t.timeit(number=10000)/10000, template, data))

def bench_js_partial(stachio, output, template, data={}):
    if timeit is None:
        warnings.warn('timeit module missing, skipping this test')
        return
    t = timeit.Timer("s.render_template('%s', %s)" % (template, data),  "from __main__ import test_partials, s")
    print("%.2f\tusec/test > js_partial %s with %s" % (1000000 * t.timeit(number=10000)/10000, template, data))

def bare(output, template, data):
    return render(template, data)

def bare_js(output, template, data):
    script = render_js(template)

def bare_partial(stachio, output, template, data={}):
    return stachio.render_template(template, data)

def test(method=bare):
    # test tag lookup
    yield method, 'a10c', 'a{{b}}c', mydict(b=10)
    yield method, 'a10c', 'a{{b}}c', mydict(b=10)
    yield method, 'ac', 'a{{b}}c', mydict(c=10)
    yield method, 'a10c', 'a{{b}}c', mydict(b='10')
    yield method, 'acde', 'a{{!b}}cde', mydict(b='10')
    if not skip_bool:
        yield method, 'aTrue', 'a{{b}}', mydict(b=True)
    yield method, 'a123', 'a{{b}}{{c}}{{d}}', mydict(b=1,c=2,d=3)
    # test falsy #sections
    if not skip_bool:
        yield method, 'ab', 'a{{#b}}b{{/b}}', mydict(b=True)
        yield method, 'a', 'a{{^b}}b{{/b}}', mydict(b=True)
        yield method, 'a', 'a{{#b}}b{{/}}', mydict(b=False)
        yield method, 'ab', 'a{{^b}}b{{/b}}', mydict(b=False)
    #test invert sections
    yield method, 'ab', 'a{{#b}}ignore me{{/b}}{{^b}}b{{/}}', mydict(b=[])
    yield method, 'ab', 'a{{#b}}b{{/b}}{{^b}}ignore me{{/}}', mydict(b=[1])
    if not skip_bool:
        yield method, 'ab', 'a{{#b}}b{{/b}}{{^b}}ignore me{{/}}', mydict(b=True)
    #test ?sections
    yield method, 'a- 1 2 3 4', 'a{{?b}}-{{#b}} {{.}}{{/}}{{/}}', mydict(b=[1,2,3,4])
    if not skip_bool:
        yield method, 'a', 'a{{?b}}ignoreme{{/}}', mydict(b=False)
    yield method, 'a', 'a{{?b}}ignoreme{{/}}', mydict(b=[])
    yield method, 'a', 'a{{?b}}ignoreme{{/}}', mydict()
    yield method, 'abb', 'a{{?b}}b{{/}}{{?b}}b{{/}}', mydict(b=[1,2,3])
    yield method, 'ab123d', 'a{{?b}}b{{#b}}{{.}}{{/}}d{{/}}', mydict(b=[1,2,3])
    #test #section scope
    yield method, 'abbbb', 'a{{#b}}b{{/b}}', mydict(b=[1,2,3,4])
    yield method, 'a1234', 'a{{#b}}{{.}}{{/b}}', mydict(b=[1,2,3,4])
    yield method, 'a a=1 a=2 a=0 a', 'a {{#b}}a={{a}} {{/b}}a', mydict(a=0,b=[{'a':1},{'a':2},{'c':1}])
    yield method, '1', '{{#a}}{{#b}}{{c}}{{/b}}{{/a}}', mydict(a={'b':{'c':1}})
    yield method, '12', '{{#a}}{{#b}}{{c}}{{/}}{{/a}}', mydict(a={'b':[{'c':1}, {'c':2}]})
    yield method, '12', '{{#a}}{{#b}}{{c}}{{/b}}{{/}}', mydict(a=[{'b':{'c':1}},{'b':{'c':2}}])
    yield method, '132', '{{#a}}{{#b}}{{c}}{{/}}{{/}}', mydict(a=[{'b':[{'c':1}, {'c':3}]},{'b':{'c':2}}])
    yield method, '132456', '{{#a}}{{#b}}{{c}}{{/b}}{{/a}}', mydict(a=[{'b':[{'c':1}, {'c':3}]},{'b':{'c':2}},{'b':[{'c':4}, {'c':5}]},{'b':{'c':6}}])
    yield method, '1', '{{#a}}{{#a}}{{c}}{{/a}}{{/a}}', mydict(a={'a':{'c':1}})
    if not skip_bool:
        yield method, '<3><3><3>', '<{{id}}><{{# a? }}{{id}}{{/ a? }}><{{# b? }}{{id}}{{/ b? }}>', {'id':3,'a?':True, 'b?':True}
    #test delim
    yield method, 'delim{{a}}', '{{=<% %>=}}<%a%>{{a}}', mydict(a='delim')
    yield method, 'delim{{a}}delim<%a%>', '{{=<% %>=}}<%a%>{{a}}<%={{ }}=%>{{a}}<%a%>', mydict(a='delim')
    #test :
    yield method, '123test', '123{{:hi}}abc{{/}}', mydict(hi='test')
    yield method, '123test', '123{{:hi}}{{:hi}}abc{{/}}{{/}}', mydict(hi='test')
    yield method, '123abc', '123{{:hi}}{{:hi2}}abc{{/}}{{/}}', mydict()
    yield method, '123cba', '123{{:hi}}{{:hi2}}abc{{/}}{{/}}', mydict(hi2='cba')
    yield method, '123abc', '123{{:hi}}abc{{/}}', mydict()
    if not skip_bool:
        yield method, '123abc', '123{{:hi}}abc{{/}}', mydict(hi=False)
    yield method, '123abc', '123{{:hi}}abc{{/}}', mydict(hi=[])
    yield method, '123test', '{{<hi}}test{{/}}123{{:hi}}abc{{/}}', mydict()
    #iterators
    yield method, '0123456789', '{{#a}}{{.}}{{/a}}', mydict(a=range(10))
    yield method, '02468', '{{#a}}{{.}}{{/a}}', mydict(a=list(filter(lambda x: x%2==0, range(10))))
    #escaping
    yield method, '&gt;&lt;', '{{a}}', mydict(a='><')
    yield method, '><', '{{&a}}', mydict(a='><')
    yield method, '><', '{{{a}}}', mydict(a='><')

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

def test_partials(method=bare_partial):
    yield method, s, '1', 'a', mydict()
    yield method, s, '1', 'b', mydict()
    yield method, s, '11', 'c', mydict()
    yield method, s, '', 'd', mydict()
    yield method, s, '555', 'd', mydict(a={'b':555})
    yield method, s, '123', 'g', mydict(a={})
    yield method, s, '555', 'e', mydict(a={'b':555})
    yield method, s, '555', 'f', mydict(a={'b':555})
    yield method, s, 'i=123', 'h', mydict()
    yield method, s, 'i=', 'i', mydict()
    yield method, s, 'showme', 'j', mydict()
    yield method, s, 'default', 'k', mydict()
    yield method, s, 'custom', 'k', mydict(e="custom")
    if not skip_bool:
        yield method, s, '<3><3><3>', 'l', {'id':3,'a':True, 'b':True}
        yield method, s, '<3><3><3>', 'm', {'id':3,'a?':True, 'b?':True}
    yield method, s, 'abb', 'n', mydict(b=[1,2,3])
    yield method, s, 'ab123d', 'o', mydict(b=[1,2,3])

def test_js(method=verify_js):
    return
    for x in test(method):
        yield x

def null(*args, **kwargs):
    return

def run(method=bare, method_partial=bare_partial, method_js=bare_js, method_js_partial=bare_js_partial):
    for x in test(method):
        x[0](*x[1:])
    for x in test_partials(method_partial):
        x[0](*x[1:])
    for x in test_js(method_js):
        x[0](*x[1:])
    for x in test_partials(method_js_partial):
        x[0](*x[1:])

def test_js_all():
    return
    expected = []
    script = 't = ('
    script += s.render_all_js()
    script += ')();\n'
    for x in test_partials():
        script += "console.log(t['{1}']([{2}]));\n".format(x[2], x[3], json.dumps(x[4]))
        expected.append(x[2])
    res = subprocess.check_output(["node", "-e", script]).split('\n')[:-1]
    assert res == expected

if __name__ == '__main__':
    
    print('starting tests')
    run(verify, verify_partial, verify_js, verify_js_partial)
    print('finished tests')
    print('testing js export templates')
    test_js_all()
    print('starting individual benchmarks')
    run(bench, bench_partial, bench_js, bench_js_partial)
    if timeit is None:
        warnings.warn('timeit module missing, skipping this test')
    else:
        print('starting combined python benchmark')
        t = timeit.Timer("run(method_js=null, method_js_partial=null)", "from __main__ import run, bare, null")
        print("%.2f\tusec/all tests" % (1000000 * t.timeit(number=10000)/10000))
        print('starting combined js benchmark')
        t = timeit.Timer("run(method=null, method_partial=null)", "from __main__ import run, bare, null")
        print("%.2f\tusec/all js tests" % (1000000 * t.timeit(number=10000)/10000))

