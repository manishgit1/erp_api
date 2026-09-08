from unicodedata import name
from django.urls import path
from master import views

urlpatterns = [
  path('contactMaster/create', views.ContactMasterCreateAPIView.as_view(), name='contact-master-create'),
  path('contactMaster/list', views.GlobalContactListAPIView.as_view(), name='contact-master-list'),
  path('contactMaster/<pk>/findById', views.GlobalContactDataByIdAPIView.as_view(), name='contact-master-data-by-id'),
  path('contactMaster/<pk>/edit', views.ContactMasterEditAPIView.as_view(), name='contact-master-edit'),
  # path('province/create',views.ProvinceCreateApiView.as_view(), name='province-create' ),
  path('province/lists', views.ProvinceListAPIView.as_view(), name='province-lists'),
  # path('district/create',views.DistrictCreateApiView.as_view(), name='district-create' ),
  path('district/lists', views.DistrictListAPIView.as_view(), name='district-lists'),
  # path('vdcMunicipality/create', views.VDCMunicipalityCreateApiView.as_view(), name='vdc-municipality-create'),
  path('vdcMunicipality/lists', views.VDCMunicipalityListAPIView.as_view(), name='vdc-municipality-lists'),
  # path('contactMaster/lists', views.GlobalContactListAPIView.as_view(), name='global-contact-list-view'),
  path('contact/checkIfContactExists/', views.CheckIfGlobalContactExistsAPIView.as_view(), name='check-if-global-contact-exists'),
  path('vdcMunicipality/getAddressInfo/', views.AddressInfoAPIView.as_view(), name='address-info-by-municipality'),

  path('clientMaster/create', views.ClientMasterCreateAPIView.as_view(), name='client-master-create'),
  path('clientMaster/checkIfClientExists/',views.CheckIfClientMasterExistsAPIView.as_view(),name='check-if-client-exists'),
  path('clientMaster/list',views.ClientMasterListAPIView.as_view(),name='client-master-list'),
  path('clientMaster/<str:pk>/findById', views.ClientMasterDataByIdAPIView.as_view(), name='client-master-data-by-id-api'),
  path('clientMaster/<str:pk>/edit', views.ClientMasterEditAPIView.as_view(), name='client-master-edit'),
  path('clientMaster/getLeadData/',views.ClientMasterGetLeadDataAPIView.as_view(),name='client-master-get-lead-data'),
  path('dashboard/metrics/', views.DashboardMetricsAPIView.as_view(), name='dashboard-metrics'),
]