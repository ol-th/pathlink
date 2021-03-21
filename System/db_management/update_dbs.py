import pymongo
import numpy as np
import pandas as pd
import sys


def replace_string(x):
    if isinstance(x, str):
        try:
            return [int(i) for i in x.split(",")]
        except ValueError:
            return float("NaN")
    return None


database_url = sys.argv[1]

variant_summaries = pd.read_csv("variant_summary.txt", sep="\t")
variant_summaries = variant_summaries.filter(["AlleleID", "RS# (dbSNP)", "Type", "ClinicalSignificance", "ReviewStatus"])
variation_allele = pd.read_csv("variation_allele.txt", sep="\t")
variation_allele.drop(columns=['Type', 'Interpreted'], inplace=True)

variant_summaries = variant_summaries.merge(variation_allele, how="inner", on="AlleleID")
variant_summaries = variant_summaries.rename(columns={"VariationID": "clinvar_ids"})

civic_variant_summaries = pd.read_csv("nightly-VariantSummaries.tsv", sep="\t", error_bad_lines=False, warn_bad_lines=True)
civic_variant_summaries.filter(["variants", "variant_id", "gene", "variant", "summary",
                                "variant_groups", "civic_variant_evidence_score", "clinvar_ids"])
civic_variant_summaries["clinvar_ids"] = civic_variant_summaries["clinvar_ids"].apply(replace_string)

civic_variant_summaries = civic_variant_summaries.explode("clinvar_ids")

variant_summaries = civic_variant_summaries.merge(variant_summaries, how="inner", on="clinvar_ids")

evidence_summaries = pd.read_csv("nightly-ClinicalEvidenceSummaries.tsv", sep="\t", error_bad_lines=False, warn_bad_lines=True)

client = pymongo.MongoClient(database_url)
db = client["variants"]
variant_summaries_collection = db["variant_summaries"]
evidence_summaries_collection = db["evidence_summaries"]

if "variant_summaries" in db.list_collection_names():
    print("Dropping variant_summaries collection...")
    variant_summaries_collection.drop()
if "evidence_summaries" in db.list_collection_names():
    print("Dropping evidence_summaries collection...")
    evidence_summaries_collection.drop()

print("Populating variant_summaries collection...")
variant_summaries.reset_index(inplace=True)
variant_summaries_collection.insert_many(variant_summaries.to_dict("records"))
print("Populating evidence_summaries collection...")
evidence_summaries.reset_index(inplace=True)
evidence_summaries_collection.insert_many(evidence_summaries.to_dict("records"))
