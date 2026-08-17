#!/usr/bin/env python3
from pathlib import Path
import re
B=Path(__file__).resolve().parent
CH=[('cap01-eletrostatica.tex',None),('cap02-conceitos-iniciais.tex',1),('cap03-associacao-resistores.tex',2),('cap04-divisores.tex',3),('cap05-potencia.tex',4),('cap06-superposicao-integrado.tex',5),('cap07-analise-nodal-integrado.tex',6),('cap08-thevenin-norton-integrado.tex',7),('cap09-maxwell.tex',8),('cap10-capacitores-indutores.tex',9),('cap11-eletromagnetismo.tex',10)]

def comments(s):
    z=[]
    for l in s.splitlines(True):
        for i,c in enumerate(l):
            if c=='%':
                n=0;j=i-1
                while j>=0 and l[j]=='\\': n+=1;j-=1
                if n%2==0: l=l[:i]+('\n' if l.endswith('\n') else '');break
        z.append(l)
    return ''.join(z)

def group(s,i,a='{',b='}'):
    d=1;j=i+1;k=j
    while j<len(s):
        if s[j]=='\\': j+=2;continue
        if s[j]==a:d+=1
        elif s[j]==b:
            d-=1
            if d==0:return s[k:j],j+1
        j+=1
    raise ValueError('grupo LaTeX nao fechado')

def spaces(s,i):
    while i<len(s) and s[i].isspace():i+=1
    return i

def opt(s,i):
    i=spaces(s,i)
    if i<len(s) and s[i]=='[':
        x,j=group(s,i,'[',']');return '['+x+']',j
    return '',i

def expand(s,base,stack=()):
    s=comments(s);o=[];p=0
    for m in list(re.finditer(r'\\input\s*\{',s)):
        if m.start()<p:continue
        o.append(s[p:m.start()]);q=s.find('{',m.start());n,e=group(s,q)
        raw=n.strip()
        f=(B/raw).resolve();f=f if f.suffix else f.with_suffix('.tex')
        if not f.exists():
            f=(base/raw).resolve();f=f if f.suffix else f.with_suffix('.tex')
        if f in stack:raise RuntimeError('ciclo de input: '+str(f))
        if not f.exists():raise FileNotFoundError(f)
        o.append('\n'+expand(f.read_text(encoding='utf-8'),f.parent,stack+(f,))+'\n');p=e
    o.append(s[p:]);return ''.join(o)

def allcmd(s,name):
    t='\\'+name;r=[];p=0
    while True:
        i=s.find(t,p)
        if i<0:return r
        a=i+len(t)
        if a<len(s) and s[a].isalpha():p=a;continue
        j=spaces(s,a)
        if j<len(s) and s[j]=='{':x,p=group(s,j);r.append('{'+x+'}')
        else:p=a

def rmcmd(s,name):
    t='\\'+name;o=[];p=0
    while True:
        i=s.find(t,p)
        if i<0:o.append(s[p:]);return ''.join(o)
        a=i+len(t)
        if a<len(s) and s[a].isalpha():o.append(s[p:a]);p=a;continue
        o.append(s[p:i]);j=spaces(s,a)
        if j<len(s) and s[j]=='{':_,p=group(s,j)
        else:o.append(t);p=a

def titlecmd(s,p,name):
    i=p+len('\\'+name);star=''
    if i<len(s) and s[i]=='*':star='*';i+=1
    i=spaces(s,i)
    if i>=len(s) or s[i]!='{':return None,p+1
    x,e=group(s,i);return '\\'+name+star+'{'+x+'}',e

def question(s,p):
    t='\\begin{questao}';i=p+len(t);op,i=opt(s,i);i=spaces(s,i);src='{}'
    if i<len(s) and s[i]=='{':x,i=group(s,i);src='{'+x+'}'
    e=s.find('\\end{questao}',i)
    if e<0:raise ValueError('questao sem fechamento')
    return op,src,s[i:e],e+len('\\end{questao}')

def filt(s,mode):
    o=[];p=0;st={'q':0,'a':0,'r':0,'sa':0,'sr':0};levels=('blocofixacao','blocoaplicacao','blocoaprofundamento','blocodesafio')
    while p<len(s):
        if s.startswith('\\begin{questao}',p):
            op,src,body,p=question(s,p);a=allcmd(body,'resposta');r=allcmd(body,'resolucao')
            st['q']+=1;st['a']+=len(a);st['r']+=len(r);st['sa']+=not a;st['sr']+=not r
            if mode=='q':o.append('\\begin{questao}'+op+src+'\n'+rmcmd(body,'resolucao')+'\n\\end{questao}\n')
            else:o.append('\\stepcounter{questao}\n'+''.join('\\resposta'+x+'\n' for x in a)+''.join('\\resolucao'+x+'\n' for x in r))
            continue
        hit=False
        for n in ('section','subsection'):
            if s.startswith('\\'+n,p):
                x,e=titlecmd(s,p,n)
                if x:o.append('\n'+x+'\n');p=e;hit=True;break
        if hit:continue
        if s.startswith('\\gabarito',p):
            x,p=opt(s,p+len('\\gabarito'));o.append('\n\\gabarito'+x+'\n');continue
        if mode=='q':
            for n in levels:
                t='\\'+n
                if s.startswith(t,p):o.append('\n'+t+'\n');p+=len(t);hit=True;break
            if hit:continue
        p+=1
    return ''.join(o),st

def main():
    z=[]
    for f,n in CH:
        if n is not None:z.append(f'\n\\setcounter{{section}}{{{n}}}\n')
        p=B/f;z.append(expand(p.read_text(encoding='utf-8'),p.parent,(p.resolve(),)))
    s=''.join(z)
    s=re.sub(r'\\SI\{([^{}]+)\}\{\\month\}',r'\1 meses',s)
    q,qs=filt(s,'q');r,rs=filt(s,'r')
    (B/'gerado-questoes.tex').write_text('% Gerado automaticamente. Nao editar.\n'+q,encoding='utf-8')
    (B/'gerado-resolucoes.tex').write_text('% Gerado automaticamente. Nao editar.\n'+r,encoding='utf-8')
    print('questoes',qs);print('resolucoes',rs)
    if not qs['q'] or qs['q']!=rs['q']:raise SystemExit('falha de consistencia')
    if qs['sa']:print('AVISO: questoes sem resposta:',qs['sa'])
    if qs['sr']:print('AVISO: questoes sem resolucao:',qs['sr'])
if __name__=='__main__':main()
