-- Prepara el esquema para una futura edición de datos (sin
-- construir todavía la pantalla de edición ni un login real).
--
-- 1. "updated_at" en participaciones: sirve para mostrar "última
--    modificación" y para detectar conflictos si dos personas
--    editan la misma carga al mismo tiempo (comparar contra el
--    valor que tenía cuando se cargó, antes de guardar).
--
-- 2. "participacion_id" en asistencias_dia: hoy esa tabla se
--    relaciona con participaciones solo por el valor de texto
--    "documento", sin foreign key real. Si en algún momento se
--    edita un documento (para corregir un typo, por ejemplo), la
--    asistencia de esa persona queda huérfana sin ningún error.
--    Con esta columna, el guardado (utils/guardado_historico.py)
--    pasa a enlazar por id en vez de por texto.
--
-- La tabla de auditoría de cambios queda para más adelante,
-- cuando se construya la edición en sí.

alter table participaciones
    add column if not exists updated_at timestamptz not null default now();

alter table asistencias_dia
    add column if not exists participacion_id
        uuid references participaciones(id) on delete cascade;

create index if not exists idx_asistencias_dia_participacion_id
    on asistencias_dia (participacion_id);
