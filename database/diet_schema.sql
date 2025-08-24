-- Esquema de base de datos para el sistema de nutrición y dietas
-- Ejecutar en Supabase SQL Editor

-- ==============================================
-- TABLAS DE ALIMENTOS Y INFORMACIÓN NUTRICIONAL
-- ==============================================

-- Tabla de alimentos base (información nutricional por 100g)
CREATE TABLE IF NOT EXISTS foods (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    name_es VARCHAR(255) NOT NULL, -- Nombre en español
    category VARCHAR(100) NOT NULL, -- 'proteinas', 'carbohidratos', 'grasas', 'verduras', 'frutas', 'lacteos', 'legumbres', 'granos', 'condimentos'
    
    -- Macronutrientes por 100g
    calories_per_100g DECIMAL(6,2) NOT NULL,
    protein_per_100g DECIMAL(5,2) NOT NULL DEFAULT 0,
    carbs_per_100g DECIMAL(5,2) NOT NULL DEFAULT 0,
    fat_per_100g DECIMAL(5,2) NOT NULL DEFAULT 0,
    fiber_per_100g DECIMAL(5,2) NOT NULL DEFAULT 0,
    sugar_per_100g DECIMAL(5,2) NOT NULL DEFAULT 0,
    
    -- Micronutrientes por 100g (opcionales pero importantes)
    sodium_mg_per_100g DECIMAL(8,2) DEFAULT 0,
    potassium_mg_per_100g DECIMAL(8,2) DEFAULT 0,
    calcium_mg_per_100g DECIMAL(8,2) DEFAULT 0,
    iron_mg_per_100g DECIMAL(8,2) DEFAULT 0,
    vitamin_c_mg_per_100g DECIMAL(8,2) DEFAULT 0,
    
    -- Información adicional
    glycemic_index INTEGER, -- Índice glucémico (0-100)
    common_serving_size_g DECIMAL(6,2), -- Tamaño de porción común en gramos
    serving_description VARCHAR(100), -- Descripción de la porción (ej: "1 taza", "1 pieza mediana")
    
    -- Flags útiles para filtros
    is_vegetarian BOOLEAN DEFAULT true,
    is_vegan BOOLEAN DEFAULT false,
    is_gluten_free BOOLEAN DEFAULT true,
    is_dairy_free BOOLEAN DEFAULT true,
    is_low_carb BOOLEAN DEFAULT false, -- < 10g carbos por 100g
    is_high_protein BOOLEAN DEFAULT false, -- > 15g proteína por 100g
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ==============================================
-- TABLAS DE PLANES DE DIETA
-- ==============================================

-- Tabla de planes de dieta personalizados
CREATE TABLE IF NOT EXISTS diet_plans (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Información básica del plan
    name VARCHAR(255) NOT NULL,
    description TEXT,
    plan_type VARCHAR(50) NOT NULL, -- 'perdida_peso', 'ganancia_musculo', 'mantenimiento', 'definicion'
    
    -- Objetivos nutricionales diarios
    target_calories INTEGER NOT NULL,
    target_protein_g DECIMAL(6,2) NOT NULL,
    target_carbs_g DECIMAL(6,2) NOT NULL,
    target_fat_g DECIMAL(6,2) NOT NULL,
    target_fiber_g DECIMAL(6,2) DEFAULT 25,
    
    -- Configuración de comidas
    meals_per_day INTEGER DEFAULT 5, -- Número de comidas al día
    breakfast_calories_percent DECIMAL(4,2) DEFAULT 25.00, -- Porcentaje de calorías para desayuno
    lunch_calories_percent DECIMAL(4,2) DEFAULT 30.00,     -- Almuerzo
    dinner_calories_percent DECIMAL(4,2) DEFAULT 25.00,    -- Cena
    snack1_calories_percent DECIMAL(4,2) DEFAULT 10.00,    -- Colación 1
    snack2_calories_percent DECIMAL(4,2) DEFAULT 10.00,    -- Colación 2
    
    -- Configuración de horarios (formato HH:MM)
    breakfast_time TIME DEFAULT '07:00',
    snack1_time TIME DEFAULT '10:00',
    lunch_time TIME DEFAULT '13:00',
    snack2_time TIME DEFAULT '16:00',
    dinner_time TIME DEFAULT '19:00',
    
    -- Restricciones alimentarias
    dietary_restrictions TEXT[], -- Array de restricciones: 'vegetariano', 'vegano', 'sin_gluten', 'sin_lactosa', etc.
    food_allergies TEXT[], -- Array de alergias alimentarias
    disliked_foods TEXT[], -- Array de alimentos que no le gustan
    
    -- Control de estado
    is_active BOOLEAN DEFAULT true,
    start_date DATE DEFAULT CURRENT_DATE,
    end_date DATE,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by_agent VARCHAR(100) DEFAULT 'nutrition_agent'
);

-- ==============================================
-- TABLAS DE COMIDAS PLANIFICADAS Y CONSUMIDAS
-- ==============================================

-- Tabla de comidas planificadas (template diario)
CREATE TABLE IF NOT EXISTS planned_meals (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    diet_plan_id UUID NOT NULL REFERENCES diet_plans(id) ON DELETE CASCADE,
    
    -- Información de la comida
    meal_type VARCHAR(50) NOT NULL, -- 'desayuno', 'colacion_1', 'almuerzo', 'colacion_2', 'cena'
    meal_name VARCHAR(255) NOT NULL,
    meal_time TIME NOT NULL,
    
    -- Objetivos nutricionales de la comida
    target_calories INTEGER NOT NULL,
    target_protein_g DECIMAL(6,2) NOT NULL,
    target_carbs_g DECIMAL(6,2) NOT NULL,
    target_fat_g DECIMAL(6,2) NOT NULL,
    
    -- Receta/instrucciones
    preparation_instructions TEXT,
    cooking_time_minutes INTEGER,
    difficulty_level VARCHAR(20) DEFAULT 'facil', -- 'facil', 'medio', 'dificil'
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla de ingredientes de comidas planificadas
CREATE TABLE IF NOT EXISTS planned_meal_ingredients (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    planned_meal_id UUID NOT NULL REFERENCES planned_meals(id) ON DELETE CASCADE,
    food_id UUID NOT NULL REFERENCES foods(id),
    
    -- Cantidad del ingrediente
    quantity_grams DECIMAL(8,2) NOT NULL,
    
    -- Valores nutricionales calculados para esta cantidad
    calories DECIMAL(8,2) NOT NULL,
    protein_g DECIMAL(6,2) NOT NULL,
    carbs_g DECIMAL(6,2) NOT NULL,
    fat_g DECIMAL(6,2) NOT NULL,
    
    -- Notas sobre el ingrediente (opcional, cocido, crudo, etc.)
    notes VARCHAR(255),
    is_optional BOOLEAN DEFAULT false,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ==============================================
-- TABLAS DE CONSUMO REAL
-- ==============================================

-- Tabla de comidas consumidas (registro diario real)
CREATE TABLE IF NOT EXISTS consumed_meals (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    diet_plan_id UUID REFERENCES diet_plans(id), -- Puede ser NULL si come algo fuera del plan
    planned_meal_id UUID REFERENCES planned_meals(id), -- NULL si no sigue el plan exactamente
    
    -- Información de la comida consumida
    meal_type VARCHAR(50) NOT NULL,
    meal_name VARCHAR(255) NOT NULL,
    consumed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    consumption_date DATE DEFAULT CURRENT_DATE,
    
    -- Valores nutricionales totales consumidos
    total_calories DECIMAL(8,2) NOT NULL DEFAULT 0,
    total_protein_g DECIMAL(6,2) NOT NULL DEFAULT 0,
    total_carbs_g DECIMAL(6,2) NOT NULL DEFAULT 0,
    total_fat_g DECIMAL(6,2) NOT NULL DEFAULT 0,
    total_fiber_g DECIMAL(6,2) NOT NULL DEFAULT 0,
    
    -- Estado y notas
    adherence_score DECIMAL(3,2) DEFAULT 1.0, -- Qué tan bien siguió el plan (0.0 - 1.0)
    satisfaction_rating INTEGER CHECK (satisfaction_rating >= 1 AND satisfaction_rating <= 5), -- 1-5 estrellas
    notes TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla de ingredientes consumidos
CREATE TABLE IF NOT EXISTS consumed_meal_ingredients (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    consumed_meal_id UUID NOT NULL REFERENCES consumed_meals(id) ON DELETE CASCADE,
    food_id UUID NOT NULL REFERENCES foods(id),
    
    -- Cantidad consumida
    quantity_grams DECIMAL(8,2) NOT NULL,
    
    -- Valores nutricionales para esta cantidad
    calories DECIMAL(8,2) NOT NULL,
    protein_g DECIMAL(6,2) NOT NULL,
    carbs_g DECIMAL(6,2) NOT NULL,
    fat_g DECIMAL(6,2) NOT NULL,
    
    -- Información adicional
    was_planned BOOLEAN DEFAULT false, -- Si este ingrediente estaba en el plan original
    substitution_for_food_id UUID REFERENCES foods(id), -- Si es sustitución de otro alimento
    notes VARCHAR(255),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ==============================================
-- TABLAS DE ANÁLISIS Y PROGRESO
-- ==============================================

-- Tabla de resumen nutricional diario
CREATE TABLE IF NOT EXISTS daily_nutrition_summary (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    diet_plan_id UUID REFERENCES diet_plans(id),
    
    summary_date DATE NOT NULL,
    
    -- Objetivos del día
    target_calories INTEGER NOT NULL,
    target_protein_g DECIMAL(6,2) NOT NULL,
    target_carbs_g DECIMAL(6,2) NOT NULL,
    target_fat_g DECIMAL(6,2) NOT NULL,
    
    -- Consumo real del día
    consumed_calories DECIMAL(8,2) NOT NULL DEFAULT 0,
    consumed_protein_g DECIMAL(6,2) NOT NULL DEFAULT 0,
    consumed_carbs_g DECIMAL(6,2) NOT NULL DEFAULT 0,
    consumed_fat_g DECIMAL(6,2) NOT NULL DEFAULT 0,
    consumed_fiber_g DECIMAL(6,2) NOT NULL DEFAULT 0,
    
    -- Análisis
    calorie_deficit_surplus DECIMAL(8,2) NOT NULL DEFAULT 0, -- Negativo = déficit, Positivo = superávit
    adherence_percentage DECIMAL(5,2) DEFAULT 0, -- Porcentaje de adherencia al plan
    meals_completed INTEGER DEFAULT 0,
    meals_planned INTEGER DEFAULT 0,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(user_id, summary_date)
);

-- ==============================================
-- TABLAS DE SUSTITUCIONES Y EQUIVALENCIAS
-- ==============================================

-- Tabla de sustituciones de alimentos (para mantener macros similares)
CREATE TABLE IF NOT EXISTS food_substitutions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    original_food_id UUID NOT NULL REFERENCES foods(id),
    substitute_food_id UUID NOT NULL REFERENCES foods(id),
    
    -- Factor de conversión (cuánto del sustituto equivale a 100g del original)
    conversion_factor DECIMAL(6,4) DEFAULT 1.0000,
    
    -- Tipo de sustitución
    substitution_type VARCHAR(50) NOT NULL, -- 'equivalent', 'similar_macros', 'similar_calories', 'dietary_restriction'
    
    -- Notas sobre la sustitución
    notes TEXT,
    confidence_score DECIMAL(3,2) DEFAULT 1.0, -- Qué tan buena es la sustitución (0.0 - 1.0)
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(original_food_id, substitute_food_id)
);

-- ==============================================
-- ÍNDICES PARA OPTIMIZACIÓN
-- ==============================================

-- Índices para foods
CREATE INDEX IF NOT EXISTS idx_foods_category ON foods(category);
CREATE INDEX IF NOT EXISTS idx_foods_name ON foods(name);
CREATE INDEX IF NOT EXISTS idx_foods_name_es ON foods(name_es);
CREATE INDEX IF NOT EXISTS idx_foods_dietary_flags ON foods(is_vegetarian, is_vegan, is_gluten_free, is_dairy_free);

-- Índices para diet_plans
CREATE INDEX IF NOT EXISTS idx_diet_plans_user_id ON diet_plans(user_id);
CREATE INDEX IF NOT EXISTS idx_diet_plans_active ON diet_plans(is_active);
CREATE INDEX IF NOT EXISTS idx_diet_plans_type ON diet_plans(plan_type);

-- Índices para planned_meals
CREATE INDEX IF NOT EXISTS idx_planned_meals_diet_plan ON planned_meals(diet_plan_id);
CREATE INDEX IF NOT EXISTS idx_planned_meals_type ON planned_meals(meal_type);
CREATE INDEX IF NOT EXISTS idx_planned_meals_time ON planned_meals(meal_time);

-- Índices para consumed_meals
CREATE INDEX IF NOT EXISTS idx_consumed_meals_user_id ON consumed_meals(user_id);
CREATE INDEX IF NOT EXISTS idx_consumed_meals_date ON consumed_meals(consumption_date);
CREATE INDEX IF NOT EXISTS idx_consumed_meals_type ON consumed_meals(meal_type);
CREATE INDEX IF NOT EXISTS idx_consumed_meals_consumed_at ON consumed_meals(consumed_at);

-- Índices para daily_nutrition_summary
CREATE INDEX IF NOT EXISTS idx_daily_nutrition_user_date ON daily_nutrition_summary(user_id, summary_date);
CREATE INDEX IF NOT EXISTS idx_daily_nutrition_date ON daily_nutrition_summary(summary_date);

-- ==============================================
-- TRIGGERS Y FUNCIONES
-- ==============================================

-- Trigger para actualizar updated_at en las tablas necesarias
CREATE TRIGGER update_foods_updated_at BEFORE UPDATE ON foods
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_diet_plans_updated_at BEFORE UPDATE ON diet_plans
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_planned_meals_updated_at BEFORE UPDATE ON planned_meals
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_daily_nutrition_summary_updated_at BEFORE UPDATE ON daily_nutrition_summary
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Función para calcular valores nutricionales automáticamente
CREATE OR REPLACE FUNCTION calculate_nutrition_values()
RETURNS TRIGGER AS $$
BEGIN
    -- Calcular valores nutricionales basados en la cantidad y el alimento
    SELECT 
        (NEW.quantity_grams / 100.0) * f.calories_per_100g,
        (NEW.quantity_grams / 100.0) * f.protein_per_100g,
        (NEW.quantity_grams / 100.0) * f.carbs_per_100g,
        (NEW.quantity_grams / 100.0) * f.fat_per_100g
    INTO 
        NEW.calories,
        NEW.protein_g,
        NEW.carbs_g,
        NEW.fat_g
    FROM foods f
    WHERE f.id = NEW.food_id;
    
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Aplicar el trigger a las tablas de ingredientes
CREATE TRIGGER calculate_planned_meal_nutrition 
    BEFORE INSERT OR UPDATE ON planned_meal_ingredients
    FOR EACH ROW EXECUTE FUNCTION calculate_nutrition_values();

CREATE TRIGGER calculate_consumed_meal_nutrition 
    BEFORE INSERT OR UPDATE ON consumed_meal_ingredients
    FOR EACH ROW EXECUTE FUNCTION calculate_nutrition_values();

-- Función para actualizar totales de comidas
CREATE OR REPLACE FUNCTION update_meal_totals()
RETURNS TRIGGER AS $$
DECLARE
    target_meal_id UUID;
    target_table TEXT;
BEGIN
    -- Determinar qué tabla y ID usar
    IF TG_TABLE_NAME = 'planned_meal_ingredients' THEN
        target_meal_id := COALESCE(NEW.planned_meal_id, OLD.planned_meal_id);
        target_table := 'planned_meals';
    ELSIF TG_TABLE_NAME = 'consumed_meal_ingredients' THEN
        target_meal_id := COALESCE(NEW.consumed_meal_id, OLD.consumed_meal_id);
        target_table := 'consumed_meals';
    END IF;
    
    -- Actualizar totales
    IF target_table = 'consumed_meals' THEN
        UPDATE consumed_meals 
        SET 
            total_calories = (SELECT COALESCE(SUM(calories), 0) FROM consumed_meal_ingredients WHERE consumed_meal_id = target_meal_id),
            total_protein_g = (SELECT COALESCE(SUM(protein_g), 0) FROM consumed_meal_ingredients WHERE consumed_meal_id = target_meal_id),
            total_carbs_g = (SELECT COALESCE(SUM(carbs_g), 0) FROM consumed_meal_ingredients WHERE consumed_meal_id = target_meal_id),
            total_fat_g = (SELECT COALESCE(SUM(fat_g), 0) FROM consumed_meal_ingredients WHERE consumed_meal_id = target_meal_id)
        WHERE id = target_meal_id;
    ELSIF target_table = 'planned_meals' THEN
        UPDATE planned_meals 
        SET 
            target_calories = (SELECT COALESCE(SUM(calories), 0) FROM planned_meal_ingredients WHERE planned_meal_id = target_meal_id),
            target_protein_g = (SELECT COALESCE(SUM(protein_g), 0) FROM planned_meal_ingredients WHERE planned_meal_id = target_meal_id),
            target_carbs_g = (SELECT COALESCE(SUM(carbs_g), 0) FROM planned_meal_ingredients WHERE planned_meal_id = target_meal_id),
            target_fat_g = (SELECT COALESCE(SUM(fat_g), 0) FROM planned_meal_ingredients WHERE planned_meal_id = target_meal_id)
        WHERE id = target_meal_id;
    END IF;
    
    RETURN COALESCE(NEW, OLD);
END;
$$ language 'plpgsql';

-- Aplicar triggers para actualizar totales
CREATE TRIGGER update_planned_meal_totals_trigger 
    AFTER INSERT OR UPDATE OR DELETE ON planned_meal_ingredients
    FOR EACH ROW EXECUTE FUNCTION update_meal_totals();

CREATE TRIGGER update_consumed_meal_totals_trigger 
    AFTER INSERT OR UPDATE OR DELETE ON consumed_meal_ingredients
    FOR EACH ROW EXECUTE FUNCTION update_meal_totals();

-- ==============================================
-- POLÍTICAS DE SEGURIDAD (RLS)
-- ==============================================

-- Habilitar RLS para todas las tablas de dieta
ALTER TABLE foods ENABLE ROW LEVEL SECURITY;
ALTER TABLE diet_plans ENABLE ROW LEVEL SECURITY;
ALTER TABLE planned_meals ENABLE ROW LEVEL SECURITY;
ALTER TABLE planned_meal_ingredients ENABLE ROW LEVEL SECURITY;
ALTER TABLE consumed_meals ENABLE ROW LEVEL SECURITY;
ALTER TABLE consumed_meal_ingredients ENABLE ROW LEVEL SECURITY;
ALTER TABLE daily_nutrition_summary ENABLE ROW LEVEL SECURITY;
ALTER TABLE food_substitutions ENABLE ROW LEVEL SECURITY;

-- Políticas para foods (lectura pública, modificación solo admin)
CREATE POLICY "Everyone can read foods" ON foods
    FOR SELECT USING (true);

CREATE POLICY "Only admins can modify foods" ON foods
    FOR ALL USING (current_setting('app.user_role', true) = 'admin');

-- Políticas para diet_plans (usuarios solo pueden ver y modificar los suyos)
CREATE POLICY "Users can view their own diet plans" ON diet_plans
    FOR SELECT USING (user_id::text = current_setting('app.current_user_id', true));

CREATE POLICY "Users can create diet plans" ON diet_plans
    FOR INSERT WITH CHECK (user_id::text = current_setting('app.current_user_id', true));

CREATE POLICY "Users can update their own diet plans" ON diet_plans
    FOR UPDATE USING (user_id::text = current_setting('app.current_user_id', true))
    WITH CHECK (user_id::text = current_setting('app.current_user_id', true));

CREATE POLICY "Users can delete their own diet plans" ON diet_plans
    FOR DELETE USING (user_id::text = current_setting('app.current_user_id', true));

-- Políticas para planned_meals (a través de diet_plans)
CREATE POLICY "Users can view planned meals from their diet plans" ON planned_meals
    FOR SELECT USING (
        diet_plan_id IN (
            SELECT id FROM diet_plans 
            WHERE user_id::text = current_setting('app.current_user_id', true)
        )
    );

CREATE POLICY "Users can create planned meals in their diet plans" ON planned_meals
    FOR INSERT WITH CHECK (
        diet_plan_id IN (
            SELECT id FROM diet_plans 
            WHERE user_id::text = current_setting('app.current_user_id', true)
        )
    );

CREATE POLICY "Users can update planned meals from their diet plans" ON planned_meals
    FOR UPDATE USING (
        diet_plan_id IN (
            SELECT id FROM diet_plans 
            WHERE user_id::text = current_setting('app.current_user_id', true)
        )
    ) WITH CHECK (
        diet_plan_id IN (
            SELECT id FROM diet_plans 
            WHERE user_id::text = current_setting('app.current_user_id', true)
        )
    );

CREATE POLICY "Users can delete planned meals from their diet plans" ON planned_meals
    FOR DELETE USING (
        diet_plan_id IN (
            SELECT id FROM diet_plans 
            WHERE user_id::text = current_setting('app.current_user_id', true)
        )
    );

-- Políticas similares para el resto de tablas...
-- [Las políticas siguen el mismo patrón: acceso solo a datos propios del usuario]

-- Políticas para consumed_meals
CREATE POLICY "Users can view their own consumed meals" ON consumed_meals
    FOR SELECT USING (user_id::text = current_setting('app.current_user_id', true));

CREATE POLICY "Users can create consumed meals" ON consumed_meals
    FOR INSERT WITH CHECK (user_id::text = current_setting('app.current_user_id', true));

CREATE POLICY "Users can update their own consumed meals" ON consumed_meals
    FOR UPDATE USING (user_id::text = current_setting('app.current_user_id', true))
    WITH CHECK (user_id::text = current_setting('app.current_user_id', true));

CREATE POLICY "Users can delete their own consumed meals" ON consumed_meals
    FOR DELETE USING (user_id::text = current_setting('app.current_user_id', true));

-- Políticas para daily_nutrition_summary
CREATE POLICY "Users can view their own nutrition summary" ON daily_nutrition_summary
    FOR SELECT USING (user_id::text = current_setting('app.current_user_id', true));

CREATE POLICY "Users can create nutrition summary" ON daily_nutrition_summary
    FOR INSERT WITH CHECK (user_id::text = current_setting('app.current_user_id', true));

CREATE POLICY "Users can update their own nutrition summary" ON daily_nutrition_summary
    FOR UPDATE USING (user_id::text = current_setting('app.current_user_id', true))
    WITH CHECK (user_id::text = current_setting('app.current_user_id', true));

-- Políticas para food_substitutions (lectura pública)
CREATE POLICY "Everyone can read food substitutions" ON food_substitutions
    FOR SELECT USING (true);

CREATE POLICY "Only admins can modify food substitutions" ON food_substitutions
    FOR ALL USING (current_setting('app.user_role', true) = 'admin');
