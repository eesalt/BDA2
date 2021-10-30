import os
import sys

import charts
import correlation as dafrenchy_correlation
import pandas as pd
from plotly import figure_factory as ff

"""
Julien - you'll need to set these variables for this to work properly.
Even then, I make no guarantees.
"""


def main():
    df = "this should be a pandas df"
    response = ""
    predictors = []

    print()
    path = "file://" + os.getcwd() + "/"
    print("Here's the working directory where you can find the files:")
    print(os.getcwd())

    # testing data only
    names = ["Sepal Length", "Sepal Width", "Petal Length", "Petal Width", "Class"]
    df = pd.read_csv("iris.data", names=names)
    df["boo_response"] = df["Class"].apply(
        lambda x: True if x == "Iris-setosa" else False
    )
    predictors = ["Sepal Length", "Sepal Width", "Class"]
    response = "Petal Length"

    test = charts.create_charts(df=df, predictors=predictors, response=response)

    # classify columns
    # first classify response type
    response_type = test.classify_column(response, "response")
    # print(f'response type is {response_type}')

    # classify predictors
    predictor_types = {}
    type = ""
    cont_predictors = []
    cat_predictors = []
    for x in predictors:
        type = test.classify_column(x, "predictor")
        predictor_types[x] = type
        if type == "continuous":
            cont_predictors.append(x)
        if type == "categorical":
            cat_predictors.append(x)

    # HW4 charts
    list_of_files = []
    list_of_predictors = []
    chart_names = []
    # for loop here
    for predictor in predictors:
        x = predictor
        # generate plots to inspect each predictor
        # plot code was generously donated by dafrenchyman
        if response_type in ["categorical"]:
            if predictor in cat_predictors:
                # Heatplot here
                file_heatplot = test.Heatplot(x)
                list_of_files.append(path + file_heatplot)
                chart_names.append("heatplot")
                list_of_predictors.append(predictor)

            elif predictor in cont_predictors:
                # violin here
                file_violin = test.Violin(x)
                list_of_files.append(path + file_violin)
                chart_names.append("violin")
                list_of_predictors.append(predictor)

                # distribution here
                file_distribution = test.Distribution(x)
                list_of_files.append(path + file_distribution)
                chart_names.append("distribution")
                list_of_predictors.append(predictor)

        elif response_type in ["continuous"]:
            if predictor in cat_predictors:
                # second violin here
                # distribution2 here
                file_violin2, file_distribution2 = test.ViolinAndDist(x)
                list_of_files.append(path + file_violin2)
                list_of_predictors.append(predictor)
                chart_names.append("violin2")
                list_of_files.append(path + file_distribution2)
                list_of_predictors.append(predictor)
                chart_names.append("distribution2")

            elif predictor in cont_predictors:
                # scatter here
                file_scatter = test.Scatter(x)
                list_of_files.append(path + file_scatter)
                chart_names.append("scatter")
                list_of_predictors.append(predictor)

    # make the table
    d = {
        "Predictor": list_of_predictors,
        "Chart Type": chart_names,
        "files": list_of_files,
    }
    lof_df = pd.DataFrame(data=d)

    # xfiles
    lof_df["chart"] = lof_df.apply(
        lambda x: '<a href="{}">{}</a>'.format(x["files"], x["Chart Type"]), axis=1
    )
    drop_columns = ["files", "Chart Type"]
    lof_df.drop(drop_columns, inplace=True, axis=1)

    filename = "HW4_charts.html"
    lof_df.to_html(filename, escape=False, render_links=True)
    print(path + filename)

    # difference mean of response - normal
    DMR_results = []
    DWMR_results = []
    chart_names = []
    list_of_predictors = []
    for x in predictors:
        if x in cat_predictors:
            type = "categorical"
        else:
            type = "continuous"
        DMR_result, DWMR_result, chart_name = test.avg_mean_of_response(x, type)
        DMR_results.append(DMR_result)
        DWMR_results.append(DWMR_result)
        chart_names.append(path + chart_name)
        list_of_predictors.append(x)
        # dmr_dict[x] = [DMR_result, DWMR_result, chart_name]
    # add a pandas df here with links
    # make the table
    d = {
        "Predictor": list_of_predictors,
        "DMR result": DMR_results,
        "DWMR result": DWMR_results,
        "files": chart_names,
    }
    lof_df = pd.DataFrame(data=d)
    lof_df.sort_values(by="DWMR result", ascending=False, inplace=True)
    # xfiles
    lof_df["Diff Mean of Response"] = lof_df.apply(
        lambda x: '<a href="{}">{}</a>'.format(x["files"], x["DMR result"]), axis=1
    )
    lof_df["Weighted Diff Mean of Response"] = lof_df.apply(
        lambda x: '<a href="{}">{}</a>'.format(x["files"], x["DWMR result"]), axis=1
    )
    drop_columns = ["files", "DMR result", "DWMR result"]
    lof_df.drop(drop_columns, inplace=True, axis=1)

    filename = "Diff_Mean_of_response_results.html"
    lof_df.to_html(filename, escape=False, render_links=True)
    print(path + filename)

    # Brute force
    if len(cat_predictors) > 1:
        DMR2_list = []
        DWMR2_list = []
        filename_list = []
        filename2_list = []
        x1_list = []
        x2_list = []
        for x1 in cat_predictors:
            for x2 in cat_predictors:
                if x1 != x2:
                    if x1 in cat_predictors:
                        x1_type = "categorical"
                    else:
                        x1_type = "continuous"
                    if x2 in cat_predictors:
                        x2_type = "categorical"
                    else:
                        x2_type = "continuous"
                    (
                        DMR_result2,
                        DWMR_result2,
                        filename,
                        filename2,
                    ) = test.two_variable_AMR(x1, x1_type, x2, x2_type)
                    x1_list.append(x1)
                    x2_list.append(x2)
                    DMR2_list.append(DMR_result2)
                    DWMR2_list.append(DWMR_result2)
                    filename_list.append(path + filename)
                    filename2_list.append(path + filename2)

        # create the brute force table
        d = {
            "x1": x1_list,
            "x2": x2_list,
            "DMR": DMR2_list,
            "WDMR": DWMR2_list,
            "DMR file": filename_list,
            "WDMR file": filename2_list,
        }
        brute_force_df = pd.DataFrame(data=d)
        brute_force_df.sort_values(by="WDMR", ascending=False, inplace=True)

        brute_force_df["Diff with mean of resp"] = brute_force_df.apply(
            lambda x: '<a href="{}">{}</a>'.format(x["DMR file"], x["DMR"]), axis=1
        )
        brute_force_df["Weighted Diff with mean of resp"] = brute_force_df.apply(
            lambda x: '<a href="{}">{}</a>'.format(x["WDMR file"], x["WDMR"]), axis=1
        )

        drop_columns = ["DMR", "WDMR", "DMR file", "WDMR file"]
        brute_force_df.drop(drop_columns, inplace=True, axis=1)

        filename = "brute_force_categoricals.html"
        brute_force_df.to_html(filename, escape=False, render_links=True)
        print(path + filename)

    if len(cont_predictors) > 1:
        # cont-cont brute force
        DMR2_list = []
        DWMR2_list = []
        filename_list = []
        filename2_list = []
        x1_list = []
        x2_list = []
        for x1 in cont_predictors:
            for x2 in cont_predictors:
                if x1 != x2:
                    if x1 in cat_predictors:
                        x1_type = "categorical"
                    else:
                        x1_type = "continuous"
                    if x2 in cat_predictors:
                        x2_type = "categorical"
                    else:
                        x2_type = "continuous"
                    (
                        DMR_result2,
                        DWMR_result2,
                        filename,
                        filename2,
                    ) = test.two_variable_AMR(x1, x1_type, x2, x2_type)
                    x1_list.append(x1)
                    x2_list.append(x2)
                    DMR2_list.append(DMR_result2)
                    DWMR2_list.append(DWMR_result2)
                    filename_list.append(path + filename)
                    filename2_list.append(path + filename2)

        # create the brute force table
        d = {
            "x1": x1_list,
            "x2": x2_list,
            "DMR": DMR2_list,
            "WDMR": DWMR2_list,
            "DMR file": filename_list,
            "WDMR file": filename2_list,
        }
        brute_force_df = pd.DataFrame(data=d)
        brute_force_df.sort_values(by="WDMR", ascending=False, inplace=True)

        brute_force_df["Diff with mean of resp"] = brute_force_df.apply(
            lambda x: '<a href="{}">{}</a>'.format(x["DMR file"], x["DMR"]), axis=1
        )
        brute_force_df["Weighted Diff with mean of resp"] = brute_force_df.apply(
            lambda x: '<a href="{}">{}</a>'.format(x["WDMR file"], x["WDMR"]), axis=1
        )

        drop_columns = ["DMR", "WDMR", "DMR file", "WDMR file"]
        brute_force_df.drop(drop_columns, inplace=True, axis=1)

        filename = "brute_force_continuous.html"
        brute_force_df.to_html(filename, escape=False, render_links=True)
        print(path + filename)

    # cat-cont brute force
    if len(cont_predictors) > 0 and len(cat_predictors) > 0:
        DMR2_list = []
        DWMR2_list = []
        filename_list = []
        filename2_list = []
        x1_list = []
        x2_list = []
        for x1 in cat_predictors:
            for x2 in cont_predictors:
                if x1 != x2:
                    if x1 in cat_predictors:
                        x1_type = "categorical"
                    else:
                        x1_type = "continuous"
                    if x2 in cat_predictors:
                        x2_type = "categorical"
                    else:
                        x2_type = "continuous"
                    (
                        DMR_result2,
                        DWMR_result2,
                        filename,
                        filename2,
                    ) = test.two_variable_AMR(x1, x1_type, x2, x2_type)
                    x1_list.append(x1)
                    x2_list.append(x2)
                    DMR2_list.append(DMR_result2)
                    DWMR2_list.append(DWMR_result2)
                    filename_list.append(path + filename)
                    filename2_list.append(path + filename2)

        # create the brute force table
        d = {
            "x1": x1_list,
            "x2": x2_list,
            "DMR": DMR2_list,
            "WDMR": DWMR2_list,
            "DMR file": filename_list,
            "WDMR file": filename2_list,
        }
        brute_force_df = pd.DataFrame(data=d)
        brute_force_df.sort_values(by="WDMR", ascending=False, inplace=True)

        brute_force_df["Diff with mean of resp"] = brute_force_df.apply(
            lambda x: '<a href="{}">{}</a>'.format(x["DMR file"], x["DMR"]), axis=1
        )
        brute_force_df["Weighted Diff with mean of resp"] = brute_force_df.apply(
            lambda x: '<a href="{}">{}</a>'.format(x["WDMR file"], x["WDMR"]), axis=1
        )

        drop_columns = ["DMR", "WDMR", "DMR file", "WDMR file"]
        brute_force_df.drop(drop_columns, inplace=True, axis=1)

        filename = "brute_force_mixed.html"
        brute_force_df.to_html(filename, escape=False, render_links=True)
        print(path + filename)

    #
    # Still need to add table output to html with chart links?
    # Correlation Coefficients
    # 2 continuous
    if len(cont_predictors) > 1:
        var1_list, var2_list, r_list = [], [], []
        for x1 in cont_predictors:
            for x2 in cont_predictors:
                r, p = dafrenchy_correlation.cont_correlation(df[x1], df[x2])
                var1_list.append(x1)
                var2_list.append(x2)
                r_list.append(r)

        # create the table
        d = {"Var1": var1_list, "Var2": var2_list, "PearsonsR": r_list}
        cont_df = pd.DataFrame(data=d)
        cont_df.sort_values(by="PearsonsR", ascending=False, inplace=True)
        filename = "Cont_corr_table.html"
        cont_df.to_html(filename, header="Continuous_variable_correlation_table")
        print(path + filename)

        # alternate heatmap
        pivot = cont_df.pivot_table("PearsonsR", ["Var1"], "Var2")
        fig = ff.create_annotated_heatmap(
            z=pivot.to_numpy(), x=pivot.index.to_list(), y=pivot.index.to_list()
        )
        filename = "Continuous_correlation_matrix.html"
        fig.write_html(file=filename, include_plotlyjs="cdn")
        print(path + filename)

    # deprecated heatmap
    # plotly_data = {'z': cont_df['PearsonsR'].tolist(),
    #               'x': cont_df['Var1'].tolist(),
    #               'y': cont_df['Var2'].tolist()
    #               }

    # cont_fig = go.Figure(
    #    data=go.Heatmap(plotly_data)
    # )
    # cont_fig.update_layout(
    #    title="Continuous correlation matrix",
    #    xaxis_title= 'variables',
    #    yaxis_title= 'variables again',
    # )
    # filename = 'cont_corr.html'
    # cont_fig.write_html(file=filename, include_plotlyjs="cdn")

    # variable 1, variable 2, correlation metric, value, p_value?
    # need a correlation matrix here

    # 2 categoricals
    if len(cat_predictors) > 1:
        var1_list, var2_list, v_list = [], [], []
        for x1 in cat_predictors:
            for x2 in cat_predictors:
                v = dafrenchy_correlation.cat_correlation(x1, x2)
                var1_list.append(x1)
                var2_list.append(x2)
                v_list.append(v)

        # create the table
        d = {"Var1": var1_list, "Var2": var2_list, "CramersV": v_list}
        cat_df = pd.DataFrame(data=d)
        cat_df.sort_values(by="CramersV", ascending=False, inplace=True)
        filename = "Cat_corr_table.html"
        cat_df.to_html(filename, header="Categorical_variable_correlation_table")
        print(path + filename)

        # alternate heatmap
        pivot = cat_df.pivot_table("CramersV", ["Var1"], "Var2")
        fig = ff.create_annotated_heatmap(
            z=pivot.to_numpy(), x=pivot.index.to_list(), y=pivot.index.to_list()
        )
        filename = "Categorical_correlation_matrix.html"
        fig.write_html(file=filename, include_plotlyjs="cdn")
        print(path + filename)

    # cont/categorical

    # categories first
    if len(cont_predictors) > 0 and len(cat_predictors) > 0:
        var1_list, var2_list, c_list = [], [], []
        for x1 in cat_predictors:
            for x2 in cont_predictors:
                c = dafrenchy_correlation.cat_cont_correlation_ratio(df[x1], df[x2])
                var1_list.append(x1)
                var2_list.append(x2)
                c_list.append(c)

        # create the table
        d = {"Var1": var1_list, "Var2": var2_list, "Correlation": c_list}
        cat_cont_df = pd.DataFrame(data=d)
        cat_cont_df.sort_values(by="Correlation", ascending=False, inplace=True)
        filename = "Cat_cont_corr_table.html"
        cat_cont_df.to_html(
            filename, header="Continuous_Categorical_variable_correlation_table"
        )
        print(path + filename)

        # alternate heatmap
        pivot = cat_cont_df.pivot_table("Correlation", ["Var1"], "Var2")
        fig = ff.create_annotated_heatmap(
            z=pivot.to_numpy(), x=list(pivot.columns), y=pivot.index.to_list()
        )
        filename = "Continuous_vs_Categorical_correlation_matrix.html"
        fig.write_html(file=filename, include_plotlyjs="cdn")
        print(path + filename)


if __name__ == "__main__":
    sys.exit(main())
