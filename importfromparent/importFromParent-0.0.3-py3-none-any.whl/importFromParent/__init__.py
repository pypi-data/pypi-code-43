def importFromParent(file: str, extension: str = ''):
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
        import os
        fst_path = os.getcwd()
        file = file; da = file
        filename = file[::-1]
        filename = filename[:filename.find('.')][::-1]
        file = da
        dame = ""
        
        faf = file.replace('..', '__{__b__a__c__k__}__')
        faf = faf.replace('.', '/')
        faf = faf.replace('__{__b__a__c__k__}__', '..')
        if extension == '':
            os.system(f'mkdir "{fst_path}\\__pycache__"')
        else:
            extension = '.' + extension
        os.chdir('..')
        os.chdir(faf[:len(faf)-len(filename)])
        os.system(f'copy /b "{filename}{extension}" "{fst_path}\\__pycache__\\__temp_imported__{extension}"')
        faf = faf.replace('/','.')
        faf = faf[:faf.find('.')]
        from __pycache__ import __temp_imported__
        return __temp_imported__
