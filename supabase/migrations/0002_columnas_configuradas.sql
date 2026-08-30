--
-- Guarda, por columna de Excel no contemplada en el esquema fijo,
-- qué nombre mostrar y qué métrica/gráfico (si alguno) generar.
-- Ver utils/clasificacion_columnas.py y utils/configuracion_columnas.py.

create table if not exists columnas_configuradas (
    id uuid primary key default gen_random_uuid(),
    columna_excel text not null unique,
    nombre_display text not null,
    tipo_dato text not null,
    metrica text not null,
    creado_en timestamptz not null default now()
);
