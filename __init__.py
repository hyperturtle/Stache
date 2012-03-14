import itertools
from cgi import escape


try:
    from sys import intern
except ImportError:
    pass

TOKEN_RAW        = intern('raw')
TOKEN_TAGOPEN    = intern('tagopen')
TOKEN_TAGINVERT  = intern('taginvert')
TOKEN_TAGCLOSE   = intern('tagclose')
TOKEN_TAGCOMMENT = intern('tagcomment')
TOKEN_TAGDELIM   = intern('tagdelim')
TOKEN_TAG        = intern('tag')
TOKEN_PARTIAL    = intern('partial')
TOKEN_PUSH       = intern('push')
TOKEN_BOOL       = intern('bool')


BOOTSRAP_PRE = """
(function(data){
  var isArray = Array.isArray || function(obj) {
        return toString.call(obj) == '[object Array]';
      },
      each = function(obj, iterator, context) {
        if (obj == null) return;
        if (Array.prototype.forEach && obj.forEach === Array.prototype.forEach) {
          obj.forEach(iterator, context);
        } else if (obj.length === +obj.length) {
          for (var i = 0, l = obj.length; i < l; i++) {
            if (i in obj && iterator.call(context, obj[i], i, obj) === breaker) return;
          }
        } else {
          for (var key in obj) {
            if (obj.hasOwnProperty(key)) {
              if (iterator.call(context, obj[key], key, obj) === breaker) return;
            }
          }
        }
      },
      map = function(obj, iterator, context) {
        var results = [];
        if (obj == null) return results;
        if (Array.prototype.map && obj.map === Array.prototype.map) return obj.map(iterator, context);
        each(obj, function(value, index, list) {
          results[results.length] = iterator.call(context, value, index, list);
        });
        if (obj.length === +obj.length) results.length = obj.length;
        return results;
      },
      htmlEncode = function(str) {
        return String(str)
          .replace(/&/g, '&amp;')
          .replace(/"/g, '&quot;')
          .replace(/'/g, '&#39;')
          .replace(/</g, '&lt;')
          .replace(/>/g, '&gt;');
      },
      lookup = function (data, datum) {
        var i = 0,
            l = data ? data.length : 0;
        for (; i < l; i += 1) {
          if (datum === '.') {
            return data[i]
          } else if (data[i] !== void 0 && data[i][datum] !== void 0 && data[i][datum] !== false) {
            if (toString.call(data[i][datum]) == '[object Function]') {
                return data[i][datum](data)
            } else {
                return data[i][datum]
            }
          }
        }
        return '';
      },
      section = function(data, tagvalue, callback, invert){
        invert = invert || false;
        if (isArray(tagvalue)) {
          if (!invert && tagvalue.length > 0) {
            return map(tagvalue, function(v) { return callback([v].concat(data))}).join('')
          } else if (invert && tagvalue.length == 0) {
            return callback(data);
          }
        } else {
          if((!invert && tagvalue) || (invert && !tagvalue)) {
            if (tagvalue !== void 0 || tagvalue !== true) {
              return callback([tagvalue].concat(data));
            } else {
              return callback(data);
            }
          }
        }
     };
"""

BOOTSRAP_POST = """
})
"""


def _checkprefix(tag, prefix):
    return tag[1:].strip() if tag and tag[0] == prefix else None


def _lookup(data, datum):
    for scope in data:
        if datum == '.':
            return str(scope)
        elif datum in scope:
            return scope[datum]
        elif hasattr(scope, datum):
            return getattr(scope, datum)
    return None


def _renderjsfunction(parts, prefix = "", postfix = "", params="data, tag"):
    return "function({params}) {{{prefix} return {content} {postfix} }}".format(
        content=_renderjsjoin(*parts),
        prefix=prefix,
        postfix=postfix,
        params=params)


def _renderjsjoin(*args):
    return "[{0}].join('');".format(','.join(args))


def render(template, data):
    return Stache().render(template, data)


def render_js(template):
    return Stache().render_js(template)


class Stache(object):
    def __init__(self):
        self.otag = '{{'
        self.ctag = '}}'
        self.templates = {}
        self.hoist = {}
        self.hoist_data = {}
        self.section_counter = 0

    def copy(self):
        copy = Stache()
        copy.templates = self.templates
        return copy

    def add_template(self, name, template):
        self.templates[name] = list(self._tokenize(template))

    def render(self, template, data={}):
        self.otag = '{{'
        self.ctag = '}}'
        return ''.join(self._parse(self._tokenize(template), data))

    def render_iter(self, template, data={}):
        copy = self.copy()
        return copy._parse(copy._tokenize(template), data)

    def render_template(self, template_name, data={}):
        self.otag = '{{'
        self.ctag = '}}'
        return ''.join(self._parse(iter(list(self.templates[template_name])), data))

    def render_template_iter(self, template_name, data={}):
        copy = self.copy()
        return copy._parse(iter(list(copy.templates[template_name])), data)

    def _js_hoisted(self, bare=True):
        hoist = ''

        if self.templates:
            hoist += "\n  var templates = {};\n"
            for name in self.templates:
                render_function = list(self._jsparse(iter(list(self.templates[name]))))
                newparams = "data"
                prefix = ""
                if not bare and self.hoist_data:
                    hoisted = map(lambda x: '"{0}": {1}, '.format(x, self.hoist_data[x], "baseData"), self.hoist_data.keys()) 
                    prefix = ' var data = [dat2, {{{0}}}];'.format(', '.join(hoisted))
                    self.hoist_data = {}
                    newparams = 'dat2';
                hoist += '  templates["{0}"] = {1};\n'.format(name, _renderjsfunction(render_function, prefix=prefix, params=newparams))
        if self.hoist:
            for name in self.hoist:
                hoist += '  var {0} = {1};\n'.format(name, self.hoist[name])
        if bare:
            if self.hoist_data:
                for name in self.hoist_data:
                    hoist += '  {2}["{0}"] = {1};\n'.format(name, self.hoist_data[name], "data")

        return hoist

    def render_js(self, template):
        copy       = self.copy()
        renderedjs = _renderjsjoin(*list(copy._jsparse(copy._tokenize(template))))
        hoist      = copy._js_hoisted()
        jstemplate = "{0}\n  {1}\n  data = [data];\n  return {2};\n{3}"

        return jstemplate.format(BOOTSRAP_PRE, hoist, renderedjs, BOOTSRAP_POST)

    def render_js_template(self, template_name):
        copy       = self.copy()
        hoist      = copy._js_hoisted(bare=False)
        jstemplate = "{0}\n  {1}\n  return templates['{2}']([data]);\n{3}"

        return jstemplate.format(BOOTSRAP_PRE, hoist, template_name, BOOTSRAP_POST)

    def render_all_js(self):
        copy       = self.copy()
        hoist      = copy._js_hoisted(bare=False)
        jstemplate = "{0}\n  var baseData={{}};\n  {1}\n  return templates;\n{2}"
        return jstemplate.format(BOOTSRAP_PRE, hoist, BOOTSRAP_POST)

    def _tokenize(self, template):
        rest  = template
        scope = []

        while rest and len(rest) > 0:
            pre_section    = rest.split(self.otag, 1)
            pre, rest      = pre_section if len(pre_section) == 2 else (pre_section[0], None)
            taglabel, rest = rest.split(self.ctag, 1) if rest else (None, None)
            taglabel       = taglabel.strip() if taglabel else ''
            open_tag       = _checkprefix(taglabel, '#')
            invert_tag     = _checkprefix(taglabel, '^') if not open_tag else None
            close_tag      = _checkprefix(taglabel, '/') if not invert_tag else None
            comment_tag    = _checkprefix(taglabel, '!') if not close_tag else None
            partial_tag    = _checkprefix(taglabel, '>') if not comment_tag else None
            push_tag       = _checkprefix(taglabel, '<') if not partial_tag else None
            bool_tag       = _checkprefix(taglabel, '?') if not push_tag else None
            booltern_tag   = _checkprefix(taglabel, ':') if not bool_tag else None
            unescape_tag   = _checkprefix(taglabel, '{') if not booltern_tag else None
            rest           = rest[1:] if unescape_tag else rest
            unescape_tag   = (unescape_tag or _checkprefix(taglabel, '&')) if not booltern_tag else None
            delim_tag      = taglabel[1:-1] if not unescape_tag and len(taglabel) >= 2 and taglabel[0] == '=' and taglabel[-1] == '=' else None
            delim_tag      = delim_tag.split(' ', 1) if delim_tag else None
            delim_tag      = delim_tag if delim_tag and len(delim_tag) == 2 else None

            if push_tag:
                pre = pre.rstrip()
                rest = rest.lstrip()

            if pre:
                yield TOKEN_RAW, pre, len(scope)

            if open_tag:
                scope.append(open_tag)
                yield TOKEN_TAGOPEN, open_tag, len(scope)
            elif bool_tag:
                scope.append(bool_tag)
                yield TOKEN_BOOL, bool_tag, len(scope)
            elif invert_tag:
                scope.append(invert_tag)
                yield TOKEN_TAGINVERT, invert_tag, len(scope)
            elif close_tag is not None:
                current_scope = scope.pop()
                if close_tag:
                    assert (current_scope == close_tag), 'Mismatch open/close blocks'
                yield TOKEN_TAGCLOSE, current_scope, len(scope)+1
            elif booltern_tag:
                scope.append(booltern_tag)
                yield TOKEN_TAG, booltern_tag, 0
                yield TOKEN_TAGINVERT, booltern_tag, len(scope)
            elif comment_tag:
                yield TOKEN_TAGCOMMENT, comment_tag, 0
            elif partial_tag:
                yield TOKEN_PARTIAL, partial_tag, 0
            elif push_tag:
                scope.append(push_tag)
                yield TOKEN_PUSH, push_tag, len(scope)
            elif delim_tag:
                yield TOKEN_TAGDELIM, delim_tag, 0
            elif unescape_tag:
                yield TOKEN_TAG, unescape_tag, True
            else:
                yield TOKEN_TAG, taglabel, False

    def _parse(self, tokens, *data):
        for token in tokens:
            #print '    token:' + str(token)
            tag, content, scope = token
            if tag == TOKEN_RAW:
                yield str(content)
            elif tag == TOKEN_TAG:
                tagvalue = _lookup(data, content)
                #cant use if tagvalue because we need to render tagvalue if it's 0
                #testing if tagvalue == 0, doesnt work since False == 0
                if tagvalue is not None and tagvalue is not False:
                    try:
                        if len(tagvalue) > 0:
                            if scope:
                                yield str(tagvalue)
                            else:
                                yield escape(str(tagvalue))
                    except TypeError:
                        if scope:
                            yield str(tagvalue)
                        else:
                            yield escape(str(tagvalue))
            elif tag == TOKEN_TAGOPEN or tag == TOKEN_TAGINVERT:
                tagvalue = _lookup(data, content)
                untilclose = itertools.takewhile(lambda x: x != (TOKEN_TAGCLOSE, content, scope), tokens)
                if (tag == TOKEN_TAGOPEN and tagvalue) or (tag == TOKEN_TAGINVERT and not tagvalue):
                    if hasattr(tagvalue, 'items'):
                        #print '    its a dict!', tagvalue, untilclose
                        for part in self._parse(untilclose, tagvalue, *data):
                            yield part
                    else:
                        try:
                            iterlist = list(iter(tagvalue))
                            if len(iterlist) == 0:
                                raise TypeError
                            #print '    its a list!', list(rest)
                            #from http://docs.python.org/library/itertools.html#itertools.tee
                            #In general, if one iterator uses most or all of the data before
                            #another iterator starts, it is faster to use list() instead of tee().
                            rest = list(untilclose)
                            for listitem in iterlist:
                                for part in self._parse(iter(rest), listitem, *data):
                                    yield part
                        except TypeError:
                            #print '    its a bool!'
                            for part in self._parse(untilclose, *data):
                                yield part
                else:
                    for ignore in untilclose:
                        pass
            elif tag == TOKEN_BOOL:
                tagvalue = _lookup(data, content)
                untilclose = itertools.takewhile(lambda x: x != (TOKEN_TAGCLOSE, content, scope), tokens)
                if tagvalue:
                    for part in self._parse(untilclose, *data):
                        yield part
                else:
                    for part in untilclose:
                        pass
            elif tag == TOKEN_PARTIAL:
                if content in self.templates:
                    for part in self._parse(iter(list(self.templates[content])), *data):
                        yield part
            elif tag == TOKEN_PUSH:
                untilclose = itertools.takewhile(lambda x: x != (TOKEN_TAGCLOSE, content, scope), tokens)
                data[-1][content] = ''.join(self._parse(untilclose, *data))
            elif tag == TOKEN_TAGDELIM:
                self.otag, self.ctag = content

    def _jsparse(self, tokens):
        self.otag = '{{'
        self.ctag = '}}'
        for token in tokens:
            tag, content, scope = token
            if tag == TOKEN_RAW:
                yield "'{0}'".format(str(content))
            elif tag == TOKEN_TAG:
                if content != '':
                    if scope:
                        yield "lookup(data, '{0}')".format(content)
                    else:
                        yield "htmlEncode(lookup(data, '{0}'))".format(content)
            elif tag == TOKEN_TAGOPEN or tag == TOKEN_TAGINVERT or tag == TOKEN_BOOL:
                untilclose = itertools.takewhile(lambda x: x != (TOKEN_TAGCLOSE, content, scope), tokens)
                inside = self._jsparse(untilclose)
                if tag == TOKEN_TAGOPEN:
                    pre = "return section(data, lookup(data, tag), function (data) {"
                    post = "});"
                    self.hoist["__section{0}".format(len(self.hoist))] = _renderjsfunction(inside, pre, post)
                    yield "__section{1}(data, '{0}')".format(content, len(self.hoist)-1)
                elif tag == TOKEN_TAGINVERT:
                    pre = "return section(data, lookup(data, tag), function (data) {"
                    post = "}, true);"
                    self.hoist["__section{0}".format(len(self.hoist))] = _renderjsfunction(inside, pre, post)
                    yield "__section{1}(data, '{0}')".format(content, len(self.hoist)-1)
                elif tag == TOKEN_BOOL:
                    pre = "var tagvalue = lookup(data, tag); if ((!isArray(tagvalue) && tagvalue) || (isArray(tagvalue)) && tagvalue.length > 0){"
                    post = "}"
                    self.hoist["__section{0}".format(len(self.hoist))] = _renderjsfunction(inside, pre, post)
                    yield "__section{1}(data, '{0}')".format(content, len(self.hoist)-1)
            elif tag == TOKEN_PARTIAL:
                yield "templates['{0}'](data)".format(content)
            elif tag == TOKEN_PUSH:
                untilclose = itertools.takewhile(lambda x: x != (TOKEN_TAGCLOSE, content, scope), tokens)
                self.hoist_data[content] = _renderjsfunction(self._jsparse(untilclose), params="data")
            elif tag == TOKEN_TAGDELIM:
                self.otag, self.ctag = content


