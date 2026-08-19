#!/bin/bash
# build_files.sh - Optimizado para Vercel con PostgreSQL

echo "🚀 Iniciando build de Vercel..."

# 1. Instalar dependencias
echo "📦 Instalando dependencias..."
pip install -r requirements.txt

# 2. Recolectar archivos estáticos (CRÍTICO para Vercel)
echo "🎨 Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

# 3. Ejecutar migraciones (SIEMPRE, sin verificar SQLite)
echo "📦 Ejecutando migraciones en PostgreSQL..."
python manage.py migrate --noinput

# 4. Sincronizar usuarios desde MongoDB a PostgreSQL
echo "🔄 Sincronizando usuarios desde MongoDB..."
python manage.py sync_users

echo "✅ Build completado exitosamente!"