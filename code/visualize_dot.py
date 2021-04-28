from logging import info, error
from subprocess import Popen, PIPE

def run_graphviz(s, layout_engine='dot'):
    """Execute dot with a layout and return a raw SVG image, or None."""
    cmd = ['dot', '-Tsvg', '-K', layout_engine]

    dot = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    stdoutdata, stderrdata = dot.communicate(s.encode('utf-8'))
    status = dot.wait()
    if status == 0:
        return stdoutdata
    else:
        fstr = "dot returned {}\n[==== stderr ====]\n{}"
        error(fstr.format(status, stderrdata.decode('utf-8')))
        return None