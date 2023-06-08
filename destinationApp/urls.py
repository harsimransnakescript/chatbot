from django.urls import path
from .views import *
from .chatbot_api import *
urlpatterns = [

    path('',index,name='index'),
    path('api/', ChatBotView.as_view(), name='api'),
    path('chat_view/',chat_view,name='chat_view'),
    path('config/', stripe_config),
    path('create-checkout-session/', create_checkout_session,name='/create-checkout-session/'),
    path('success/', success,name ='success'),
    path('cancelled/', cancelled,name ='cancelled'),
    path('send_emails_user/',send_emails_user,name='send_emails_user'),
    path('send_email_agent/',send_email_agent, name='send_email_agent'),
    path('api/token/', MyTokenObtainPairView.as_view(), name='token-obtain-pair'),
    path('api/token/refresh/', MyTokenRefreshView.as_view(), name='token-refresh'),#
    path('api/resgister', ApiUserRegister.as_view(), name='resgister'),

]