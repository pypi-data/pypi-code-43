import pandas as pd
import numpy as np

def dist_frequenza(matrice, colonna, save=False, tipo="categoriale", lista_ordinale=False):
    '''
    matrice: passare un dataframe di pandas
    colonna: indicare la colonna su cui effettuare la distribuzione di frequenza
    save: [False oppure nome del file] scegli se salvare o meno la tabella in excel
    tipo:
        "categoriale": classi non ordinate
        "ordinale": classi ordinate
        "cardinale": valori numerici
    lista_ordinale: una lista di valori attraverso il cui ordinare il risultato del tipo ordinale
    '''

    frequenza = matrice[colonna].value_counts(dropna=False)
    percentuale = matrice[colonna].value_counts(normalize=True, dropna=False) * 100
    distribuzione = pd.concat([frequenza, percentuale], axis=1)
    distribuzione.columns = ["Frequenze", "Percentuale"]
    if tipo == "categoriale":
        pass
    elif tipo == "ordinale":
        try:
            distribuzione = distribuzione.reindex(lista_ordinale)
            distribuzione = distribuzione.fillna(0)
            distribuzione["Cumulata"] = distribuzione["Percentuale"].cumsum()

            # distribuzione["cumsum"] = distribuzione[colonna].cumsum()
        except:
            try:
                distribuzione = distribuzione.loc[lista_ordinale]
                distribuzione = distribuzione.fillna(0)
                distribuzione["Cumulata"] = distribuzione["Percentuale"].cumsum()

            except:
                print("errore, non corrispondenza con le categorie")


    elif tipo == "cardinale":
        distribuzione.sort_index(inplace=True)

        try:
            distribuzione["Cumulata"] = distribuzione["Percentuale"].cumsum()

        except:
            print("errore nella rimozione dell'incrocio Totale - Cumulata")

    distribuzione.loc["Totale"] = distribuzione.apply(sum)

    distribuzione["Percentuale"] = distribuzione["Percentuale"].round(2)
    try:
        # distribuzione["Cumulata"] = distribuzione["Cumulata"].round(2)
        if tipo == "cardinale" or tipo == "ordinale":
            distribuzione.loc["Totale", "Cumulata"] = ""
    except:
        pass

    if save == False:
        return distribuzione
    else:
        distribuzione.to_excel(str(save) + ".xlsx")
        return distribuzione


def estrai_valore(cella):
    try:
        return int(cella[0])
    except:
        return cella

def plot_dist_frequenza(distribuzione, tipo="categoriale", Y="Percentuale", x_label="Valori", y_label="Percentuale",
                        figsize=(12, 8), missing=None):
    '''
    distribuzione: inserire risultato della funzione dist_frequenza
    tipo:
        "categoriale": classi non ordinate
        "ordinale": classi ordinate
        "cardinale": valori numerici
    x_label: etichetta asse x
    y_label: etichetta_asse y
    '''
    import matplotlib.pyplot as plt
    import seaborn as sns
    if tipo == "categoriale":
        p_color = 'muted'
    elif tipo == "ordinale":
        p_color = "Blues_d"
    elif tipo == "cardinale":
        p_color = "Blues_d"
        print("------------------------------------------------------------------------------")
        print(
            "si consiglia di utilizzare una diversa visualizzazione: cerca sul motore di ricerca sns.distplot ed applicalo sulla matrice dati originaria ")
        print("------------------------------------------------------------------------------")
    distribuzione = distribuzione.iloc[:-1, :]

    if missing != None:
        distribuzione = distribuzione.drop(missing)

    fig, ax = plt.subplots(figsize=figsize)
    x = 0

    # distribuzione.index = distribuzione.index.map(lambda x: str(x))
    g = sns.barplot(x=distribuzione.index, y=Y, data=distribuzione, ax=ax, palette=p_color, order=distribuzione.index)
    for index, row in distribuzione.iterrows():
        stringa = "N.{},\n {}%".format(row.Frequenze, row.Percentuale)
        g.text(x, row[Y] - row[Y] * 0.50, stringa, color="black", ha="center")
        x = x + 1
    g.set_xticklabels(g.get_xticklabels(), rotation=90)
    g.set(xlabel=x_label, ylabel=y_label)
    return g


def recode_da_dizionario(x, dizionario, nan=False, totale=True):
    '''
    da applicare ad un vettore o ad una matrice dati tramite la funzione map, applymap
    x: il valore da ricodificare
    dizionario: il dizionario da cui estrarre i valori di recodifica E.G.
                              {1: "sinistra",
                              2: "centro sinistra",
                              3: "centro",
                              4: "centro destra",
                              5: "destra"}
    nan: True, ricodifica i valori non presenti dentro il dizionario in nan
    totale: se True non ricodifica la modalità "Totale" generata automaticamente da dist_frequenza in nan

    '''
    try:
        return dizionario[x]
    except:
        if x == "Totale" and totale == True:
            return x
        elif nan == True:
            return np.nan
        else:
            return x


def Sq(series):
    series = series
    prob = series / series.sum()
    return ((prob*prob).sum(),  '{:.3f}'.format((prob*prob).sum()))

def Sq_norm(series):
    #prob = series / series.sum()
    series = series
    k=len(series)
    sq_x = Sq(series)[0]
    return ((sq_x-(1/k)) / (1-(1/k)), '{:.3f}'.format((sq_x-(1/k)) / (1-(1/k))))

def Eq(series):
    series = series
    sq_norm_x = Sq_norm(series)
    return ((1-sq_norm_x[0]), '{:.3f}'.format((1-sq_norm_x[0])))

def Sq_output(series):
    return {"Eq": Eq(series),
           "Sq": Sq(series),
           "Sq_Norm": Sq_norm(series)}

def gini(array):
    """Calculate the Gini coefficient of a numpy array."""
    # based on bottom eq: http://www.statsdirect.com/help/content/image/stat0206_wmf.gif
    # from: http://www.statsdirect.com/help/default.htm#nonparametric_methods/gini.htm
    array = array.flatten() #all values are treated equally, arrays must be 1d
    if np.amin(array) < 0:
        array -= np.amin(array) #values cannot be negative
    array += 0.0000001 #values cannot be 0
    array = np.sort(array) #values must be sorted
    index = np.arange(1,array.shape[0]+1) #index per array element
    n = array.shape[0]#number of array elements
    return ((np.sum((2 * index - n  - 1) * array)) / (n * np.sum(array))) #Gini coefficient