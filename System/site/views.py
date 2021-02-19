from . import app, middleware
import flask


@app.route('/')
@app.route('/index')
def index():
    return flask.render_template("search.html")


@app.route('/results', methods=["POST"])
def results():
    result_list = middleware.search(flask.request.form['search'])
    return flask.render_template("results.html", results=result_list)
