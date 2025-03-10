#!/bin/bash

# Directorio base de indigo_drivers
INDIGO_DRIVERS_DIR="./indigo-master/indigo_drivers"

# Función para verificar si un archivo es un enlace simbólico roto
check_symlink() {
    local file="$1"
    if [ -L "$file" ] && [ ! -e "$file" ]; then
        return 0  # Es un enlace roto
    else
        return 1  # No es un enlace roto
    fi
}

# Función para restaurar enlaces específicos conocidos
restore_known_links() {
    local driver_dir="$1"
    local base_name=$(basename "$driver_dir")
    
    # Caso específico para ccd_qhy2
    if [[ "$base_name" == "ccd_qhy2" ]]; then
        if [ -f "$driver_dir/indigo_ccd_qhy2.cpp" ]; then
            echo "Restaurando enlace para $driver_dir/indigo_ccd_qhy2.cpp"
            rm "$driver_dir/indigo_ccd_qhy2.cpp"
            ln -s "../ccd_qhy/indigo_ccd_qhy.cpp" "$driver_dir/indigo_ccd_qhy2.cpp"
        fi
    fi
    
    # Añadir más casos específicos aquí si se conocen
}

# Función principal
main() {
    echo "Iniciando verificación de enlaces simbólicos en $INDIGO_DRIVERS_DIR"
    
    # Recorrer todos los subdirectorios
    for dir in "$INDIGO_DRIVERS_DIR"/*/ ; do
        if [ -d "$dir" ]; then
            echo "Verificando directorio: $dir"
            
            # Buscar todos los archivos en el directorio
            find "$dir" -type l -exec sh -c '
                for link; do
                    if [ ! -e "$link" ]; then
                        echo "Enlace roto encontrado: $link"
                    fi
                done
            ' sh {} +
            
            # Intentar restaurar enlaces conocidos
            restore_known_links "$dir"
        fi
    done
    
    echo "Verificación completada"
}

# Ejecutar el script
main

# Verificar resultado
echo "Verificando resultado final..."
find "$INDIGO_DRIVERS_DIR" -type l -exec sh -c '
    for link; do
        if [ ! -e "$link" ]; then
            echo "ADVERTENCIA: Enlace aún roto: $link"
        fi
    done
' sh {} +