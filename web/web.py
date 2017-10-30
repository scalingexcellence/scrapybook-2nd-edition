#!/usr/bin/env python

import json
import os
import random
import re


from zope.interface import Interface, Attribute
from zope.interface.declarations import implementer
from twisted.python.components import registerAdapter
from twisted.internet.task import deferLater
from twisted.web.resource import Resource
from twisted.web.util import redirectTo
from twisted.web.server import Session
from twisted.internet import reactor, endpoints
from twisted.web.static import File
from twisted.web import server

from model import Model
from view import View


class SettingsFromUrl(object):

    url_to_settings = {
        # Website structure
        "ti": "SPEED_TOTAL_ITEMS",
        "dp": "SPEED_DETAILS_PER_INDEX_PAGE",
        "id": "SPEED_ITEMS_PER_DETAIL",
        "ds": "SPEED_DETAIL_EXTRA_SIZE",
        "ip": "SPEED_INDEX_POINTAHEAD",
        # Response times
        "rr": "SPEED_T_RESPONSE",
        "ar": "SPEED_API_T_RESPONSE",
        "dr": "SPEED_DETAIL_T_RESPONSE",
        "ir": "SPEED_INDEX_T_RESPONSE",
    }

    def __init__(self, request):
        parts = request.URLPath().pathList(unquote=True)
        k_v_pairs = map(lambda i: i.decode().split(":"), parts)
        vars = filter(lambda i: len(i) == 2, k_v_pairs)
        mapped = SettingsFromUrl.url_to_settings
        self._settings = {}
        for key, value in vars:
            if key in mapped:
                self._settings[mapped[key]] = value

    def getfloat(self, key, default):
        return float(self._settings.get(key, default))

    def getint(self, key, default):
        return int(self._settings.get(key, default))


class BaseResource(Resource):
    isLeaf = True

    def render_GET(self, request):
        settings = SettingsFromUrl(request)

        gen_delay = settings.getfloat('SPEED_T_RESPONSE', self.default_delay)
        delay = settings.getfloat(self.class_delay_setting, gen_delay)

        # https://twistedmatrix.com/documents/13.0.0/web/howto/
        #web-in-60/asynchronous-deferred.html
        d = deferLater(reactor, delay, lambda: request)
        d.addCallback(self._delayedRender, settings)
        return server.NOT_DONE_YET

    render_POST = render_GET


def get_if(request, k, default, cls):
    try:
        return cls(request.args[k.encode('utf-8')][0].decode())
    except:
        return default


class Api(BaseResource):

    class_delay_setting = 'SPEED_API_T_RESPONSE'
    default_delay = 3

    def _delayedRender(self, request, settings):
        text = get_if(request, 'text', '', str)
        json = json.dumps({"translation": "api-t-{}".format("".join(text))})
        request.write(json.encode('utf-8'))
        request.finish()


class Index(BaseResource):

    class_delay_setting = 'SPEED_INDEX_T_RESPONSE'
    default_delay = 0.5

    def _delayedRender(self, request, settings):
        details_per_index = settings.getint(
            'SPEED_DETAILS_PER_INDEX_PAGE', 20)
        items_per_page = settings.getint('SPEED_ITEMS_PER_DETAIL', 1)
        limit = settings.getint('SPEED_TOTAL_ITEMS', 1000)
        index_lookahead = settings.getint('SPEED_INDEX_POINTAHEAD', 1)

        p = get_if(request, 'p', 1, int)

        page_worth = details_per_index * items_per_page
        # ...divide with roundup
        max_pages = (limit + page_worth - 1) / page_worth

        if p >= 1 and p <= max_pages:
            base = (p-1) * details_per_index
            request.write(b'<ul>')
            for i in range(details_per_index):
                id = ((base+i)*items_per_page)+1
                if id <= limit:
                    ids = [id, min(id + items_per_page - 1, limit)]
                    irange = sorted(list(set(ids)))
                    srange = "-".join([str(i) for i in irange])
                    request.write(('<li><a class="item" href="detail'
                                  '?id0=%d">item %s</a></li>' % (id, srange))
                                  .encode('utf-8'))

            request.write(b'</ul>')

            for i in range(index_lookahead):
                if (p+i) < max_pages:
                    request.write(b'<a class="nav" href="index?p=%d">next</a> '
                                  % (p+i+1))

        request.finish()


class Detail(BaseResource):

    class_delay_setting = 'SPEED_DETAIL_T_RESPONSE'
    default_delay = 1

    def _delayedRender(self, request, settings):
        items_per_page = settings.getint('SPEED_ITEMS_PER_DETAIL', 1)
        limit = settings.getint('SPEED_TOTAL_ITEMS', 1000)
        garbage_size = settings.getint('SPEED_DETAIL_EXTRA_SIZE', 0)

        id0 = get_if(request, 'id0', 1, int)
        request.write(b'<ul>')
        for idx in range(id0, min(id0+items_per_page, limit+1)):
            request.write(b'<li>')
            request.write(b'<h3>I\'m %d</h3>' % idx)
            request.write(b'<div class="info">useful info for id: %d</div>'
                          % idx)
            request.write(b'</li>')
        request.write(b'</ul>')
        request.write(b'<!--')
        request.write(b'i' * garbage_size)
        request.write(b'-->')
        request.finish()


class Benchmark(Resource):
    isLeaf = True
    def render_GET(self, request):
        return ('Benchmark section. Browse: '
                '<a href="index">index</a> '
                '<a href="detail">detail</a>, '
                '<a href="api?text=hi">api</a>').encode('utf-8')


class ILoginGate(Interface):
    nonce = Attribute("random nonce")
    logged_in = Attribute("true if successfully logged in")


@implementer(ILoginGate)
class LoginGate(object):

    def __init__(self, session):
        self.nonce = str(random.random())
        self.logged_in = False


registerAdapter(LoginGate, Session, ILoginGate)


class Dynamic(Resource):

    def __init__(self):
        Resource.__init__(self)

    def getChild(self, name, request):
        return self

    def render_GET(self, request):
        session = request.getSession()
        tsession = ILoginGate(session)

        try:
            if request.path == b"/dynamic":
                return View.render_form()
            elif request.path == b"/dynamic/nonce":
                return View.render_form(tsession.nonce)
            elif request.path == b"/dynamic/gated":
                if not tsession.logged_in:
                    return redirectTo(b"/dynamic/error", request)

                return View.render_gated()
        except:
            pass

        session.expire()
        return View.render_error()

    def render_POST(self, request):
        session = request.getSession()
        tsession = ILoginGate(session)
        location = b"/dynamic/error"

        try:
            if request.path not in [b"/dynamic/nonce-login", b"/dynamic/login"]:
                raise Exception(b'unsupported login type')

            if request.path == b"/dynamic/nonce-login":
                nonce = request.args.get(b'nonce', [''])[0].decode()
                if tsession.nonce != nonce:
                    session.expire()
                    raise Exception(b'invalid nonce')

            if (request.args.get(b'user', [''])[0] != b'user' or
                    request.args.get(b'pass', [''])[0] != b'pass'):
                if session:
                    session.expire()
                raise Exception('invalid user/pass')

            tsession.logged_in = True
            location = b"/dynamic/gated"

        except:
            pass

        return redirectTo(location, request)


class Maps(BaseResource):
    class_delay_setting = 'SPEED_MAPS_T_RESPONSE'
    default_delay = 0.25

    def __init__(self, model):
        # 250 ms default delay
        BaseResource.__init__(self)

        self.model = model

    def _delayedRender(self, request, settings):
        try:
            address = get_if(request, 'address', '', str)

            location = self.model.get_location(address)

            request.setHeader("content-type", "application/json")
            request.write(View.render_maps(location))

        except:
            request.write('can\'t find page. sorry')

        request.finish()


class Properties(BaseResource):

    class_delay_setting = 'SPEED_PROPERTIES_T_RESPONSE'
    default_delay = 0.25

    def __init__(self, model):
        # 250 ms default delay
        BaseResource.__init__(self)

        self.model = model
        self.properties = 50000
        self.per_index = 30

    def _delayedRender(self, request, settings):
        try:
            path = request.path.decode()
            properties, per_index = self.properties, self.per_index
            if path == '/properties/api.json':
                items = []
                for i in range(30):
                    item = self.model.get_item(i)
                    items.append({'id': i, "title": "better " + item['title']})

                request.setHeader("content-type", "application/json")
                request.write(json.dumps(items).encode('utf-8'))

            elif path.startswith("/properties/index_"):

                m = re.search(r'.*_(\d+)', path)
                if not m:
                    raise Exception(b'expected number')

                page = int(m.group(1))

                # Divide with roundup
                indices = (properties + per_index - 1) // per_index
                if page >= indices:
                    raise Exception(b'invalid index number')

                np = 'index_%05d.html' % (page + 1)

                start = per_index * page
                end = min(per_index * (page + 1), properties)

                index = {
                    'page': page,
                    'nextp': None if page >= (indices-1) else np,
                    'items': self.model.get_items(range(start, end))
                }

                request.write(View.render_index(index))

            elif path.startswith('/properties/property_'):
                m = re.search(r'.*_(\d+)', path)
                if not m:
                    raise Exception(b'expected number')

                pid = int(m.group(1))

                if pid >= properties:
                    raise Exception(b'invalid property number')

                item = self.model.get_item(pid)

                request.write(View.render_property(item))
            else:
                raise Exception(b'unknown page')

        except:
            request.write(b'can\'t find page. sorry')

        request.finish()


class Home(Resource):
    isLeaf = True

    def render_GET(self, request):
        r = ('Welcome to Scrapy Book. Try: '
                '<a href="properties/index_00000.html">properties</a> '
                '<a href="images">images</a>, '
                '<a href="dynamic">dynamic</a>, '
                '<a href="benchmark/">benchmark</a> '
                '<a href="maps/api/geocode/json?sensor=false&address=Camden%20Town%2C%20London">maps</a>')
        return r.encode('utf-8')

if __name__ == '__main__':

    path = os.path.dirname(os.path.abspath(__file__))

    os.chdir(path)
    
    root = Resource()

    root.model = Model()
    root.putChild(b'', Home())
    benchmark = Resource()
    root.putChild(b'benchmark', benchmark)
    benchmark.putChild(b'', Benchmark())
    benchmark.putChild(b'api', Api())
    benchmark.putChild(b'index', Index())
    benchmark.putChild(b'detail', Detail())
    root.putChild(b'properties', Properties(root.model))
    root.putChild(b'maps', Maps(root.model))
    root.putChild(b'images', File('images'))
    root.putChild(b'static', File('static'))
    root.putChild(b'dynamic', Dynamic())

    factory = server.Site(root)

    endpoint = endpoints.TCP4ServerEndpoint(reactor, 9312)
    endpoint.listen(factory)

    reactor.run()
