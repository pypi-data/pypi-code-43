import pandas as pd
import csv

def detector(string):
    count = 0
    for x in string:
        if x == '%':
            mid = count
        if x == '-':
            back = count
        count=count+1
    organsim_id = string[:mid]
    front_p = string[mid+1:back]
    back_p = string[back+1:]
    print(organsim_id,front_p,back_p)
    return  organsim_id,front_p,back_p

def header(string):
    counter = 0
    for x in string:
        if x == '_':
            point = counter
            break
        counter=counter+1
    name = string[:point]
    return name
def position_output(workingdir, outdir):
    import os 
    file_name_list = os.listdir(workingdir)
    file_name_list_1 = []
    for file_name in file_name_list:
        if 'blast_results' in file_name and file_name[-1] == 'v':
            file_name_list_1.append(file_name)

    csv_list = []
    for file_name in file_name_list_1:
        file_name1 = workingdir + '/' + file_name
        csv_table = pd.read_csv(file_name1)
        csv_column = csv_table['subject id']
        for id_position in csv_column:
            organsim_id,front_p,back_p = detector(id_position)
            name = header(file_name)
            csv_list.append([organsim_id,name,front_p,back_p])
    #reduce_re = []
    #for num in range(len(csv_list)-1):
        #for x in csv_list[num+1:][2]:
            #if csv_list[num][2] == x:
                #reduce_re.append(num) 
    #sorted(reduce_re, reverse=True)
    #for x in reduce_re:
        #del csv_list[x]
    with open(outdir+'/protein_position.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['organism','gene','start','end'])
            for row in csv_list:
                writer.writerow(row)

#position_output()