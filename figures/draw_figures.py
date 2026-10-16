"""Vector drawing primitives; copied into each independent project generator."""
import argparse
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon, Circle, FancyArrowPatch

plt.rcParams.update({'font.family':'STIXGeneral', 'mathtext.fontset':'stix',
                     'font.size':9, 'pdf.fonttype':42, 'ps.fonttype':42,
                     'text.usetex':False, 'axes.unicode_minus':False})
CM = 1 / 2.54

class Drawing:
    def __init__(self, bounds):
        x0,y0,x1,y1 = bounds
        self.fig = plt.figure(figsize=((x1-x0)*CM,(y1-y0)*CM))
        self.ax = self.fig.add_axes([0,0,1,1], xlim=(x0,x1), ylim=(y0,y1))
        self.ax.set_aspect('equal'); self.ax.axis('off')
        self.nodes = {}
        self.labels = []

    def text(self,x,y,label,size=9,ha='center',va='center'):
        artist=self.ax.text(x,y,label,fontsize=size,ha=ha,va=va,
                            linespacing=1.15,clip_on=False,zorder=4)
        self.labels.append([artist,None])
        return artist

    def box(self,name,x,y,w,h,label,dashed=False,shape='rect',size=9):
        style = {'edgecolor':'black','facecolor':'white','linewidth':.55,
                 'linestyle':(0,(4,3)) if dashed else 'solid', 'zorder':2}
        if shape == 'diamond':
            obj = Polygon([(x-w/2,y),(x,y+h/2),(x+w/2,y),(x,y-h/2)],**style)
        elif shape == 'circle': obj = Circle((x,y),w/2,**style)
        else: obj = Rectangle((x-w/2,y-h/2),w,h,**style)
        self.ax.add_patch(obj); self.text(x,y,label,size)
        self.labels[-1][1]=(x-w/2,y-h/2,x+w/2,y+h/2)
        self.nodes[name] = (x,y,w,h,shape)

    def point(self,name,side):
        x,y,w,h,_ = self.nodes[name]
        return {'n':(x,y+h/2),'s':(x,y-h/2),'e':(x+w/2,y),
                'w':(x-w/2,y),'nw':(x-w/2,y+h/2),
                'ne':(x+w/2,y+h/2),'c':(x,y)}[side]

    def line(self,points,dashed=False):
        xs,ys=zip(*points)
        self.ax.plot(xs,ys,color='black',linewidth=.55,
                     linestyle=(0,(4,3)) if dashed else 'solid',zorder=1)

    def arrow(self,p,q,dashed=False,via=()):
        points=[p,*via,q]
        if via:self.line(points[:-1],dashed)
        self.ax.add_patch(FancyArrowPatch(points[-2],points[-1],
                         arrowstyle='-|>',mutation_scale=7.5,linewidth=.55,
                         color='black',shrinkA=0,shrinkB=0,
                         linestyle=(0,(4,3)) if dashed else 'solid',zorder=1))

    def edge(self,a,b,sa='s',sb='n',**kwargs):
        self.arrow(self.point(a,sa),self.point(b,sb),**kwargs)

    def frame(self,x,y,w,h):
        self.ax.add_patch(Rectangle((x,y),w,h,fill=False,edgecolor='black',
                                   linewidth=.55,linestyle=(0,(4,3)),zorder=0))

    def save(self,out,name):
        # Fixed physical canvas: do not enlarge or rasterize the scientific figure.
        self.fig.canvas.draw()
        renderer=self.fig.canvas.get_renderer()
        x0,x1=self.ax.get_xlim();y0,y1=self.ax.get_ylim()
        for artist,node in self.labels:
            b=artist.get_window_extent(renderer).transformed(self.ax.transData.inverted())
            if b.x0<x0-.02 or b.x1>x1+.02 or b.y0<y0-.02 or b.y1>y1+.02:
                raise ValueError(name+': clipped label '+repr(artist.get_text()))
            if node and (b.x0<node[0]-.02 or b.x1>node[2]+.02 or b.y0<node[1]-.02 or b.y1>node[3]+.02):
                raise ValueError(name+': label exceeds node '+repr(artist.get_text()))
        self.fig.savefig(out/(name+'.pdf'),format='pdf',
                         metadata={'Creator':'Python Matplotlib','Producer':None,
                                   'CreationDate':None,'ModDate':None})
        plt.close(self.fig)


def epoch(out):
    d=Drawing((0,0,8.8,3.95))
    for y,label in [(3.0,'Origin $o$'),(2.0,'Early $r$'),(1.0,'Late $r$')]:
        d.arrow((1.6,y),(8.5,y));d.text(1.35,y,label,8.2,ha='right')
    for t in range(5):d.text(1.6+1.5*t,.61,str(t),8)
    d.ax.plot([1.6],[3.0],'ko',markersize=3)
    d.arrow((1.6,3.0),(3.1,2.0))
    d.arrow((1.6,3.0),(4.6,1.0),dashed=True)
    d.text(2.95,2.75,'$g=0$',8.5)
    for y in (1.0,2.0):
        d.line([(4.48,y-.15),(4.72,y+.15)])
        d.line([(4.48,y+.15),(4.72,y-.15)])
    d.text(6.05,2.22,'Query: $-1$',8.5)
    d.text(6.05,1.22,'Query: $0$',8.5)
    d.text(5.6,3.55,r'$d\in\{1,2\}$',8.5)
    d.text(4.4,.17,r'$\times$: reset before arrivals; query after arrivals',8)
    d.save(out,'epoch')


def gadget(out):
    d=Drawing((0,-.3,8.9,4.7))
    ys=[3.3,2.4,1.5,.6]
    for y,label in zip(ys,[r'$x_e$',r'$r_u$',r'$r_v$',r'$z$']):
        d.arrow((1.35,y),(8.6,y));d.text(1.05,y,label,8.5,ha='right')
    def x(t):return 1.5+1.05*t
    for t in range(7):d.text(x(t),.32,str(t),8)
    d.arrow((x(1),3.3),(x(3),2.4));d.text(2.75,2.76,'Send 1',7.8)
    d.arrow((x(2),3.3),(x(3),1.5));d.text(5.05,1.98,'Send 2',7.8)
    d.arrow((x(5),2.4),(x(6),.6));d.arrow((x(5),1.5),(x(6),.6))
    d.line([(x(2)-.12,3.15),(x(2)+.12,3.45)])
    d.line([(x(2)-.12,3.45),(x(2)+.12,3.15)])
    for y in (2.4,1.5):d.frame(x(4)-.16,y-.16,.32,.32)
    d.ax.plot([x(6)],[.6],'ko',markersize=3)
    d.text(4.6,4.17,'Origin packet: send 0, arrive 1 or 2',8.5)
    d.text(4.5,-.05,r'$\times$: mandatory reset; dashed box: optional reset',7.8)
    d.save(out,'gadget')


def numerical(out, previews=False):
    import csv
    root=Path(__file__).resolve().parent.parent/'results'/'derived'
    plt.rcParams.update({'font.size':8,'axes.labelsize':8,'xtick.labelsize':8,
                         'ytick.labelsize':8,'legend.fontsize':8,
                         'axes.linewidth':.6,'lines.linewidth':.8,
                         'lines.markersize':4,'axes.spines.top':False,
                         'axes.spines.right':False})
    with (root/'phase-slice.csv').open(encoding='utf-8-sig',newline='') as f:
        rows=list(csv.DictReader(f))
    fig,ax=plt.subplots(figsize=(3.48,2.0),layout='constrained')
    for key,label,marker,style in [('synchronous','Synchronous','o','-'),
                                  ('optimized','Optimized, equal rate','s','--')]:
        ax.plot([float(r['W']) for r in rows],[float(r[key]) for r in rows],
                color='black',marker=marker,ls=style,label=label,
                markerfacecolor='black' if key=='synchronous' else 'white')
    ax.set(xlabel='Rolling window $W$ (slots)',ylabel='Exact age bound (slots)',
           xlim=(1.7,8.3),ylim=(3.5,5.7),xticks=list(range(2,9)),yticks=[4,5])
    ax.legend(loc='lower center',bbox_to_anchor=(.5,1.01),ncol=2,
              frameon=False,handlelength=2,columnspacing=.9)
    ax.grid(alpha=.2,lw=.4)
    fig.savefig(out/'phases.pdf',metadata={'Creator':'Python Matplotlib',
                'Producer':None,'CreationDate':None,'ModDate':None})
    if previews:
        fig.savefig(out/'phases.png',dpi=600)
        fig.savefig(out/'phases.svg',metadata={'Date':None})
    plt.close(fig)
    with (root/'scaling-events.csv').open(encoding='utf-8-sig',newline='') as f:
        rows=list(csv.DictReader(f))
    fig,ax=plt.subplots(figsize=(3.48,2.25),layout='constrained')
    for prefix,label,marker,style in [('producer','Producer','o','-'),
                                    ('verifier','Positive verifier','s','--')]:
        errors=[[float(r[prefix+'_cpu_error_'+side]) for r in rows]
                for side in ('minus','plus')]
        if any(x<0 for e in errors for x in e):raise ValueError('Negative error bar')
        ax.errorbar([float(r['m']) for r in rows],
                    [float(r[prefix+'_cpu_median_ms']) for r in rows],
                    yerr=errors,color='black',marker=marker,ls=style,
                    capsize=2,elinewidth=.6,label=label)
    ax.set_xscale('log',base=2);ax.set_yscale('log');ax.set_ylim(.15,250)
    ax.set_xticks([256,1024,4096,8192],labels=['256','1024','4096','8192'])
    ax.set(xlabel='Scheduled messages $m$',ylabel='CPU time (ms)')
    ax.legend(loc='lower center',bbox_to_anchor=(.5,1.01),ncol=2,
              frameon=False,handlelength=2,columnspacing=.9)
    ax.grid(alpha=.2,lw=.4)
    fig.savefig(out/'scaling.pdf',metadata={'Creator':'Python Matplotlib',
                'Producer':None,'CreationDate':None,'ModDate':None})
    if previews:
        fig.savefig(out/'scaling.png',dpi=600)
        fig.savefig(out/'scaling.svg',metadata={'Date':None})
    plt.close(fig)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,default=Path(__file__).resolve().parent)
    parser.add_argument('--preview-exports',action='store_true',help='Also update PNG/SVG numeric previews')
    a=parser.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    epoch(a.output);gadget(a.output);numerical(a.output,a.preview_exports)
