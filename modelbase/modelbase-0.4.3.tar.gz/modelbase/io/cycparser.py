import pandas as pd


class Cyc:
    """Class to parse x-cyc database files, like MetaCyc or LycoCyc.
    As a convenience function, all reactions in which a compound is
    present are automatically mapped to the compounds.
    Notes:
        Only the first type of a reaction is parsed.
        For compounds in reactions of the format |Pi| the vertical bars are
        removed.
    """

    def __init__(self, datapath, exclude_files=None):
        """Read in the x-cyc.
        datapath is x-cyc/version/data/"""
        self._datapath = datapath

        if not exclude_files:
            exclude_files = []

        if "genes" not in exclude_files:
            self.genes = self._parse_genes()
        if "enzrxns" not in exclude_files:
            self.enyzmes_to_reactions = self._parse_enzymes_to_reactions()
        if "reactions" not in exclude_files:
            self.reactions = self._parse_reactions()
        if "compounds" not in exclude_files:
            self.compounds = self._parse_compounds()
        if "compound_classes" not in exclude_files:
            self.compound_classes = self._parse_compound_classes()
        if "proteins" not in exclude_files:
            self.proteins = self._parse_proteins()

        # Map reactions to compounds
        self._map_reactions_to_compounds()

        # Fill up InChi formula column, then remove formula column
        # self._fill_up_inchi_formula()

    @staticmethod
    def _read_file_and_remove_comments(filepath, encoding="cp1252"):
        file = open(filepath, "r", encoding=encoding).readlines()
        # Remove top comment lines
        for i, line in enumerate(file):
            if line.startswith("UNIQUE-ID"):
                break
        return file[i:]

    @staticmethod
    def _repair_compound_str(s):
        """ Takes a string of the form "(H 4), (C 6), (N 4)"
            to the form "C6H4N4"
        """
        s = s.replace("(", "").replace(")", "").split(", ")
        s = sorted(s, key=lambda x: x[0])
        s = [i.split(" ") for i in s]
        s = "".join(["".join(i) for i in s])
        return s

    def _parse_genes(self):
        filepath = self._datapath + "genes.dat"
        file = self._read_file_and_remove_comments(filepath)

        cyc_genes = {}
        for line in file:
            try:
                identifier, content = line.strip().split(" - ")
            except ValueError:  # line = //
                continue

            if identifier == "UNIQUE-ID":
                ID = content
                cyc_genes[ID] = {"Name": None, "Product": None}
            elif identifier == "COMMON-NAME":
                cyc_genes[ID]["Name"] = content
            elif identifier == "PRODUCT":
                cyc_genes[ID]["Product"] = content
        return pd.DataFrame(cyc_genes).T

    def _parse_enzymes_to_reactions(self):
        filepath = self._datapath + "enzrxns.dat"
        file = self._read_file_and_remove_comments(filepath)

        cyc_gene_product_to_reaction = {}
        for line in file:
            try:
                identifier, content = line.strip().split(" - ")
            except ValueError:  # line = //
                continue

            if identifier == "UNIQUE-ID":
                ID = content
                cyc_gene_product_to_reaction[ID] = {"Enzyme": None, "Reactions": None}

            elif identifier == "ENZYME":
                cyc_gene_product_to_reaction[ID]["Enzyme"] = content

            elif identifier == "REACTION":
                cyc_gene_product_to_reaction[ID]["Reactions"] = content

        return pd.DataFrame(cyc_gene_product_to_reaction).T

    def _parse_reactions(self):
        filepath = self._datapath + "reactions.dat"
        file = self._read_file_and_remove_comments(filepath)

        cyc_reactions = {}
        for i, line in enumerate(file):
            try:
                identifier, content = line.strip().split(" - ")
            except ValueError:  # line = //
                continue

            if identifier == "UNIQUE-ID":
                ID = content
                cyc_reactions[ID] = {
                    "CANNOT-BALANCE": False,
                    "COMMON-NAME": None,
                    "DIRECTION": None,
                    "EC-NUMBER": None,
                    "ENZYMATIC-REACTION": None,
                    "TYPES": None,
                    "ORPHAN": False,
                    "LEFT": None,
                    "LEFT-COEF": None,
                    "RIGHT": None,
                    "RIGHT-COEF": None,
                    "RXN-LOCATIONS": None,
                }

            elif identifier == "CANNOT-BALANCE":
                cyc_reactions[ID]["CANNOT-BALANCE"] = content

            elif identifier == "COMMON-NAME":
                cyc_reactions[ID]["COMMON-NAME"] = content

            elif identifier == "REACTION-DIRECTION":
                cyc_reactions[ID]["DIRECTION"] = content

            elif identifier == "EC-NUMBER":
                cyc_reactions[ID]["EC-NUMBER"] = content

            elif identifier == "ENZYMATIC-REACTION":
                #  Should I change this into a list as well?
                if not cyc_reactions[ID]["ENZYMATIC-REACTION"]:
                    cyc_reactions[ID]["ENZYMATIC-REACTION"] = content
                else:
                    cyc_reactions[ID]["ENZYMATIC-REACTION"] += ", " + content

            elif identifier == "TYPES":
                if not cyc_reactions[ID]["TYPES"]:
                    cyc_reactions[ID]["TYPES"] = content
                else:  # Only take the first type
                    pass

            elif identifier == "ORPHAN?":
                if content == ":NO":
                    cyc_reactions[ID]["ORPHAN"] = False
                else:
                    cyc_reactions[ID]["ORPHAN"] = True

            elif identifier == "LEFT":
                cpd = [content][0]
                if cpd.startswith("|"):
                    cpd = cpd[1:-1]
                if not cyc_reactions[ID]["LEFT"]:
                    cyc_reactions[ID]["LEFT"] = [cpd]
                    cyc_reactions[ID]["LEFT-COEF"] = {cpd: 1}
                else:
                    cyc_reactions[ID]["LEFT"].append(cpd)
                    cyc_reactions[ID]["LEFT-COEF"].update({cpd: 1})

            elif identifier == "RIGHT":
                cpd = [content][0]
                if cpd.startswith("|"):
                    cpd = cpd[1:-1]
                if not cyc_reactions[ID]["RIGHT"]:
                    cyc_reactions[ID]["RIGHT"] = [cpd]
                    cyc_reactions[ID]["RIGHT-COEF"] = {cpd: 1}
                else:
                    cyc_reactions[ID]["RIGHT"].append(cpd)
                    cyc_reactions[ID]["RIGHT-COEF"].update({cpd: 1})

            elif identifier == "^COEFFICIENT":
                if file[i - 1].startswith("LEFT"):
                    # Take last compound
                    cpd = cyc_reactions[ID]["LEFT"][-1]
                    try:
                        cyc_reactions[ID]["LEFT-COEF"][cpd] = int(content)
                    except ValueError:
                        #######################################################
                        # Is this a good idea?
                        #######################################################
                        cyc_reactions[ID]["LEFT-COEF"][cpd] = None

                elif file[i - 1].startswith("RIGHT"):
                    # Take last compound
                    cpd = cyc_reactions[ID]["RIGHT"][-1]
                    try:
                        cyc_reactions[ID]["RIGHT-COEF"][cpd] = int(content)
                    except ValueError:
                        #######################################################
                        # Is this a good idea?
                        #######################################################
                        cyc_reactions[ID]["LEFT-COEF"][cpd] = None
                else:
                    print("Neither left nor right: ", line)

            elif identifier == "RXN-LOCATIONS":
                cyc_reactions[ID]["RXN-LOCATIONS"] = content

        return pd.DataFrame(cyc_reactions).T

    def _parse_compounds(self):
        filepath = self._datapath + "compounds.dat"
        file = self._read_file_and_remove_comments(filepath)
        cyc_compounds = {}

        for line in file:
            try:
                identifier, content = line.strip().split(" - ")
            except ValueError:  # line = //
                continue

            if identifier == "UNIQUE-ID":
                ID = content
                cyc_compounds[ID] = {
                    "CHEMICAL-FORMULA": None,
                    "COMMON-NAME": None,
                    "INCHI": None,
                    "MASS": None,
                    "SMILES": None,
                }

            elif identifier == "CHEMICAL-FORMULA":
                if not cyc_compounds[ID]["CHEMICAL-FORMULA"]:
                    cyc_compounds[ID]["CHEMICAL-FORMULA"] = content
                else:
                    cyc_compounds[ID]["CHEMICAL-FORMULA"] += ", " + content

            elif identifier == "COMMON-NAME":
                cyc_compounds[ID]["COMMON-NAME"] = content

            elif identifier == "INCHI":
                cyc_compounds[ID]["INCHI"] = content

                # INCHI_string = content
                # cyc_compounds[ID]['INCHI'] = INCHI_string

                # INCHI_string = INCHI_string.split('/')
                # try:
                #     cyc_compounds[ID]['INCHI-FORMULA'] = INCHI_string[1]
                # except IndexError:
                #     cyc_compounds[ID]['INCHI-FORMULA'] = None
                # try:
                #     cyc_compounds[ID]['INCHI-CONNECTIONS'] = INCHI_string[2]
                # except IndexError:
                #     cyc_compounds[ID]['INCHI-CONNECTIONS'] = None

            elif identifier == "MOLECULAR-WEIGHT":
                cyc_compounds[ID]["MASS"] = content

            elif identifier == "SMILES":
                cyc_compounds[ID]["SMILES"] = content

        return pd.DataFrame(cyc_compounds).T

    def _parse_compound_classes(self):
        filepath = self._datapath + "classes.dat"
        file = self._read_file_and_remove_comments(filepath)
        cyc_classes = {}
        for line in file:
            try:
                identifier, content = line.strip().split(" - ")
            except ValueError:  # line = //
                continue

            if identifier == "UNIQUE-ID":
                ID = content
                cyc_classes[ID] = {"Types": None, "Common-Name": None}
            elif identifier == "TYPES":
                cyc_classes[ID]["Types"] = content

            elif identifier == "COMMON-NAME":
                cyc_classes[ID]["Common-Name"] = content

        return pd.DataFrame(cyc_classes).T

    def _parse_proteins(self):
        filepath = self._datapath + "proteins.dat"
        file = self._read_file_and_remove_comments(filepath)

        cyc_proteins = {}
        for line in file:
            try:
                identifier, content = line.strip().split(" - ")
            except ValueError:  # line = //
                continue

            if identifier == "UNIQUE-ID":
                ID = content
                cyc_proteins[ID] = {"Common-Name": None, "Smiles": None}
            elif identifier == "COMMON-NAME":
                cyc_proteins[ID]["Common-Name"] = content

            elif identifier == "SMILES":
                cyc_proteins[ID]["Smiles"] = content

        return pd.DataFrame(cyc_proteins).T

    def _map_reactions_to_compounds(self):
        cpd_in_rec = pd.Series(None, self.compounds.index)
        for rec, (left, right) in self.reactions.loc[:, ["LEFT", "RIGHT"]].iterrows():
            try:
                for direction in (left, right):
                    for i in direction:
                        try:
                            cpd_in_rec.loc[i].add(rec)
                        except ValueError:  # Check if this was the right kind
                            cpd_in_rec.loc[i] = set([rec])
            except TypeError:  # None if no reactants are present
                continue
        self.compounds["IN-REACTION"] = cpd_in_rec

    def _fill_up_inchi_formula(self):
        # Get NAs
        nas = self.compounds.isna()
        # Filter out those for which nor INCHI formula, but a chemical formula
        # is given
        df_filter = nas["INCHI-FORMULA"] & (~nas["CHEMICAL-FORMULA"])
        cpds = self.compounds[df_filter]
        cpds = cpds["CHEMICAL-FORMULA"].apply(self._repair_compound_str)

        self.compounds.loc[cpds.index, "INCHI-FORMULA"] = cpds
        # Drop chemical formula column
        # self.compounds.drop(columns=['CHEMICAL-FORMULA'], inplace=True)
