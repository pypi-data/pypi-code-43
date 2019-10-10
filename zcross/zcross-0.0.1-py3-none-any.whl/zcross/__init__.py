import xml.etree.ElementTree as et

import re
import os


re_reference = re.compile(r'@(\w+){([\w\-]+),([\s\S]*)}', re.MULTILINE)

class ZCross:
    
    def __init__(self, databases=[]):
        
        if isinstance(databases, str):
            databases = [databases]
        
        
        self.databases = []
        
        data_dir = None
        
        if 'ZCROSS_DATA' in os.environ and os.path.exists(os.environ['ZCROSS_DATA']):
            data_dir = os.environ['ZCROSS_DATA']
            
        if os.path.exists('/opt/zcross/share/zcross/data'):
            data_dir = '/opt/zcross/share/zcross/data'
            
        if data_dir is None:
            raise Exception('Unable to find ZCross data file: define ZCROSS_DATA env variable.')
                
        for r, d, f in os.walk('/opt/zcross/share/zcross/data'):
            for fx in f:
                if fx.endswith('.xml'):
                    
                    load = True
                    filename = os.path.join(r, fx)
                    
                    if databases:
                        basename = os.path.splitext(os.path.basename(filename))[0]
                        load = basename in databases
                    
                    if load:
                        self.load_file(filename)

    def load_file(self, filename):
        
        source = et.parse(filename) 

        xml  = source.getroot()
        
        for child in xml.getchildren():
            tag = clean_ns(child.tag)
            
            if tag == 'database':
                self.databases.append(Database(child))
         
        


class Base:
    
    def __init__(self, xml, skip = [], cast_map = {}):
        
        for key, value in xml.attrib.items():
            setattr(self,key,convert(key, value, cast_map))
            
        for child in xml.getchildren():
            
            tag = clean_ns(child.tag)
            
            if not tag in skip:
            
                if len(child.getchildren()) > 0:
                    
                    for childXml in child.getchildren():
                        
                        childTag = clean_ns(childXml.tag)
                        
                        childClass = globals()[childTag.capitalize()]
                        
                        if not hasattr(self, tag):
                            setattr(self, tag, list())
                            
                        getattr(self, tag).append(childClass(childXml))
            
                elif len(child.attrib) > 0:
                    currentClass = globals()[tag.capitalize()]
                    setattr(self,tag,currentClass(child))
                else:
                    setattr(self,tag,convert(tag, child.text, cast_map))
        
        if len(xml.getchildren()) == 0 and xml.text is not None:
            setattr(self, 'value',xml.text.strip())

        
class Database(Base):
    def __init__(self, xml):
         super().__init__(xml)
         
    def __str__(self):
        return self.name
        
    def __repr__(self):
        return '<Database {}>'.format(self.id)
            
    
class Reference:
    def __init__(self, xml):
        self.id = xml.get('id')
        
        m = re_reference.match(xml.text.strip())
        
        if m:
            self.label = m.group(2)
            self.type = m.group(1)
            content = m.group(3)
            
            # Parsing content
            
            section = 0
            
            current_key = ''
            current_value = ''
                        
             
            level = 0
                     
            for c in content:

                if c == '=' and level == 0:
                    if section == 0:
                        section = 1
                        continue
                elif c == ',' and level == 0:
                    if section == 1:
                        section = 2
                        continue
                elif c == '{':
                    level += 1
                elif c == '}':
                    level -= 1
                    
                
                if section == 0:
                    current_key += c
                if section == 1:
                    current_value += c
                if section == 2:
                    key = current_key.strip()
                    value = current_value.strip()
                    
                    if value.startswith('{') and value.endswith('}'):
                        value = value.strip('{').strip('}')
                        
                    setattr(self, key, value)
                    
                    current_key   = ''
                    current_value = ''
                    level = 0
                    section = 0
                      
    def __str__(self):
        return self.label
        
    def __repr__(self):
        return '<Reference {}: {}>'.format(self.type, self.label)
        
    def bibtex(self):
        s = '@{}{{{},\n'.format(self.type, self.label)
        for k,v in vars(self).items():
            if k not in ['label','type','id']:
                s += '\t{} = {{{}}},\n'.format(k,v)
        s += '}'
        
        return s
        
        
        
class Group(Base):
    def __init__(self, xml):
        super().__init__(xml)
        
    def __str__(self):
        return 'Group {}'.format(self.id)
    
    def __repr__(self):
        return '<{}>'.format(str(self))
    
class Process(Base):
    def __init__(self, xml):
        super().__init__(xml, ['data_x', 'data_y'], cast_map = {'id': int, 'momentOrder': int})
        
        xml_x = xml.find('{https://zcross.net}data_x')
        xml_y = xml.find('{https://zcross.net}data_y')
        
        unit_x = xml_x.get('units')
        unit_y = xml_y.get('units')
        
        type_x = xml_x.get('type')
        type_y = xml_y.get('type')
        
        data_x = [ float(d) for d in xml_x.text.split(' ')] if xml_x.text is not None else []
        data_y = [ float(d) for d in xml_y.text.split(' ')] if xml_y.text is not None else []
        
        setattr(self, type_x, data_x)
        setattr(self, type_y, data_y)
        
        setattr(self, type_x + '_units', unit_x)
        setattr(self, type_y + '_units', unit_y)
        
        self.complete_reaction()

    def __str__(self):
        s = ''      
        s += ' + '.join(str(r) for r in self.reactants)
        s += ' → '
        s += ' + '.join(str(p) for p in self.products)
        return s

    def __repr__(self):
        return '<Reaction: {}>'.format(str(self))
        
        
    def complete_reaction(self):
        
        if self.reactants is not None and not hasattr(self, 'products'):
            self.products = self.reactants
            
        #if len(self.reactants) == 2 and isinstance(self.reactants[1], Molecule):
            
            #fail = False
            
            #buffer_reactant = self.reactants[1].explode()
            
            
            #for product in self.products():
                #if isinstance(product, Molecule):
                    #buffer_product = product.explode()
                    
                    #for atom, qty in buffer_product.items():
                        #if atom in buffer_reactant:
                            #buffer_reactant[atom] -= qty
                            
                            #if buffer_reactant[atom] < 0:
                                #fail = True
                                #break
                            #if buffer_reactant[atom] == 0:
                                #buffer_reactant.pop(atom)
                        #else:
                            #fail = True
                            #break
                #if fail:
                    #break
                    
            #if not fail and len(buffer_reactant):
                #self.products.append(Molecule(''))
            
            
            
            
        
            
        
        
   
        
class Electron(Base):
    def __init__(self, xml):
        super().__init__(xml)
        
    def __str__(self):
        return 'e'
        
    def __repr__(self):
        return '<Electron>'
        
        
molecule_pat1 = re.compile('([0-9]+)')
molecule_pat2 = re.compile('\s*([A-Z][a-z]?)([0-9]*)\s*')

class Molecule(Base):
    def __init__(self, xml):
        super().__init__(xml, cast_map={'charge': int})
        self.explode()
        
    def __str__(self):
        
        s = self.value
        
        if hasattr(self, 'charge'):
            if abs(self.charge) > 1:
                s += (get_scripted_number(abs(self.charge), True, False) if abs(self.charge) >  1 else '') 
                
            if self.charge > 0:
                s += '⁺'
                
            if self.charge < 0:
                s += '⁻'
            
                
        if hasattr(self, 'state'):
            s += '(' + self.state + ')'
        
        return s
        
    def __repr__(self):
        return '<Molecule: {}>'.format(str(self))
        
    
    
        
    def explode(self):
        
        s = self.value
        global_reciept = {}

        for start,end,level in self.__find_parens():

            local_reciept = {}
            
            formula  = s[start+1:end]
            multiply = 1 
            m1 = molecule_pat1.match(s, end+1)
            if m1:
                multiply = int(m1.group(1))
                end = m1.span(1)[1]
                
            # Parsing   
            m2 = molecule_pat2.match(formula)
            while m2:
                atom = m2.group(1)
                
                qty  = 1
                if m2.group(2):
                    qty = int(m2.group(2))
                    
                if atom not in local_reciept:
                    local_reciept[atom] = 0
                local_reciept[atom] += qty
                                
                m2 = molecule_pat2.match(formula, m2.span(1)[1])
                
            
            for atom, qty in local_reciept.items():
                
                if atom not in global_reciept:
                    global_reciept[atom] = 0
                
                global_reciept[atom] += qty * multiply
                
            # Cleaning
            s = s[:start] + ' ' * (end-start+1) + s[end+1:]
                
        return global_reciept
                 
            
            
        
    def __find_parens(self):
        results = []
        pstack = []
        
        results.append((-1, len(self.value), 0))

        for i, c in enumerate(self.value):
            if c == '(':
                pstack.append(i)
            elif c == ')':
                if len(pstack) == 0:
                    raise IndexError("No matching closing parens at: " + str(i))
                results.append((pstack.pop(), i, len(pstack)+1))

        if len(pstack) > 0:
            raise IndexError("No matching opening parens at: " + str(pstack.pop()))

        results.sort(key=lambda result: result[0], reverse=True)
        
        return results
    
    
class Parameter(Base):
    def __init__(self, xml):
        super().__init__(xml)
        
    def __str__(self):
        return self.name + ' = ' + self.value + (' ' + self.units if hasattr(self, 'units') else '')
    
   
    
    
def clean_ns(tag):
    return tag.split("}")[1][0:]
    
    
def convert(tag, value, cast_map={}):
    
    if tag in cast_map:
        return cast_map[tag](value)
    else:
        return value

def get_scripted_number(number, superscript, forcePlus):

    if not isinstance(number, int):
        raise "Argument 'number' must be an int"

    digitsSuper = ['⁰','¹','²','³','⁴','⁵','⁶','⁷','⁸','⁹']
    digitsSub   = ['₀','₁','₂','₃','₄','₅','₆','₇','₈','₉']

    s= ''

    if number < 0:
        if superscript:
            s += '⁻';
        else:
            s += '₋';
    
    elif number > 0 and forcePlus:
        if superscript:
            s += '⁺'
        else:
            s += '₊'

    while number > 0:
        
        if superscript:
            s = digitsSuper[number % 10] + s
        else:
            s = digitsSub[number % 10] + s
            
        number //= 10
    

    return s

