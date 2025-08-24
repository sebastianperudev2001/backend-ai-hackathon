-- =====================================================
-- DESHABILITAR RLS TEMPORALMENTE PARA TESTING
-- =====================================================
-- Ejecutar este archivo en Supabase SQL Editor para
-- deshabilitar temporalmente las políticas RLS y poder
-- hacer testing del sistema de memoria

-- IMPORTANTE: Solo usar en desarrollo/testing
-- NO ejecutar en producción

-- Deshabilitar RLS temporalmente
ALTER TABLE conversation_sessions DISABLE ROW LEVEL SECURITY;
ALTER TABLE conversation_messages DISABLE ROW LEVEL SECURITY;

-- Verificar que RLS está deshabilitado
SELECT 
    schemaname,
    tablename,
    rowsecurity
FROM pg_tables 
WHERE tablename IN ('conversation_sessions', 'conversation_messages');

-- Mostrar mensaje de confirmación
SELECT 'RLS deshabilitado para testing - RECUERDA HABILITARLO DESPUÉS' as status;
