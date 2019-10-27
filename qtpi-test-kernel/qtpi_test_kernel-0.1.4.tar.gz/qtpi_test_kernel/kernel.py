from ipykernel.kernelbase import Kernel
import subprocess

class QtpiTestKernel(Kernel):
    implementation = 'Qtpi'
    implementation_version = '1.0'
    language = 'qtpi'
    language_version = '1.0'
    language_info = {
        'name': 'Any text',
        'mimetype': 'text/plain',
        'file_extension': '.txt',
    }
    banner = "Qtpi Test kernel - Enables user to input qtpi syntax and run the quantum processes."

    def do_execute(self, code, silent, store_history=True, user_expressions=None,
                   allow_stdin=False):
        if not silent:
            with open("input.py","w") as f:
                f.write(code)
                f.close()
            with open("input.qtp","w") as a:
                a.write(code)
                a.close()
            cp = subprocess.Popen(["qtpi/Qtpi", "input.qtp"], stdout=subprocess.PIPE, stderr=subprocess.PIPE,)
            stdout_value, stderr_value = cp.communicate()
            stdOutput = repr(stdout_value)
            stdError = repr(stderr_value)
            fulloutput = stdOutput + "\n" + stdError
            exactOutput = fulloutput[2:-5]
            splitedOutput = exactOutput.split("\\n")
            s = ""
            for item in splitedOutput:
                   s += "\n" + item
            with open("output.qtp","w") as ou:
                ou.write(s)
                ou.close()
            # cp = subprocess.run(["/home/miroslav/qtpi/Qtpi", "output.qtp"], universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # if cp.stdout != "":
            # output = cp.stdout
            # else:
            # output = cp.stderr
            stream_content = {'name': 'stdout', 'text': s}
            self.send_response(self.iopub_socket, 'stream', stream_content)
            
        return {'status': 'ok',
                # The base class increments the execution count
                'execution_count': self.execution_count,
                'payload': [],
                'user_expressions': {},
               }
