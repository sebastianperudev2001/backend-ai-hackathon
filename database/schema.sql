-- Esquema de base de datos para el sistema de fitness
-- Ejecutar en Supabase SQL Editor

-- Tabla de usuarios
CREATE TABLE IF NOT EXISTS users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    phone_number VARCHAR(20) NOT NULL UNIQUE, -- Número de WhatsApp
    name VARCHAR(255),
    email VARCHAR(255),
    age INTEGER,
    gender VARCHAR(20), -- 'masculino', 'femenino', 'otro'
    height_cm INTEGER, -- Altura en centímetros
    weight_kg DECIMAL(5,2), -- Peso en kilogramos
    fitness_level VARCHAR(50) DEFAULT 'principiante', -- 'principiante', 'intermedio', 'avanzado'
    goals TEXT[], -- Array de objetivos: 'perder_peso', 'ganar_musculo', 'resistencia', etc.
    medical_conditions TEXT[], -- Condiciones médicas relevantes
    preferences JSONB, -- Preferencias adicionales en formato JSON
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_activity_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla de rutinas de ejercicio
CREATE TABLE IF NOT EXISTS workouts (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    started_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    ended_at TIMESTAMP WITH TIME ZONE,
    duration_minutes INTEGER, -- Calculado automáticamente
    total_sets INTEGER DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla de ejercicios (catálogo)
CREATE TABLE IF NOT EXISTS exercises (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    category VARCHAR(100) NOT NULL, -- 'fuerza', 'cardio', 'flexibilidad'
    muscle_groups TEXT[], -- Array de grupos musculares
    equipment VARCHAR(255), -- Equipo necesario
    instructions TEXT,
    difficulty_level VARCHAR(50), -- 'principiante', 'intermedio', 'avanzado'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla de series de ejercicios
CREATE TABLE IF NOT EXISTS workout_sets (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    workout_id UUID NOT NULL REFERENCES workouts(id) ON DELETE CASCADE,
    exercise_id UUID NOT NULL REFERENCES exercises(id),
    set_number INTEGER NOT NULL, -- Número de serie dentro del ejercicio
    weight DECIMAL(6,2), -- Peso utilizado
    weight_unit VARCHAR(10) DEFAULT 'kg', -- 'kg', 'lbs'
    repetitions INTEGER, -- Número de repeticiones
    duration_seconds INTEGER, -- Para ejercicios de tiempo (plancha, etc.)
    distance_meters DECIMAL(8,2), -- Para ejercicios de distancia (correr, etc.)
    rest_seconds INTEGER, -- Tiempo de descanso después de la serie
    difficulty_rating INTEGER CHECK (difficulty_rating >= 1 AND difficulty_rating <= 10), -- 1-10
    notes TEXT,
    completed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para mejorar performance
CREATE INDEX IF NOT EXISTS idx_users_phone_number ON users(phone_number);
CREATE INDEX IF NOT EXISTS idx_users_fitness_level ON users(fitness_level);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);
CREATE INDEX IF NOT EXISTS idx_workouts_user_id ON workouts(user_id);
CREATE INDEX IF NOT EXISTS idx_workouts_started_at ON workouts(started_at);
CREATE INDEX IF NOT EXISTS idx_workout_sets_workout_id ON workout_sets(workout_id);
CREATE INDEX IF NOT EXISTS idx_workout_sets_exercise_id ON workout_sets(exercise_id);
CREATE INDEX IF NOT EXISTS idx_exercises_category ON exercises(category);
CREATE INDEX IF NOT EXISTS idx_exercises_difficulty ON exercises(difficulty_level);

-- Trigger para actualizar updated_at automáticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_workouts_updated_at BEFORE UPDATE ON workouts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_exercises_updated_at BEFORE UPDATE ON exercises
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Trigger para calcular duración del workout automáticamente
CREATE OR REPLACE FUNCTION calculate_workout_duration()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.ended_at IS NOT NULL AND NEW.started_at IS NOT NULL THEN
        NEW.duration_minutes = EXTRACT(EPOCH FROM (NEW.ended_at - NEW.started_at)) / 60;
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER calculate_workout_duration_trigger BEFORE UPDATE ON workouts
    FOR EACH ROW EXECUTE FUNCTION calculate_workout_duration();

-- Trigger para actualizar total_sets en workouts
CREATE OR REPLACE FUNCTION update_workout_total_sets()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE workouts 
    SET total_sets = (
        SELECT COUNT(*) 
        FROM workout_sets 
        WHERE workout_id = COALESCE(NEW.workout_id, OLD.workout_id)
    )
    WHERE id = COALESCE(NEW.workout_id, OLD.workout_id);
    RETURN COALESCE(NEW, OLD);
END;
$$ language 'plpgsql';

CREATE TRIGGER update_workout_total_sets_trigger 
    AFTER INSERT OR DELETE ON workout_sets
    FOR EACH ROW EXECUTE FUNCTION update_workout_total_sets();

-- Insertar algunos ejercicios básicos
INSERT INTO exercises (name, category, muscle_groups, equipment, instructions, difficulty_level) VALUES
-- Ejercicios de fuerza
('Flexiones', 'fuerza', ARRAY['pecho', 'triceps', 'hombros'], 'ninguno', 'Posición de plancha, bajar el pecho hasta casi tocar el suelo y subir', 'principiante'),
('Sentadillas', 'fuerza', ARRAY['cuadriceps', 'gluteos', 'pantorrillas'], 'ninguno', 'Pies separados al ancho de hombros, bajar como si te sentaras en una silla', 'principiante'),
('Plancha', 'fuerza', ARRAY['core', 'hombros'], 'ninguno', 'Mantener posición de flexión sin moverse', 'principiante'),
('Dominadas', 'fuerza', ARRAY['espalda', 'biceps'], 'barra', 'Colgarse de la barra y subir hasta que el mentón pase la barra', 'avanzado'),
('Lunges', 'fuerza', ARRAY['cuadriceps', 'gluteos'], 'ninguno', 'Dar un paso adelante y bajar la rodilla trasera hacia el suelo', 'intermedio'),

-- Ejercicios de cardio
('Burpees', 'cardio', ARRAY['todo_el_cuerpo'], 'ninguno', 'Flexión, salto hacia atrás, salto hacia adelante, salto vertical', 'intermedio'),
('Jumping Jacks', 'cardio', ARRAY['todo_el_cuerpo'], 'ninguno', 'Saltar abriendo piernas y brazos simultáneamente', 'principiante'),
('Mountain Climbers', 'cardio', ARRAY['core', 'piernas'], 'ninguno', 'Posición de plancha, alternar rodillas hacia el pecho', 'intermedio'),
('Correr', 'cardio', ARRAY['piernas', 'cardiovascular'], 'ninguno', 'Trotar o correr a ritmo constante', 'principiante'),

-- Ejercicios de flexibilidad
('Estiramiento de cuadriceps', 'flexibilidad', ARRAY['cuadriceps'], 'ninguno', 'De pie, doblar rodilla hacia atrás y sostener el pie', 'principiante'),
('Estiramiento de isquiotibiales', 'flexibilidad', ARRAY['isquiotibiales'], 'ninguno', 'Sentado, extender una pierna y alcanzar los dedos del pie', 'principiante'),
('Gato-Vaca', 'flexibilidad', ARRAY['espalda'], 'ninguno', 'En cuatro patas, arquear y redondear la espalda alternadamente', 'principiante')

ON CONFLICT (name) DO NOTHING;

-- Habilitar Row Level Security (RLS) para seguridad
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE workouts ENABLE ROW LEVEL SECURITY;
ALTER TABLE workout_sets ENABLE ROW LEVEL SECURITY;
ALTER TABLE exercises ENABLE ROW LEVEL SECURITY;

-- Políticas de seguridad básicas
-- Los usuarios pueden ver y modificar solo su propio perfil
CREATE POLICY "Users can manage their own profile" ON users
    FOR ALL USING (id::text = current_setting('app.current_user_id', true));

-- Los usuarios pueden ver y modificar solo sus propios workouts
CREATE POLICY "Users can manage their own workouts" ON workouts
    FOR ALL USING (user_id::text = current_setting('app.current_user_id', true));

-- Los workout_sets están vinculados a workouts, así que heredan la seguridad
CREATE POLICY "Users can manage sets from their workouts" ON workout_sets
    FOR ALL USING (
        workout_id IN (
            SELECT id FROM workouts 
            WHERE user_id::text = current_setting('app.current_user_id', true)
        )
    );

-- Los ejercicios son públicos (todos pueden leerlos)
CREATE POLICY "Everyone can read exercises" ON exercises
    FOR SELECT USING (true);

-- Solo administradores pueden modificar ejercicios (opcional)
CREATE POLICY "Only admins can modify exercises" ON exercises
    FOR ALL USING (current_setting('app.user_role', true) = 'admin');

-- Insertar usuario demo para pruebas
INSERT INTO users (
    phone_number, 
    name, 
    fitness_level, 
    goals, 
    preferences
) VALUES (
    '+51998555878',
    'Usuario Demo',
    'principiante',
    ARRAY['ganar_musculo', 'mejorar_resistencia'],
    '{"preferred_workout_time": "morning", "language": "es", "notifications": true}'::jsonb
) ON CONFLICT (phone_number) DO UPDATE SET
    name = EXCLUDED.name,
    fitness_level = EXCLUDED.fitness_level,
    goals = EXCLUDED.goals,
    preferences = EXCLUDED.preferences,
    updated_at = NOW();
