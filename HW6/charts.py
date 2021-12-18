import numpy as np
import pandas as pd
import statsmodels.api
from plotly import express as px
from plotly import figure_factory as ff
from plotly import graph_objects as go
from plotly.subplots import make_subplots
from sklearn.metrics import confusion_matrix


class create_charts:
    """
    class to hold methods to create charts
    """

    def __init__(self, df=pd.DataFrame(), predictors=[], response=""):
        self.df = df
        self.predictors = predictors
        self.response = response

    # test function
    def class_test(self, col):
        print(self.df[col].sum())

    # move the type testing here
    def classify_column(self, col, col_type):
        """
        classifies the column provided
        col is string
        type is string: "response" or "predictor"
        """
        if col_type == "response":
            response = col

            if self.df[response].unique().size > 2:
                type = "continuous"
            else:
                # hard coding to boolean rather than categorical
                type = "boolean"

        else:
            # Determine if predictors are categorical or continuous
            cont_master_list = self.df._get_numeric_data().columns.to_list()
            predictor = col
            type = ""
            if predictor in cont_master_list:
                type = "continuous"
            if self.df.dtypes[predictor] == "float64":
                type = "continuous"
            if type == "":
                if True in self.df[predictor].unique().tolist():
                    type = "categorical"
            if type == "":
                if self.df.dtypes[predictor] == "O":
                    type = "categorical"
            length = len(self.df[predictor])
            unique = len(pd.unique(self.df[predictor]))
            if type == "":
                if unique / length < 0.1:
                    type = "categorical"
            if type == "":
                type = input(
                    f"Toss me a bone, what's the predictor type for {predictor}? "
                    f"(continuous, categorical, or boolean):"
                )
            if type == "":
                print("that's not very nice")
                type = "categorical"
            # predictor_types[predictor] = predictor_type
            # if type == "continuous":
            # cont_predictor_col_names.append(predictor)
        return type

    # move the chart functions here
    # Heatplot
    def Heatplot(self, x):
        df = self.df
        y = self.response
        conf_matrix = confusion_matrix(df[x].astype(str), df[y].astype(str))
        fig_cat_cat = go.Figure(
            data=go.Heatmap(z=conf_matrix, zmin=0, zmax=conf_matrix.max())
        )
        fig_cat_cat.update_layout(
            title="",
            xaxis_title="Response",
            yaxis_title="Predictor",
        )
        filename = "/results/" + x + " heatmap.html"
        fig_cat_cat.write_html(file=filename, include_plotlyjs="cdn")
        return filename

    def Violin(self, x):
        # violin plot on predictor grouped by response
        df = self.df
        y = self.response
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
        filename = "/results/" + x + " violin.html"
        fig_2.write_html(file=filename, include_plotlyjs="cdn")
        return filename

    def Distribution(self, x):
        # distribution plot on predictor grouped by response
        # Create distribution plot with custom bin_size
        self.df
        self.response
        hist_data = [self.df[x]]
        group_labels = [x]
        fig_1 = ff.create_distplot(hist_data, group_labels)
        fig_1.update_layout(
            title=f"Distribution for {x}",
            xaxis_title="Predictor",
            yaxis_title="Distribution",
        )
        filename = "/results/" + x + "cont predict by cat resp distplot.html"
        fig_1.write_html(file=filename, include_plotlyjs="cdn")
        return filename

    def ViolinAndDist(self, x):
        df = self.df
        y = self.response
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
                    x=np.repeat(curr_group, n),
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
        filename = "/results/" + x + " violin.html"
        fig_2.write_html(file=filename, include_plotlyjs="cdn")
        # distribution plot on response grouped by predictor
        fig_1 = ff.create_distplot(hist_data, group_labels)
        fig_1.update_layout(
            title=f"Distribution for {x}",
            xaxis_title="Response",
            yaxis_title="Distribution",
        )
        filename2 = "/results/" + x + " dist.html"
        fig_2.write_html(file=filename2, include_plotlyjs="cdn")
        return filename, filename2

    def Scatter(self, x):
        # scatter plot with trendline
        df = self.df
        y = self.response
        fig = px.scatter(x=df[x], y=df[y], trendline="ols")
        fig.update_layout(
            title=f"Scatterplot for {x}",
            xaxis_title="Predictor",
            yaxis_title="Response",
        )
        # fig.show()
        filename = "/results/" + x + " scatter.html"
        fig.write_html(
            file=filename,
            include_plotlyjs="cdn",
        )
        return filename

    def Regression(self, x):
        df = self.df
        y = self.response
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
        filename = "/results/" + x + " ts and ps.html"
        fig.write_html(file=filename, include_plotlyjs="cdn")
        return filename, t_value, p_value

    # def RandomForest(self):
    #    # Random Forest Variable importance ranking (continuous predictors only, categorical response)
    #    df = self.df
    #    cont_predictors = df[cont_predictor_col_names]
    #    y = self.response
    #    rf = RandomForestClassifier(random_state=1234)
    #    rf.fit(cont_predictors, df[y])
    #    feature_importance = rf.feature_importances_.tolist()
    #    # generate a table with all the variables and their rankings
    #    predictor_table = pd.DataFrame(
    #        list(zip(cont_predictor_col_names, feature_importance)),
    #        columns=["Predictors", "Feature Importances"],
    #    )

    #   return predictor_table

    # move the average mean of response here
    def avg_mean_of_response(self, predictor, predictor_type):
        x = predictor
        y = self.response
        if predictor_type == "continuous":
            bin_count = 10
            bins = pd.cut(x=self.df[x], bins=bin_count)
            averages = self.df[y].groupby(bins).mean()
            bins = bins.value_counts()
            counts_df = bins.to_frame().reset_index()
            df2 = averages.to_frame().reset_index()
            counts_df = counts_df.rename(columns={"index": "bins", x: "counts"})
        else:
            bin_count = len(self.df[x].unique())
            averages = self.df.groupby(x, as_index=False)[y].mean()
            counts_df = self.df.groupby(x, as_index=False)[y].count()
            counts_df = counts_df.rename(columns={x: "bins", y: "counts"})
            df2 = averages.reset_index()

        df2["means"] = df2[y]
        df2["population mean"] = self.df[y].mean()

        df2["difference with mean of response"] = df2.apply(
            lambda z: z["population mean"] - z["means"], axis=1
        )
        df2["squared difference"] = (
            1 / bin_count * np.power(df2["difference with mean of response"], 2)
        )

        df2_merged = pd.merge(
            left=df2, right=counts_df, how="left", left_on=x, right_on="bins"
        )
        df2_merged["population"] = df2_merged["counts"].sum()
        df2_merged["weighted difference with mean of response"] = df2_merged.apply(
            lambda z: np.power((z["population mean"] - z["means"]), 2)
            * z["counts"]
            / z["population"],
            axis=1,
        )
        DMR_result = df2["squared difference"].sum()
        DWMR_result = df2_merged["weighted difference with mean of response"].sum()

        diff_fig = make_subplots(specs=[[{"secondary_y": True}]])
        diff_fig.add_trace(
            go.Bar(x=df2_merged.index, y=df2_merged["counts"], name="count"),
            secondary_y=False,
        )
        diff_fig.add_trace(
            go.Scatter(
                x=df2_merged.index,
                y=df2_merged["means"],
                mode="lines",
                name="bin mean of response",
            ),
            secondary_y=True,
        )
        # diff_fig.add_trace(
        #     go.Scatter(
        #         x=df2_merged.index,
        #         y=df2_merged["weighted difference with mean of response"],
        #         mode="lines",
        #         name="bin weighted mean of response",
        #     ),
        #     secondary_y=True,
        # )
        diff_fig.add_trace(
            go.Scatter(
                x=df2_merged.index,
                y=df2_merged["population mean"],
                mode="lines",
                name="pop mean",
            ),
            secondary_y=True,
        )
        diff_fig.update_layout(bargap=0.1)

        plot_name = (
            "/results/"
            + predictor
            + " binned difference with mean of response (weighted and unweighted).html"
        )
        diff_fig.write_html(file=plot_name, include_plotlyjs="cdn")
        return DMR_result, DWMR_result, plot_name

    def two_variable_AMR(
        self, predictor1, predictor1_type, predictor2, predictor2_type
    ):
        # Testing for diff mean of response with 2 variables
        x1 = predictor1
        x2 = predictor2
        y = self.response
        df = self.df
        # dynamic bin column naming
        x1_bins = x1 + " bins"
        x2_bins = x2 + " bins"
        # create the bins
        if predictor1_type == "continuous":
            x1_bin_count = 10
            df[x1_bins] = pd.cut(x=df[x1], bins=x1_bin_count)
        else:
            x1_bin_count = len(df[x1].unique())
            df[x1_bins] = df[x1]
            # bin_count = len(self.df[x].unique())
            # averages =self.df.groupby(x, as_index=False)[y].mean()
            # counts_df = self.df.groupby(x, as_index=False)[y].count()
            # counts_df = counts_df.rename(columns={x:'bins',y:'counts'})
            # df2 = averages.reset_index()
        if predictor2_type == "continuous":
            x2_bin_count = 10
            df[x2_bins] = pd.cut(x=df[x2], bins=x2_bin_count)
        else:
            x2_bin_count = len(df[x2].unique())
            df[x2_bins] = df[x2]
        # average and mean
        # definitely not sure about this bin count
        bin_count = x1_bin_count * x2_bin_count
        averages = df.groupby([x1_bins, x2_bins]).agg({y: np.mean}).reset_index()
        counts = df.groupby([x1_bins, x2_bins]).agg({y: np.size}).reset_index()

        # rename mean column
        averages.rename(columns={y: "mean"}, inplace=True)
        # merge average and counts
        averages = pd.merge(
            averages,
            counts,
            how="left",
            left_on=[x1_bins, x2_bins],
            right_on=[x1_bins, x2_bins],
        )
        # rename counts column
        averages.rename(columns={y: "count"}, inplace=True)

        # set the population mean
        averages["population mean"] = df[y].mean()
        averages["population"] = averages["count"].sum()

        # calculate the AMR
        averages["difference with mean of response"] = averages.apply(
            lambda z: z["population mean"] - z["mean"], axis=1
        )
        averages["squared difference"] = (
            1 / bin_count * np.power(averages["difference with mean of response"], 2)
        )
        averages["weighted difference with mean of response"] = averages.apply(
            lambda z: np.power((z["population mean"] - z["mean"]), 2)
            * z["count"]
            / z["population"],
            axis=1,
        )
        DMR_result = [averages["squared difference"].sum()]
        DWMR_result = [averages["weighted difference with mean of response"].sum()]

        # first plot for average mean of response
        plotly_data = {
            "z": averages["difference with mean of response"].tolist(),
            "x": averages[x1_bins].astype(str).tolist(),
            "y": averages[x2_bins].astype(str).tolist(),
        }

        fig = go.Figure(data=go.Heatmap(plotly_data))
        fig.update_layout(
            title="Difference with Mean of Response for " + y,
            xaxis_title=x1 + " binned",
            yaxis_title=x2 + " binned",
        )
        filename = (
            "/results/" + x1 + "_" + x2 + " Difference with mean of response.html"
        )
        fig.write_html(file=filename, include_plotlyjs="cdn")

        # 2nd plot for weighted
        plotly_data2 = {
            "z": averages["weighted difference with mean of response"].tolist(),
            "x": averages[x1_bins].astype(str).tolist(),
            "y": averages[x2_bins].astype(str).tolist(),
        }

        fig2 = go.Figure(data=go.Heatmap(plotly_data2))
        fig2.update_layout(
            title="Weighted difference with Mean of Response for " + y,
            xaxis_title=x1 + " binned",
            yaxis_title=x2 + " binned",
        )
        filename2 = (
            "/results/"
            + x1
            + "_"
            + x2
            + " Weighted difference with mean of response.html"
        )
        fig2.write_html(file=filename2, include_plotlyjs="cdn")

        return [DMR_result, DWMR_result, filename, filename2]
