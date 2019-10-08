from subprocess import call

def call_editor(editor_cmd, file_path):
    return call([editor_cmd, file_path])
