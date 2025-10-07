from django.urls import path, include

from api.users.views import list_users, get_user, add_user, update_user, delete_user

urlpatterns = [
    # Users
    path("users/", list_users, name="list_users"),              
    path("users/add/", add_user, name="add_user"),              
    path("users/<int:user_id>/", get_user, name="get_user"),    
    path("users/<int:user_id>/update/", update_user, name="update_user"),  
    path("users/<int:user_id>/delete/", delete_user, name="delete_user"),
]