from . import app, middleware
from flask import request, render_template


@app.route('/')
@app.route('/index')
def index():
    return render_template("search.html")


@app.route('/results', methods=["POST", "GET"])
def results():
    result_list = ["No results found - you shouldn't be here"]
    if request.method == "POST":
        result_list = middleware.search(request.form["search"])
    elif request.method == "GET":
        result_list = middleware.search(request.args.get("search"))
    return render_template("results.html", results=result_list)


@app.route('/enrichment', methods=["GET"])
def enrichment():
    genes = request.args.get("genes")
    return render_template("enrichment.html", genes=genes)
