
import webapp2, cgi, jinja2, os, re
from google.appengine.ext import db
from datetime import datetime

# set up jinja
template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class Add_Post(db.Model):
    #add db headers
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)

class Handler(webapp2.RequestHandler):
    # A base RequestHandler class for our app. The other handlers inherit form this one.
    def renderError(self, error_code):
        """ Sends an HTTP error code and a generic "oops!" message to the client. """
        self.error(error_code)
        self.response.write("Oops! Something went wrong.")

class MainPage(Handler):
    #main page to display 5 most recent posts at /blog
    def get(self, subject="", content="", error=""):

        New_Posts = db.GqlQuery("SELECT * FROM Add_Post ORDER BY created DESC limit 5")
        t = jinja_env.get_template("frontpage.html")
        response = t.render(
                        New_Posts = New_Posts,
                        error = self.request.get("error"))
        self.response.write(response)

class newpost(Handler):
    #page to add posts /blog/newpost
    def get(self):
        subject = self.request.get("subject")
        content = self.request.get("content")

        t = jinja_env.get_template("newpost.html")
        response = t.render(
                        subject = subject,
                        content = content,
                        error = self.request.get("error"))
        self.response.write(response)

    def post(self):
        #if correct display, otherwise render error
        subject = self.request.get("subject")
        content = self.request.get("content")

        t = jinja_env.get_template("newpost.html")

        if subject and content:
            p = Add_Post(subject = subject, content = content)
            p.put()
            self.redirect('/blog/%s' % str(p.key().id()))

        else:
            error = "We need both a Subject AND some Content"
            response = t.render(
                            subject = subject,
                            content = content,
                            error = error)
            self.response.write(response)

class ViewPostHandler(webapp2.RequestHandler):
    #get post by id
    def get(self, id, subject="", content=""):
        post = Add_Post.get_by_id(int(id))

        if not post:
            error = "<h1>That id does not appear to exist</h1>"
            self.response.write(error)
        else:
            t = jinja_env.get_template("permalink.html")
            response = t.render(post = post, subject=subject, content=content)

            self.response.write(response)

app = webapp2.WSGIApplication([
    ('/blog', MainPage),
    ('/blog/newpost', newpost),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler),


], debug=True)
