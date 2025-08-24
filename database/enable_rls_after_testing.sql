-- =====================================================
-- REHABILITAR RLS DESPUÉS DEL TESTING
-- =====================================================
-- Ejecutar este archivo en Supabase SQL Editor para
-- rehabilitar las políticas RLS después del testing

-- Habilitar RLS nuevamente
ALTER TABLE conversation_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversation_messages ENABLE ROW LEVEL SECURITY;

-- Verificar que RLS está habilitado
SELECT 
    schemaname,
    tablename,
    rowsecurity
FROM pg_tables 
WHERE tablename IN ('conversation_sessions', 'conversation_messages');

-- Mostrar mensaje de confirmación
SELECT 'RLS rehabilitado - Sistema seguro para producción' as status;
