import os

# Definimos la estructura basada en la guía [cite: 49-127]
folders = [
    ".github/workflows",
    "src/sre/config",
    "src/sre/data",
    "src/sre/retrieval",
    "src/sre/generation",
    "src/sre/monitoring",
    "src/sre/api",
    "src/sre/utils",
    "tests/unit",
    "tests/integration",
    "tests/llm_tests",
    "mlops/mlflow",
    "mlops/monitoring/grafana/dashboards",
    "notebooks/experiments",
    "docs"
]

files = [
    "src/__init__.py",
    "src/sre/__init__.py",
    "src/sre/config/__init__.py",
    "src/sre/data/__init__.py",
    "src/sre/retrieval/__init__.py",
    "src/sre/generation/__init__.py",
    "src/sre/monitoring/__init__.py",
    "src/sre/api/__init__.py",
    "src/sre/utils/__init__.py",
    "tests/__init__.py",
    ".env.example",
    ".gitignore",
    "README.md"
]

# Crear carpetas
for folder in folders:
    os.makedirs(folder, exist_ok=True)
    print(f"Creada carpeta: {folder}")

# Crear archivos vacíos (init)
for file in files:
    with open(file, 'w') as f:
        pass
    print(f"Creado archivo: {file}")

print("\n✅ Estructura de proyecto completada.")