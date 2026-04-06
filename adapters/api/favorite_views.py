from django.contrib import messages
from django.shortcuts import render, redirect
from infrastructure.container import get_favorite_usecases



def favoritos_view(request):
    if request.user.is_authenticated:
        favorites = get_favorite_usecases().get_user_favorites(request.user.id)
        is_guest = False
    else:
        favorites = _guest_favorite_items(request)
        is_guest = True
    return render(request, 'favoritos.html', {'favorites': favorites, 'is_guest': is_guest})


def favorite_remove(request, pk):
    if request.method == 'POST':
        if request.user.is_authenticated:
            try:
                get_favorite_usecases().remove_favorite(pk)
                messages.success(request, 'Favorito eliminado.')
            except Exception as e:
                messages.error(request, str(e))
        else:
            guest_favs = request.session.get('guest_favorites', [])
            if pk in guest_favs:
                guest_favs.remove(pk)
                request.session['guest_favorites'] = guest_favs
    return redirect('favoritos')


def _guest_favorite_items(request):
    from infrastructure.container import get_product_usecases
    guest_favs = request.session.get('guest_favorites', [])
    uc = get_product_usecases()
    items = []
    for pid in guest_favs:
        product = uc.get_product_by_id(int(pid))
        if product and product.is_active:
            items.append({
                'id': pid,
                'product_id': product.id,
                'product_name': product.name,
                'product_image': product.get_image_url(),
                'product_price': product.price,
                'product_category_name': product.category_name,
            })
    return items
