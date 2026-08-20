import pandas as pd


def preparar_datos(df):

    df["fecha"] = pd.to_datetime(
        df["fecha"],
        format="%d/%m/%Y"
    )

    df["fecha_texto"] = (
        df["fecha"].dt.strftime("%d/%m/%Y")
    )

    df["hora_inicio_actividad"] = pd.to_datetime(
        df["hora_inicio_actividad"],
        format="%H:%M"
    )

    df["hora_fin_actividad"] = pd.to_datetime(
        df["hora_fin_actividad"],
        format="%H:%M"
    )

    df["hora_ingreso"] = pd.to_datetime(
        df["hora_ingreso"],
        format="%H:%M"
    )

    df["hora_egreso"] = pd.to_datetime(
        df["hora_egreso"],
        format="%H:%M"
    )

    df["permanencia"] = (
        df["hora_egreso"]
        - df["hora_ingreso"]
    )

    df["permanencia_minutos"] = (
        df["permanencia"]
        / pd.Timedelta(minutes=1)
    )

    return df