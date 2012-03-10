from __init__ import Stache, render
import timeit

def verify(output, template, data):
    print "%s with %s" % (template, data)
    result = render(template, data)
    result_iter = ''.join(Stache().render_iter(template, data))
    print "Result: %s\n" % result
    assert result == output
    assert result == result_iter

def bench(output, template, data):
    t = timeit.Timer("render('%s', %s)" % (template, data), "from __main__ import render")
    print "%.2f\tusec/test > %s with %s" % (1000000 * t.timeit(number=10000)/10000, template, data)

def bare(output, template, data):
    return render(template, data)

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
    yield method, 'ab', 'a{{#b}}b{{/b}}{{^b}}ignore me{{/}}', dict(b=[1])
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
    yield method, 'a a=1 a=2 a=0 ', 'a {{#b}}a={{a}} {{/b}}', dict(a=0,b=[{'a':1},{'a':2},{'c':1}])
    yield method, '1', '{{#a}}{{#b}}{{c}}{{/b}}{{/a}}', dict(a={'b':{'c':1}})
    yield method, '12', '{{#a}}{{#b}}{{c}}{{/}}{{/a}}', dict(a={'b':[{'c':1}, {'c':2}]})
    yield method, '12', '{{#a}}{{#b}}{{c}}{{/b}}{{/}}', dict(a=[{'b':{'c':1}},{'b':{'c':2}}])
    yield method, '132', '{{#a}}{{#b}}{{c}}{{/}}{{/}}', dict(a=[{'b':[{'c':1}, {'c':3}]},{'b':{'c':2}}])
    yield method, '132456', '{{#a}}{{#b}}{{c}}{{/b}}{{/a}}', dict(a=[{'b':[{'c':1}, {'c':3}]},{'b':{'c':2}},{'b':[{'c':4}, {'c':5}]},{'b':{'c':6}}])
    yield method, '1', '{{#a}}{{#a}}{{c}}{{/a}}{{/a}}', dict(a={'a':{'c':1}})
    yield method, '<3><3><3>', '<{{id}}><{{# a? }}{{id}}{{/ a? }}><{{# b? }}{{id}}{{/ b? }}>', {'id':3,'a?':True, 'b?':True}
    #test delim
    yield method, 'delim{{}}', '{{=<% %>=}}<%a%>{{}}', dict(a='delim')
    #test :
    yield method, '123test', '123{{:hi}}abc{{/}}', dict(hi='test')
    yield method, '123test', '123{{:hi}}{{:hi}}abc{{/}}{{/}}', dict(hi='test')
    yield method, '123abc', '123{{:hi}}{{:hi2}}abc{{/}}{{/}}', dict()
    yield method, '123cba', '123{{:hi}}{{:hi2}}abc{{/}}{{/}}', dict(hi2='cba')
    yield method, '123abc', '123{{:hi}}abc{{/}}', dict()
    yield method, '123abc', '123{{:hi}}abc{{/}}', dict(hi=False)
    yield method, '123abc', '123{{:hi}}abc{{/}}', dict(hi=[])
    yield method, '123test', '{{<hi}}test{{/}}123{{:hi}}abc{{/}}', dict()

def verify_partial(stachio, output, template, data={}):
    print "%s with %s" % (template, data)
    result = stachio.render_template(template, data)
    print "Result: %s\n" % result
    assert output == result

def bare_partial(stachio, output, template, data={}):
    return stachio.render_template(template, data)

def test_partials(method = bare_partial):
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

    yield method, s, '1', 'b'
    yield method, s, '11', 'c'
    yield method, s, '555', 'e', dict(a={'b':555})
    yield method, s, '555', 'f', dict(a={'b':555})
    yield method, s, 'i=123', 'h'



def run(method=bare, partial_method=bare_partial):
    for x in test(method):
        x[0](*x[1:])
    for x in test_partials(partial_method):
        x[0](*x[1:])

if __name__ == '__main__':
    print 'starting tests'
    run(verify, verify_partial)
    print 'finished tests'
    print 'starting individual benchmarks'
    run(bench)
    print 'starting combined benchmark'
    t = timeit.Timer("run()", "from __main__ import run, bare")
    print "%.2f\tusec/all tests" % (1000000 * t.timeit(number=10000)/10000)