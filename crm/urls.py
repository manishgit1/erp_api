from django.urls import path
from crm import views


urlpatterns = [
  path('leadQuotation/create', views.LeadQuotationCreateAPIView.as_view(), name='lead-quotation-create'),
  path('leadQuotation/list', views.LeadQuotationListAPIView.as_view(), name='lead-quotation-list'),

  path('inquiryFollowUp/list', views.InquiryFollowUpListDataAPIView.as_view(), name='inquiry-follow-up-list-data'),
  path('documentApproval/list', views.DocumentApprovalListDataAPIView.as_view(), name='document-approval-list-data'),
  path('printModalSearch/search', views.PrintModalSearchListDataAPIView.as_view(), name='print-modal-search-list-data'),

  path('documentUpload/create',views.DocumentUploadCreateAPIView.as_view(), name='document-upload-create'),
  path('documentUpload/upload',views.DocumentUploadUploadAPIView.as_view(), name='document-upload'),

  path('documentApproval/rejectApprove/create',views.DocumentApprovalRejectApproveCreateAPIView.as_view(), name='document-approval-reject-approve'),

  path('approvedDocuments/list', views.ApprovedDocumentsListDataAPIView.as_view(), name='approved-documents-list'),

  path('leadQuotation/getEmiSchedule', views.EMIScheduleAPIView.as_view(), name='emi-schedule'),
]