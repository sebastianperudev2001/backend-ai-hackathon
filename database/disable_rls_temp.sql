-- SCRIPT TEMPORAL PARA DESHABILITAR RLS DURANTE DESARROLLO
-- ⚠️ SOLO PARA DESARROLLO - NO USAR EN PRODUCCIÓN

-- Deshabilitar RLS temporalmente para permitir operaciones sin contexto
ALTER TABLE users DISABLE ROW LEVEL SECURITY;
ALTER TABLE workouts DISABLE ROW LEVEL SECURITY;
ALTER TABLE workout_sets DISABLE ROW LEVEL SECURITY;

-- Nota: Los ejercicios ya son públicos, no necesitan cambios

-- Para volver a habilitar RLS más tarde, ejecutar:
-- ALTER TABLE users ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE workouts ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE workout_sets ENABLE ROW LEVEL SECURITY;
