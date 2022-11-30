import pymongo
import numpy as np
import pandas as pd
import sys

"""
    Pull Data from CiViC and ClinVar files and push to MongoDB Collection.
"""


def replace_string(x):
    if isinstance(x, str):
        try:
            return [int(i) for i in x.split(",")]
        except ValueError:
            return None
    return None


def main():
    database_url = sys.argv[1]

    variant_summaries_file = open("clinvar_variant_summary.txt", "r")
    variant_summaries_lines = variant_summaries_file.readlines()
    edited_header = variant_summaries_lines[0][1:]
    variant_summaries_file.close()
    variant_summaries_file = open("clinvar_variant_summary.txt", "w")
    variant_summaries_file.write(edited_header)
    for line in variant_summaries_lines[1:]:
        variant_summaries_file.write(line)

    variant_summaries_file.close()

    variant_summaries = pd.read_csv("clinvar_variant_summary.txt", sep="\t")
    variant_summaries = variant_summaries.filter(
        ["AlleleID", "RS# (dbSNP)", "Type", "ClinicalSignificance", "ReviewStatus"]
    )

    variation_allele_file = open("clinvar_variation_allele.txt", "r")
    variation_allele_lines = variation_allele_file.readlines()

    number_comments = 0
    while variation_allele_lines[number_comments].startswith("#"):
        number_comments += 1

    edited_header = variation_allele_lines[number_comments - 1][1:]

    variation_allele_file.close()
    variation_allele_file = open("clinvar_variation_allele.txt", "w")
    variation_allele_file.write(edited_header)
    for line in variation_allele_lines[number_comments:]:
        variation_allele_file.write(line)

    variation_allele_file.close()

    variation_allele = pd.read_csv("clinvar_variation_allele.txt", sep="\t")
    for col in variation_allele.columns:
        print(col)
    variation_allele.drop(columns=["Type", "Interpreted"], inplace=True)

    variant_summaries = variant_summaries.merge(
        variation_allele, how="inner", on="AlleleID"
    )
    variant_summaries = variant_summaries.rename(columns={"VariationID": "clinvar_ids"})

    civic_variant_summaries = pd.read_csv(
        "civic_variant_summary.tsv",
        sep="\t",
        error_bad_lines=False,
        warn_bad_lines=True,
    )
    civic_variant_summaries.filter(
        [
            "variants",
            "variant_id",
            "gene",
            "variant",
            "summary",
            "variant_groups",
            "civic_variant_evidence_score",
            "clinvar_ids",
        ]
    )
    civic_variant_summaries["clinvar_ids"] = civic_variant_summaries[
        "clinvar_ids"
    ].apply(replace_string)

    civic_variant_summaries = civic_variant_summaries.explode("clinvar_ids")

    variant_summaries = civic_variant_summaries.merge(
        variant_summaries, how="inner", on="clinvar_ids"
    )

    evidence_summaries = pd.read_csv(
        "clinvar_evidence_summary.tsv",
        sep="\t",
        error_bad_lines=False,
        warn_bad_lines=True,
    )

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


if __name__ == "__main__":
    main()
