#!/usr/bin/env python3
from tornado.httpclient import AsyncHTTPClient
import markdown
import sys
import tornado.ioloop
import tornado.web


URL = "https://raw.githubusercontent.com/%s/%s.md"


def get_md_async(target, path, callback):
    http_client = AsyncHTTPClient()
    http_client.fetch(URL % (target, path), callback)


def convert_to_html(md):
    return markdown.markdown(md, extensions=['attr_list'])


class MarkdownHandler(tornado.web.RequestHandler):
    def initialize(self, target):
        self.target = target

    @tornado.web.asynchronous
    def get(self, path):
        get_md_async(self.target, path, self._on_download)

    def _on_download(self, response):
        self.write(response.body.decode("utf-8"))
        self.set_header('Content-Type', 'text/plain; charset="utf-8"')
        self.finish()


class HTMLHandler(tornado.web.RequestHandler):
    def initialize(self, target):
        self.target = target

    @tornado.web.asynchronous
    def get(self, path):
        get_md_async(self.target, path, self._on_download)

    def _on_download(self, response):
        self.write(convert_to_html(response.body.decode("utf-8")))
        self.finish()


if __name__ == '__main__':
    assert (len(sys.argv) == 2)
    args = dict(target=sys.argv[1])
    Application = tornado.web.Application
    application = Application([(r"/(.*)\.html", HTMLHandler, args),
                               (r"/(.*)\.md", MarkdownHandler, args)])
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
