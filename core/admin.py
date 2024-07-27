from django.contrib import admin
from .models import *
import requests
from .serializers import *
from django.http import Http404
import json
from django.utils.safestring import mark_safe


admin.site.site_header = 'RotiJugaad Admin'
admin.site.site_title = 'RotiJugaad Admin'
admin.site.index_title = 'RotiJugaad Admin'



def send_notification(userID,title,message):
    auth="AAAAy_Ot87Q:APA91bF2pzFV51Xy1VBiiQm78APJl4S5NkicsdSKfPJxrSrU-tTXODlJPr-0VWhLeZKxDQkkI_rPG5n79068vcFjz07IXjwcuFCUozCRjvF9SNv-DLPzpWntdw7eJU9Rt9yoSYTIFu1Q"
    fcmUrl="https://fcm.googleapis.com/fcm/send"

    serializer_class = RegisteredUsersSerializer
    notification_serializer_class=NotificationSerializer

    try:
        user= RegisteredUsers.objects.get(Phone_No=userID)
    except RegisteredUsers.DoesNotExist:
        raise Http404
    
    serializer = serializer_class(user, many=False)
    serialized_data=serializer.data

    token=serialized_data['Device_ID']
    print(token)

    notificationData={
        'User_ID':userID,
        'Notification_Text':message
    }

    serializer = notification_serializer_class(data=notificationData)
    if serializer.is_valid():
        serializer.save()
        print('saved')

    notification={
        'title':title,
        'body':message,
        'sound':'default'
    }

    apns={
        'headers':{'apns-priority':5},
        'payload':{'aps':{'content_available':True}}
    }

    fcmNotification={
        'to':token,
        'notification':notification,
        'data':notification
    }

    headers={
        'Authorization' : 'key='+auth,
        'Content-Type' : 'application/json'
    }

    r = requests.post(fcmUrl, data=json.dumps(fcmNotification), headers=headers)
    api_response = r.json() 
    print(api_response)


def send_all_notification(title,message,type):
    auth="AAAAy_Ot87Q:APA91bF2pzFV51Xy1VBiiQm78APJl4S5NkicsdSKfPJxrSrU-tTXODlJPr-0VWhLeZKxDQkkI_rPG5n79068vcFjz07IXjwcuFCUozCRjvF9SNv-DLPzpWntdw7eJU9Rt9yoSYTIFu1Q"
    fcmUrl="https://fcm.googleapis.com/fcm/send"

    serializer_class = RegisteredUsersSerializer
    notification_serializer_class=NotificationSerializer

    if type=='EE':
        tokens= Employee.objects.values_list('User_ID__Device_ID', flat=True)
    else:
        tokens= Employer.objects.values_list('User_ID__Device_ID', flat=True)

    tokens=list(tokens)
    print(tokens)

    notificationData={
        'Notification_Text':message
    }

    serializer = notification_serializer_class(data=notificationData)
    if serializer.is_valid():
        serializer.save()
        print('saved')

    notification={
        'title':title,
        'body':message,
        'sound':'default'
    }

    apns={
        'headers':{'apns-priority':5},
        'payload':{'aps':{'content_available':True}}
    }

    fcmNotification={
        'registration_ids':tokens,
        'notification':notification,
        'data':notification
    }

    headers={
        'Authorization' : 'key='+auth,
        'Content-Type' : 'application/json'
    }

    r = requests.post(fcmUrl, data=json.dumps(fcmNotification), headers=headers)
    api_response = r.json() 
    print(api_response)



class RegisteredUsersAdmin(admin.ModelAdmin):
    list_display=('Phone_No','Account_Type','Name')

    search_fields = (
        "Name",
        "Phone_No",
    )

    def has_add_permission(self, request, obj=None):
        return False
    
class EmployeeAdmin(admin.ModelAdmin):
    list_display=('User_ID','EmployeeID','Name','Contact_No','Age','Gender','Active_Pack','Profile_Completed','Approved','Active')

    def save_model(self, request, obj, form, change):
        print('admin save triggered ')
        if form.initial['Approved']==False and form.cleaned_data['Approved']==True:
            send_notification(form.initial['User_ID'],"RotiJugaad","Congratulations, Your profile is approved now.")
        super(EmployeeAdmin, self).save_model(request, obj, form, change)

    list_filter = [
         "Profile_Completed",
         "Approved",
         "Active",
         "Gender"
    ]
    search_fields = (
        "User_ID",
        "EmployeeID",
        "Name",
        "Contact_No",
    )

    def has_add_permission(self, request, obj=None):
        return False
    
class EmployerAdmin(admin.ModelAdmin):
    list_display=('User_ID','EmployerID','Name','Phone_No','Organization','Address','Organization_Type','Profile_Completed','Approved','Active')

    def save_model(self, request, obj, form, change):
        print('admin save triggered ')
        if form.initial['Approved']==False and form.cleaned_data['Approved']==True:
            send_notification(form.initial['User_ID'],"RotiJugaad","Congratulations, Your profile is approved now.")
        super(EmployerAdmin, self).save_model(request, obj, form, change)


    def Phone_No(self, obj):
        return obj.User_ID.Phone_No

    list_filter = [
         "Profile_Completed",
         "Approved",
         "Active",
         "Organization_Type"
    ]
    search_fields = (
        "User_ID",
        "EmployerID",
        "Name",
        "Organization",
        "Address",
        "Organization_Type"
    )

    def has_add_permission(self, request, obj=None):
        return False
    
class PaymentEmployeeAdmin(admin.ModelAdmin):
    list_display=('employee_name','employee_phone','Order_ID','inv_number','invoice_total','inv_date','subscription_name','view_invoice')

    def employee_name(self,obj):
        return obj.Employee_ID.Name

    def employee_phone(self, obj):
        return obj.Employee_ID.Contact_No
    
    def view_invoice(self, obj):
        id=obj.Order_ID
        return mark_safe('<a href="../../../employee_invoice/'+str(id)+'/" target="_blank"><button style="border-radius:8px;background-color:#0D98BA;border:none;color:#ffffff;padding:4px;" type="button">View Invoice</button></a>')

    list_filter = [
         "subscription_name",
    ]
    search_fields = (
        "Employee_ID",
        "inv_date",
        "inv_number",
        "name",
        "subscription_name"
    )
    
    def has_add_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
class PaymentEmployerAdmin(admin.ModelAdmin):
    list_display=('Order_ID','Employer_ID','inv_date','inv_number','name','subscription_name','invoice_total','view_invoice')

    list_filter = [
         "subscription_name",
    ]
    search_fields = (
        "Employer_ID",
        "inv_date",
        "inv_number",
        "name",
        "subscription_name"
    )

    def view_invoice(self, obj):
        id=obj.Order_ID
        return mark_safe('<a href="../../../employer_invoice/'+str(id)+'/" target="_blank"><button style="border-radius:8px;background-color:#0D98BA;border:none;color:#ffffff;padding:4px;" type="button">View Invoice</button></a>')

    
    def has_add_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
class EmployeeToEmployerJobAdmin(admin.ModelAdmin):
    list_display=('Job_ID','Date','Employee_ID','Organization_Name','Organization_Category','Salary_Frequency')

    list_filter = [
         "Salary_Frequency",
         "Organization_Name"
    ]
    search_fields = (
        "Job_ID",
        "Date",
        "Employee_ID",
        "Organization_Name",
        "Organization_Category",
        "Salary_Frequency"
    )

    def has_add_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
class EmployerToEmployeeJobAdmin(admin.ModelAdmin):
    list_display=('Job_ID','Date','Employer_ID','Name','Salary','Salary_Frequency')

    list_filter = [
         "Salary_Frequency",
    ]
    search_fields = (
        "Job_ID",
        "Date",
        "Employer_ID",
        "Name",
        "Salary",
        "Salary_Frequency"
    )

    def has_add_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
class JobAdmin(admin.ModelAdmin):
    list_display=('Job_ID','Job_Profile','Vacancy','Employer_ID','Contact_No','Salary_Offered','Frequency','Sent_Interests','Received_Interests')

    list_filter = [
         "Frequency",
    ]
    search_fields = (
        "Job_ID",
        "Job_Profile",
        "Employer_ID",
        "Contact_No",
        "Salary_Offered",
        "Frequency"
    )

    def has_add_permission(self, request, obj=None):
        return False
    
class EmployeeToEmployerCallAdmin(admin.ModelAdmin):
    list_display=('Job_ID','Employee_ID','Organization_Name','Organization_Category','Date','Contact_No')

    list_filter = [
         "Organization_Category",
    ]
    search_fields = (
        "Job_ID",
        "Employee_ID",
        "Organization_Name",
        "Organization_Category",
        "Contact_No"
    )

    def has_add_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False

class EmployerToEmployeeCallAdmin(admin.ModelAdmin):
    list_display=('Job_ID','Employer_ID','Employee_ID','Name','City','Date','Contact_No')

    list_filter = [
         "City",
    ]
    search_fields = (
        "Job_ID",
        "Employer_ID",
        "Employee_ID",
        "Name",
        "City",
        "Contact_No"
    )

    def has_add_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
class EmployeeSubscriptionAdmin(admin.ModelAdmin):
    list_display=('Plan_ID','Plan_Name','Visible','Validity_In_Days','Price','Discounted_Price','Contact_Credit','Interest_Credit')

    search_fields = (
        "Plan_Name",
    )

class EmployerSubscriptionAdmin(admin.ModelAdmin):
    list_display=('Plan_ID','Plan_Name','Visible','Validity_in_days','Price','Discounted_Price','Contact_Credit','Interest_Credit','Job_Post_Credit')

    search_fields = (
        "Plan_Name",
    )

class RequestACallAdmin(admin.ModelAdmin):
    list_display=('Name','Phone_No')

    search_fields = (
        "Name",
        "Phone_No",
    )

    def has_add_permission(self, request, obj=None):
        return False
    
class ReferredByAdmin(admin.ModelAdmin):
    list_display=('Referral_ID','Referrer_Name')

    search_fields = (
        "Referral_Name",
    )

class JobCategoryAdmin(admin.ModelAdmin):
    list_display=('Category_ID','Category','Category_Hindi','Photo')

    search_fields = (
        "Category",
        "Category_Hindi",
    )

class HiringTableAdmin(admin.ModelAdmin):
    list_display=('Job_ID','Employee_ID','Employer_ID','Date','Job_Profile','Salary','Salary_Frequency','Contact_No')

    list_filter = [
         "Salary_Frequency",
    ]
    search_fields = (
        "Job_ID",
        "Employer_ID",
        "Employee_ID",
        "Job_Profile",
        "Salary",
        "Salary_Frequency",
        "Contact_No"
    )

    def has_add_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
class ContactPhoneAdmin(admin.ModelAdmin):
    list_display=('Phone',)

    search_fields = (
        "Phone",
    )


class NotificationAdmin(admin.ModelAdmin):
    list_display = ('User_ID', 'Notification_ID','Notification_Text','Notification_Date')

    def has_add_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
class AppNotificationAdmin(admin.ModelAdmin):
    list_display = ('Notification_ID','Notification_Title','Notification_Message','Notification_Date','resend_notification')
    
    def save_model(self, request, obj, form, change):
        send_all_notification(form.cleaned_data['Notification_Title'],form.cleaned_data['Notification_Message'],form.cleaned_data['Type'])
        super(AppNotificationAdmin, self).save_model(request, obj, form, change)

    def resend_notification(self, obj):
        id=obj.Notification_ID
        return mark_safe('<a href="../../../resend_notification/'+str(id)+'/"><button style="border-radius:8px;background-color:#0D98BA;border:none;color:#ffffff;padding:4px;" type="button">Resend Notification</button></a>')


    def has_change_permission(self, request, obj=None):
        return False

class TransactionAdmin(admin.ModelAdmin):
    list_display=('OID','Date','Amount','CfOrderId','Order_ID','Employee_ID','Employer_ID','Type','Plan_ID','Status')

    list_filter = [
         "Plan_ID",
         "Status",
         "Type"
    ]
    search_fields = (
        "Plan_ID",
        "Employer_ID",
        "Employee_ID",
        "Status",
    )

    def has_add_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    

class JobOtpAdmin(admin.ModelAdmin):
    list_display=('Date','Employee_ID','Job_ID','Otp')

    search_fields = (
        "Job_ID",
        "Employee_ID",
    )

    def has_add_permission(self, request, obj=None):
        return False
    

class EmployeeJobPreferenceAdmin(admin.ModelAdmin):
    list_display=('ID','User_ID','Employee_ID','Category')

    list_filter = [
         "Category",
    ]
    search_fields = (
        "User_ID",
        "Employee_ID",
        "Category",
    )

    def has_add_permission(self, request, obj=None):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    

class EmployeeQualificationAdmin(admin.ModelAdmin):
    list_display=('QualificationID','User_ID','Employee_ID','Organization','Role','Duration','DurationType')

    list_filter = [
         "Role",
         "DurationType",
         "Duration"
    ]
    search_fields = (
        "User_ID",
        "Employee_ID",
        "Organization",
        "Role",
        "DurationType"
    )

    def has_add_permission(self, request, obj=None):
        return False



admin.site.register(RegisteredUsers,RegisteredUsersAdmin)
admin.site.register(Employee,EmployeeAdmin)
admin.site.register(Employer,EmployerAdmin)
admin.site.register(Payment_Employee,PaymentEmployeeAdmin)
admin.site.register(Payment_Employer,PaymentEmployerAdmin)
admin.site.register(Employee_To_Employer_Job,EmployeeToEmployerJobAdmin)
admin.site.register(Employer_To_Employee_Job,EmployerToEmployeeJobAdmin)
admin.site.register(Job,JobAdmin)
admin.site.register(Employee_To_Employer_Call,EmployeeToEmployerCallAdmin)
admin.site.register(Employer_To_Employee_Call,EmployerToEmployeeCallAdmin)
admin.site.register(EmployeeSubscription,EmployeeSubscriptionAdmin)
admin.site.register(EmployerSubscription,EmployerSubscriptionAdmin)
admin.site.register(RequestACall,RequestACallAdmin)
admin.site.register(ReferredBy,ReferredByAdmin)
admin.site.register(JobCategory,JobCategoryAdmin)
admin.site.register(HiringTable,HiringTableAdmin)
admin.site.register(Contact_phone,ContactPhoneAdmin)
admin.site.register(Notification,NotificationAdmin)
admin.site.register(AppNotification,AppNotificationAdmin)
admin.site.register(Transaction,TransactionAdmin)
admin.site.register(JobOtp,JobOtpAdmin)
admin.site.register(EmployeeJobPreference,EmployeeJobPreferenceAdmin)
admin.site.register(EmployeeQualification,EmployeeQualificationAdmin)
