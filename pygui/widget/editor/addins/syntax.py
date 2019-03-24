import builtins
import re
import keyword
import tkinter as tk


def any(name, alternates):
    return "(?P<%s>" % name + "|".join(alternates) + ")"
    
    
def ty():
    kw = r"\b" + any("KEYWORD", keyword.kwlist) + r"\b"
    builtinlist = [str(name) for name in dir(builtins)
                                        if not name.startswith('_')]
    builtinlist.remove('print')
    builtin = r"([^.'\"\\#]\b|^)" + any("BUILTIN", builtinlist) + r"\b"
    comment = any("COMMENT", [r"#[^\n]*"])
    stringprefix = r"(\br|u|ur|R|U|UR|Ur|uR|b|B|br|Br|bR|BR)?"
    sqstring = stringprefix + r"'[^'\\\n]*(\\.[^'\\\n]*)*'?"
    dqstring = stringprefix + r'"[^"\\\n]*(\\.[^"\\\n]*)*"?'
    sq3string = stringprefix + r"'''[^'\\]*((\\.|'(?!''))[^'\\]*)*(''')?"
    dq3string = stringprefix + r'"""[^"\\]*((\\.|"(?!""))[^"\\]*)*(""")?'
    string = any("STRING", [sq3string, dq3string, sqstring, dqstring])
    return kw + "|" + builtin + "|" + comment + "|" + string +\
           "|" + any("SYNC", [r"\n"])
           

def _coordinate(start, end, string):
    srow=string[:start].count('\n')+1 # starting row
    scolsplitlines=string[:start].split('\n')
    if len(scolsplitlines)!=0:
        scolsplitlines=scolsplitlines[len(scolsplitlines)-1]
    scol=len(scolsplitlines)# Ending Column
    lrow=string[:end+1].count('\n')+1
    lcolsplitlines=string[:end].split('\n')
    if len(lcolsplitlines)!=0:
        lcolsplitlines=lcolsplitlines[len(lcolsplitlines)-1]
    lcol=len(lcolsplitlines)+1# Ending Column
    return '{}.{}'.format(srow, scol),'{}.{}'.format(lrow, lcol)#, (lrow, lcol)
    
    
def coordinate(pattern, string, txt):
    line=string.splitlines()
    start=string.find(pattern)  # Here Pattern Word Start
    end=start+len(pattern) # Here Pattern word End
    srow=string[:start].count('\n')+1 # starting row
    scolsplitlines=string[:start].split('\n')
    if len(scolsplitlines)!=0:
        scolsplitlines=scolsplitlines[len(scolsplitlines)-1]
    scol=len(scolsplitlines)# Ending Column
    lrow=string[:end+1].count('\n')+1
    lcolsplitlines=string[:end].split('\n')
    if len(lcolsplitlines)!=0:
        lcolsplitlines=lcolsplitlines[len(lcolsplitlines)-1]
    lcol=len(lcolsplitlines)# Ending Column
    return '{}.{}'.format(srow, scol),'{}.{}'.format(lrow, lcol)
    
    
def check(k={}):
    if k['COMMENT']!=None:
     return 'comment','green'
    elif k['BUILTIN']!=None:
     return 'builtin','VioletRed'
    elif k['STRING']!=None:
     return 'string','blue'
    elif k['KEYWORD']!=None:
     return 'keyword','orange'
    else:
     return 'ss','NILL'


txtfilter=re.compile(ty(),re.S)


class PythonSyntaxColor(object):
    
    def __init__(self, txtbox=None):
        self.txt = txtbox
        self.txt.bind("<Any-KeyPress>", self.trigger)
        
    def binding_function_configurations(self):
        self.txt.storeobj['ColorLight'] = self.trigger
        
    def trigger(self, event=None):
        val = self.txt.get('1.0', tk.END)
        if len(val) == 1:
            return
        for i in ['comment', 'builtin', 'string', 'keyword']:
            self.txt.tag_remove(i, '1.0', tk.END)
        for i in txtfilter.finditer(val):
            start = i.start()
            end = i.end()-1
            tagtype, color = check(k=i.groupdict())
            if color != 'NILL':
                ind1, ind2 = _coordinate(start, end, val)
                self.txt.tag_add(tagtype, ind1, ind2)
                self.txt.tag_config(tagtype, foreground=color)
