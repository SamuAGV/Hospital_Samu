🏥 MedInsight Hospital - Sistema Integral de Gestión Hospitalaria
📋 Descripción
MedInsight Hospital es un sistema integral de gestión hospitalaria desarrollado con Django, MongoDB y Machine Learning. Permite administrar pacientes, citas, consultas, hospitalizaciones, laboratorio, farmacia, y ofrece análisis avanzados con modelos predictivos.

🚀 Tecnologías Utilizadas
Tecnología	Versión	Descripción
Python	3.11+	Lenguaje de programación
Django	4.2.7	Framework web
MongoDB Atlas	Última	Base de datos NoSQL
SQLite	-	Base de datos para sesiones
scikit-learn	1.3.2	Machine Learning
Plotly	5.18.0	Visualización de datos
Bootstrap	5.3.2	Framework CSS
Font Awesome	6.4.2	Iconos
📦 Requisitos Previos
1. Python
bash
# Verificar versión de Python
python --version
# Debe ser Python 3.11 o superior
2. MongoDB Atlas (Cuenta gratuita)
Crear cuenta en MongoDB Atlas

Crear un cluster (gratuito)

Obtener la cadena de conexión

3. Git
bash
# Verificar que Git esté instalado
git --version
🔧 Instalación Paso a Paso
1. Clonar el repositorio
bash
# Clonar el repositorio
git clone <URL_DEL_REPOSITORIO>
cd hospital

# O si tienes el proyecto en un archivo zip, extraerlo
unzip medinsight-hospital.zip
cd medinsight-hospital
2. Crear y activar entorno virtual
bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual (Windows)
venv\Scripts\activate

# Activar entorno virtual (Mac/Linux)
source venv/bin/activate
3. Instalar dependencias
bash
# Instalar todas las dependencias
pip install -r requirements.txt
Si el archivo requirements.txt no existe, crearlo con:
bash
cat > requirements.txt << 'EOF'
asgiref==3.12.1
certifi==2026.7.22
crispy-bootstrap5==0.7
Django==4.2.7
django-crispy-forms==2.1
dnspython==2.4.2
joblib==1.3.2
numpy==1.26.2
pandas==2.1.4
plotly==5.18.0
pymongo==4.6.0
python-dotenv==1.0.0
scikit-learn==1.3.2
scipy==1.16.3
sqlparse==0.6.0
tenacity==9.1.4
threadpoolctl==3.6.0
EOF

pip install -r requirements.txt
4. Configurar variables de entorno
bash
# Crear archivo .env
cat > .env << 'EOF'
# Django Settings
SECRET_KEY=django-insecure-change-me-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# MongoDB Settings
MONGO_URI=mongodb+srv://USUARIO:CONTRASENA@cluster0.xxxxx.mongodb.net/
MONGO_DB_NAME=medinsight_hospital
EOF
⚠️ IMPORTANTE: Reemplazar USUARIO y CONTRASENA con tus credenciales de MongoDB Atlas.

5. Verificar conexión a MongoDB
bash
# Verificar conexión
python check_mongodb.py
Resultado esperado:

text
✅ Conectado a MongoDB: medinsight_hospital
📁 Colecciones en medinsight_hospital:
  (No hay colecciones creadas)
6. Crear usuario administrador
bash
# Crear usuario admin en MongoDB
python create_admin_mongodb.py

# Sincronizar usuarios a Django
python sync_users_to_django.py
Credenciales predeterminadas:

Usuario: admin

Contraseña: admin123

7. Migrar base de datos SQLite
bash
# Crear tablas de Django
python manage.py migrate
8. Migrar modelos de Machine Learning (opcional)
bash
# Migrar modelos ML (si existen)
python ml/migrate_models.py
9. Insertar datos de prueba (opcional)
bash
# Insertar datos masivos (1200 pacientes, 3000 citas, etc.)
python insert_big_data.py

# O insertar solo datos básicos
python insert_test_data.py
10. Ejecutar el servidor
bash
# Iniciar servidor de desarrollo
python manage.py runserver
11. Acceder al sistema
Abrir navegador en: http://localhost:8000/

Credenciales:

Usuario: admin

Contraseña: admin123

📂 Estructura del Proyecto
text
hospital/
├── apps/                          # Módulos Django
│   ├── core/                      # Núcleo (dashboard, utilidades)
│   ├── users/                     # Autenticación y usuarios
│   ├── patients/                  # Gestión de pacientes
│   ├── appointments/              # Gestión de citas
│   ├── consultations/             # Gestión de consultas
│   ├── hospitalizations/          # Gestión de hospitalizaciones
│   ├── emergency/                 # Gestión de urgencias
│   ├── laboratory/                # Gestión de laboratorio
│   ├── pharmacy/                  # Gestión de farmacia
│   ├── specialties/               # Gestión de especialidades
│   ├── analytics/                 # Análisis y gráficas
│   ├── machine_learning/          # Modelos de Machine Learning
│   └── reports/                   # Generación de reportes
├── hospital_project/              # Configuración Django
│   ├── settings.py                # Configuración principal
│   ├── urls.py                    # Rutas principales
│   └── wsgi.py                    # Configuración WSGI
├── templates/                     # Templates HTML
│   ├── base.html                  # Template base
│   ├── core/                      # Templates del core
│   ├── users/                     # Templates de usuarios
│   └── ...                        # Módulos
├── static/                        # Archivos estáticos
│   ├── css/                       # Estilos CSS
│   └── js/                        # JavaScript
├── ml/                            # Modelos ML
│   └── modelos/                   # Modelos entrenados (.pkl)
├── scripts/                       # Scripts de utilidad
│   ├── check_mongodb.py           # Verificar conexión
│   ├── create_admin_mongodb.py    # Crear admin
│   ├── sync_users_to_django.py    # Sincronizar usuarios
│   └── insert_big_data.py         # Insertar datos masivos
├── manage.py                      # Comando de Django
├── requirements.txt               # Dependencias
└── .env                          # Variables de entorno
📋 Módulos del Sistema
Módulo	URL	Descripción
Dashboard	/	Resumen general y gráficas
Pacientes	/patients/	CRUD de pacientes
Citas	/appointments/	Agendamiento y gestión de citas
Consultas	/consultations/	Registro de consultas médicas
Hospitalización	/hospitalizations/	Ingresos, altas y ocupación
Urgencias	/emergency/	Registro de urgencias
Laboratorio	/laboratory/	Solicitudes y resultados
Farmacia	/pharmacy/	Medicamentos e inventario
Especialidades	/specialties/	Catálogo de especialidades
Machine Learning	/ml/	Predicciones y modelos
Análisis	/analytics/	Gráficas y mapas de calor
Reportes	/reports/	Reportes y exportaciones
Configuración	/users/settings/	Preferencias de usuario
🔧 Comandos Útiles
Scripts de Utilidad
bash
# Verificar conexión a MongoDB
python check_mongodb.py

# Verificar usuarios en MongoDB
python check_users.py

# Crear usuario admin en MongoDB
python create_admin_mongodb.py

# Sincronizar usuarios de MongoDB a Django
python sync_users_to_django.py

# Insertar datos masivos (1200 pacientes, 3000 citas, etc.)
python insert_big_data.py

# Insertar datos de prueba básicos
python insert_test_data.py

# Eliminar todos los datos de MongoDB
python delete_all_data.py

# Migrar modelos de Machine Learning
python ml/migrate_models.py
Comandos Django
bash
# Ejecutar servidor de desarrollo
python manage.py runserver

# Crear superusuario en Django
python manage.py createsuperuser

# Ejecutar migraciones
python manage.py migrate

# Crear migraciones
python manage.py makemigrations

# Verificar sintaxis
python manage.py check

# Abrir shell de Django
python manage.py shell
Limpiar caché
bash
# Eliminar archivos __pycache__
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null

# Eliminar archivos .pyc
find . -type f -name "*.pyc" -delete
🐛 Solución de Problemas Comunes
Error: MongoDB no conectado
bash
# Verificar que la URI en .env es correcta
cat .env | grep MONGO_URI

# Probar conexión manual
python check_mongodb.py
Error: Usuario no encontrado
bash
# Crear usuario admin nuevamente
python create_admin_mongodb.py
python sync_users_to_django.py
Error: Tablas de Django no existen
bash
python manage.py migrate
Error: No se ven datos en el dashboard
bash
# Insertar datos de prueba
python insert_big_data.py
Error: Módulo no encontrado
bash
# Instalar dependencias faltantes
pip install -r requirements.txt
Error: Puerto 8000 en uso
bash
# Usar otro puerto
python manage.py runserver 8001
📊 Datos de Prueba
El script insert_big_data.py inserta:

Colección	Cantidad	Descripción
Pacientes	1,200	Datos demográficos de pacientes
Médicos	50	Médicos de diferentes especialidades
Especialidades	10	Catálogo de especialidades
Citas	3,000	Citas con diferentes estados
Consultas	3,000	Consultas médicas
Hospitalizaciones	500	Ingresos y altas
Diagnósticos	1,000	Diagnósticos asociados a consultas
Tratamientos	800	Tratamientos asociados a consultas
Medicamentos	200	Catálogo de medicamentos
Inventario	100	Movimientos de inventario
🚀 Despliegue en Producción
Vercel
bash
# Verificar que vercel.json existe
cat vercel.json

# Desplegar en Vercel
vercel deploy

# Configurar variables de entorno en Vercel:
# - MONGO_URI
# - MONGO_DB_NAME
# - SECRET_KEY
# - DEBUG=False
Variables de Entorno para Producción
env
# Django
SECRET_KEY=tu_clave_secreta_aqui
DEBUG=False
ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com

# MongoDB
MONGO_URI=mongodb+srv://usuario:contraseña@cluster.mongodb.net/
MONGO_DB_NAME=medinsight_hospital
📚 Documentación Adicional
Django Documentation

MongoDB Documentation

scikit-learn Documentation

Plotly Documentation

📝 Licencia
Este proyecto es académico y fue desarrollado para la asignatura de Extracción del Conocimiento en Bases de Datos.

👨‍💻 Autor
Desarrollado por estudiantes de Ingeniería en Desarrollo y Gestión de Software

🙏 Agradecimientos
MGTI. Héctor Velázquez Estrada - Docente de la Comisión

M.T.I Carlos Millán Hinojosa - Director de Carrera

¡MedInsight Hospital - Inteligencia de Datos para Decisiones Clínicas! 🏥🚀

