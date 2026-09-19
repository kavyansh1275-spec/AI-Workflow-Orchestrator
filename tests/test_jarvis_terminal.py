from core.jarvis_terminal import JarvisTerminal
def test_terminal_runs_real_python(tmp_path):
    output=[]
    code=JarvisTerminal(tmp_path).run(["python","-c","print('jarvis-terminal-ok')"],emit=lambda e:output.append(e.line),timeout=30)
    assert code==0 and "jarvis-terminal-ok" in output
