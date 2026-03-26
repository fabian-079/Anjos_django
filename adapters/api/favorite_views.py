from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from infrastructure.container import get_favorite_usecases


@login_required
def favoritos_view(request):
    favorites = get_favorite_usecases().get_user_favorites(request.user.id)
    return render(request, 'favoritos.html', {'favorites': favorites})


@login_required
def favorite_remove(request, pk):
    if request.method == 'POST':
        try:
            get_favorite_usecases().remove_favorite(pk)
            messages.success(request, 'Favorito eliminado.')
        except Exception as e:
            messages.error(request, str(e))
    return redirect('favoritos')
