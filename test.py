try:
    from __init__ import Stache, render, render_js
except ImportError:
    from . import Stache, render, render_js

import timeit
import subprocess

def verify(output, template, data):
    print("%s with %s" % (template, data))
    result = render(template, data)
    result_iter = ''.join(Stache().render_iter(template, data))
    print("Result: %s\n" % result)
    assert result == output
    assert result == result_iter

def verify_js(output, template, data):
    import json
    script = render_js(template)
    print("%s with %s" % (template, data))
    result = subprocess.check_output(["node", "-e", "console.log({0}({1}))".format(script,  json.dumps(data))]).strip()
    print("Result: %s\n" % result)
    assert output.lower() == result

def verify_partial(stachio, output, template, data={}):
    print("%s with %s" % (template, data))
    result = stachio.render_template(template, data)
    print("Result: %s\n" % result)
    assert output == result

def verify_js_partial(stachio, output, template, data={}):
    import json
    print("%s with %s" % (template, data))
    script = stachio.render_js_template(template)
    result = subprocess.check_output(["node", "-e", "console.log({0}({1}))".format(script,  json.dumps(data))]).strip()
    print("Result: %s\n" % result)
    assert output.lower() == result

def bench(output, template, data):
    t = timeit.Timer("render('%s', %s)" % (template, data), "from __main__ import render")
    print("%.2f\tusec/test > python %s with %s" % (1000000 * t.timeit(number=10000)/10000, template, data))

def bench_js(output, template, data):
    t = timeit.Timer("render_js('%s')" % (template), "from __main__ import render_js")
    print("%.2f\tusec/test > js %s with %s" % (1000000 * t.timeit(number=10000)/10000, template, data))

def bench_partial(stachio, output, template, data={}):
    t = timeit.Timer("s.render_template('%s', %s)" % (template, data),  "from __main__ import test_partials, s")
    print("%.2f\tusec/test > python partial %s with %s" % (1000000 * t.timeit(number=10000)/10000, template, data))

def bench_js_partial(stachio, output, template, data={}):
    t = timeit.Timer("s.render_template('%s', %s)" % (template, data),  "from __main__ import test_partials, s")
    print("%.2f\tusec/test > js_partial %s with %s" % (1000000 * t.timeit(number=10000)/10000, template, data))

def bare(output, template, data):
    return render(template, data)

def bare_js(output, template, data):
    script = render_js(template)

def bare_partial(stachio, output, template, data={}):
    return stachio.render_template(template, data)

def bare_js_partial(stachio, output, template, data={}):
    return stachio.render_js_template(template)

def test(method=bare):
    # test tag lookup
    yield method, 'a10c', 'a{{b}}c', dict(b=10)
    yield method, 'a10c', 'a{{b}}c', dict(b=10)
    yield method, 'ac', 'a{{b}}c', dict(c=10)
    yield method, 'a10c', 'a{{b}}c', dict(b='10')
    yield method, 'acde', 'a{{!b}}cde', dict(b='10')
    yield method, 'aTrue', 'a{{b}}', dict(b=True)
    yield method, 'a123', 'a{{b}}{{c}}{{d}}', dict(b=1,c=2,d=3)
    # test falsy #sections
    yield method, 'ab', 'a{{#b}}b{{/b}}', dict(b=True)
    yield method, 'a', 'a{{^b}}b{{/b}}', dict(b=True)
    yield method, 'a', 'a{{#b}}b{{/}}', dict(b=False)
    yield method, 'ab', 'a{{^b}}b{{/b}}', dict(b=False)
    #test invert sections
    yield method, 'ab', 'a{{#b}}ignore me{{/b}}{{^b}}b{{/}}', dict(b=[])
    yield method, 'ab', 'a{{#b}}b{{/b}}{{^b}}ignore me{{/}}', dict(b=[1])
    yield method, 'ab', 'a{{#b}}b{{/b}}{{^b}}ignore me{{/}}', dict(b=True)
    #test ?sections
    yield method, 'a- 1 2 3 4', 'a{{?b}}-{{#b}} {{.}}{{/}}{{/}}', dict(b=[1,2,3,4])
    yield method, 'a', 'a{{?b}}ignoreme{{/}}', dict(b=False)
    yield method, 'a', 'a{{?b}}ignoreme{{/}}', dict(b=[])
    yield method, 'a', 'a{{?b}}ignoreme{{/}}', dict()
    yield method, 'abb', 'a{{?b}}b{{/}}{{?b}}b{{/}}', dict(b=[1,2,3])
    yield method, 'ab123d', 'a{{?b}}b{{#b}}{{.}}{{/}}d{{/}}', dict(b=[1,2,3])
    #test #section scope
    yield method, 'abbbb', 'a{{#b}}b{{/b}}', dict(b=[1,2,3,4])
    yield method, 'a1234', 'a{{#b}}{{.}}{{/b}}', dict(b=[1,2,3,4])
    yield method, 'a a=1 a=2 a=0 a', 'a {{#b}}a={{a}} {{/b}}a', dict(a=0,b=[{'a':1},{'a':2},{'c':1}])
    yield method, '1', '{{#a}}{{#b}}{{c}}{{/b}}{{/a}}', dict(a={'b':{'c':1}})
    yield method, '12', '{{#a}}{{#b}}{{c}}{{/}}{{/a}}', dict(a={'b':[{'c':1}, {'c':2}]})
    yield method, '12', '{{#a}}{{#b}}{{c}}{{/b}}{{/}}', dict(a=[{'b':{'c':1}},{'b':{'c':2}}])
    yield method, '132', '{{#a}}{{#b}}{{c}}{{/}}{{/}}', dict(a=[{'b':[{'c':1}, {'c':3}]},{'b':{'c':2}}])
    yield method, '132456', '{{#a}}{{#b}}{{c}}{{/b}}{{/a}}', dict(a=[{'b':[{'c':1}, {'c':3}]},{'b':{'c':2}},{'b':[{'c':4}, {'c':5}]},{'b':{'c':6}}])
    yield method, '1', '{{#a}}{{#a}}{{c}}{{/a}}{{/a}}', dict(a={'a':{'c':1}})
    yield method, '<3><3><3>', '<{{id}}><{{# a? }}{{id}}{{/ a? }}><{{# b? }}{{id}}{{/ b? }}>', {'id':3,'a?':True, 'b?':True}
    #test delim
    yield method, 'delim{{a}}', '{{=<% %>=}}<%a%>{{a}}', dict(a='delim')
    yield method, 'delim{{a}}delim<%a%>', '{{=<% %>=}}<%a%>{{a}}<%={{ }}=%>{{a}}<%a%>', dict(a='delim')
    #test :
    yield method, '123test', '123{{:hi}}abc{{/}}', dict(hi='test')
    yield method, '123test', '123{{:hi}}{{:hi}}abc{{/}}{{/}}', dict(hi='test')
    yield method, '123abc', '123{{:hi}}{{:hi2}}abc{{/}}{{/}}', dict()
    yield method, '123cba', '123{{:hi}}{{:hi2}}abc{{/}}{{/}}', dict(hi2='cba')
    yield method, '123abc', '123{{:hi}}abc{{/}}', dict()
    yield method, '123abc', '123{{:hi}}abc{{/}}', dict(hi=False)
    yield method, '123abc', '123{{:hi}}abc{{/}}', dict(hi=[])
    yield method, '123test', '{{<hi}}test{{/}}123{{:hi}}abc{{/}}', dict()
    #iterators
    yield method, '0123456789', '{{#a}}{{.}}{{/a}}', dict(a=range(10))
    yield method, '02468', '{{#a}}{{.}}{{/a}}', dict(a=list(filter(lambda x: x%2==0, range(10))))
    #escaping
    yield method, '&gt;&lt;', '{{a}}', dict(a='><')
    yield method, '><', '{{&a}}', dict(a='><')
    yield method, '><', '{{{a}}}', dict(a='><')

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
    yield method, s, '1', 'a', dict()
    yield method, s, '1', 'b', dict()
    yield method, s, '11', 'c', dict()
    yield method, s, '', 'd', dict()
    yield method, s, '555', 'd', dict(a={'b':555})
    yield method, s, '123', 'g', dict(a={})
    yield method, s, '555', 'e', dict(a={'b':555})
    yield method, s, '555', 'f', dict(a={'b':555})
    yield method, s, 'i=123', 'h', dict()
    yield method, s, 'i=', 'i', dict()
    yield method, s, 'showme', 'j', dict()
    yield method, s, 'default', 'k', dict()
    yield method, s, 'custom', 'k', dict(e="custom")
    yield method, s, '<3><3><3>', 'l', {'id':3,'a':True, 'b':True}
    yield method, s, '<3><3><3>', 'm', {'id':3,'a?':True, 'b?':True}
    yield method, s, 'abb', 'n', dict(b=[1,2,3])
    yield method, s, 'ab123d', 'o', dict(b=[1,2,3])

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
    print('starting combined python benchmark')
    t = timeit.Timer("run(method_js=null, method_js_partial=null)", "from __main__ import run, bare, null")
    print("%.2f\tusec/all tests" % (1000000 * t.timeit(number=10000)/10000))
    print('starting combined js benchmark')
    t = timeit.Timer("run(method=null, method_partial=null)", "from __main__ import run, bare, null")
    print("%.2f\tusec/all js tests" % (1000000 * t.timeit(number=10000)/10000))

