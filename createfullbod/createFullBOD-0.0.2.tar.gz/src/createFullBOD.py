import xml.etree.ElementTree as xml
import uuid
from datetime import datetime

def createRoot(root):
    bod = xml.Element(root)
    bod.attrib['xmlns']='http://schema.infor.com/InforOAGIS/2'
    return bod

def createApplArea(lid,compId):
    appArea = xml.Element('ApplicationArea')
    sender = xml.SubElement(appArea,'Sender')
    logicalID = xml.SubElement(sender,'LogicalID')
    logicalID.text = lid
    componentID = xml.SubElement(sender,'ComponentID')
    componentID.text = compId
    confCode = xml.SubElement(sender,'ConfirmationCode')
    confCode.text = 'OnError'
    creationDT = xml.SubElement(appArea,'CreationDateTime')
    now = datetime.now()
    ml = now.strftime("%f")
    creationDT.text = now.strftime("%Y-%m-%dT%H:%M:%S") + ":" + ml[0:3] + "Z"
    bodID = xml.SubElement(appArea,'BODID')
    uuid1 = uuid.uuid1()
    bodID.text = str(uuid1)
    return appArea

def createDataArea():
    dataArea = xml.Element('DataArea')
    return dataArea

def createVerb(verb,aev,locv,aexv):
    verb = xml.Element(verb)
    ae = xml.SubElement(verb,'AccountingEntityID')
    ae.text = aev
    loc = xml.SubElement(verb,'LocationID')
    loc.text = locv
    ac = xml.SubElement(verb,'ActionCriteria')
    aex = xml.SubElement(ac,'ActionExpression')
    aex.attrib['actionCode']=aexv
    return verb

def renameTag(xml, oldtag,newtag):
    for element in xml.iter(oldtag):
        element.tag = newtag    

def createFullBOD(verb,noun,lid,erp,ae,loc,action,body):
    root = createRoot(verb+noun)
    aa = createApplArea(lid,erp)
    vb = createVerb(verb,ae,loc,action)
    body.insert(0,vb)
    root.append(aa)
    root.append(body)
    renameTag(root,'root','DataArea')
    renameTag(root,'element',noun)
    return root

