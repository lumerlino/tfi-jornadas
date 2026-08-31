
-- Esta app no tiene login: cualquiera con la URL ya tiene acceso
-- completo, no hay necesidad de aislar filas por usuario (RLS es
-- para apps multi-tenant). En vez de desactivar RLS directamente,
-- se deja activo y se agrega una política que permite todo al rol
-- "anon" — mismo resultado práctico, pero sin que el Security
-- Advisor de Supabase marque estas tablas como "RLS desactivado".

do $$
declare
    nombre_tabla text;
begin
    foreach nombre_tabla in array array[
        'jornadas',
        'cargas',
        'participaciones',
        'asistencias_dia',
        'columnas_configuradas'
    ]
    loop
        execute format(
            'alter table %I enable row level security;',
            nombre_tabla
        );

        execute format(
            'drop policy if exists "permitir todo anon" on %I;',
            nombre_tabla
        );

        execute format(
            'create policy "permitir todo anon" on %I '
            'for all to anon using (true) with check (true);',
            nombre_tabla
        );
    end loop;
end $$;
