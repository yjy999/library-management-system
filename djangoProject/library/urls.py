from django.urls import path
from library import views

from django.views.generic.base import RedirectView
app_name = "library"

urlpatterns = [
    path("register/", views.register),  # 注册函数
    path("login/", views.login),
    path('logout/', views.logout),
    path('add_publisher/', views.add_publisher),
    path("publisher_list/", views.publisher_list, name="publisher_list"),
    path("publisher_list/<int:page>", views.publisher_list, name="publisher_list"),
    path("update_publisher/", views.update_publisher, name="update_publisher"),
    path("delete_publisher/", views.delete_publisher, name="delete_publisher"),

    path("add_book/", views.add_book, name="add_book"),
    path("book_list/", views.book_list, name="book_list"),
    path("book_list/<int:page>", views.book_list, name="book_list"),
    path("update_book/", views.update_book, name="update_book"),
    path("delete_book/", views.delete_book, name="delete_book"),

    path("add_author/", views.add_author, name="add_author"),
    path("author_list/", views.author_list, name="author_list"),
    path("author_list/<int:page>/", views.author_list, name="author_list"),
    path('update_author/', views.update_author, name="update_author"),
    path("delete_author/", views.delete_author, name="delete_author"),

    path("add_user/", views.add_user, name="add_user"),
    path("user_list/", views.user_list, name="user_list"),
    path("user_list/<int:page>", views.user_list, name="user_list"),
    path("update_user/", views.update_user, name="update_user"),
    path("delete_user/", views.delete_user, name="delete_user"),

     path('index/', views.index),
     path('index/<int:page>', views.index, name="index"),
     path("search/", views.search, name="search"),

    path('sdulibrary/', RedirectView.as_view(url='http://www.lib.sdu.edu.cn'))

]
