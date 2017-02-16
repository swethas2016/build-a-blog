#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import os
import jinja2
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)
class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Blog(db.Model):
    title = db.StringProperty(required = True)
    blog_content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class MainPage(Handler):
    def get(self, title = "", blog_content = ""):
        blogs = db.GqlQuery("SELECT * FROM Blog "
                            " ORDER BY created DESC LIMIT 5 ")

        self.render("frontpage.html", title = title, blog_content = blog_content, blogs = blogs)

class NewPost(Handler):
    def render_front(self, title = "", blog_content = "", error = ""):
        blogs = db.GqlQuery("SELECT * FROM Blog "
                            " ORDER BY created DESC LIMIT 5 ")

        self.render("newpost1.html", title = title, blog_content = blog_content, error = error, blogs = blogs)

    def get(self):
        self.render_front()
    def post(self):
        title = self.request.get("title")
        blog_content = self.request.get("blog_content")

        if title and blog_content:
            b = Blog(title = title, blog_content = blog_content)
            b.put()
            self.redirect("/blog/%s" %str(b.key().id()))
        else:
            error = "we need both a title and some content!"
            self.render_front(title, blog_content, error)
# class BlogPage(Handler):
#     def post(self):
#         self.render("blog_page.html")
class ViewPostHandler(webapp2.RequestHandler):
    def get(self, id):
        if Blog.get_by_id(int(id)) == None:
            error = "Oops! There is no post available for this id"
            self.response.write(error)
        else:
            blog_id = Blog.get_by_id(int(id))
            self.response.write(blog_id.title)
            self.response.write("<div>")
            self.response.write(blog_id.blog_content)

    # def post(self):
    #     blog_id = self.request.get("id")
    #     blog_list = Blog.get_by_id( int(blog_id) )

        # if not blog_list:
        #     self.renderError(400)
        #     return

        # update the movie's ".watched" property to True
        #watched_movie.watched = True
        # blog_list.put()

        # render confirmation page
        # t = jinja_env.get_template("blog_page.html")
        # content = t.render(id = title)
        # self.response.write(content)

app = webapp2.WSGIApplication([(webapp2.Route('/blog/<id:\d+>', ViewPostHandler)),
    ('/', MainPage),('/newpost', NewPost)
], debug=True)
