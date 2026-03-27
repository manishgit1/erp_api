from django.urls import path
from tools import views

urlpatterns = [
    path('loanType/create',views.LoanTypeCreateAPIView.as_view(), name='loan-type-create'),
    path('loanType/list', views.LoanTypeListAPIView.as_view(), name='loan-type-list'),
    path('leadSource/create',views.LeadSourceCreateAPIView.as_view(), name='lead-source-create'),
    path('leadSource/list', views.LeadSourceListAPIView.as_view(), name='lead-source-list'),

    path('gender/create', views.ClientTypeGenderCreateAPIView.as_view(), name='gender-create'),
    path('gender/list',views.ClientTypeGenderListAPIView.as_view(),  name='gender-list'),

    path('salutation/create', views.SalutationCreateAPIView.as_view(), name='salutation-create'),
    path('salutation/list',views.SalutationListAPIView.as_view(),  name='salutation-list'),

    path('documentType/create', views.DocumentTypeCreateAPIView.as_view(), name='document-type-create'),
    path('documentType/list',views.DocumentTypeListAPIView.as_view(),  name='document-type-list'),

    path('nationality/create', views.NationalityCreateAPIView.as_view(), name='nationality-create'),
    path('nationality/list',views.NationalityListAPIView.as_view(),  name='nationality-list'),

    path('education/create', views.EducationCreateAPIView.as_view(), name='education-create'),
    path('education/list',views.EducationListAPIView.as_view(),  name='education-list'),

    path('registrationAuthority/create', views.RegistrationAuthorityCreateAPIView.as_view(), name='registration-authority-create'),
    path('registrationAuthority/list',views.RegistrationAuthorityListAPIView.as_view(),  name='registration-authority-list'),

    path('systemDate/getDate',views.GetBusinessDateAPIView.as_view(),name='get-business-date'),

    path('loanPaymentScheme/create', views.LoanPaymentSchemeCreateAPIView.as_view(), name='loan-payment-scheme-create'),
    path('loanPaymentScheme/list',views.LoanPaymentSchemeListAPIView.as_view(),  name='loan-payment-scheme-list'),

    path('loanPurposeCode/create', views.LoanPurposeCodeCreateAPIView.as_view(), name='loan-purpose-create'),
    path('loanPurposeCode/list',views.LoanPurposeCodeListAPIView.as_view(),  name='loan-purpose-list'),



]