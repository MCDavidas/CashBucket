from django.urls import path

from . import views


app_name = 'records'
urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('rates/', views.rates_view, name='rates'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    path('dashboard/menu/', views.menu_view, name='menu'),

    path('dashboard/budget/', views.budget_view, name='budget'),
    path('dashboard/budget/remove/<int:param>/', views.remove_limit_view, name='budget_remove'),

    path('dashboard/workplace/<str:param>/<int:count>/', views.dashboard_view, name='dashboard'),
    path('dashboard/workplace_income/<str:param>/<int:count>/', views.dashboard_income_view, name='dashboard_income'),

    path('dashboard/category/graph/<str:param>/', views.category_graph_view, name='category_graph'),
    path('dashboard/category/<str:workflow_param>/', views.category_view, name='category'),

    path('dashboard/new/<str:workflow_param>/', views.new_record_view, name='new_record'),
    path('dashboard/profile/', views.profile_view, name='profile'),
    path('dashboard/remove/<int:record_type>/<int:param>/<str:workflow_param>/', views.remove_view, name='remove'),

    path('dashboard/searh/', views.search_view, name='search'),

    path('dashboard/analytics/graph/<str:param>/', views.graph_view, name='graph'),
    path('dashboard/analytics/<str:workflow_param>/', views.analytics_view, name='analytics'),
]
