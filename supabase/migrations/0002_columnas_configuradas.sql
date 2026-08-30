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

-- Seed
insert into columnas_configuradas
    (columna_excel, nombre_display, tipo_dato, metrica)
values
    ('Rol principal', 'Rol principal', 'categorica', 'Barras'),
    ('Miembro UNLa', 'Miembro UNLa', 'booleana', 'Tasa (%)'),
    ('Tipo inscripción', 'Tipo de inscripción', 'categorica', 'Barras'),
    ('Source', 'Origen de inscripción', 'categorica', 'Barras')
on conflict (columna_excel) do nothing;
