#!/usr/bin/env python3
"""
Limpieza de datos históricos antiguos antes de nueva carga
"""

import os
import glob
from pathlib import Path
import shutil

def cleanup_historical_data():
    """Limpiar datos históricos antiguos"""
    print("🧹 LIMPIEZA DE DATOS HISTÓRICOS ANTIGUOS")
    print("="*50)
    
    # Directorios a limpiar
    cleanup_dirs = [
        "historical_data/individual",
        "historical_data"
    ]
    
    total_files_removed = 0
    total_size_freed = 0
    
    for directory in cleanup_dirs:
        if os.path.exists(directory):
            print(f"\n📂 Limpiando: {directory}")
            
            if directory == "historical_data/individual":
                # Limpiar archivos CSV individuales
                csv_files = glob.glob(f"{directory}/*.csv")
                print(f"   📊 Archivos CSV encontrados: {len(csv_files)}")
                
                for csv_file in csv_files:
                    try:
                        size = os.path.getsize(csv_file)
                        os.remove(csv_file)
                        total_files_removed += 1
                        total_size_freed += size
                        if len(csv_files) <= 10:  # Solo mostrar detalles si son pocos
                            print(f"   ✅ Eliminado: {os.path.basename(csv_file)}")
                    except Exception as e:
                        print(f"   ❌ Error eliminando {csv_file}: {e}")
                
                if len(csv_files) > 10:
                    print(f"   ✅ Eliminados: {len(csv_files)} archivos CSV")
            
            elif directory == "historical_data":
                # Limpiar archivos combinados antiguos
                combined_files = glob.glob(f"{directory}/combined_historical_data_*.csv") 
                report_files = glob.glob(f"{directory}/load_report_*.txt")
                
                all_files = combined_files + report_files
                print(f"   📊 Archivos de carga encontrados: {len(all_files)}")
                
                for file_path in all_files:
                    try:
                        size = os.path.getsize(file_path)
                        os.remove(file_path)
                        total_files_removed += 1
                        total_size_freed += size
                        print(f"   ✅ Eliminado: {os.path.basename(file_path)}")
                    except Exception as e:
                        print(f"   ❌ Error eliminando {file_path}: {e}")
        else:
            print(f"   ℹ️  Directorio no existe: {directory}")
    
    # Convertir tamaño a MB
    size_mb = total_size_freed / (1024 * 1024)
    
    print(f"\n📊 RESUMEN DE LIMPIEZA:")
    print(f"   • Archivos eliminados: {total_files_removed}")
    print(f"   • Espacio liberado: {size_mb:.1f} MB")
    
    if total_files_removed > 0:
        print(f"   ✅ Directorio limpio y listo para nueva carga")
    else:
        print(f"   ℹ️  No había archivos antiguos que limpiar")

def verify_cleanup():
    """Verificar que la limpieza fue exitosa"""
    print(f"\n🔍 VERIFICACIÓN POST-LIMPIEZA:")
    print("="*50)
    
    # Verificar directorios
    dirs_info = []
    
    for directory in ["historical_data/individual", "historical_data"]:
        if os.path.exists(directory):
            files = os.listdir(directory)
            # Filtrar solo archivos relevantes
            csv_files = [f for f in files if f.endswith('.csv')]
            txt_files = [f for f in files if f.endswith('.txt')]
            relevant_files = csv_files + txt_files
            
            dirs_info.append({
                'dir': directory, 
                'files': len(relevant_files),
                'details': relevant_files[:5]  # Mostrar solo primeros 5
            })
        else:
            dirs_info.append({'dir': directory, 'files': 0, 'details': []})
    
    for info in dirs_info:
        print(f"📂 {info['dir']}: {info['files']} archivos")
        if info['details']:
            for file in info['details']:
                print(f"   • {file}")
            if info['files'] > 5:
                print(f"   • ... y {info['files'] - 5} más")
    
    total_remaining = sum(info['files'] for info in dirs_info)
    if total_remaining == 0:
        print(f"\n✅ LIMPIEZA COMPLETA - Directorios vacíos y listos")
    else:
        print(f"\n⚠️  Quedan {total_remaining} archivos (pueden ser de otras operaciones)")

if __name__ == "__main__":
    print("🧹 SCRIPT DE LIMPIEZA DE DATOS HISTÓRICOS")
    print("="*50)
    
    # Confirmar operación
    print("⚠️  ADVERTENCIA: Este script eliminará todos los datos históricos antiguos")
    print("   • Archivos CSV individuales en historical_data/individual/")
    print("   • Archivos combinados en historical_data/")
    print("   • Reportes de carga anteriores")
    
    response = input("\n¿Continuar con la limpieza? (s/N): ").lower().strip()
    
    if response in ['s', 'si', 'sí', 'y', 'yes']:
        cleanup_historical_data()
        verify_cleanup()
        print(f"\n🎉 LIMPIEZA COMPLETADA - Listo para nueva carga")
    else:
        print(f"\n❌ Limpieza cancelada por el usuario")
