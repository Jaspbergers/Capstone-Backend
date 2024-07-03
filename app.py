from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
# import os

app = Flask(__name__)
CORS(app)

# basedir = os.path.abspath(os.path.dirname(__file__))
# app.config['SQLALCHEMY_DATABASE_URI'] ='sqlite:///' + os.path.join(basedir, "app.sqlite")
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://backend_alxy_user:SBVs8J1G1bLAhVe1abMf1bUZFQE7rSuY@dpg-cq2rvqcs1f4s73f4ofu0-a.oregon-postgres.render.com/backend_alxy'

db= SQLAlchemy(app)
ma = Marshmallow(app)

class Blogpost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    category = db.Column(db.String(100))
    content = db.Column(db.String, nullable=False)
    author = db.Column(db.String)
    published = db.Column(db.String)

    def __init__(self, title, category, content, author, published):
        self.title = title
        self.category = category
        self.content = content
        self.author = author
        self.published = published

class BlogpostSchema(ma.Schema):
    class Meta:
        fields = ('id','title', 'category', 'content', 'author', 'published')


blogpost_schema = BlogpostSchema()
blogposts_schema = BlogpostSchema(many=True)


# **** Endpoint to create a new blog post **** #
@app.route('/blogpost/add_new', methods=["POST"])
def add_blogpost():
    if request.content_type != 'application/json':
        return jsonify('Error: Data must be sent as JSON')
    
    post_data = request.get_json()
    title = post_data.get('title')
    category = post_data.get('category')
    content = post_data.get('content')
    author = post_data.get('author')
    published = post_data.get('published')

    if title == None:
        return jsonify("Error: You must provide a title for your post.")
    if content == None:
        return jsonify("Error: You must provide content to post.")
    if author == None:
        return jsonify("Error: You must provide an author name to post.")

    new_blogpost = Blogpost(title, category, content, author, published)
    db.session.add(new_blogpost)
    db.session.commit()

    return jsonify(blogpost_schema.dump(new_blogpost))

# **** Endpoint to query all blog posts **** #
@app.route("/blogposts", methods=["GET"])
def get_blogposts():
    all_blogposts = db.session.query(Blogpost).all()
    return jsonify(blogposts_schema.dump(all_blogposts))

# **** Endpoint for querying a single blogpost **** #
@app.route("/blogpost/<id>", methods=["GET"])
def get_blogpost(id):
    get_blogpost = db.session.query(Blogpost).filter(Blogpost.id == id).first()
    return jsonify(blogpost_schema.dump(get_blogpost))

# **** Endpoint for editing a blog post **** #
@app.route("/blogpost/<id>", methods=["PUT"])
def edit_blogpost(id):
    if request.content_type != 'application/json':
        return jsonify("Error: Data must be sent as JSON!")
    
    put_data = request.get_json()
    title = put_data.get('title')
    category = put_data.get('category')
    content = put_data.get('content')
    author = put_data.get('author')
    published = put_data.get('published')

    edit_blogpost = db.session.query(Blogpost).filter(Blogpost.id == id).first()

    if title != None:
        edit_blogpost.title = title
    if category != None:
        edit_blogpost.category = category
    if content != None:
        edit_blogpost.content = content
    if author != None:
        edit_blogpost.author = author
    if published != None:
        edit_blogpost.published = published

    db.session.commit()
    return jsonify(blogpost_schema.dump(edit_blogpost))

# **** Endpoint for deleting a blog post **** #
@app.route('/blogpost/delete/<id>', methods=["DELETE"])
def delete_blogpost(id):
    delete_blogpost = db.session.query(Blogpost).filter(Blogpost.id == id).first()
    db.session.delete(delete_blogpost)
    db.session.commit()
    return jsonify("Blog post has been deleted.", blogpost_schema.dump(delete_blogpost))


# **** Endpoint for adding multiple blog posts **** #
@app.route('/blogpost/add/multi', methods=["POST"])
def add_multi_blogposts():
    if request.content_type != "application/json":
        return jsonify("Error: Your Data must be sent as JSON")
    
    post_data = request.get_json()
    blogposts = post_data.get('blogposts')

    new_blogposts = []

    for blogpost in blogposts:
        title = blogpost.get('title')
        category = blogpost.get('category')
        content = blogpost.get('content')
        author = blogpost.get('author')
        published = blogpost.get('published')

        existing_blogpost_check = db.session.query(Blogpost).filter(Blogpost.title == title).first()
        if existing_blogpost_check is None:
            new_post = Blogpost(title, category, content, author, published)
            db.session.add(new_post)
            db.session.commit()
            new_blogposts.append(blogpost_schema.dump(new_post))

    return jsonify(blogposts_schema.dump(new_blogposts))

if __name__ == '__main__':
    app.run()