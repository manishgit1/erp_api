from django.urls import path
from loan import views

urlpatterns = [
    path('loanRequest/create', views.LoanRequestCreateAPIView.as_view(), name='loan-request-list-create'),
    path('loanRequest/list', views.LoanRequestListAPIView.as_view(), name='loan-request-list'),
    # path('loan-request/<str:pk>/', views.LoanRequestDetailView.as_view(), name='loan-request-detail'),
    path('loanRequest/pending/list',views.PendingLoanRequestListAPIView.as_view(),name='pending-loan-request-list'),
    path('loanRequest/reverted/list',views.RevertedLoanRequestListAPIView.as_view(),name='reverted-loan-request-list'),
    path('loanRequest/rejected/list',views.RejectedLoanRequestListAPIView.as_view(),name='rejected-loan-request-list'),
    path('loanRequest/approved/list',views.ApprovedLoanRequestListAPIView.as_view(),name='approved-loan-request-list'),

    path('loanRequest/approveRejectRevert',views.ApproveRejectRevertLoanRequest.as_view(),name='approve-reject-revert-loan-request'),
    path('loanRequest/<str:pk>/timeline',views.LoanRequestTimelineAPIView.as_view(),name='loan-request-timeline'),

    path('workflow/list',views.RequestWorkflowListAPIView.as_view(),name='workflow-list'),
    path('workflow/create',views.RequestWorkflowCreateAPIView.as_view(),name='workflow-create'),

]
