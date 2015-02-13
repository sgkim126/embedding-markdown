#!/usr/bin/env python3
from tornado.httpclient import AsyncHTTPClient
import argparse
import markdown
import tornado.ioloop
import tornado.web


URL = "https://raw.githubusercontent.com/%s/%s.md"


def get_md_async(target, path, callback):
    http_client = AsyncHTTPClient()
    http_client.fetch(URL % (target, path), callback)


def convert_to_html(md):
    return markdown.markdown(md, extensions=['attr_list'])


def convert_to_javascript(md):
    document_format = "document.write('%s')"
    html = convert_to_html(md)
    return document_format % html.replace("'", "\\'").replace("\n", "\\n")


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


class JavascriptHandler(tornado.web.RequestHandler):
    def initialize(self, target):
        self.target = target

    @tornado.web.asynchronous
    def get(self, path):
        get_md_async(self.target, path, self._on_download)

    def _on_download(self, response):
        self.write(convert_to_javascript(response.body.decode("utf-8")))
        self.set_header('Content-Type',
                        'application/javascript; charset="utf-8"')
        self.finish()


if __name__ == '__main__':
    description = ("Parsing markdown from github"
                   "and making javascript for embedding.")
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--port', help='port number', default=8888, type=int,
                        dest='port')
    parser.add_argument('target')

    args = parser.parse_args()
    app_config = dict(target=args.target)
    Application = tornado.web.Application
    application = Application([(r"/(.*)\.html", HTMLHandler, app_config),
                               (r"/(.*)\.js", JavascriptHandler, app_config),
                               (r"/(.*)\.md", MarkdownHandler, app_config)])
    application.listen(args.port)
    tornado.ioloop.IOLoop.instance().start()
