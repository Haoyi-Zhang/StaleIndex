"""Verify all consumed figures against fresh direct-Python generation."""
from pathlib import Path
import subprocess
import sys
import tempfile
HERE=Path(__file__).resolve().parent
if __name__=='__main__':
    with tempfile.TemporaryDirectory(prefix='staleness-figures-') as tmp:
        out=Path(tmp)
        subprocess.run([sys.executable,'-B',str(HERE/'draw_figures.py'),
                        '--output',str(out)],check=True,timeout=60)
        for name in ('epoch','gadget','scaling','phases'):
            if (out/(name+'.pdf')).read_bytes() != (HERE/(name+'.pdf')).read_bytes():
                raise RuntimeError('Stale or nondeterministic figure: '+name)
    print('Four consumed vector figures regenerate exactly from retained inputs.')
