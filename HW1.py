import sys

import numpy as np
import pandas as pd
import plotly.express as px
from sklearn.ensemble import AdaBoostClassifier, RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier


def main():
    # import data into pandas df
    names = ["Sepal Length", "Sepal Width", "Petal Length", "Petal Width", "Class"]
    df = pd.read_csv("iris.data", names=names)
    df_norm = pd.melt(df, id_vars=["Class"])

    # print out summary statistics
    print("Means:")
    print(np.mean(df[{"Sepal Length", "Sepal Width", "Petal Length", "Petal Width"}]))
    print("Mins")
    print(np.min(df[{"Sepal Length", "Sepal Width", "Petal Length", "Petal Width"}]))
    print("Maxes")
    print(np.max(df[{"Sepal Length", "Sepal Width", "Petal Length", "Petal Width"}]))
    print("25th percentiles:")
    print(df.quantile(0.25, numeric_only=True))
    print("50th percentiles:")
    print(df.quantile(0.50, numeric_only=True))
    print("75th percentiles:")
    print(df.quantile(0.75, numeric_only=True))

    # plotly charts
    sepal_plots = {}
    petal_plots = {}
    for unique_class in df["Class"].unique():
        plot = px.scatter(
            df[df["Class"] == unique_class],
            x="Sepal Length",
            y="Sepal Width",
            title=unique_class,
        )
        sepal_plots[unique_class] = plot
        plot2 = px.scatter(
            df[df["Class"] == unique_class],
            x="Petal Length",
            y="Petal Width",
            title=unique_class,
        )
        petal_plots[unique_class] = plot2

    for key in sepal_plots:
        sepal_plots[key].show()

    for key in petal_plots:
        sepal_plots[key].show()

    # cool bar
    means = df.groupby("Class").mean().reset_index()
    bar = px.bar(means, x="Class", y="Sepal Length", color="Class")
    bar.show()

    # violin
    violin = px.violin(df_norm, x="variable", y="value", color="Class")
    violin.show()

    # scatter matrix
    scatter = px.scatter_matrix(
        df,
        dimensions=["Sepal Length", "Sepal Width", "Petal Length", "Petal Width"],
        color="Class",
    )
    scatter.show()

    # parallel categories
    parallel = px.parallel_categories(
        df_norm, color="value", color_continuous_scale=px.colors.sequential.Purp
    )
    parallel.show()

    # sklearn
    y = df["Class"]
    x_orig = df[["Sepal Length", "Sepal Width", "Petal Length", "Petal Width"]]

    # pipelines
    forest_pipe = Pipeline(
        [
            ("StandardScaler", StandardScaler()),
            ("RandomForest", RandomForestClassifier(random_state=4321)),
        ]
    )
    forest_pipe.fit(x_orig, y)
    forest_prediction = forest_pipe.predict(x_orig)
    print(f"Random Forest Predictions: {forest_prediction}")

    decision_pipe = Pipeline(
        [
            ("StandardScaler", StandardScaler()),
            ("DecisionTree", DecisionTreeClassifier(random_state=4321)),
        ]
    )
    decision_pipe.fit(x_orig, y)
    decision_prediction = decision_pipe.predict(x_orig)
    print(f"Decision Tree Predictions: {decision_prediction}")

    Ada_pipe = Pipeline(
        [
            ("StandardScaler", StandardScaler()),
            ("AdaBoost", AdaBoostClassifier(random_state=4321)),
        ]
    )
    Ada_pipe.fit(x_orig, y)
    Ada_prediction = Ada_pipe.predict(x_orig)
    print(f"AdaBoost Predictions: {Ada_prediction}")
    return


if __name__ == "__main__":
    sys.exit(main())
