#!/bin/bash
# build_files.sh

echo "🚀 Iniciando build de Vercel..."

# Instalar dependencias
echo "📦 Instalando dependencias..."
pip install -r requirements.txt

# Recolectar archivos estáticos
echo "🎨 Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

# 🔥 EJECUTAR MIGRACIONES (Esto creará la tabla auth_user en PostgreSQL)
echo "📦 Ejecutando migraciones forzadas en PostgreSQL..."
python manage.py migrate --noinput

# 🔥 SINCRONIZAR USUARIOS DE MONGODB A POSTGRESQL
echo "🔄 Sincronizando usuarios desde MongoDB a PostgreSQL..."
python manage.py sync_users

echo "✅ Build completado exitosamente!"