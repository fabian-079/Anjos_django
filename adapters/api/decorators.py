from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect


def admin_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info("🛡️ DECORADOR admin_required EJECUTÁNDOSE")
        logger.info(f"   Usuario: {request.user}")
        logger.info(f"   Autenticado: {request.user.is_authenticated}")
        
        try:
            is_admin = request.user.is_admin()
            logger.info(f"   Es admin: {is_admin}")
            
            if not is_admin:
                logger.warning("   ❌ Usuario no es admin - PermissionDenied")
                raise PermissionDenied
            else:
                logger.info("   ✅ Usuario es admin - continuando")
        except Exception as e:
            logger.error(f"   ❌ Error en is_admin(): {str(e)}")
            # Intentar método alternativo
            try:
                is_admin_alt = request.user.is_staff or request.user.is_superuser
                logger.info(f"   Es admin (alternativo): {is_admin_alt}")
                if not is_admin_alt:
                    raise PermissionDenied
            except Exception as e2:
                logger.error(f"   ❌ Error en método alternativo: {str(e2)}")
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
