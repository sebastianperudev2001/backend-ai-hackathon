-- Habilitar RLS (Row Level Security) para las tablas de dietas
-- Ejecutar en Supabase SQL Editor para restaurar seguridad en producción

-- ==============================================
-- HABILITAR RLS PARA TABLAS DE DIETAS
-- ==============================================

-- Tabla de alimentos
ALTER TABLE foods ENABLE ROW LEVEL SECURITY;

-- Tabla de planes de dieta
ALTER TABLE diet_plans ENABLE ROW LEVEL SECURITY;

-- Tabla de comidas planificadas
ALTER TABLE planned_meals ENABLE ROW LEVEL SECURITY;

-- Tabla de ingredientes de comidas planificadas
ALTER TABLE planned_meal_ingredients ENABLE ROW LEVEL SECURITY;

-- Tabla de comidas consumidas
ALTER TABLE consumed_meals ENABLE ROW LEVEL SECURITY;

-- Tabla de ingredientes consumidos
ALTER TABLE consumed_meal_ingredients ENABLE ROW LEVEL SECURITY;

-- Tabla de resumen nutricional diario
ALTER TABLE daily_nutrition_summary ENABLE ROW LEVEL SECURITY;

-- Tabla de sustituciones de alimentos
ALTER TABLE food_substitutions ENABLE ROW LEVEL SECURITY;

-- ==============================================
-- RECREAR POLÍTICAS DE SEGURIDAD PRINCIPALES
-- ==============================================

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

-- Políticas para planned_meal_ingredients
CREATE POLICY "Users can view ingredients from their planned meals" ON planned_meal_ingredients
    FOR SELECT USING (
        planned_meal_id IN (
            SELECT pm.id FROM planned_meals pm
            JOIN diet_plans dp ON pm.diet_plan_id = dp.id
            WHERE dp.user_id::text = current_setting('app.current_user_id', true)
        )
    );

CREATE POLICY "Users can create ingredients in their planned meals" ON planned_meal_ingredients
    FOR INSERT WITH CHECK (
        planned_meal_id IN (
            SELECT pm.id FROM planned_meals pm
            JOIN diet_plans dp ON pm.diet_plan_id = dp.id
            WHERE dp.user_id::text = current_setting('app.current_user_id', true)
        )
    );

CREATE POLICY "Users can update ingredients from their planned meals" ON planned_meal_ingredients
    FOR UPDATE USING (
        planned_meal_id IN (
            SELECT pm.id FROM planned_meals pm
            JOIN diet_plans dp ON pm.diet_plan_id = dp.id
            WHERE dp.user_id::text = current_setting('app.current_user_id', true)
        )
    ) WITH CHECK (
        planned_meal_id IN (
            SELECT pm.id FROM planned_meals pm
            JOIN diet_plans dp ON pm.diet_plan_id = dp.id
            WHERE dp.user_id::text = current_setting('app.current_user_id', true)
        )
    );

CREATE POLICY "Users can delete ingredients from their planned meals" ON planned_meal_ingredients
    FOR DELETE USING (
        planned_meal_id IN (
            SELECT pm.id FROM planned_meals pm
            JOIN diet_plans dp ON pm.diet_plan_id = dp.id
            WHERE dp.user_id::text = current_setting('app.current_user_id', true)
        )
    );

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

-- Políticas para consumed_meal_ingredients
CREATE POLICY "Users can view ingredients from their consumed meals" ON consumed_meal_ingredients
    FOR SELECT USING (
        consumed_meal_id IN (
            SELECT id FROM consumed_meals 
            WHERE user_id::text = current_setting('app.current_user_id', true)
        )
    );

CREATE POLICY "Users can create ingredients in their consumed meals" ON consumed_meal_ingredients
    FOR INSERT WITH CHECK (
        consumed_meal_id IN (
            SELECT id FROM consumed_meals 
            WHERE user_id::text = current_setting('app.current_user_id', true)
        )
    );

CREATE POLICY "Users can update ingredients from their consumed meals" ON consumed_meal_ingredients
    FOR UPDATE USING (
        consumed_meal_id IN (
            SELECT id FROM consumed_meals 
            WHERE user_id::text = current_setting('app.current_user_id', true)
        )
    ) WITH CHECK (
        consumed_meal_id IN (
            SELECT id FROM consumed_meals 
            WHERE user_id::text = current_setting('app.current_user_id', true)
        )
    );

CREATE POLICY "Users can delete ingredients from their consumed meals" ON consumed_meal_ingredients
    FOR DELETE USING (
        consumed_meal_id IN (
            SELECT id FROM consumed_meals 
            WHERE user_id::text = current_setting('app.current_user_id', true)
        )
    );

-- Políticas para daily_nutrition_summary
CREATE POLICY "Users can view their own nutrition summary" ON daily_nutrition_summary
    FOR SELECT USING (user_id::text = current_setting('app.current_user_id', true));

CREATE POLICY "Users can create nutrition summary" ON daily_nutrition_summary
    FOR INSERT WITH CHECK (user_id::text = current_setting('app.current_user_id', true));

CREATE POLICY "Users can update their own nutrition summary" ON daily_nutrition_summary
    FOR UPDATE USING (user_id::text = current_setting('app.current_user_id', true))
    WITH CHECK (user_id::text = current_setting('app.current_user_id', true));

CREATE POLICY "Users can delete their own nutrition summary" ON daily_nutrition_summary
    FOR DELETE USING (user_id::text = current_setting('app.current_user_id', true));

-- Políticas para food_substitutions (lectura pública)
CREATE POLICY "Everyone can read food substitutions" ON food_substitutions
    FOR SELECT USING (true);

CREATE POLICY "Only admins can modify food substitutions" ON food_substitutions
    FOR ALL USING (current_setting('app.user_role', true) = 'admin');

-- ==============================================
-- VERIFICACIÓN
-- ==============================================

-- Consulta para verificar que RLS está habilitado
SELECT 
    schemaname,
    tablename,
    rowsecurity,
    CASE 
        WHEN rowsecurity = true THEN '🔒 RLS HABILITADO'
        ELSE '🔓 RLS DESHABILITADO'
    END as status
FROM pg_tables 
WHERE tablename IN (
    'foods',
    'diet_plans', 
    'planned_meals',
    'planned_meal_ingredients',
    'consumed_meals',
    'consumed_meal_ingredients',
    'daily_nutrition_summary',
    'food_substitutions'
)
ORDER BY tablename;

-- Verificar que las políticas fueron creadas
SELECT 
    schemaname,
    tablename,
    policyname,
    CASE 
        WHEN cmd = 'r' THEN 'SELECT'
        WHEN cmd = 'w' THEN 'UPDATE'
        WHEN cmd = 'a' THEN 'INSERT'
        WHEN cmd = 'd' THEN 'DELETE'
        WHEN cmd = '*' THEN 'ALL'
        ELSE cmd
    END as command_type
FROM pg_policies 
WHERE tablename IN (
    'foods',
    'diet_plans', 
    'planned_meals',
    'planned_meal_ingredients',
    'consumed_meals',
    'consumed_meal_ingredients',
    'daily_nutrition_summary',
    'food_substitutions'
)
ORDER BY tablename, policyname;
