-- Deshabilitar RLS (Row Level Security) para las tablas de dietas
-- Ejecutar en Supabase SQL Editor cuando necesites acceso completo para testing/desarrollo

-- ==============================================
-- DESHABILITAR RLS PARA TABLAS DE DIETAS
-- ==============================================

-- Tabla de alimentos
ALTER TABLE foods DISABLE ROW LEVEL SECURITY;

-- Tabla de planes de dieta
ALTER TABLE diet_plans DISABLE ROW LEVEL SECURITY;

-- Tabla de comidas planificadas
ALTER TABLE planned_meals DISABLE ROW LEVEL SECURITY;

-- Tabla de ingredientes de comidas planificadas
ALTER TABLE planned_meal_ingredients DISABLE ROW LEVEL SECURITY;

-- Tabla de comidas consumidas
ALTER TABLE consumed_meals DISABLE ROW LEVEL SECURITY;

-- Tabla de ingredientes consumidos
ALTER TABLE consumed_meal_ingredients DISABLE ROW LEVEL SECURITY;

-- Tabla de resumen nutricional diario
ALTER TABLE daily_nutrition_summary DISABLE ROW LEVEL SECURITY;

-- Tabla de sustituciones de alimentos
ALTER TABLE food_substitutions DISABLE ROW LEVEL SECURITY;

-- ==============================================
-- ELIMINAR POLÍTICAS EXISTENTES (OPCIONAL)
-- ==============================================

-- Políticas para foods
DROP POLICY IF EXISTS "Everyone can read foods" ON foods;
DROP POLICY IF EXISTS "Only admins can modify foods" ON foods;

-- Políticas para diet_plans
DROP POLICY IF EXISTS "Users can view their own diet plans" ON diet_plans;
DROP POLICY IF EXISTS "Users can create diet plans" ON diet_plans;
DROP POLICY IF EXISTS "Users can update their own diet plans" ON diet_plans;
DROP POLICY IF EXISTS "Users can delete their own diet plans" ON diet_plans;

-- Políticas para planned_meals
DROP POLICY IF EXISTS "Users can view planned meals from their diet plans" ON planned_meals;
DROP POLICY IF EXISTS "Users can create planned meals in their diet plans" ON planned_meals;
DROP POLICY IF EXISTS "Users can update planned meals from their diet plans" ON planned_meals;
DROP POLICY IF EXISTS "Users can delete planned meals from their diet plans" ON planned_meals;

-- Políticas para planned_meal_ingredients
DROP POLICY IF EXISTS "Users can view ingredients from their planned meals" ON planned_meal_ingredients;
DROP POLICY IF EXISTS "Users can create ingredients in their planned meals" ON planned_meal_ingredients;
DROP POLICY IF EXISTS "Users can update ingredients from their planned meals" ON planned_meal_ingredients;
DROP POLICY IF EXISTS "Users can delete ingredients from their planned meals" ON planned_meal_ingredients;

-- Políticas para consumed_meals
DROP POLICY IF EXISTS "Users can view their own consumed meals" ON consumed_meals;
DROP POLICY IF EXISTS "Users can create consumed meals" ON consumed_meals;
DROP POLICY IF EXISTS "Users can update their own consumed meals" ON consumed_meals;
DROP POLICY IF EXISTS "Users can delete their own consumed meals" ON consumed_meals;

-- Políticas para consumed_meal_ingredients
DROP POLICY IF EXISTS "Users can view ingredients from their consumed meals" ON consumed_meal_ingredients;
DROP POLICY IF EXISTS "Users can create ingredients in their consumed meals" ON consumed_meal_ingredients;
DROP POLICY IF EXISTS "Users can update ingredients from their consumed meals" ON consumed_meal_ingredients;
DROP POLICY IF EXISTS "Users can delete ingredients from their consumed meals" ON consumed_meal_ingredients;

-- Políticas para daily_nutrition_summary
DROP POLICY IF EXISTS "Users can view their own nutrition summary" ON daily_nutrition_summary;
DROP POLICY IF EXISTS "Users can create nutrition summary" ON daily_nutrition_summary;
DROP POLICY IF EXISTS "Users can update their own nutrition summary" ON daily_nutrition_summary;
DROP POLICY IF EXISTS "Users can delete their own nutrition summary" ON daily_nutrition_summary;

-- Políticas para food_substitutions
DROP POLICY IF EXISTS "Everyone can read food substitutions" ON food_substitutions;
DROP POLICY IF EXISTS "Only admins can modify food substitutions" ON food_substitutions;

-- ==============================================
-- VERIFICACIÓN
-- ==============================================

-- Consulta para verificar que RLS está deshabilitado
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

-- Consulta para verificar políticas restantes
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
