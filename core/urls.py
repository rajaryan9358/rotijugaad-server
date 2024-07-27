from django.urls import path

from .views import *

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Registered Users
    path('employee_invoice/<id>/',employee_invoice),
    path('employer_invoice/<id>/',employer_invoice),
    path('resend_notification/<id>/',resend_notification),
    path('api/registered-users/', RegisteredUsersAPIView.as_view(), name='registered-users'),
    path('api/registered-users/<phone_no>/', RegisteredUsersAPIView.as_view(), name='registered-users'),

    path('api/registered-users/<str:user_id>/employee', UserEmployeeAPIView.as_view(), name='user-employee'),
    path('api/registered-users/<str:user_id>/employer', UserEmployerAPIView.as_view(), name='user-employer'),


    # Employee
    path('api/employees/', EmployeeAPIView.as_view(), name='employee-list'),
    path('api/employees/<int:employee_id>/', EmployeeDetailAPIView.as_view(), name='employee-detail'),

    path('api/employee-qualification/', EmployeeQualificationAPIView.as_view(), name='employee-qualification'),
    path('api/employee-qualification/<user_id>/', EmployeeQualificationAPIView.as_view(), name='employee-qualification'),

    path('api/employee-jobpreference/<employee_id>/', EmployeeJobPreferenceAPIView.as_view(), name='employee-jobpreference'),


    # Employer
    path('api/employers/', EmployerAPIView.as_view(), name='employer-list'),
    path('api/employers/<int:employer_id>/', EmployerDetailAPIView.as_view(), name='employer-detail'),

    # Payment
    path('api/payment-employee/', PaymentEmployeeAPIView.as_view(), name='payment-employee'),
    path('api/payment-employee/<int:employee_id>/', PaymentEmployeeAPIView.as_view(), name='payment-employee'),
    
    path('api/payment-employer/', PaymentEmployerAPIView.as_view(), name='payment-employer'),
    path('api/payment-employer/<int:employer_id>/', PaymentEmployerAPIView.as_view(), name='payment-employer'),

    # Notification API
    path('api/notifications/', NotificationAPIView.as_view(), name='notification-list'),
    path('api/notifications/<int:user_id>/', NotificationAPIView.as_view(), name='notification-detail'),

    # EmployeeToEmployerJob
    path('api/employee-to-employer-job/', EmployeeToEmployerJobAPIView.as_view(), name='employee-to-employer-job'),

    # EmployerToEmployeeJob
    path('api/employer-to-employee-job/', EmployerToEmployeeJobAPIView.as_view(), name='employer-to-employee-job'),

    # AvailableCandidates
    path('api/available-candidates/', AvailableCandidatesAPIView.as_view(), name='available-candidates'),

    # EmployeeToEmployerCall
    path('api/employee-to-employer-call/', EmployeeToEmployerCallAPIView.as_view(), name='employee-to-employer-call'),

    # EmployerToEmployeeCall
    path('api/employer-to-employee-call/', EmployerToEmployeeCallAPIView.as_view(), name='employer-to-employee-call'),


    # Job
    path('api/jobs/', JobAPIView.as_view(), name='job-list'),
    path('api/jobs/<int:pk>/', JobExtendedAPIView.as_view(), name='job-extended'),
    path('api/delete-job/<int:pk>/', JobDeleteAPIView.as_view(), name='job-delete'),

    # Employee Subscription
    path('api/employee-subscriptions/', EmployeeSubscriptionAPIView.as_view(), name='employee-subscriptions'),

    # Employer Subscription
    path('api/employer-subscriptions/', EmployerSubscriptionAPIView.as_view(), name='employer-subscriptions'),

    # Request A Call
    path('api/request-a-call/', RequestACallAPIView.as_view(), name='request-a-call'),

    # Referred By
    path('api/referred-by/', ReferredByAPIView.as_view(), name='referred-by'),

    # Job Category
    path('api/job-categories/', JobCategoryAPIView.as_view(), name='job-categories'),

    # Hiring Table
    path('api/hiring-table/', HiringTableAPIView.as_view(), name='hiring-table'),
    path('api/hiring-table/<int:employer_id>/', HiringTableAPIView.as_view(), name='hiring-table'),
    path('api/contact_phones/', ContactPhoneList.as_view(), name='contact-phone-list'),

    #Job Otp
    path('api/job-otp/<int:employee_id>/<int:job_id>/', JobOtpAPIView.as_view(), name='job-otp'),
    path('api/job-otp/', JobOtpAPIView.as_view(), name='job-otp'),

    path('api/cashfree/',CashFreeAPIView.as_view(),name='cashfree'),
    path('api/cashfree/<int:oid>/',CashFreeAPIView.as_view(),name='cashfree')

]
