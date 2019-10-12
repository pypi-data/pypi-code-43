import sys
import os
import re
# import argparse


def main():
    fichier_input_java = sys.argv[1]
    fichier_output_py = os.path.basename(fichier_input_java)[:-5] + ".py"
    parse(fichier_input_java, fichier_output_py)
    # TODO : os.system("black " + fichier_output_py)


def camel_case_to_snake_case(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def supprimer_types(instruc):
    return instruc.replace("int ", "").replace("double ", "").replace("float ", "").replace("boolean ", "")\
        .replace("short ", "").replace("long ", "").replace("byte ", "").replace("String ", "")


def traiter_methode(methode):
    contenu = ""

    for instruction in methode:

        # Suppression des tabulations, point-virgules
        instruction = instruction.strip("\t\n ").replace(";", "")

        # Traitement des commentaires
        instruction = traiter_commentaires(instruction)

        # Traitement des sysout
        instruction = instruction.replace("System.out.println", "print")

        # Remplacement de 'this' par 'self'
        instruction = instruction.replace("this", "self")
        # TODO : ajouter 'self' si on fait référence à un attribut sans le 'this'

        # Si c'est une condition (if uniquement)
        if instruction.startswith(("if", "else if", "else")):
            instruction = traiter_condition(instruction)

        # Si c'est une boucle while
        elif instruction.startswith("while"):
            instruction = traiter_boucle_while(instruction)

        # Si c'est une boucle for
        elif instruction.startswith("for"):
            instruction = traiter_boucle_for(instruction)

        # Suppression des accolades qui restent
        instruction = instruction.strip("}")

        # TODO : ne pas remplacer les majuscules dans les chaines de caractères et commentaires
        contenu += "        " + camel_case_to_snake_case(supprimer_types(instruction))
        contenu += "\n"

    return contenu


def traiter_condition(condition):

    # Traitement du else if
    condition = condition.replace("else if", "elif")

    # Traitement des parenthèses et accolades
    condition = condition.replace("(", " ").replace(")", "").replace("{", ":")

    # Traitement des opérateurs
    condition = condition.replace("&&", "and").replace("||", "or").replace("!", "not ")

    return condition


def traiter_boucle_while(boucle_while):
    return boucle_while


def traiter_boucle_for(boucle_for):
    return boucle_for


def traiter_commentaires(instruc):
    nouvo = instruc.replace("//", "#").replace("/**", '"""').replace("/*", '"""').replace("*/", '"""')
    print(nouvo)
    return nouvo


def parse(fichier_input, fichier_output):

    nom_de_la_classe = ""
    classe_mere = None
    attributs = []
    attributs_de_classe = {}
    constructeurs = []
    methodes = []
    params_methodes = {}
    corps_methodes = {}
    methodes_statiques = []

    with open(fichier_input, 'r') as fichier:

        lignes_du_fichier_java = fichier.readlines()
        iterateur = iter(lignes_du_fichier_java)
        nb_total_lignes = len(lignes_du_fichier_java)
        print(nb_total_lignes)
        i = 0

        while i < nb_total_lignes:

            ligne = next(iterateur)

            ligne = ligne.strip("\n\r\t ")

            # TODO : traitement des commentaires Javadoc

            # Détermination du nom de la classe
            if ligne.startswith("public class"):
                print("Nom de la classe :", ligne.split()[2])
                nom_de_la_classe = ligne.split()[2]

                # Détermination de la classe mère
                if "extends" in ligne:
                    print("Nom de la classe mère :", ligne.split()[4])
                    classe_mere = ligne.split()[4]

            # Détermination des attributs
            elif ligne.startswith(("public", "private", "protected")) and ligne.endswith(";"):

                # Détermination des attributs de classe
                if "static" in ligne:
                    print("Attribut de classe :", ligne.split()[3],
                          ", valeur :", ligne.replace(" ", "").strip(";").split("=")[1])
                    attributs_de_classe[ligne.split()[3]] = ligne.replace(" ", "").strip(";").split("=")[1]
                else:
                    print("Attribut :", ligne.split()[2].strip(";"))
                    attributs.append(ligne.split()[2].strip(";"))

            # Détermination des constructeurs
            elif ligne.startswith(("public " + nom_de_la_classe,
                                   "private " + nom_de_la_classe,
                                   "protected " + nom_de_la_classe)) and ligne.endswith(" {"):
                print("Constructeur")

            # Détermination des méthodes
            elif ligne.startswith(("public", "private", "protected")) and ligne.endswith(" {"):

                # Détermination des méthodes statiques
                if "static" in ligne:
                    print("Méthode de classe :", ligne.split()[3].split("(")[0])
                    nom_methode = ligne.split()[3].split("(")[0]
                    methodes_statiques.append(ligne.split()[3].split("(")[0])
                else:
                    print("Méthode :", ligne.split()[2].split("(")[0])
                    nom_methode = ligne.split()[2].split("(")[0]

                    # On ajoute pas les getters et setters
                    if not nom_methode.startswith(("get", "set")):
                        methodes.append(ligne.split()[2].split("(")[0])

                # Récupération des paramètres de la méthode
                parametres = [p.strip(",") for p in re.search(r"\(.*\)", ligne).group(0).strip("()").split(" ")][1::2]
                print("Paramètres de", nom_methode, ":", parametres)

                # On ajoute que les méthodes qui ont des paramètres
                if not len(parametres) == 0:
                    params_methodes[nom_methode] = parametres

                # Récupération du corps de la méthode
                # Mise en place d'un compteur d'accolades pour déterminer la fin de la fonction
                accolades = 1

                # Création de l'entrée correspondante dans le dictionnaire de corps de méthodes
                corps_methodes[nom_methode] = []

                while accolades > 0:
                    # Récupération de la ligne suivante
                    ligne_corps = next(iterateur)
                    i += 1

                    # Ajout de l'instruction dans l'entrée correspondante dans le dictionnaire de corps de méthodes
                    corps_methodes[nom_methode].append(ligne_corps)

                    # Calcul d'accolades
                    accolades += ligne_corps.count('{')
                    accolades -= ligne_corps.count('}')

            i += 1

    print(corps_methodes)

    # Suppression des surcharges de méthodes
    methodes = list(set(methodes))
    methodes_statiques = list(set(methodes_statiques))

    # Ecriture du fichier Python
    with open(fichier_output.lower(), 'w') as fichier:

        # Ecriture de l'en-tête de la classe
        fichier.write("class " + nom_de_la_classe)

        # Ecriture de la classe mère si elle existe
        if classe_mere is not None:
            fichier.write("(" + classe_mere + ")")

        # Sauts de ligne et indentation
        fichier.write(":")
        fichier.write("\n\n")
        fichier.write("    ")

        # Ecriture des attributs de classe
        for attr, val in attributs_de_classe.items():
            fichier.write(camel_case_to_snake_case(attr) + " = " + val)

        # Ecriture du constructeur
        fichier.write("def __init__(self")

        if len(attributs) > 0:
            fichier.write(", ")
            fichier.write(', '.join([camel_case_to_snake_case(a) for a in attributs]))

        fichier.write("):")

        # Ecriture des attributs dans le constructeur
        for attr in attributs:
            # Sauts de ligne et tabulation
            fichier.write("\n")
            fichier.write("        ")
            fichier.write("self." + camel_case_to_snake_case(attr) + " = " + camel_case_to_snake_case(attr))

        # Sauts de ligne et indentation
        fichier.write("\n\n")
        fichier.write("    ")

        # Ecriture des méthodes
        for meth in methodes:

            # Gestion du cas de toString
            if meth == "toString":
                fichier.write("def __str__(self")
            else:
                fichier.write("def " + camel_case_to_snake_case(meth) + "(self")

            # Ecriture des paramètres de la méthode
            if meth in params_methodes:
                fichier.write(", ")
                fichier.write(', '.join([camel_case_to_snake_case(p) for p in params_methodes[meth]]))

            fichier.write("):")

            # Ecriture du code de la méthode
            # TODO : traitement
            fichier.write("\n")

            contenu_methode = traiter_methode(corps_methodes[meth])
            fichier.write(contenu_methode)

            fichier.write("\n\n")
            fichier.write("    ")

        # Ecriture des méthodes statiques
        for meth in methodes_statiques:
            fichier.write("@staticmethod")
            fichier.write("\n")
            fichier.write("    ")
            fichier.write("def " + camel_case_to_snake_case(meth) + "(")

            # Ecriture des paramètres de la méthode
            if meth in params_methodes:
                fichier.write(', '.join([camel_case_to_snake_case(p) for p in params_methodes[meth]]))

            fichier.write("):")

            # Ecriture du code de la méthode statique
            # TODO : traitement
            fichier.write("\n")

            contenu_methode = traiter_methode(corps_methodes[meth])
            fichier.write(contenu_methode)

            fichier.write("\n\n")
            fichier.write("    ")


if __name__ == '__main__':
    main()
