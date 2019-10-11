def importFromParent(file: str, extension: str = 'py', file_dir: str = ''):
    import os
    if file_dir != '':
        os.chdir(file_dir)
    no_slash = 0
    for slash in ('\\','/','\\'[0:1]):
        if slash in file:
            def error(err: str):
                print(f'\033[31mERROR: "{err}"!\033[0m');exit()
                pass #as: end
            error('String "file" can not have slashes. Please, use dots instead')
        else:
            no_slash += (1/3)
    fst_path = filename = ""
    if float(no_slash) == 1.0: # if there's no slash in string "file":
        
        fst_path = os.getcwd()
        file = file; da = file
        filename = file[::-1]
        filename = filename[:filename.find('.')][::-1]
        file = da
        dame = ""
        
        faf = file.replace('..', '__{__b__a__c__k__}__')
        faf = faf.replace('.', '/')
        faf = faf.replace('__{__b__a__c__k__}__', '..')
        fm = '__temp_imported__'
        if extension == '':
            os.system(f'start /wait cmd /c mkdir "{fst_path}\\__pycache__\\{fm}"')
        else:
            os.system(f'start /wait cmd /c mkdir "{fst_path}\\__pycache__"')
            extension = '.' + extension
        os.chdir('..')
        os.chdir(faf[:len(faf)-len(filename)])
        os.system(f'start /wait cmd /c copy /b "{filename}{extension}" "{fst_path}\\__pycache__\\{fm}{extension}"')
        faf = faf.replace('/','.')
        faf = faf[:faf.find('.')]
        from __pycache__ import __temp_imported__
        return __temp_imported__

importFromParent.__doc__ = open('iFP_help.txt','r').read()
help(importFromParent)
input('#END')
