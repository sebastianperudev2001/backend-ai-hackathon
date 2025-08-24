-- =====================================================
-- MIGRACIÓN DE SISTEMA DE MEMORIA PARA CHATBOT IA
-- =====================================================
-- Ejecutar este archivo en el SQL Editor de Supabase
-- para agregar las tablas de memoria al sistema existente

-- Tabla de sesiones de conversación
CREATE TABLE IF NOT EXISTS conversation_sessions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_name VARCHAR(255), -- Nombre opcional de la sesión
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_activity_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT true,
    metadata JSONB, -- Información adicional sobre la sesión
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla de mensajes de conversación
CREATE TABLE IF NOT EXISTS conversation_messages (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    session_id UUID NOT NULL REFERENCES conversation_sessions(id) ON DELETE CASCADE,
    message_type VARCHAR(20) NOT NULL CHECK (message_type IN ('human', 'ai', 'system', 'function')),
    content TEXT NOT NULL,
    metadata JSONB, -- Para almacenar información adicional como tool calls, context, etc.
    agent_name VARCHAR(100), -- Qué agente generó el mensaje (si es AI)
    token_count INTEGER, -- Número de tokens del mensaje
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para optimizar consultas de memoria
CREATE INDEX IF NOT EXISTS idx_conversation_sessions_user_id ON conversation_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_conversation_sessions_active ON conversation_sessions(is_active);
CREATE INDEX IF NOT EXISTS idx_conversation_sessions_last_activity ON conversation_sessions(last_activity_at);
CREATE INDEX IF NOT EXISTS idx_conversation_messages_session_id ON conversation_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_conversation_messages_created_at ON conversation_messages(created_at);
CREATE INDEX IF NOT EXISTS idx_conversation_messages_type ON conversation_messages(message_type);

-- Trigger para actualizar last_activity_at en sessions cuando se agrega un mensaje
CREATE OR REPLACE FUNCTION update_session_activity()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE conversation_sessions 
    SET last_activity_at = NOW(),
        updated_at = NOW()
    WHERE id = NEW.session_id;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_session_activity_trigger 
    AFTER INSERT ON conversation_messages
    FOR EACH ROW EXECUTE FUNCTION update_session_activity();

-- Trigger para actualizar updated_at en conversation_sessions
CREATE TRIGGER update_conversation_sessions_updated_at BEFORE UPDATE ON conversation_sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Habilitar Row Level Security (RLS) para las nuevas tablas
ALTER TABLE conversation_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversation_messages ENABLE ROW LEVEL SECURITY;

-- Políticas de seguridad para conversation_sessions
CREATE POLICY "Users can view their own conversation sessions" ON conversation_sessions
    FOR SELECT USING (user_id::text = current_setting('app.current_user_id', true));

CREATE POLICY "Users can create conversation sessions" ON conversation_sessions
    FOR INSERT WITH CHECK (user_id::text = current_setting('app.current_user_id', true));

CREATE POLICY "Users can update their own conversation sessions" ON conversation_sessions
    FOR UPDATE USING (user_id::text = current_setting('app.current_user_id', true))
    WITH CHECK (user_id::text = current_setting('app.current_user_id', true));

CREATE POLICY "Users can delete their own conversation sessions" ON conversation_sessions
    FOR DELETE USING (user_id::text = current_setting('app.current_user_id', true));

-- Políticas de seguridad para conversation_messages
CREATE POLICY "Users can view messages from their sessions" ON conversation_messages
    FOR SELECT USING (
        session_id IN (
            SELECT id FROM conversation_sessions 
            WHERE user_id::text = current_setting('app.current_user_id', true)
        )
    );

CREATE POLICY "Users can create messages in their sessions" ON conversation_messages
    FOR INSERT WITH CHECK (
        session_id IN (
            SELECT id FROM conversation_sessions 
            WHERE user_id::text = current_setting('app.current_user_id', true)
        )
    );

CREATE POLICY "Users can update messages from their sessions" ON conversation_messages
    FOR UPDATE USING (
        session_id IN (
            SELECT id FROM conversation_sessions 
            WHERE user_id::text = current_setting('app.current_user_id', true)
        )
    ) WITH CHECK (
        session_id IN (
            SELECT id FROM conversation_sessions 
            WHERE user_id::text = current_setting('app.current_user_id', true)
        )
    );

CREATE POLICY "Users can delete messages from their sessions" ON conversation_messages
    FOR DELETE USING (
        session_id IN (
            SELECT id FROM conversation_sessions 
            WHERE user_id::text = current_setting('app.current_user_id', true)
        )
    );

-- =====================================================
-- VERIFICACIÓN DE LA MIGRACIÓN
-- =====================================================

-- Verificar que las tablas fueron creadas
SELECT 'conversation_sessions' as table_name, COUNT(*) as record_count FROM conversation_sessions
UNION ALL
SELECT 'conversation_messages' as table_name, COUNT(*) as record_count FROM conversation_messages;

-- Mostrar estructura de las tablas
SELECT 
    table_name,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns 
WHERE table_name IN ('conversation_sessions', 'conversation_messages')
ORDER BY table_name, ordinal_position;
