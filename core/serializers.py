from rest_framework import serializers
from .models import *

class RegisteredUsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegisteredUsers
        fields = '__all__'

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'

class EmployeeQualificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeQualification
        fields = '__all__'

class EmployeeJobPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeJobPreference
        fields = '__all__'

class EmployerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employer
        fields = '__all__'

class PaymentEmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment_Employee
        fields = '__all__'

class PaymentEmployerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment_Employer
        fields = '__all__'

class EmployeeToEmployerJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee_To_Employer_Job
        fields = '__all__'

class EmployerToEmployeeJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employer_To_Employee_Job
        fields = '__all__'

class EmployeeToEmployerCallSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee_To_Employer_Call
        fields = '__all__'

class EmployerToEmployeeCallSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employer_To_Employee_Call
        fields = '__all__'

class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = '__all__'

class EmployeeSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeSubscription
        fields = '__all__'

class EmployerSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployerSubscription
        fields = '__all__'

class RequestACallSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestACall
        fields = '__all__'

class ReferredBySerializer(serializers.ModelSerializer):
    class Meta:
        model = ReferredBy
        fields = '__all__'

class JobCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = JobCategory
        fields = '__all__'

class HiringTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = HiringTable
        fields = '__all__'

class ContactPhoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact_phone
        fields = '__all__'

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'

class AppNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppNotification
        fields = '__all__'

class JobOtpSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobOtp
        fields = '__all__'

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'