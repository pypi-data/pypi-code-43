# Load your usual SpaCy model (one of SpaCy English models)
import spacy
nlp = spacy.load('en')

# Add neural coref to SpaCy's pipe
import neuralcoref
neuralcoref.add_to_pipe(nlp)

import os
from stanfordnlp.server import CoreNLPClient

class WrapperCoreference:
    def __init__(self):
        self.CoreNLPCoref_printChains = False
        self.CoreNLPCoref_onlyPronominal = True
        self.numberRequestFails = 20
        self.returnFullInformationReferences = True
        pass
    
    
 
        
    #-----
    # > wc.NeuralCoref(u'My sister has a dog. She loves him.')
    #
    # output system: [
    #    {'start': 0, 'end': 9, 'text': 'My sister', 'resolved': 'My sister'}, 
    #    {'start': 21, 'end': 24, 'text': 'She', 'resolved': 'My sister'}, 
    #    {'start': 14, 'end': 19, 'text': 'a dog', 'resolved': 'a dog'}, 
    #    {'start': 31, 'end': 34, 'text': 'him', 'resolved': 'a dog'}
    #   ]
    #
    ## we keep only the correferences
    # returned value: [
    #   {'start': 21, 'end': 24, 'text': 'She', 'resolved': 'My sister'}, 
    #   {'start': 31, 'end': 34, 'text': 'him', 'resolved': 'a dog'}
    #  ]
    def NeuralCoref(self, text):
        doc = nlp(text)
        #doc._.has_coref
        #doc._.coref_clusters 


        mentions = [{'start':    mention.start_char,
                        'end':      mention.end_char,
                        'text':     mention.text,
                        'resolved': cluster.main.text
                    }
                    for cluster in doc._.coref_clusters
                    for mention in cluster.mentions]
        return [m for m in mentions if m["text"]!=m["resolved"]]

        
        





    #-------
    def setCoreNLP(self,coreNLP):
        os.environ['CORENLP_HOME'] = coreNLP; #requiremnt of NLP
        
    # Here I'm taking into account only those correferences from pronominal
    def CoreNLPCoref(self, text):
        if text[0] == " ":
            text = "-" + text[1:]
        # set up the client
        client = CoreNLPClient(output_format='json', properties={'annotators': 'coref', 'coref.algorithm' : 'statistical'}, timeout=1200000, memory='16G')
        
        # submit the request to the server
        answer_fail = True
        for i in range(self.numberRequestFails):
            answer_fail = True
            try:
                ann = client.annotate(text)    
            except Exception as err:
                print("[Error handled]:",err)
                continue
            answer_fail = False
            break
            
        if answer_fail: 
            return []
        mychains = list()
        R = []
        chains = eval(str(ann))
        
        Sent = {}
        for s in chains["sentences"]:
            Sent[s["index"]] = {}
            for t in s["tokens"]:
                Sent[s["index"]][t["index"]] = {
                    "originalText":t["originalText"], 
                    "characterOffsetBegin":t["characterOffsetBegin"],
                    "characterOffsetEnd":t["characterOffsetEnd"],
                    "pos":t["pos"],
                    "ner":t["ner"]                    
                }
        
        Coref = {}        
        for c_id in chains["corefs"].keys():
            coref = chains["corefs"][c_id]
            Coref[c_id] = []
            for c in coref:
                Coref[c_id].append({
                    "id":int(c["id"]), 
                    "sentNum":int(c["sentNum"])-1, 
                    "type":c["type"], 
                    "text":c["text"],
                    "startIndex":int(c["startIndex"]),
                    "endIndex":int(c["endIndex"]),
                    "ini": Sent[int(c["sentNum"])-1][int(c["startIndex"])]["characterOffsetBegin"],
                    "fin": Sent[int(c["sentNum"])-1][int(c["endIndex"])-1]["characterOffsetEnd"],
                    }
                )
        
            
        R = []
        for cor in Coref:
            if self.CoreNLPCoref_printChains:
                print(' <-> '.join([text[x["ini"]:x["fin"]] for x in Coref[cor]]))
            
            FullResolved = []
            if len(Coref[cor])>0:
                # searching first for Non-pronominal token
                no_pronoun = 0
                resolved = Coref[cor][no_pronoun]["text"]
                for i in range(len(Coref[cor])):
                    x = Coref[cor][i]
                    if x["type"] != "PRONOMINAL":
                        no_pronoun = i
                        resolved = Coref[cor][no_pronoun]["text"]
                        
                        if self.returnFullInformationReferences:
                            FullResolved.append({'start':x["ini"],
                                'end':x["fin"],
                                'text':x["text"]})
                
                # creating the response
                for i in range(len(Coref[cor])):
                    x = Coref[cor][i]
                    if i!=no_pronoun:
                        if x["type"] != "PRONOMINAL"  and self.CoreNLPCoref_onlyPronominal: continue
                        r = {
                                'start':x["ini"],
                                'end':x["fin"],
                                'text':x["text"],#text[x["ini"]:x["fin"]],
                                'resolved': resolved
                            }
                        if self.returnFullInformationReferences:
                            r["fullInformation"] = FullResolved
                        
                        R.append(r)
                        
                        
        return R
                    


