#!/bin/bash

# Verificar que se haya proporcionado al menos un argumento
if [ $# -lt 1 ]; then
    echo "Error: Debe proporcionar un archivo como argumento."
    echo "Uso: $0 <archivo.log>"
    exit 1
fi

ARCHIVO="$1"

# Verificar que el archivo exista
if [ ! -f "$ARCHIVO" ]; then
    echo "Error: El archivo '$ARCHIVO' no existe."
    exit 1
fi

# análisis del archivo
LINEAS=$(wc -l < "$ARCHIVO")
PALABRAS=$(wc -w < "$ARCHIVO")
CARACTERES=$(wc -c < "$ARCHIVO")
ERRORES=$(grep -c "ERROR" "$ARCHIVO" || true)
WARNINGS=$(grep -c "WARN" "$ARCHIVO" || true)


echo "===== REPORTE DE ANÁLISIS ====="
echo "Archivo analizado: $ARCHIVO"
echo "Cantidad de líneas: $LINEAS"
echo "Cantidad de palabras: $PALABRAS"
echo "Cantidad de caracteres: $CARACTERES"
echo "Cantidad de líneas con ERROR: $ERRORES"
echo "Cantidad de líneas con WARN: $WARNINGS"