import Bio.KEGG.REST as kegg


result = kegg.kegg_find('ORTHOLOGY', 'PTEN')
result = result.read().split('\n')
gene = kegg.kegg_get(result[0].split('\t')[0])
gene = gene.read().split('\n')
pathways = []
index = 0;
while not 'PATHWAY' in gene[index]:
    index += 1
while not 'DISEASE' in gene[index]:
    pathways.append(gene[index])
    index += 1

print("The PTEN gene is involved in these processes: ")
for i in pathways:
    print(i)
