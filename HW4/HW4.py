import sys

import numpy
import pandas as pd
import statsmodels.api
from plotly import express as px
from plotly import figure_factory as ff
from plotly import graph_objects as go
from plotly.subplots import make_subplots
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix


def main():
    """Set the arguments below until I can get argparse in here"""
    # arguments: df, response (string), predictors (list)
    # testing data only
    # names = ["Sepal Length", "Sepal Width", "Petal Length", "Petal Width", "Class"]
    # df = pd.read_csv("iris.data", names=names)
    # df['boo_response']=df['Class'].apply(lambda x: True if x=='Iris-setosa' else False)

    # Hey user, set these until I get argparse in here
    df = pd.DataFrame()
    response = ""
    predictors = []
    # predictor = 'Sepal Length'

    # testing only
    # create boolean response - probably should remove
    # df['boo_response']=df['Class'].apply(lambda x: True if x=='Iris-setosa' else False)

    # steps
    # Determine if response is continuous or boolean
    y = response
    if df[response].unique().size > 2:
        response_type = "continuous"
    else:
        # hard coding to boolean rather than categorical
        response_type = "boolean"

    # Determine if predictors are categorical or continuous
    cont_master_list = df._get_numeric_data().columns.to_list()
    predictor_types = {}
    cont_predictor_col_names = []
    for predictor in predictors:
        predictor_type = ""
        if predictor in cont_master_list:
            predictor_type = "continuous"
        if True in df[predictor].unique().tolist():
            predictor_type = "boolean"
        if predictor_type == "":
            if df.dtypes[predictor] == "O":
                predictor_type = "categorical"
        if predictor_type == "":
            predictor_type = input(
                f"Toss me a bone, what's the predictor type for {predictor}? "
                f"(continuous, categorical, or boolean):"
            )
        if predictor_type == "":
            print("that's not very nice")
            predictor_type = "categorical"
        predictor_types[predictor] = predictor_type
        if predictor_type == "continuous":
            cont_predictor_col_names.append(predictor)

    # Heatplot
    def Heatplot(x):
        conf_matrix = confusion_matrix(df[x].astype(str), df[y].astype(str))
        fig_cat_cat = go.Figure(
            data=go.Heatmap(z=conf_matrix, zmin=0, zmax=conf_matrix.max())
        )
        fig_cat_cat.update_layout(
            title="",
            xaxis_title="Response",
            yaxis_title="Predictor",
        )
        filename = x + " heatmap.html"
        fig_cat_cat.write_html(file=filename, include_plotlyjs="cdn")
        return filename

    def Violin(x):
        # violin plot on predictor grouped by response
        fig_2 = go.Figure(
            data=go.Violin(
                y=df[y],
                x=df[x],
                line_color="black",
                box_visible=True,
                meanline_visible=True,
            )
        )
        fig_2.update_layout(
            title=x + " Violin",
            xaxis_title="Response",
            yaxis_title="Predictor",
        )
        filename = x + " violin.html"
        fig_2.write_html(file=filename, include_plotlyjs="cdn")
        return filename

    def Distribution(x):
        # distribution plot on predictor grouped by response
        # Create distribution plot with custom bin_size
        hist_data = [df[x]]
        group_labels = [x]
        fig_1 = ff.create_distplot(hist_data, group_labels)
        fig_1.update_layout(
            title=f"Distribution for {x}",
            xaxis_title="Predictor",
            yaxis_title="Distribution",
        )
        filename = x + "cont predict by cat resp distplot.html"
        fig_1.write_html(file=filename, include_plotlyjs="cdn")

    def ViolinAndDist(x):
        n = len(df.index)
        group_labels = [thing for thing in df[x].unique()]
        hist_data = []
        for thing in group_labels:
            hist_data.append(df[df[x] == thing][y].to_list())

        # violin plot on response grouped by predictor
        fig_2 = go.Figure()
        for curr_hist, curr_group in zip(hist_data, group_labels):
            fig_2.add_trace(
                go.Violin(
                    x=numpy.repeat(curr_group, n),
                    y=curr_hist,
                    name=curr_group,
                    box_visible=True,
                    meanline_visible=True,
                )
            )
        fig_2.update_layout(
            title=f"Violin for {x}",
            xaxis_title="Groupings",
            yaxis_title="Response",
        )
        filename = x + " violin.html"
        fig_2.write_html(file=filename, include_plotlyjs="cdn")
        # distribution plot on response grouped by predictor
        fig_1 = ff.create_distplot(hist_data, group_labels)
        fig_1.update_layout(
            title=f"Distribution for {x}",
            xaxis_title="Response",
            yaxis_title="Distribution",
        )
        filename2 = x + " dist.html"
        fig_2.write_html(file=filename2, include_plotlyjs="cdn")
        return filename, filename2

    def Scatter(x):
        # scatter plot with trendline
        fig = px.scatter(x=df[x], y=df[y], trendline="ols")
        fig.update_layout(
            title=f"Scatterplot for {x}",
            xaxis_title="Predictor",
            yaxis_title="Response",
        )
        # fig.show()
        filename = x + " scatter.html"
        fig.write_html(
            file=filename,
            include_plotlyjs="cdn",
        )

    def Regression(x):
        # regression: continuous response
        predictor_name = statsmodels.api.add_constant(df[x])
        linear_regression_model = statsmodels.api.OLS(df[y], predictor_name)
        linear_regression_model_fitted = linear_regression_model.fit()
        # print(linear_regression_model_fitted.summary())

        # p value and t score (continuous predictors only) along with its plot
        t_value = round(linear_regression_model_fitted.tvalues[1], 6)
        p_value = "{:.6e}".format(linear_regression_model_fitted.pvalues[1])
        # print(f"t value: {t_value}", f"p value: {p_value}")
        # Plot the figure
        fig = px.scatter(x=df[x], y=df[y], trendline="ols")
        fig.update_layout(
            title=f"Variable: {x}: (t-value={t_value}) (p-value={p_value})",
            xaxis_title=f"Variable: {x}",
            yaxis_title="y",
        )
        filename = x + " ts and ps.html"
        fig.write_html(file=filename, include_plotlyjs="cdn")
        return filename, t_value, p_value

    list_of_files = []
    # for loop here
    for predictor in predictors:
        predictor_type = predictor_types.get(predictor)
        x = predictor
        # generate plots to inspect each predictor
        # plot code was generously donated by dafrenchyman
        if response_type in ["boolean"]:
            if predictor_type in ["boolean", "categorical"]:
                # Heatplot here
                file_heatplot = Heatplot(x)
                list_of_files.append(file_heatplot)

            elif predictor_type == "continuous":
                # violin here
                file_violin = Violin(x)
                list_of_files.append(file_violin)

                # distribution here
                file_distribution = Distribution(x)
                list_of_files.append(file_distribution)

        elif response_type in ["continuous"]:
            if predictor_type in ["boolean", "categorical"]:
                # second violin here
                # distribution2 here
                file_violin2, file_distribution2 = ViolinAndDist(x)
                list_of_files.append(file_violin2)
                list_of_files.append(file_distribution2)

            elif predictor_type == "continuous":
                # scatter here
                file_scatter = Scatter(x)
        # calculate the ranking algorithms
        if predictor_type == "continuous":
            if response_type == "continuous":
                # regression here
                file_regression, t_value, p_value = Regression(x)
                list_of_files.append(file_regression)

            elif response_type == "boolean":
                # logistic regression: boolean response
                logistic_regression_model = statsmodels.api.Logit(df[y], df[x]).fit()
                print(logistic_regression_model.summary())

                # I had to remove this to accomodate flake8. I'm not happy about that
                # try:
                # t_value = round(logistic_regression_model.tvalues[1], 6)
                # p_value = "{:.6e}".format(logistic_regression_model.pvalues[1])
                # except:
                # pass

    # difference with mean of response along with its plot (weighted and unweighted)
    # mean of response per bin
    # 1/number of bins * sum(each bin mean - pop mean)^2
    def avg_mean_of_response(predictor):
        x = predictor
        y = response
        bin_count = 10
        bins = pd.cut(x=df[x], bins=bin_count)
        averages = df[y].groupby(bins).mean()
        bins = bins.value_counts()
        counts_df = bins.to_frame().reset_index()
        counts_df = counts_df.rename(columns={"index": "bins", x: "counts"})
        df2 = averages.to_frame().reset_index()
        df2["means"] = df2[y]
        df2["population mean"] = df[y].mean()

        df2["difference with mean of response"] = df2.apply(
            lambda z: z["population mean"] - z["means"], axis=1
        )
        df2["squared difference"] = (
            1 / bin_count * numpy.power(df2["difference with mean of response"], 2)
        )

        df2_merged = pd.merge(
            left=df2, right=counts_df, how="left", left_on=x, right_on="bins"
        )
        df2_merged["population"] = df2_merged["counts"].sum()
        df2_merged["weighted difference with mean of response"] = df2_merged.apply(
            lambda z: numpy.power((z["population mean"] - z["means"]), 2)
            * z["counts"]
            / z["population"],
            axis=1,
        )
        DMR_result = [x, df2["squared difference"].sum()]
        DWMR_result = [x, df2_merged["weighted difference with mean of response"].sum()]

        diff_fig = make_subplots(specs=[[{"secondary_y": True}]])
        diff_fig.add_trace(
            go.Bar(x=df2_merged.index, y=df2_merged["counts"], name="count"),
            secondary_y=False,
        )
        diff_fig.add_trace(
            go.Scatter(
                x=df2_merged.index,
                y=df2_merged["squared difference"],
                mode="lines",
                name="bin mean of response",
            ),
            secondary_y=True,
        )
        diff_fig.add_trace(
            go.Scatter(
                x=df2_merged.index,
                y=df2_merged["weighted difference with mean of response"],
                mode="lines",
                name="bin weighted mean of response",
            ),
            secondary_y=True,
        )
        diff_fig.add_trace(
            go.Scatter(
                x=df2_merged.index,
                y=df2_merged["population mean"],
                mode="lines",
                name="pop mean",
            ),
            secondary_y=False,
        )
        diff_fig.update_layout(bargap=0.1)

        plot_name = (
            predictor
            + ": binned difference with mean of response (weighted and unweighted).html"
        )
        diff_fig.write_html(file=plot_name, include_plotlyjs="cdn")
        return DMR_result, DWMR_result, plot_name

    DMR_results = []
    DWMR_results = []
    for predictor in predictors:
        DMR_result, DWMR_result, file_MR = avg_mean_of_response(predictor)
        list_of_files.append(file_MR)
        DMR_results.append(DMR_result)
        DWMR_results.append(DWMR_result)

    df_results = pd.DataFrame(
        DMR_results, columns=["variable", "difference with mean of response"]
    )
    df2_results = pd.DataFrame(
        DWMR_results, columns=["variable", "difference with weighted mean of response"]
    )
    df_results = pd.merge(
        left=df_results,
        right=df2_results,
        how="left",
        left_on="variable",
        right_on="variable",
    )

    def RandomForest():
        # Random Forest Variable importance ranking (continuous predictors only, categorical response)
        cont_predictors = df[cont_predictor_col_names]
        y = response
        rf = RandomForestClassifier(random_state=1234)
        rf.fit(cont_predictors, df[y])
        feature_importance = rf.feature_importances_.tolist()
        # generate a table with all the variables and their rankings
        predictor_table = pd.DataFrame(
            list(zip(cont_predictor_col_names, feature_importance)),
            columns=["Predictors", "Feature Importances"],
        )

        return predictor_table

    # continuous only
    if response_type == "boolean" and cont_predictor_col_names != []:
        results_table = RandomForest()
        print(results_table)

    if "results_table" in locals():
        df_results = pd.merge(
            left=df_results,
            right=results_table,
            how="left",
            left_on="variable",
            right_on="Predictors",
        )
    print(df_results)
    df_results.to_html("results.html")

    # HTML or excel based rankings report with links to the plots
    print(
        "I never did get either the html with links or the excel with links to work..."
    )
    print("but here are those files which you'll find in your local folder:")
    for file in list_of_files:
        print(file)


if __name__ == "__main__":
    sys.exit(main())
