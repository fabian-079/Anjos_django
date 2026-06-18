from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect


def admin_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        print("🛡️🛡️🛡️ DECORADOR admin_required EJECUTÁNDOSE - RAILWAY")
        print(f"   Usuario: {request.user}")
        print(f"   Autenticado: {request.user.is_authenticated}")
        
        try:
            is_admin = request.user.is_admin()
            print(f"   Es admin: {is_admin}")
            
            if not is_admin:
                print("   ❌ Usuario no es admin - PermissionDenied")
                raise PermissionDenied
            else:
                print("   ✅ Usuario es admin - continuando")
        except Exception as e:
            print(f"   ❌ Error en is_admin(): {str(e)}")
            # Intentar método alternativo
            try:
                is_admin_alt = request.user.is_staff or request.user.is_superuser
                print(f"   Es admin (alternativo): {is_admin_alt}")
                if not is_admin_alt:
                    raise PermissionDenied
                else:
                    print("   ✅ Usuario es admin (alternativo) - continuando")
            except Exception as e2:
                print(f"   ❌ Error en método alternativo: {str(e2)}")
                raise PermissionDenied
        
        return view_func(request, *args, **kwargs)
    return wrapper


def cliente_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if not (request.user.is_client() or request.user.is_admin()):
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper
