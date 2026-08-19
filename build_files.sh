#!/bin/bash
# build_files.sh

echo "🚀 Iniciando build de Vercel..."

# Instalar dependencias
echo "📦 Instalando dependencias..."
pip install -r requirements.txt

# Recolectar archivos estáticos (CRÍTICO para Vercel)
echo "🎨 Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

# 🔥 EJECUTAR MIGRACIONES (Crea la tabla auth_user)
echo "📦 Ejecutando migraciones..."
python manage.py migrate --noinput

# 🔥 SINCRONIZAR USUARIOS (Usa tu comando sync_users)
echo "🔄 Sincronizando usuarios desde MongoDB..."
python manage.py sync_users

echo "✅ Build completado exitosamente!"