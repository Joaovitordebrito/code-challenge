import xml.etree.ElementTree as et
from neo4j import GraphDatabase
import logging
from neo4j.exceptions import ServiceUnavailable
import json

class App:

    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        # Don't forget to close the driver connection when you are finished with it
        self.driver.close()


    def create_protein_relation(
    self, 
    accessionValue, 
    varRecommendedFullName, 
    varRecommendedShortName, 
    varAlternativeFullName, 
    varAlternativeShortName,
    varGene,
    VarOrganismName,
    varOrganismDbReferenceType,
    varOrganismDbReferenceId,
    varReference,
    varReferenceType,
    varReferenceDate,
    varReferenceAuthors,
    varFeatureAttribs,
    varFeatureType):
        with self.driver.session(database="neo4j") as session:
            result = session.execute_write(
                self._create_and_return_friendship, 
                accessionValue, 
                varRecommendedFullName, 
                varRecommendedShortName, 
                varAlternativeFullName, 
                varAlternativeShortName,
                varGene,
                VarOrganismName,
                varOrganismDbReferenceType,
                varOrganismDbReferenceId,
                varReference,
                varReferenceType,
                varReferenceDate,
                varReferenceAuthors,
                varFeatureAttribs,
                varFeatureType)
            for row in result:
                print("Created")

    @staticmethod
    def _create_and_return_friendship(
    tx, 
    accessionValue, 
    varRecommendedFullName, 
    varRecommendedShortName, 
    varAlternativeFullName, 
    varAlternativeShortName,
    varGene,
    VarOrganismName,
    varOrganismDbReferenceType,
    varOrganismDbReferenceId,
    varReference,
    varReferenceType,
    varReferenceDate,
    varReferenceAuthors,
    varFeatureAttribs,
    varFeatureType):

        query = (
            "CREATE (p:Protein { id: $accessionValue }) "
            "CREATE (fn:Full_name { fullName: $varRecommendedFullName }) "
            "CREATE (sn:short_name { shortName: $varRecommendedShortName }) "
            "CREATE (afn:alternative_full_name { alternativeFullName: $varAlternativeFullName }) "
            "CREATE (asn:alternative_short_name { alternativeFullName: $varAlternativeShortName }) "
            "CREATE (ge:gene { gene: $varGene }) "
            "CREATE (or:organism { name: $varOrganismName, type: $varOrganismDbReferenceType, id: $varOrganismDbReferenceId }) "
            "CREATE (re:reference { type: $varReferenceType, date: $varReferenceDate  } ) "
            "CREATE (rea:reference_author { author: $varReferenceAuthors }) "
            "CREATE (fea:feature { type: $varFeatureType }) "
            "CREATE (p)-[:HAS_FULL_NAME]->(fn) "
            "CREATE (p)-[:HAS_SHORT_NAME]->(sn) "
            "CREATE (p)-[:HAS_ALTERNATIVE_FULL_NAME]->(afn) "
            "CREATE (p)-[:HAS_ALTERNATIVE_SHORT_NAME]->(asn) "
            "CREATE (p)-[:FROM_GENE]->(ge) "
            "CREATE (p)-[:IN_ORGANISM]->(or) "
            "CREATE (p)-[:HAS_REFERENCE]->(re) "
            "CREATE (re)-[:HAS_AUTHOR]->(rea) "
            "CREATE (p)-[:HAS_FEATURE]->(fea) "
            "RETURN p, fn, sn, afn, asn, ge, or, re, rea, fea"
        )
        
        referenceType=[]
        referenceDate=[]
        referenceAuthors =[]
        for reference in varReference:
            referenceType.append(reference['citation']['type'])
            referenceDate.append(reference['citation']['date'])


            referenceAuthors.append(reference['authors'])

        geneValue = ''
        for gene in varGene:
            if gene.get('primary') is not None:
                geneValue = gene.get('primary')
        
        organismName = ''
        for name in VarOrganismName:
            if name.get('scientific') is not None:
                 organismName = name.get('scientific')

        featureType = varFeatureAttribs[0]['type']
        
                 


        result = tx.run(query, 
        accessionValue=accessionValue[0], 
        varRecommendedFullName=varRecommendedFullName[0], 
        varRecommendedShortName=varRecommendedShortName,
        varAlternativeFullName=varAlternativeFullName,
        varAlternativeShortName=varAlternativeShortName,
        varGene = geneValue,
        varOrganismName=organismName,
        varOrganismDbReferenceType = varOrganismDbReferenceType,
        varOrganismDbReferenceId=varOrganismDbReferenceId,
        varReferenceType = referenceType[0],
        varReferenceDate = referenceDate[0],
        varReferenceAuthors= referenceAuthors[0],
        varFeatureAttribs = varFeatureAttribs[0],
        varFeatureType = featureType,
        
        )
        try:
            return [{"p": row["p"]["id"], "fn": row["fn"]["fullName"]}
                    for row in result]
        except ServiceUnavailable as exception:
            logging.error("{query} raised an error: \n {exception}".format(
                query=query, exception=exception))
            raise


tree = et.parse('Q9Y261.xml')
root = tree.getroot()

#accession
accessionValue = []
for accession in root.iter("{http://uniprot.org/uniprot}accession"):
    accessionValue.append(accession.text)


#recommended names 
varRecommendedFullName = []
varRecommendedShortName = []
for recommendedName in root.iter("{http://uniprot.org/uniprot}recommendedName"):
    for recommendedFullName in recommendedName.iter("{http://uniprot.org/uniprot}fullName"):
        varRecommendedFullName.append(recommendedFullName.text)

    for recommendedShortName in recommendedName.iter("{http://uniprot.org/uniprot}shortName"):
        varRecommendedShortName.append(recommendedShortName.text)

    

#alternative names
varAlternativeFullName = []
varAlternativeShortName = []
for alternativeName in root.iter("{http://uniprot.org/uniprot}alternativeName"):
    
    for alternativeFullName in alternativeName.iter("{http://uniprot.org/uniprot}fullName"):
        varAlternativeFullName.append(alternativeFullName.text)

    for alternativeShortName in alternativeName.iter("{http://uniprot.org/uniprot}shortName"):
        varAlternativeShortName.append(alternativeShortName.text)

    
#gene
varGene = []
for gene in root.iter("{http://uniprot.org/uniprot}gene"):
    for name in gene.iter("{http://uniprot.org/uniprot}name"):
        geneType = name.get('type')
        varGene.append({geneType: name.text})


#organism
VarOrganismName = []
varOrganismDbReferenceType = []
varOrganismDbReferenceId = []
varOrganismTaxon = []
for organism in root.iter("{http://uniprot.org/uniprot}organism"):
    for name in organism.iter("{http://uniprot.org/uniprot}name"):
        OrganismType = name.get('type')
        VarOrganismName.append({OrganismType: name.text})
        
    for dbReference in organism.iter("{http://uniprot.org/uniprot}dbReference"):
        dbReferenceType = dbReference.get('type')
        dbReferenceId = dbReference.get('id')
        varOrganismDbReferenceType.append(dbReferenceType)
        varOrganismDbReferenceId.append(dbReferenceId)

    for lineage in organism.iter("{http://uniprot.org/uniprot}lineage"):
        for taxon in organism.iter("{http://uniprot.org/uniprot}taxon"):
            varOrganismTaxon.append(taxon.text)

#reference
varReference = []
varReferenceType = []
varReferenceDate = []
varReferenceAuthors= []


for reference in root.iter("{http://uniprot.org/uniprot}reference"):

    obj = {
        "citation": {},
        "authors": []
    }
    citation = reference.find("{http://uniprot.org/uniprot}citation")
        
    obj['citation'] = citation.attrib


    authorlist = citation.find("{http://uniprot.org/uniprot}authorList")
    for author in authorlist.iter("{http://uniprot.org/uniprot}person"):
            
            obj['authors'].append(author.get('name'))

    varReference.append(obj)

#feature
varFeatureAttribs = []
varFeatureType = []
for feature in root.iter("{http://uniprot.org/uniprot}feature"):
    varFeatureAttribs.append(feature.attrib)




if __name__ == "__main__":
    uri = "bolt://localhost:7999"
    user = "neo4j"
    password = "password"
    app = App(uri, user, password)
    app.create_protein_relation(
    accessionValue, 
    varRecommendedFullName, 
    varRecommendedShortName, 
    varAlternativeFullName, 
    varAlternativeShortName,
    varGene,
    VarOrganismName,
    varOrganismDbReferenceType,
    varOrganismDbReferenceId,
    varReference,
    varReferenceType,
    varReferenceDate,
    varReferenceAuthors,
    varFeatureAttribs,
    varFeatureType,
    )
    app.close()