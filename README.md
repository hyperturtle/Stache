[![Build Status](https://secure.travis-ci.org/hyperturtle/Stache.png)](http://travis-ci.org/hyperturtle/Stache)

# Stache

Trimmed mustache logic-less templates

Fork of https://github.com/hyperturtle/Stache with:

  * support for Cpython 2.2 up to and including Python 3.x
  * Also works with Jython 2.x.
  * Fix for trailing blank newlines (https://github.com/hyperturtle/Stache/issues/2)
  * regular Python unittest based test suite

Also see https://github.com/SmithSamuelM/staching which includes a fix for https://github.com/hyperturtle/Stache/issues/2 but doesn't support older Python versions, use if older Python support is not required.

Implements everything from [Mustache.5](http://mustache.github.com/mustache.5.html)
**except for lambdas** in < 200 lines of code. Plus four new things. Implied closing tags
`{{/}}`, Self referencer `{{.}}`, Existence check `{{?exists}}{{/exists}}` and data pusher 
`{{< blah}}{{/blah}}`, `{{:default}}`


# Also, the ability to compile to javascript code!

## render_js(template_string)

Compiles an inline script to javascript code

## Stache().render_js_template(template_name)

Compiles all the templates and sets the entry point to the template name

## render_all_js()

Compiles all the templates and returns a template object.

```python
stachio = Stache()
stachio.add_template('template_name', templatefile.read())
write('var t = ' + stachio.render_all_js() ';')
```

```javascript
var content = t['template_name']([{myparams:3}])
$("#container").html(content)
```

# Why?

Because the current [Pystache](https://github.com/defunkt/pystache) implementation
has holes. And because I wanted to learn about python generators. As a result
my codebase is considerabley smaller and easier to grok too(at least for me). It consists
of two main methods, `_tokenize`, and `_parse`, both python generators. `_tokenize` creates
tokens and `_parse` consumes and renders them. Also benchmarking the two with my tests,
mine was slightly faster, around 2x to 3x.

# Existing Stuff

## {{tag}}

Renders the value of tag, html escaped, within the current scope

## {{{unescape}}} & {{&unescape}}

Don't html escape the value

## {{#section}}{{/section}}

Section blocks. Renders the enclosed block if

- `section` is true
- `section` exists

If `section` exists and is a(n):

- Array: It renders the enclosed block for each element in the array, placing the
current element in scope
- Dict: It renders the enclosed block once and places the Dict as the current scope

## {{^invert}}{{/invert}}

Renders the enclosed block if `invert` is an empty string, empty array, false,
or doesn't exist. The opposite the the section block.

## {{! comments - ignore me }}

Ignores the text within the tag

## {{>partial}}

Looks up the `partial` template and renders it with the current context

# New Stuff

## {{/}} Implied closing tag

Whenever you use {{/}} it implies the closing of the nearest block.

    {{#open}}stuff goes here{{/}}

Is the same as:

    {{#open}}stuff goes here{{/open}}

## {{.}} Self Referencer

This renders the current "scope". This is useful if you want to iterate over an array
and wrap them.

    {{#array}}<li>{{.}}</li>\n{{/array}}

with `array = [1,2,3,'yay']` will produce:

```html
<li>1</li>
<li>2</li>
<li>3</li>
<li>yay</li>
````

## Existence Check {{?exists}}{{/}}

Forces a check of the tag name, rather than imply that it is a section block. This
is useful for check if an array has members rather than iterate over the members

    {{?array}}
    stuff\n
    {{/}}

with `{array: [1, 2, 3, 4]}` results in:

    stuff

as opposed to

    {{#array}}
    stuff\n
    {{/}}

which would render

    stuff
    stuff
    stuff
    stuff

## {{:default}}stuff{{/}}

This is equivalent to `{{default}}{{^default}}stuff{{/}}`

It renders the enclosed section if default doesn't exist, empty or false

## {{<thing}} Pusher {{/thing}}

It renders the inner block and adds it to the global scope.

    {{<thing}}
    It takes this. You can put anything in here.
    {{tags}}, {{#blocks}}{{/blocks}}, etc.
    {{/thing}}

and it populates the global scope with a key of `thing`. Watch out, it can override
existing vars. A convention such as

    {{<namespace.thing}}{{/namespace.thing}}

or similiar will help with collisions. This is helpful if you want to use stache
templates for masterpages/inheritance.
Lets say you have these templates:

#### master =

    <div id="header">
    {{header}}
    </div>

    <div id="footer">
    {{footer}}
    </div>

#### page = 

    {{<header}}
    {{name}}
    {{/header}}

    {{<footer}}
    footer
    {{/footer}}

    {{>master}}

Rendering the `page` template with `{'name': 'Stachio'}` will produce

```html
<div id="header">
Stachio
</div>

<div id="footer">
footer
</div>
```

You can also apply the inverted block or default block to supply default blocks

#### master =
    
    <div id="header">
    {{header}}
    {{^header}}Default Header{{/header}}
    </div>

    <div id="footer">
    {{:footer}}Default Footer{{/footer}}
    </div>

Rendering `{{<footer}}Custom Footer{{/footer}}{{>master}}` with `{}` will produce

```html
<div id="header">
Default Header
</div>

<div id="footer">
Custom Footer
</div>
```

# Install

    pip install stache

Optionally install Nose for running nosetests, there is a regular unittest that does not require nose).

    pip install nose

# Test

Pure python tests can be ran with:

    python testsuite.py

The Python and javascript tests can be ran with `python test.py` or if you have nosetests:

    cd stache
    nosetests

# Benchmark

    python test.py

# Usage:

    >>> from Stache import Stache
    >>> Stache().render("Hello {{who}}!", dict(who="World"))
    Hello World

or

    >>> import Stache
    >>> Stache.render("Hello {{world}}!", dict(world="Stache!"))
    Hello Stache!

## To populate partials:

    >>> from Stache import Stache
    >>> stachio = Stache()
    >>> stachio.add_template('main', 'a = {{a}};')
    >>> stachio.add_template('main1', 'b = [ {{#b}}{{.}} {{/b}}];')
    >>> stachio.add_template('main2', 'stachio')
    >>> stachio.add_template('woah', '{{>main}} {{>main1}} {{>main2}}')
    >>> stachio.render_template('woah',dict(a=1, b=[1,2,3,4,5]))
    a = 1; b = [ 1 2 3 4 5 ] stachio

If you want to put in dynamic file loading of partials you can override
`Stache().templates` with a `dict()` like object and override the `__get__` and
load the template in `__get__` if it doesn't exist. Once you load up the template,
you'll need to call `self.add_template(template_name, template)` to tokenize the
template.

I don't think this is ideal though... Ideas for populating partials are welcome.

## Efficient use with async wsgi:

For wsgi apps that support async, you can yield parts of the rendered template as
they render. `render_iter` and `render_template_iter` both produce iterators that
are yield'ed as it is generated.

    >>> for part in Stache.render_iter("Hello {{world}}!", dict(world="Stache!")):
    >>>     yield part
    Hello
    Stache!

# Timeline:

I'm wary of lambdas, because I want the templates to be language agnostic.
The main reason I liked Mustache in the first place is because of possibility of
template reuse.

Some future ideas I have is rendering to javascript templates to be used on browser
frontend, bypassing the need for a client side script to compile it into javascript
