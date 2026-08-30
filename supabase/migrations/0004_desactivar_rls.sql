
-- Esta app no tiene login: cualquiera con la URL ya tiene acceso
-- completo, no hay necesidad de aislar filas por usuario (RLS es
-- para apps multi-tenant). Se desactiva en vez de armar políticas
-- que no aportan nada acá.

alter table jornadas disable row level security;
alter table cargas disable row level security;
alter table participaciones disable row level security;
alter table asistencias_dia disable row level security;
alter table columnas_configuradas disable row level security;
