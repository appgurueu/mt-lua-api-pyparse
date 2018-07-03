# -*- coding: utf-8 -*-
print("**Minetest lua_api.txt Markdown parser - mt-lua-api-pyparse - converts Markdown to HTML document with navigation**")
print("**Written by Lars Müller alias LMD in Python 3.5 - requires Python >= 3.2**")
print("**Furthermore, this script has to be in the same folder as generate_bg.py, template.html, jumbotron.css, and the images taken from Minetest Game.**")
print("**The images taken from Minetest Game are licensed under CC-BY-SA 3.0, credits go to the Minetest Artists.**")
#from cgi import html
from xml.sax.saxutils import escape, unescape

html_escape_table = {
    '"': "&quot;",
    "'": "&apos;"
}

def html_escape(text):
    return escape(text, html_escape_table)

import urllib.request as url
import urllib.parse as parse
print("**Generating underground Minetest scene...**")
exec(open("generate_bg.py","r").read()) # IMPORTANT - GENERATES THE BEAUTIFUL BACKGROUND !
print("**...finished generating scene.**")
import math

# This python script grabs the newest lua_api.txt from Minetest GitHub repo and converts it to HTML, plus adding some bookmarks & css
# So mainly MD -> HTML. Written by me to improve my rusty Python skills.
# © Lars Müller @appguru.eu

print("**Grabbing newest lua_api.txt, make sure you have an internet connection...**")

link = "https://raw.githubusercontent.com/minetest/minetest/master/doc/lua_api.txt" # Grab newest lua_api.txt
f = url.urlopen(link)
markdown = parse.unquote(str(f.read().decode("ascii","ignore"))) # Read & convert

print("**...grabbed newest lua_api.txt from official Minetest repository.**")

liste=0 # Which sublist we are in right NOW
headers=[] # Stores all the headers + IDs
ID=0 # Stores header ID counter

print("**Starting parsing...**")

def parse_markdown(string,parent=False): # PARSES A SINGLE LINE !
    global liste
    global ID
    global headers
    suffix=""
    prefix=""
    if string.find("*") != -1 and (string[0:string.find("*")].count(" ") == string.find("*")) and not (parent or string[string.find("*")+1]=="*"): # LISTS
        prevliste=liste
        liste=1+int(string.find("*")/3)
        if (liste > prevliste):
            for i in range(0,liste-prevliste):
                prefix+="<ul>"
        elif (liste < prevliste):
            for i in range(0,prevliste-liste):
                prefix+="</ul>"
        return prefix+"<li>"+parse_markdown(string[string.find("*")+2:],parent=True)+"</li>"+suffix
    if not parent and liste != 0 and string=="":
        for i in range(0,liste):
            prefix+="</ul>"
        liste=0
    if (len(string)) == 0:
        return prefix+"<br>"
    if (string[-2:]=="  "):
        return prefix+parse_markdown(string[:-2],parent=True)+"<br>"
    if (string[0]=="#"):
        space=string.find(" ")
        c=string[0:space-1].count("#")
        if space==-1 or string[space+1:].count(" ")==len(string)-space-1:
            return "<br>"
        if (space-1==c):
            ID+=1
            c+=1
            temp="<h"+str(c)+'>'+parse_markdown(string[space+1:],parent=True)+"</h"+str(c)+">"
            headers.append((temp,str(ID)))
            temp=prefix+temp[:3]+' id="gheader'+str(ID)+'"'+temp[3:]
            return temp
    bold=False
    boldamount=string.count("**")
    ba=0
    italic=False
    code=False
    link=False
    link2=False
    codeamount=string.count("`")
    ca=0
    startindex=0
    tags=[]
    currentstring=""
    index=-1
    while index in range(-1,len(string)-1):
        index+=1
        appendtag=False
        c=string[index]
        if c == "`":
            if ca < codeamount:
                code=not code
                ca=ca+1
                if not code: # We have just closed a code fragment
                    tags.append((string[startindex+1:index],"code"))
                    continue
                else: # A new one starts : SAVE INDEX + SAVE CURRENT STRING !
                    appendtag=True
        elif not code:
            if c == "*" and len(string) > index+1 and string[index+1] == "*":
                if ba < boldamount:
                    index+=1
                    bold=not bold
                    ba=ba+1
                    if not bold: # We have just closed a code fragment
                        tags.append((string[startindex+1:index-1],"bold"))
                        continue
                    else: # A new one starts : SAVE INDEX + SAVE CURRENT STRING !
                        appendtag=True
            elif c == "<" and not link:
                appendtag=True
                link=True
            elif c == ">" and link:
                link=False
                tags.append((string[startindex+1:index],"link"))
                continue
            elif c == "[":
                breakit=False
                text=""
                for i in range(index+2,len(string)-3):
                    c2=string[i]
                    if (c2 == "]"):
                        text=string[index+1:i]
                        if string[i+1]=="(":
                            for j in range(i+3,len(string)):
                                c3=string[j]
                                if (c3 == ")"):
                                    breakit=True
                                    tags.append((text,"link",string[i+2:j]))
                                    index=j+1
                        break
                if breakit:
                    continue
        if appendtag:
            tags.append((currentstring,"normal"))
            currentstring=""
            startindex=index
            continue
        if not bold and not code and not link and not link2:
            currentstring+=c
    if len(currentstring)  != 0:
        tags.append((currentstring,"normal"))
    result=""
    for tag in tags:
        string=tag[0]
        p=""
        s=""
        if tag[1]=="code":
            p,s="<code>","</code>"
        elif tag[1]=="bold":
            p,s="<b>","</b>"
        elif tag[1]=="link":
            if len(tag) == 2:
                if tag[0][0:4] == "http": # CHECK LINKS !
                    p,s='<a href="'+tag[0]+'">',"</a>"
            else:
                p,s='<a href="'+tag[2]+'">',"</a>"
        elif tag[1]=="italic":
            p,s="<em>","</em>"
        result+=p+html_escape(string)+s
    return prefix+"<p>"+result+"</p>"

def parse_md(string): # Parse line by line
    lines=string.split("\n")
    ret=""
    for i in range(len(lines)-1,0,-1): # Convert alternate header writings(underlines)
        if abs(len(lines[i-1])-len(lines[i])) < 3:
            if lines[i].count("=")==len(lines[i]):
                lines[i]=""
                lines[i-1]="# "+lines[i-1]
            elif lines[i].count("-")==len(lines[i]):
                lines[i]=""
                lines[i-1]="## "+lines[i-1]
    i=0
    ident=False
    segments=0
    for line in lines:
        prefix=""
        suffix=""
        asteriskpos=line.find("*")
        # or (len(line) > 1 and line[0]=="\t" and (asteriskpos==-1 or line[0:asteriskpos].count("\t") != asteriskpos)))
        if liste== 0 and ((len(line) > 4 and line[0:4]==" "*4 and (asteriskpos==-1 or asteriskpos > 1 or line[0:asteriskpos].count(" ") != asteriskpos))):
            if not ident:
                prefix="<pre><code>"
                #print("START : "+line[4:])
                ident=True
        elif ident:
            ident=False
            prefix="</code></pre>"
            segments+=1
        #else:
            #if (len(line > 4)
            #print("{"+line[0:4]+";"+line[0]+"}")
            
        lval=""
        if ident:
            lval=html_escape(line[4:])+"\n"
        else:
            lval=parse_markdown(line)
        ret+=prefix+lval
        i=i+1
    print("**Found "+str(segments)+" multi-line code segments.**")
    if ident:
        ident=False
        return ret+"</code></pre>"
    return ret

def code(): # Parse multi-line code fragments
    global markdown
    last=-1
    i=0
    stuff=[]
    while (i < len(markdown)):
        if markdown[i:i+3]=="`"*3: # Handle GitHub style code tags
            i=i+3
            if last < 0:
                start=-(last+1)
                last=i
                stuff.append((markdown[start:last-3],False))
            else:
                stuff.append((markdown[last:i-3],True))
                last=-i-1
        i=i+1

    start=-(last+1)
    stuff.append((markdown[start:],False))
    #print(stuff)

    markdown=""
    for s in stuff:
        if s[1]:
            markdown+="<pre><code>"+s[0]+"</code></pre>"
        else:
            markdown+=parse_md(s[0])

code()

print("**...finished parsing.**")

nav=""

print("**Creating content table...**")

for header in headers:
    nav+="""<li><a class="nav-link" href="#gheader"""+header[1]+"""">"""+header[0]+"""</a></li>""" # Create navbar

print("**...finished creating content table. "+str(len(headers))+" Headers are included.**")

# FINAL - THE FINAL HTML, BOOTSTRAP BASED DOCUMENT OUR HTML IS INSERTED IN
final = open('template.html', 'r').read()
print("**Inserting content into template file...**")
markdown=final.replace("<!--PLACESTUFF-->",markdown)
print("**...finished inserting content.**")
print("**Inserting content table into template file...**")
markdown=markdown.replace("<!--PLACENAV-->",nav)
print("**...finished inserting content table.**")
print("**Saving as lua_api.html...**")
file = open('lua_api.html', 'w') # SAVE AS lua_api.html
file.write(markdown)
print("**...saved.**")
print("**Parser finished successfully and lua_api.html was generated.**")
file.close()
