from . import pathwaycommons_helper
import sys

name = sys.argv[1]
pathways_dict = pathwaycommons_helper.pathway_given_pathway(name)

print("Pathways that use the " + name + " pathway: \n")
for pathway in pathways_dict.items():
    print(pathway[0])
    print()
    for desc in pathway[1]:
        print(desc)
    print()
