import sys
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.varLib.instancer import instantiateVariableFont
f=TTFont(sys.argv[1]); f=instantiateVariableFont(f,{'wght':int(sys.argv[2])})
gs=f.getGlyphSet(); cmap=f.getBestCmap(); upm=f['head'].unitsPerEm
cap=f['OS/2'].sCapHeight
x=0; parts=[]; track=0.02*upm; eb=None
for ch in "ЗЕРНА":
    g=cmap[ord(ch)]; pen=SVGPathPen(gs)
    gs[g].draw(TransformPen(pen,(1,0,0,-1,x,cap)))
    if ch=='Е':
        bp=BoundsPen(gs); gs[g].draw(bp); b=bp.bounds; eb=(x+b[0],x+b[2])
    parts.append(pen.getCommands()); x+=gs[g].width+track
w=x-track
# два зерна над Е
def bean(cx,cy,r,rot):
    rx,ry=r*0.72,r
    return (f'<g transform="translate({cx:.0f} {cy:.0f}) rotate({rot})">'
            f'<ellipse rx="{rx:.0f}" ry="{ry:.0f}"/>'
            f'<path d="M0 {-ry*0.78:.0f} C {rx*0.55:.0f} {-ry*0.3:.0f} {-rx*0.55:.0f} {ry*0.3:.0f} 0 {ry*0.78:.0f}" fill="none" stroke="var(--slit,#2340D9)" stroke-width="{r*0.16:.0f}" stroke-linecap="round"/></g>')
r=cap*0.15; ex0,ex1=eb; cy=-r*1.55
beans=bean(ex0+(ex1-ex0)*0.22,cy,r,-25)+bean(ex0+(ex1-ex0)*0.78,cy,r,25)
top=cy-r-10
print(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-10 {top:.0f} {w+20:.0f} {cap-top+10:.0f}"><g fill="currentColor"><path d="{" ".join(parts)}"/>{beans}</g></svg>')
