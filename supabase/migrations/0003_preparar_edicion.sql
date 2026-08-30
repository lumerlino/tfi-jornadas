
alter table participaciones
    add column if not exists updated_at timestamptz not null default now();

alter table asistencias_dia
    add column if not exists participacion_id
        uuid references participaciones(id) on delete cascade;

create index if not exists idx_asistencias_dia_participacion_id
    on asistencias_dia (participacion_id);
