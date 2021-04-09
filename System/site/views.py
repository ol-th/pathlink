from . import app, middleware, api
from bson import json_util
from flask import request, render_template, jsonify


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


# --------------------------------------------- API
@app.route('/api/pathway', methods=["GET"])
def pathway_api():
    identifier = request.args.get("id")
    options = request.args.get("options")
    return jsonify(api.get_pathway(identifier, options=options))


@app.route('/api/gene', methods=["GET"])
def gene_api():
    name = request.args.get("name")
    options = request.args.get("options")
    return jsonify(api.get_gene(name=name, options=options))


@app.route('/api/variant', methods=["GET"])
def variant_api():
    gene_name = request.args.get("gene_name")
    variant_name = request.args.get("variant")
    if all(v is not None for v in [gene_name, variant_name]):
        result = api.gene_variant_data(gene_name, variant_name)
        result_list = list(result)
        output = {"results": json_util.dumps(result_list)}
        return jsonify(api.gene_variant_data(gene_name, variant_name))
    return ""


@app.route('/api/pathway_gene_interaction', methods=["GET"])
def pathway_gene_interaction_api():
    pathway_name = request.args.get("pathway_name")
    pathway_kegg_id = request.args.get("pathway_kegg_id")
    gene_name = request.args.get("gene_name")
    gene_kegg = request.args.get("gene_kegg")
    gene_uniprot = request.args.get("gene_uniprot")
    return jsonify(api.pathway_gene_interaction(pathway_name, pathway_kegg_id=pathway_kegg_id, gene_name=gene_name,
                                                gene_kegg=gene_kegg, gene_uniprot=gene_uniprot))


@app.route('/api/variant_evidence', methods=["GET"])
def variant_evidence_api():
    gene_name = request.args.get("gene_name")
    variant_name = request.args.get("variant")
    if all(v is not None for v in [gene_name, variant_name]):
        return jsonify(api.variant_evidence(gene_name, variant_name))
    return ""


@app.route('/api/functional_enrichment', methods=["GET"])
def functional_enrichment_api():
    gene_list = request.args.get("genes").split("+")
    direct, indirect = api.functional_enrichment(gene_list)
    return jsonify({
        "direct": direct,
        "indirect": indirect
    })


@app.route('/api/pathway_to_cypher', methods=["GET"])
def pathway_to_cypher_api():
    pathway_id = request.args.get("id")
    options = request.args.get("options")
    return jsonify(api.neo4j_pathway(pathway_id, options=options))
