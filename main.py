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
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)

    def render(self):
        self._render_text = self.entry.replace('\n', '<br>')
        return render_str("create.html", e = self)


class MainHandler(Handler):
    def get(self):
        posts = db.GqlQuery("SELECT * FROM Entries ORDER BY created DESC")
        self.render("base.html", posts=posts)

class CreatePost(Handler):
    def get(self):
        # get error
        title = ""
        entry = ""
        error = self.request.get("error")
        #render page with error_element
        self.render("create.html", title=title, entry=entry, error=error)

    def post(self):
        title= self.request.get("title")
        entry = self.request.get("entry")

        if title and entry:
            e = Entries(title = title, entry = entry)
            e.put()

            self.redirect('/blog')

        else:
            error = "We need both a title and entry!"
            self.redirect('/create')



app = webapp2.WSGIApplication([
    ('/blog', MainHandler),
    ('/create', CreatePost)
], debug=True)
