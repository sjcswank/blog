import os
import jinja2
import webapp2

import re
import cgi

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                               autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Entries(db.Model):
    title = db.StringProperty(required = True)
    entry = db.TextProperty(required = True)
    created = db.DateProperty(auto_now_add = True)

class MainHandler(Handler):
    def render_front(self, title="", entry="", error=""):
        entries = db.GqlQuery("SELECT * FROM Entries "
                           "ORDER BY created DESC ")
        self.render("front.html", title=title, entry=entry, error=error, entries=entries)

    def get(self):
        self.render_front()

class CreateHandler(Handler):
    def get(self):
        self.render("create.html")

    def post(self):
        title= self.request.get("title")
        entry = self.request.get("entry")

        if title and entry:
            e = Entries(title = title, entry = entry)
            e.put()
            id = e.key().id()
            self.redirect('/blog/' + str(id))

        else:
            error = "We need both a title and entry!"
            self.render("create.html", title=title, entry=entry, error=error)

class ViewPostHandler(Handler):
    def get(self, id):
        #self.response.write(id)
        entries = Entries.get_by_id(int(id))
        if entries:
            self.render("viewpost.html", title=entries.title, created=entries.created, entry=entries.entry)
        else:
            error = "<h2>This is not the entry you are looking for.</h2>"
            self.render('front.html', error=error)



app = webapp2.WSGIApplication([
    ('/blog', MainHandler),
    ('/create', CreateHandler),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
