
-- Correr manualmente en el editor SQL de Supabase. No hay filas
-- reales que se pierdan: las tablas viejas están vacías al momento
-- de esta migración.

drop table if exists asistencias_dia cascade;
drop table if exists participaciones cascade;
drop table if exists cargas cascade;
drop table if exists jornadas cascade;

create table jornadas (
    id uuid primary key default gen_random_uuid(),
    anio integer not null unique,
    fecha_inicio date not null,
    fecha_fin date not null,
    created_at timestamptz not null default now()
);

create table cargas (
    id uuid primary key default gen_random_uuid(),
    jornada_id uuid not null references jornadas(id) on delete cascade,
    numero_carga integer not null,
    fecha_carga timestamptz not null default now(),
    unique (jornada_id, numero_carga)
);

create table participaciones (
    id uuid primary key default gen_random_uuid(),
    carga_id uuid not null references cargas(id) on delete cascade,
    nombre text,
    apellido text,
    documento text,
    mail text,
    miembro_unla text,
    rol_principal text,
    otro_rol_principal text,
    investigador_carreras text,
    otro_investigador_carreras text,
    tipo_inscripcion text,
    source text,
    is_welcome_mail_sent boolean,
    qr_code text,
    is_present_original boolean,
    is_assistance_certify_sent boolean,
    asistio boolean,
    -- Columnas del Excel que todavía no tienen una columna propia
    -- (ej. un campo nuevo agregado al formulario de inscripción).
    -- Ver utils/guardado_historico.py::columnas_no_mapeadas.
    datos_extra jsonb
);

-- Asistencia día por día. No se modela como columnas fijas porque
-- las fechas cambian de edición a edición (ver utils/limpieza_datos.py
-- ::detectar_columnas_asistencia / construir_asistencia_larga, que
-- arman esto mismo en memoria antes de guardarlo acá).
create table asistencias_dia (
    id uuid primary key default gen_random_uuid(),
    carga_id uuid not null references cargas(id) on delete cascade,
    documento text,
    fecha date not null,
    asistio boolean not null
);
