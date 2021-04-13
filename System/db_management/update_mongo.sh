#!/bin/bash
rm *.txt
rm *.tsv
rm *.gz
curl https://ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited/variant_summary.txt.gz --output clinvar_variant_summary.txt.gz
gunzip clinvar_variant_summary.txt.gz
curl https://ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited/variation_allele.txt.gz --output clinvar_variation_allele.txt.gz
gunzip clinvar_variation_allele.txt.gz
curl https://civicdb.org/downloads/nightly/nightly-VariantSummaries.tsv --output civic_variant_summary.tsv
curl https://civicdb.org/downloads/nightly/nightly-ClinicalEvidenceSummaries.tsv --output clinvar_evidence_summary.tsv
python3 update_dbs.py mongodb://127.0.0.1:27017
python3 kegg_parser.py mongodb://127.0.0.1:27017