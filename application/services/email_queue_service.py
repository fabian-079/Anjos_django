import json
import os
import threading
import time
from datetime import datetime
from django.conf import settings

class EmailQueueService:
    def __init__(self):
        self.queue_file = os.path.join(settings.BASE_DIR, 'email_queue.json')
        self.processing = False
        self._ensure_queue_file()
    
    def _ensure_queue_file(self):
        """Asegurar que el archivo de cola existe"""
        if not os.path.exists(self.queue_file):
            with open(self.queue_file, 'w') as f:
                json.dump([], f)
    
    def add_to_queue(self, subject, message, user_role=None):
        """Agregar tarea de email a la cola"""
        print("📝 AGREGANDO TAREA A COLA DE EMAILS")
        
        task = {
            'id': str(int(time.time() * 1000)),
            'subject': subject,
            'message': message,
            'user_role': user_role,
            'created_at': datetime.now().isoformat(),
            'status': 'pending'
        }
        
        # Leer cola actual
        try:
            with open(self.queue_file, 'r') as f:
                queue = json.load(f)
        except:
            queue = []
        
        # Agregar nueva tarea
        queue.append(task)
        
        # Guardar cola
        with open(self.queue_file, 'w') as f:
            json.dump(queue, f, indent=2)
        
        print(f"✅ TAREA AGREGADA A COLA: {task['id']}")
        
        # Iniciar procesamiento en background si no está corriendo
        if not self.processing:
            threading.Thread(target=self._process_queue, daemon=True).start()
        
        return task['id']
    
    def _process_queue(self):
        """Procesar cola en background"""
        if self.processing:
            return
        
        self.processing = True
        print("🔄 INICIANDO PROCESAMIENTO DE COLA EN BACKGROUND")
        
        try:
            while True:
                # Leer tareas pendientes
                try:
                    with open(self.queue_file, 'r') as f:
                        queue = json.load(f)
                except:
                    queue = []
                
                # Buscar tareas pendientes
                pending_tasks = [t for t in queue if t['status'] == 'pending']
                
                if not pending_tasks:
                    print("   No hay tareas pendientes - esperando...")
                    time.sleep(10)
                    continue
                
                # Procesar primera tarea pendiente
                task = pending_tasks[0]
                print(f"   Procesando tarea: {task['id']}")
                
                # Actualizar estado
                for t in queue:
                    if t['id'] == task['id']:
                        t['status'] = 'processing'
                        t['started_at'] = datetime.now().isoformat()
                        break
                
                with open(self.queue_file, 'w') as f:
                    json.dump(queue, f, indent=2)
                
                # Procesar email
                try:
                    from infrastructure.container import get_email_usecases
                    email_uc = get_email_usecases()
                    
                    result = email_uc._send_mass_email_sync_direct(
                        task['subject'], 
                        task['message'], 
                        task['user_role']
                    )
                    
                    # Marcar como completada
                    for t in queue:
                        if t['id'] == task['id']:
                            t['status'] = 'completed'
                            t['completed_at'] = datetime.now().isoformat()
                            t['result'] = result
                            break
                    
                    print(f"   ✅ TAREA COMPLETADA: {task['id']} - {result} correos")
                    
                except Exception as e:
                    # Marcar como error
                    for t in queue:
                        if t['id'] == task['id']:
                            t['status'] = 'error'
                            t['error'] = str(e)
                            t['error_at'] = datetime.now().isoformat()
                            break
                    
                    print(f"   ❌ ERROR EN TAREA: {task['id']} - {str(e)}")
                
                # Guardar cambios
                with open(self.queue_file, 'w') as f:
                    json.dump(queue, f, indent=2)
                
                # Pequeña pausa entre tareas
                time.sleep(2)
                
        except Exception as e:
            print(f"❌ ERROR EN PROCESAMIENTO DE COLA: {str(e)}")
        finally:
            self.processing = False
            print("🏁 PROCESAMIENTO DE COLA FINALIZADO")
    
    def get_queue_status(self):
        """Obtener estado de la cola"""
        try:
            with open(self.queue_file, 'r') as f:
                queue = json.load(f)
            
            pending = len([t for t in queue if t['status'] == 'pending'])
            processing = len([t for t in queue if t['status'] == 'processing'])
            completed = len([t for t in queue if t['status'] == 'completed'])
            errors = len([t for t in queue if t['status'] == 'error'])
            
            return {
                'pending': pending,
                'processing': processing,
                'completed': completed,
                'errors': errors,
                'total': len(queue),
                'is_processing': self.processing
            }
        except:
            return {'pending': 0, 'processing': 0, 'completed': 0, 'errors': 0, 'total': 0, 'is_processing': False}

# Instancia global
email_queue = EmailQueueService()
