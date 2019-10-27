# -*- coding: utf-8 -*-
# system libraries

def main():
    # -*- coding: utf-8 -*-
    # system libraries

    import webbrowser

    import os
    import pandas as pd
    from collections import OrderedDict
    # flask libraries
    from flask import Flask, request, render_template, url_for, redirect, send_from_directory
    import flask
    # from flask_bootstrap import Bootstrap
    import json
    from stats_tools import tools
    from stats_tools import table
    import seaborn as sns
    from scipy.cluster.vq import kmeans, vq
    import uuid

    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    from plotting.altarian import altair_monovariate, altair_bivariate
    import pandas_profiling
    import re


    # statistical libraries

    # Accessible Drag and Drop with Multiple Items
    ## https://codepen.io/SitePoint/pen/vEzXbj/

    # flask execution
    APP_ROOT = os.path.dirname(os.path.abspath(__file__))
    ALLOWED_EXTENSIONS = set(["xlsx", "csv"])

    os.chdir(APP_ROOT)
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'gogogogo'

    app.config["CLIENT_IMAGES"] = "./static/images"

    # Bootstrap(app)

    def allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    '''
    flask index
    "/" - index: first page
    "/upload": upload file and return to index  
    "/load": loaded dataset. first 5 lines and options
    "/action": redirect to specific options  
    '/calc': options for calc and recode  
    '/monovariate_plot': output of monovatiate plot  
    '/info': output of calc function 
    '''

    @app.route("/")
    def index():
        files = os.listdir("./static/uploads/")

        return render_template("index.html", files=files, upload="initial")

    @app.route('/upload_file', methods=['GET', 'POST'])
    def upload_file():

        if request.method == 'POST':
            f = request.files['file']
            if allowed_file(f.filename):
                f.save(os.path.join(APP_ROOT, 'static', 'uploads', f.filename))
                files = os.listdir("./static/uploads/")
                return render_template("index.html", files=files, upload="true")
            else:
                return render_template("index.html", files=files, upload="false")

    @app.route('/load', methods=['GET', 'POST'])
    def load():
        g = request
        if g.form["file_config"] == "remove":
            os.remove("./static/uploads/" + g.form["load"])
            files = os.listdir("./static/uploads/")
            return render_template("index.html", files=files, upload="removed")
        else:
            if g.form["file_config"] == "standard_excel":
                flask.session["selected_file"] = g.form["load"]
                dataset = pd.read_excel("./static/uploads/" + g.form["load"])
            elif g.form["file_config"] == "excel_google_form":
                dataset = dataset.applymap(lambda x: tools.google_form_likert(x))
                dataset.to_excel("./static/uploads/" + "__gform__" + g.form["load"])
                flask.session["selected_file"] = "__gform__" + g.form["load"]
            elif g.form["file_config"] == "csv1":
                print(g.form["load"])
                dataset = pd.read_csv("./static/uploads/" + g.form["load"], sep=";")
                print(dataset)
                dataset.to_excel("./static/uploads/" + g.form["load"] + ".xlsx")
                flask.session["selected_file"] = g.form["load"] + ".xlsx"
            elif g.form["file_config"] == "csv2":
                print(g.form["load"])
                dataset = pd.read_csv("./static/uploads/" + g.form["load"], sep=",")
                print(dataset)
                dataset.to_excel("./static/uploads/" + g.form["load"] + ".xlsx")
                flask.session["selected_file"] = g.form["load"] + ".xlsx"
            else:
                pass
            variable_name_type = OrderedDict()
            # variable_name_type.update(dataset.dtypes.to_dict(into=OrderedDict))
            variable_name_type.update(dataset.dtypes.to_dict())
            html_data = dataset.head(500).to_html(table_id="head_data", classes="table table-striped table-bordered display nowrap")

            return render_template("select_action.html",
                                   selected_file=flask.session["selected_file"],
                                   html_data=html_data)


    @app.route('/action', methods=['GET', 'POST'])
    def action():
        g = request


        if g.form["select_action"] == "monovariate":
            dataset = pd.read_excel("./static/uploads/" + flask.session["selected_file"])
            variable_name_type = OrderedDict()
            # variable_name_type.update(dataset.dtypes.to_dict(into=OrderedDict))
            variable_name_type.update(dataset.dtypes.to_dict())

            return render_template("monovariate_selection.html",
                                   variable_name_type=variable_name_type,
                                   dataset=flask.session["selected_file"])
        if g.form["select_action"] == "recode":
            dataset = pd.read_excel("./static/uploads/" + flask.session["selected_file"])
            variable_name_type = OrderedDict()
            # variable_name_type.update(dataset.dtypes.to_dict(into=OrderedDict))
            variable_name_type.update(dataset.dtypes.to_dict())

            return render_template("recode_selection.html",
                                   variable_name_type=variable_name_type,
                                   dataset=flask.session["selected_file"])

        if g.form["select_action"] == "bivariate_and_regression":
            dataset = pd.read_excel("./static/uploads/" + flask.session["selected_file"])
            variable_name_type = OrderedDict()
            # variable_name_type.update(dataset.dtypes.to_dict(into=OrderedDict))


            variable_name_type.update(dataset.loc[:, (dataset.dtypes != "object").values].dtypes.to_dict())
            return render_template("bivariate_selection.html",
                                   variable_name_type=variable_name_type,
                                   dataset=flask.session["selected_file"])

        if g.form["select_action"] == "multi cross tab":
            dataset = pd.read_excel("./static/uploads/" + flask.session["selected_file"])
            variable_name_type = OrderedDict()
            # variable_name_type.update(dataset.dtypes.to_dict(into=OrderedDict))


            variable_name_type.update(dataset.dtypes.to_dict())
            return render_template("ncross_selection.html",
                                   variable_name_type=variable_name_type,
                                   dataset=flask.session["selected_file"])

        if g.form["select_action"] == "k-mean":
            dataset = pd.read_excel("./static/uploads/" + flask.session["selected_file"])
            variable_name_type = OrderedDict()
            # variable_name_type.update(dataset.dtypes.to_dict(into=OrderedDict))


            variable_name_type.update(dataset.dtypes.to_dict())
            return render_template("cluster_selection.html",
                                   variable_name_type=variable_name_type,
                                   dataset=flask.session["selected_file"])

        elif g.form["select_action"] == "calc":
            dataset = pd.read_excel("./static/uploads/" + flask.session["selected_file"])
            variable_name_type = OrderedDict()
            variable_name_type.update(dataset.dtypes.to_dict())

            return render_template("calc.html", variable_name_type=variable_name_type,
                                   dataset=flask.session["selected_file"])
        elif g.form["select_action"] == "profiling":
            return redirect(url_for("profiling"))




        else:
            return str(g.form["select_action"])

    @app.route('/calc', methods=['GET', 'POST'])
    def calc_file():
        g = request
        dataset = pd.read_excel("./static/uploads/" + flask.session["selected_file"])
        variable_name_type = OrderedDict()
        variable_name_type.update(dataset.dtypes.to_dict(into=OrderedDict))

        return render_template("calc.html", variable_name_type=variable_name_type,
                               dataset=flask.session["selected_file"])

    @app.route('/monovariate_plot', methods=['GET', 'POST'])
    def monovariate_plot():
        g = request.form.getlist('monovariate')
        options_tipo_var = request.form["var_type"]
        options_ordinal_list = request.form["ordinal_list"]
        options_drop = request.form["drop_missing"]

        print(options_tipo_var)
        print(options_ordinal_list)

        flask.session["monovariate_plot"] = {
            "g": g,
            "options_tipo_var": options_tipo_var,
            "options_ordinal_list": options_ordinal_list
        }

        if request.form["ordinal_list"] == "":
            lista_ordinale = False
        else:
            lista_ordinale = request.form["ordinal_list"].split(",")
            try:
                lista_ordinale = [int(x) for x in lista_ordinale]
            except:
                lista_ordinale
        print(lista_ordinale)
        dataset = pd.read_excel("./static/uploads/" + flask.session["selected_file"])

        if options_drop == "drop":
            dataset.dropna(subset=[g[0]], inplace=True)
        elif options_drop == "no_drop":
            pass

        unique_values = dataset[g[0]].unique()

        data = table.dist_frequenza(dataset,
                                    g[0],
                                    save=False,
                                    tipo=options_tipo_var,
                                    lista_ordinale=lista_ordinale)
        data.to_html()
        data_non_tot = data.drop("Totale")

        if lista_ordinale != False:
            data.index = data.index.map(str)

        datatest = pd.DataFrame({"X": data_non_tot.index.values,
                                 "Frequency": data_non_tot["Frequenze"].values})

        equilibrium_values = tools.Sq_output(datatest["Frequency"])
        if options_tipo_var == "cardinale":
            characteristic_values = {
                "mean": datatest["Frequency"].mean(),
                "standard deviation": datatest["Frequency"].std(),
                "gini index": tools.gini(datatest["Frequency"].values)

            }

        if options_tipo_var == "categoriale":
            characteristic_values = {
                "mode": datatest[datatest["Frequency"] == datatest["Frequency"].max()]["X"].values[0],
                "total equilibrium": datatest["Frequency"].sum() / len(datatest["Frequency"].unique()),
                "Sq": equilibrium_values["Sq"],
                "Sq_norm": equilibrium_values["Sq_Norm"],
                "Eq": equilibrium_values["Eq"]

            }

        chart = altair_monovariate(data=datatest, options_tipo_var=options_tipo_var, lista_ordinale=lista_ordinale)

        return render_template("monovariate_plot.html",
                               operation_form=g,
                               chart_json=chart.to_json(),
                               data=data.to_html(),
                               unique_values=unique_values,
                               options_tipo_var=options_tipo_var,
                               characteristic_values=characteristic_values
                               )

    @app.route('/set_monovariate_plot_sorted', methods=["GET", 'POST'])
    def set_monovariate_plot_sorted():
        posted = request.get_json()
        print(posted['cagory_order'])
        flask.session["options_categorical_list"] = posted['cagory_order']
        print("this is" + str(flask.session["options_categorical_list"]))
        return "change_page"

    @app.route('/monovariate_plot_sorted', methods=["GET", 'POST'])
    def monovariate_plot_sorted():

        g = flask.session["monovariate_plot"]["g"]
        options_tipo_var = flask.session["monovariate_plot"]["options_tipo_var"]
        options_categorical_list = flask.session["options_categorical_list"]

        dataset = pd.read_excel("./static/uploads/" + flask.session["selected_file"])
        unique_values = dataset[g[0]].unique()

        data = table.dist_frequenza(dataset,
                                    g[0],
                                    save=False,
                                    tipo="categoriale",
                                    lista_ordinale=options_categorical_list)
        data.to_html()
        data_non_tot = data.drop("Totale")

        datatest = pd.DataFrame({"X": data_non_tot.index.values,
                                 "Frequency": data_non_tot["Frequenze"].values})
        print(datatest)
        datatest.dropna(inplace=True)
        datatest.set_index(datatest["X"], inplace=True)
        datatest.index = datatest.index.map(str)
        datatest = datatest.loc[options_categorical_list]
        print("{}{}".format(data.columns[0], ":Q"), "{}{}".format(data.columns[1], ":0"))

        equilibrium_values = tools.Sq_output(datatest["Frequency"])
        if options_tipo_var == "cardinale":
            characteristic_values = {
                "mean": datatest["Frequency"].mean(),
                "standard deviation": datatest["Frequency"].std(),
                "gini index": tools.gini(datatest["Frequency"].values)

            }

        if options_tipo_var == "categoriale":
            characteristic_values = {
                "mode": datatest[datatest["Frequency"] == datatest["Frequency"].max()]["X"].values[0],
                "total equilibrium": datatest["Frequency"].sum() / len(datatest["Frequency"].unique()),
                "Sq": equilibrium_values["Sq"],
                "Sq_norm": equilibrium_values["Sq_Norm"],
                "Eq": equilibrium_values["Eq"]

            }
        chart = altair_monovariate(data=datatest, options_tipo_var=options_tipo_var,
                                   lista_ordinale=options_categorical_list)

        return render_template("monovariate_plot.html",
                               operation_form=g,
                               chart_json=chart.to_json(),
                               data=data.to_html(),
                               unique_values=unique_values, options_tipo_var=options_tipo_var,
                               characteristic_values=characteristic_values)

    @app.route('/recode_operation', methods=['GET', 'POST'])
    def recode_operation():
        g = request.form.getlist('recode_var')
        flask.session["recode_var"] = g

        dataset = pd.read_excel("./static/uploads/" + flask.session["selected_file"])
        unique_values = dataset[g[0]].unique()

        data = table.dist_frequenza(dataset,
                                    g[0],
                                    save=False,
                                    tipo="categoriale")

        return render_template("recode_operation.html",
                               operation_form=g,
                               data=data.to_html(),
                               unique_values=unique_values,

                               )

    @app.route('/recode_output', methods=['GET', 'POST'])
    def recode_output():
        g = request.values.to_dict()
        new_var_name = g["new_variabile_name"]
        recode_var = flask.session["recode_var"]
        print(recode_var[0])
        dataset = pd.read_excel("./static/uploads/" + flask.session["selected_file"])

        def recode(dictionary, x):
            try:
                return dictionary[x]
            except:
                return x

        dataset[new_var_name] = dataset[recode_var[0]].apply(lambda x: recode(g, x))
        dataset.to_excel("./static/uploads/" + flask.session["selected_file"])

        output = dataset.to_html(table_id="result_data")
        return render_template("classification_output.html", data=output)

    @app.route('/bivariate_plot', methods=['GET', 'POST'])
    def bivariate_plot():
        g_x = request.form.getlist('bivariate_x')[0]
        g_y = request.form.getlist('bivariate_y')[0]

        print(g_x, g_y)

        dataset = pd.read_excel("./static/uploads/" + flask.session["selected_file"])
        data = dataset

        correlation = data[[g_x, g_y]].corr()

        chart = altair_bivariate(dataset, g_x, g_y)

        script = request.form["textarea_script"]
        print(script)
        plt.figure()
        result = eval(script, {'data': data, "pd": pd, "sns": sns})
        img_name = uuid.uuid4()
        flask.session["img.png"] = img_name

        plt.savefig("./static/images/{}.png".format(img_name))
        plt.figure()
        img_link = url_for("get_image", image_name="{}.png".format(img_name))

        # maybe solution https://stackoverflow.com/questions/53268133/generate-image-on-the-fly-using-flask-and-matplotlib
        return render_template("bivariate_plot.html",
                               operation_form=str((g_x, g_y)),
                               chart_json=chart.to_json(),
                               correlation=correlation.to_html(),
                               img_link=img_link)

    @app.route('/ncrosstab_output', methods=['GET', 'POST'])
    def ncrosstab_output():
        script = request.form["textarea_script"]
        flask.session["script"] = script
        data = pd.read_excel("./static/uploads/" + flask.session["selected_file"])
        result = eval(script, {'data': data, "pd": pd})

        '''
        index = script.split("index=[")[1].split("]],")[0]
        columns = script.split("columns=[")[1].split("]],")[0]
        print(index, columns)
        '''
        try:
            print(result.index.nlevels)
            flask.session["ncrosstab_classification_index"] = result.index.nlevels
        except:
            pass
        try:
            print(result.columns.nlevels)
            flask.session["ncrosstab_classification_columns"] = result.columns.nlevels

        except:
            pass

        if result.index.nlevels == 1 & result.columns.nlevels == 1:
            abilitate_tipology = "abilitate"
        else:
            abilitate_tipology= "disabilitate"

        flask.session["ncrosstab_output"] = result.to_html(classes="draggable", table_id="corr_tab")
        flask.session["ncrosstab_output_margin"] = "pass"
        flask.session["crosstab_output_descriptive"] = "pass"

        return render_template("crosstab_output.html",
                               table=result.to_html(classes="draggable",
                                                    table_id="corr_tab"),
                               abilitate_tipology=abilitate_tipology)

    @app.route('/ncrosstab_classification', methods=['GET', 'POST'])
    def ncrosstab_classification():
        result = flask.session["ncrosstab_output"]
        ncrosstab_classification_index = flask.session["ncrosstab_classification_index"]
        ncrosstab_classification_columns = flask.session["ncrosstab_classification_columns"]
        return render_template("crosstab_classification.html",
                               table=result,
                               classification_index=ncrosstab_classification_index,
                               classification_columns=ncrosstab_classification_columns
                               )

    @app.route('/cluster_output', methods=["POST"])
    def cluster_output():
        dataset = pd.read_excel("./static/uploads/" + flask.session["selected_file"])
        data = dataset

        nome_var = request.form["new_var_name"]
        script = request.form["textarea_script"]
        result = eval(script, {'data': data, "pd": pd, "vq": vq, "kmeans": kmeans})
        data_select = data[result[0]]
        data_select.dropna(inplace=True)
        data_select = data_select.applymap(float)

        data_values = data_select.values

        centroids, _ = kmeans(data_values, result[1])
        # assign each sample to a cluster
        idx, _ = vq(data_values, centroids)
        data_select[nome_var] = idx
        output = pd.concat([data_select[nome_var], data], axis=1)
        plt.figure()
        variabile = eval(script)[0]
        if len(variabile) == 2:
            img_name = uuid.uuid4()

            c = output[nome_var]
            flask.session["img.png"] = img_name
            for classes in c.unique():
                output_temp = output[output[nome_var] == classes]
                x = output_temp[variabile[0]]
                y = output_temp[variabile[1]]

                result = sns.scatterplot(x=x, y=y, data=output_temp, cmap="tab20c", label = classes)
                result.legend()

            #result.figure.savefig("./static/images/{}.png".format(img_name))
            plt.savefig("./static/images/{}.png".format(img_name))
            img_link = url_for("get_image", image_name="{}.png".format(img_name))
        elif len(variabile) == 3:
            img_name = uuid.uuid4()

            c = output[nome_var]

            flask.session["img.png"] = img_name
            result = plt.axes(projection='3d')
            for classes in c.unique():
                output_temp = output[output[nome_var] == classes]
                x = output_temp[variabile[0]]
                y = output_temp[variabile[1]]
                z = output_temp[variabile[2]]


                result.scatter3D(x, y, z, cmap="tab20c", label = classes)
                result.legend()

            plt.savefig("./static/images/{}.png".format(img_name))
            img_link = url_for("get_image", image_name="{}.png".format(img_name))
        else:
            img_link = ""

        output = output.to_html(table_id="result_data")
        plt.figure()
        return render_template("classification_output.html", data=output, img_link=img_link)

    @app.route('/info', methods=['GET', 'POST'])
    def info():
        g = request
        print(g.form)
        dataset = g.form["dataset"]
        data = pd.read_excel("./static/uploads/" + dataset)
        result = eval(g.form["formula"], {'data': data})

        if g.form["new_variabile"] == "":
            if isinstance(result, pd.Series):
                return eval(g.form["formula"], {'data': data}).to_frame().to_html()
            elif not isinstance(result, pd.Series):
                return eval(g.form["formula"], {'data': data})
        else:
            data[g.form["new_variabile"]] = eval(g.form["formula"], {'data': data})
            dataset = g.form["dataset"]
            data.to_excel("./static/uploads/" + dataset)
            # return "<h> nuova variabile </h>" + data[g.form["new_variabile"]].to_frame().to_html()
            output = pd.concat([data[g.form["new_variabile"]], data], axis=1)

            output = output.to_html(table_id="result_data")
            return render_template("classification_output.html", data=output)

    @app.route("/post_arrive", methods=["GET", 'POST'])
    def post_arrive():
        posted = request.get_json()['category_order']
        recode = posted
        try:
            data = pd.read_excel("./static/uploads/" + flask.session["selected_file"])
            import numpy as np
            data["type_" + recode['vary'] + "_" + recode['varx']] = np.nan

            def set_typo(row, recode):
                for item in recode['dataframe']:
                    if (row[recode['varx']] == item['categoryx']) & (row[recode['vary']] == item['categoryy']):
                        print(row[recode['varx']] == item['categoryx'], row[recode['varx']], item['categoryx'],
                              row[recode['vary']], item['categoryy'], item["value"])
                        return item["value"]
                    else:
                        pass

            data["type_" + recode['vary'] + "_" + recode['varx']] = data.apply(lambda row: set_typo(row, recode), axis=1)
            data.to_excel("./static/uploads/" + flask.session["selected_file"])
            return "executed: you can find the new variabile in the last columns of dataframe"
        except:
            return "error.. somethings wrong"
    @app.route("/profiling", methods=["GET", 'POST'])
    def profiling():
        data = pd.read_excel("./static/uploads/" + flask.session["selected_file"])
        #profile = data.profile_report(title=flask.session["selected_file"])
        profile = pandas_profiling.ProfileReport(data)
        print(dir(profile))
        profile.title = flask.session["selected_file"]
        profile.to_file(output_file="./templates/profiling.html")
        return render_template("profiling.html")

    @app.route("/get-image/<image_name>")
    def get_image(image_name):
        try:
            return send_from_directory(app.config["CLIENT_IMAGES"], filename="{}.png".format(flask.session["img.png"]),
                                       as_attachment=False)
        except FileNotFoundError:
            abort(404)

    @app.route("/jupyter")
    def jupyter():
        import webbrowser
        url = "http://localhost:8888/"
        import os
        import subprocess
        #threading.Timer(1.50, lambda: os.system("jupyter notebook"))
        proc = subprocess.Popen('jupyter notebook', shell=True, stdout=subprocess.PIPE)
        return "start jupyter"

    app.run(port=5555, debug=False)

if __name__ == "__main__":
    main()