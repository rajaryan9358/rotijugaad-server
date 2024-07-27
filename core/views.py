from django.shortcuts import render
from rest_framework.views import APIView
from .models import *
from .serializers import *
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
import random
import requests
import json
from datetime import datetime,timedelta
from datetime import date
import pandas as pd
from django.shortcuts import redirect


# from cashfree_pg.models.create_order_request import CreateOrderRequest
# from cashfree_pg.api_client import Cashfree
# from cashfree_pg.models.customer_details import CustomerDetails

def send_all_notification(title,message,type):
    auth="AAAAy_Ot87Q:APA91bF2pzFV51Xy1VBiiQm78APJl4S5NkicsdSKfPJxrSrU-tTXODlJPr-0VWhLeZKxDQkkI_rPG5n79068vcFjz07IXjwcuFCUozCRjvF9SNv-DLPzpWntdw7eJU9Rt9yoSYTIFu1Q"
    fcmUrl="https://fcm.googleapis.com/fcm/send"

    notification_serializer_class=AppNotificationSerializer

    if type=='EE':
        tokens= Employee.objects.values_list('User_ID__Device_ID', flat=True)
    else:
        tokens= Employer.objects.values_list('User_ID__Device_ID', flat=True)

    tokens=list(tokens)
    print(tokens)

    notificationData={
        'Notification_Title':title,
        'Notification_Message':message,
        'Type':type
    }

    serializer = notification_serializer_class(data=notificationData)
    if serializer.is_valid():
        serializer.save()

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


def employee_invoice(request,id):
    payment_employee = Payment_Employee.objects.get(Order_ID=id)
    serializer = PaymentEmployeeSerializer(payment_employee, many=False)
    serialized_data = serializer.data

    employee=Employee.objects.get(EmployeeID=serialized_data['Employee_ID'])
    emp_serializer=EmployeeSerializer(employee,many=False)
    serialized_data['organization']=emp_serializer.data['Name']

    invoice=generate_invoice(serialized_data)
    return render(request, 'invoice.html',{'invoice_data': invoice})

def employer_invoice(request,id):
    payment_employer = Payment_Employer.objects.get(Order_ID=id)
    serializer = PaymentEmployerSerializer(payment_employer, many=False)
    serialized_data = serializer.data

    employer=Employer.objects.get(EmployerID=serialized_data['Employer_ID'])
    empr_serializer=EmployerSerializer(employer,many=False)
    serialized_data['organization']=empr_serializer.data['Organization']

    invoice=generate_invoice(serialized_data)
    return render(request, 'invoice.html',{'invoice_data': invoice})

def resend_notification(request,id):
    notification = AppNotification.objects.get(Notification_ID=id)
    serializer = AppNotificationSerializer(notification, many=False)
    serialized_data = serializer.data

    title=serialized_data['Notification_Title']
    message=serialized_data['Notification_Message']
    type=serialized_data['Type']

    send_all_notification(title,message,type)

    return redirect('/admin/core/appnotification')

def send_notification(userID,message):
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
        'title':'RotiJugaad',
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

def number_to_word(number):
    def get_word(n):
        words = {0: "", 1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five", 6: "Six", 7: "Seven", 8: "Eight",
                 9: "Nine", 10: "Ten", 11: "Eleven", 12: "Twelve", 13: "Thirteen", 14: "Fourteen", 15: "Fifteen",
                 16: "Sixteen", 17: "Seventeen", 18: "Eighteen", 19: "Nineteen", 20: "Twenty", 30: "Thirty",
                 40: "Forty", 50: "Fifty", 60: "Sixty", 70: "Seventy", 80: "Eighty", 90: "Ninety"}
        if n <= 20:
            return words[n]
        else:
            ones = n % 10
            tens = n - ones
            return words[tens] + " " + words[ones]

    def get_all_word(n):
        d = [100, 10, 100, 100]
        v = ["", "Hundred And", "Thousand", "lakh"]
        w = []
        for i, x in zip(d, v):
            t = get_word(n % i)
            if t != "":
                t += " " + x
            w.append(t.rstrip(" "))
            n = n // i
        w.reverse()
        w = ' '.join(w).strip()
        if w.endswith("And"):
            w = w[:-3]
        return w

    arr = str(number).split(".")
    number = int(arr[0])
    crore = number // 10000000
    number = number % 10000000
    word = ""
    if crore > 0:
        word += get_all_word(crore)
        word += " crore "
    word += get_all_word(number).strip() + " Rupees Only"
    # if len(arr) > 1:
    #     if len(arr[1]) == 1:
    #         arr[1] += "0"
    #     word += " and " + get_all_word(int(arr[1])) + " paisa"
    return word

def generate_invoice(data):
    orderId=data['Order_ID']
    invoiceDate=pd.to_datetime(data['inv_date']).strftime("%d/%m/%Y")
    invoiceNumber=data['inv_number']
    userName=data['user_name']
    name=data['name']
    address=data['address']
    subsName=data['subscription_name']
    subsStart=pd.to_datetime(data['subscription_start']).strftime("%d/%m/%Y")
    subsEnd=pd.to_datetime(data['subscription_end']).strftime("%d/%m/%Y")
    listPrice=data['list_price']
    discount=data['discount']
    amount=data['amount']
    invoiceTotal=data['invoice_total']
    totalWord=number_to_word(invoiceTotal)
    organization=data['organization']

    html="<!DOCTYPE html> <html lang='en'> <head> <meta charset='UTF-8' /> <meta name='viewport' content='width=device-width, initial-scale=1.0' /> <title>Invoice</title> <style> *, body { margin: 0; padding: 0; } .mt-16 { margin-top: 16px; } .mt-8 { margin-top: 8px; } .mt-4 { margin-top: 4px; } table, th, td { border: 1px solid black; border-collapse: collapse; } th, td { padding: 20px; } @media print { .pagebreak { page-break-before: always; } /* page-break-after works, as well */ } </style> </head> <body> <div style='margin: 40px; text-align: center'> <img style='justify-content: center; align-items: center' src='https://storage.googleapis.com/rotijugaad-data/static/admin/roti_jugaad_logo.png' height='100px' alt='' /> <h2 class='mt-8'>INVOICE</h2> <h3 class='mt-4'>ROTI JUGAAD</h3> <h4 class='mt-4'> 1<sup>st</sup> FLoor, Basera Guest House, Saharanpur-247001 (UP) </h4> <div class='mt-16' style='display: grid; grid-template-columns: auto auto' > <div style='grid-column: 1/2; text-align: start'> <b>Invoice Date : </b>"+str(invoiceDate)+"</div> <div style='grid-column: 2/2; text-align: end'> <b>Invoice Number:</b>"+str(invoiceNumber)+"</div> </div> <hr style='margin-top: 20px' /> <div style='text-align: start'> <div class='mt-8'><b>Organization : </b>"+str(organization)+"</div> <div class='mt-8'><b>Name: </b>"+str(name)+"</div> <div class='mt-8'><b>Bill to/Ship to Address: </b>"+str(address)+"</div> <div class='mt-8'><b>Salesperson: </b>Online</div> </div> <hr style='margin-top: 10px' /> <table style='width: 100%; margin-top: 10px'> <thead> <th>S. No.</th> <th>Product Subscription</th> <th>Subscription Start Date</th> <th>Subscription End Date</th> </thead> <tbody> <tr> <td>1</td> <td>"+str(subsName)+"</td> <td>"+str(subsStart)+"</td> <td>"+str(subsEnd)+"</td> </tr> </tbody> </table> <div style=' display: grid; grid-template-columns: auto auto; gap: 16px; margin-top: 20px; ' > <div style='grid-column: 1/2; text-align: start'> <b>List Price INR</b> </div> <div style='grid-column: 2/2; text-align: end'>"+str(listPrice)+"</div> <div style='grid-column: 1/2; text-align: start'> <b>Discount INR</b> </div> <div style='grid-column: 2/2; text-align: end'>"+str(discount)+"</div> <div style='grid-column: 1/2; text-align: start'><b>Amount INR</b></div> <div style='grid-column: 2/2; text-align: end'>"+str(amount)+"</div> <div style='grid-column: 1/2; text-align: start'> <b>Invoice Total INR</b> </div> <div style='grid-column: 2/2; text-align: end'>"+str(invoiceTotal)+"</div> <div style='grid-column: 1/2; text-align: start'> <b>Total (In words)</b> </div> <div style='grid-column: 2/2; text-align: end'>"+str(totalWord)+"</div> </div> <div style=' text-align: end; margin-top: 20px; font-weight: 800; font-size: 18px; ' > For ROTI JUGAAD </div> <div style=' text-align: end; margin-top: 20px; font-weight: 800; font-size: 16px; ' > Authorised Signatory </div> <div style=' text-align: start; margin-top: 20px; font-weight: 800; font-size: 16px; ' > Please note the following </div> <ul style='text-align: start; font-weight: 800'> <li style='margin-top: 8px'> This invoice is recognized subject to realization of payment/confirmation. </li> <li style='margin-top: 4px'> Refer term and conditions attached in the next page. </li> <li style='margin-top: 4px'> All disputes subject to Saharanpur Jurisdiction only. </li> <li style='margin-top: 4px'>This is computer generated invoice.</li> </ul> <div style=' display: flex; flex-direction: row; justify-content: space-between; margin-top: 20px; ' > <div style='text-align: start'> <b>Customer Support</b><br /><br /><b>Email:</b> rotijugaad@gmail.com </div> <div style='text-align: start'> <b >Billing/Head Office<br />Roti Jugaad<br />1st Floor, Basera Guest House<br />Saharanpur - 247001<br />Uttar Pradesh, India</b > </div> </div> </div> <div class='pagebreak'> </div> <div style='margin: 40px; text-align: center'> <img style='justify-content: center; align-items: center' src='https://storage.googleapis.com/rotijugaad-data/static/admin/roti_jugaad_logo.png' height='100px' alt='' /> <h2 style='margin-top: 20px;'>Terms and Conditions</h2> <ul style='text-align: start; font-weight: 800;margin-top: 30px;font-size: 17px;'> <li class='mt-4'>The complete Terms & Conditions (TnC) in relation to the product/services offered & accepted by the customer, and in relation to the general TnC on portal usage are available on the application (portal) for which services have been subscribed.</li> <li class='mt-4'>The payment released against the invoice deems confirmation & acceptance to all the terms & conditions, as amended from time to time.</li> <li class='mt-4'>The usage of the portal and its associated services constitue a binding agreement with Roti Jugaad and customer's agreement to abide by the same.</li> <li class='mt-4'>The content on the portal is the property of Roti Jugaad or its content suppliers or customers. Roti Jugaad further reserves its right to post the data on the portal or on such other affiliated sites and publications as Roti Jugaad may deem fit and proper at no extra cost to the subscriber/user.</li> <li class='mt-4'>Roti Jugaad reserves its right to reject any insertion or information/data provided by the subscriber without assigning any reason either before uploading or after uploading the vacancy details, but in such an eventuality, any amount so paid for shall be refunded to the subscriber on a pro-rata basis at the sole discretion of Roti Jugaad.</li><li class='mt-4'>Engaging in any conduct prohibited by law or usage of services in any manner so as to impair the interests and functioning of Roti Jugaad. or its Users may result in withdrawal of Service. If your Cheque is returned dishonored or in case of a charge back on an online transaction (including credit card payment), services will be immediately deactivated. In case of cheques dishonored, the reactiviation would be done only on payment of an additional Rs 500 per instance of dishonor.</li> <li class='mt-4'>Roti Jugaad does not gaurantee (i) the quality or quantity of response to any of its services (ii) server uptime or applications working properly. All is on a best effort basis and liability is limited to refund of amount paid on pro-rated basis only. Roti Jugaad undertakes no liability for free services.</li> <li class='mt-4'>The service is neither re-saleable nor transferable by the Subscriber to any other person, corporate body, firm or individual.</li> <li class='mt-4'>Refund, if any shall be admissible at the sole discretion of Roti Jugaad.</li> <li class='mt-4'>Laws of India as applicable shall govern. Courts in Saharanpur will have exclusive Jurisdiction in case of any dispute.</li> </ul> </div> </body> </html>"

    return html

class RegisteredUsersAPIView(APIView):
    serializer_class = RegisteredUsersSerializer

    def get_object(self, phone_no):
        try:
            return RegisteredUsers.objects.get(Phone_No=phone_no)
        except RegisteredUsers.DoesNotExist:
            raise Http404
        
    def get(self, request,phone_no, format=None):
        try:
            user = RegisteredUsers.objects.get(Phone_No=phone_no)
            serializer = self.serializer_class(user, many=False)
            return Response(serializer.data)
        except RegisteredUsers.DoesNotExist:
            return Response(status=status.HTTP_204_NO_CONTENT)

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)

        if RegisteredUsers.objects.filter(Phone_No=request.data['Phone_No']).exists():
            return Response({"Phone_No":["Phone No Already Registered"]}, status=status.HTTP_400_BAD_REQUEST)
        
        if serializer.is_valid():
            serializer.save()
            serialized_data = serializer.data
            return Response(serialized_data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, phone_no, format=None):
        instance = self.get_object(phone_no)
        serializer = self.serializer_class(
            instance, data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            serialized_data = serializer.data
            return Response(serialized_data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class EmployeeAPIView(APIView):
    serializer_class = EmployeeSerializer

    def get(self, request, format=None):
        employees = Employee.objects.all()
        serializer = self.serializer_class(employees, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):

        try:
            phone=request.data['User_ID']
            employee=Employee.objects.get(User_ID=phone)
            serializer = self.serializer_class(employee, many=False)

            return Response(serializer.data)
        except Employee.DoesNotExist:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.save()
                serialized_data = serializer.data
                return Response(serialized_data, status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class UserEmployeeAPIView(APIView):
    serializer_class=EmployeeSerializer
    job_preference_serializer_class=EmployeeJobPreferenceSerializer
    qualification_serializer_class=EmployeeQualificationSerializer
        
    def get(self, request, user_id, format=None):
        try:
            employee = Employee.objects.get(User_ID=user_id)
            serializer = self.serializer_class(employee)
            x=serializer.data

            jobPreference=EmployeeJobPreference.objects.filter(Employee_ID=x['EmployeeID']).values('Category__Category','User_ID','ID','Employee_ID')
            # jobSerializer=self.job_preference_serializer_class(jobPreference,many=True)
            x['job_preference']=jobPreference

            qualification=EmployeeQualification.objects.filter(Employee_ID=x['EmployeeID'])
            qualificationSerializer=self.qualification_serializer_class(qualification,many=True)
            x['qualifications']=qualificationSerializer.data

            # validityDate=datetime.strptime(x['Validity'],"%Y-%m-%dT%H:%M:%S.%f%z")
            validityDate=pd.to_datetime(x['Validity'])
            now=datetime.now().replace(microsecond=0).replace(tzinfo=validityDate.tzinfo)

            if now>validityDate and (x['Total_Contact_Credits'] or x['Total_Interest_Credits'] or x['Contact_Credits'] or x['Interest_Credits']):
                employee_serializer = self.serializer_class(employee, data={"Contact_Credits":0,"Interest_Credits":0,"Total_Contact_Credits":0,"Total_Interest_Credits":0}, partial=True)
                if employee_serializer.is_valid():
                    employee_serializer.save()

            return Response(x)
        except Employee.DoesNotExist:
            return Response(status=status.HTTP_204_NO_CONTENT)
    

class UserEmployerAPIView(APIView):
    serialier_class=EmployerSerializer
        
    def get(self, request, user_id, format=None):
        try:
            employer = Employer.objects.get(User_ID=user_id)
            serializer = self.serialier_class(employer)
            x=serializer.data

            validityDate=pd.to_datetime(x['Validity'])
            now=datetime.now().replace(microsecond=0).replace(tzinfo=validityDate.tzinfo)

            if now>validityDate and (x['Total_Contact_Credits'] or x['Total_Interest_Credits'] or x['Contact_Credits'] or x['Interest_Credits'] or x['Job_Post_Credits'] or x['Total_Job_Post_Credits']):
                employer_serializer = self.serialier_class(employer, data={"Contact_Credits":0,"Interest_Credits":0,"Total_Contact_Credits":0,"Total_Interest_Credits":0,"Total_Job_Post_Credits":0,"Job_Post_Credits":0}, partial=True)
                if employer_serializer.is_valid():
                    employer_serializer.save()

            return Response(x)
        except Employer.DoesNotExist:
            return Response(status=status.HTTP_204_NO_CONTENT)


class EmployeeDetailAPIView(APIView):
    serializer_class = EmployeeSerializer
    job_preference_serializer_class=EmployeeJobPreferenceSerializer
    qualification_serializer_class=EmployeeQualificationSerializer

    def get_object_by_employee_id(self, employee_id):
        try:
            employee = Employee.objects.get(EmployeeID=employee_id)
            return employee
        except Employee.DoesNotExist:
            raise Http404

    def get(self, request, employee_id, format=None):
        employee = self.get_object_by_employee_id(employee_id)
        serializer = self.serializer_class(employee)

        x=serializer.data

        jobPreference=EmployeeJobPreference.objects.filter(Employee_ID=x['EmployeeID']).values('Category__Category','User_ID','ID','Employee_ID')
            # jobSerializer=self.job_preference_serializer_class(jobPreference,many=True)
        x['job_preference']=jobPreference

        qualification=EmployeeQualification.objects.filter(Employee_ID=x['EmployeeID'])
        qualificationSerializer=self.qualification_serializer_class(qualification,many=True)
        x['qualifications']=qualificationSerializer.data

        validityDate=pd.to_datetime(x['Validity'])
        now=datetime.now().replace(microsecond=0).replace(tzinfo=validityDate.tzinfo)

        if now>validityDate and (x['Total_Contact_Credits'] or x['Total_Interest_Credits'] or x['Contact_Credits'] or x['Interest_Credits']):
            employee_serializer = self.serializer_class(employee, data={"Contact_Credits":0,"Interest_Credits":0,"Total_Contact_Credits":0,"Total_Interest_Credits":0}, partial=True)
            if employee_serializer.is_valid():
                employee_serializer.save()

        return Response(x)

    def put(self, request, employee_id, format=None):
        employee = self.get_object_by_employee_id(employee_id)
        serializer = self.serializer_class(employee, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            serialized_data = serializer.data
            return Response(serialized_data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmployeeQualificationAPIView(APIView):
    serializer_class=EmployeeQualificationSerializer

    def get_object(self, qualification_id):
        try:
            qualification = EmployeeQualification.objects.get(QualificationID=qualification_id)
            return qualification
        except Employer.DoesNotExist:
            raise Http404
        

    def get(self,request,user_id,format=None):
        try:
            qualifications=EmployeeQualification.objects.filter(User_ID=user_id)
            serializer=self.serializer_class(qualifications,many=True)
            return Response(serializer.data)
        except EmployeeQualification.DoesNotExist:
            return Response(status=status.HTTP_204_NO_CONTENT)
    
    def post(self,request,format=None):
        serializer=self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            serialized_data=serializer.data
            return Response(serialized_data,status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    def put(self,request,user_id,format=None):
        qualification = self.get_object(user_id)
        serializer = self.serializer_class(qualification, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            serialized_data = serializer.data
            return Response(serialized_data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self,request,user_id,format=None):
        qualification = self.get_object(user_id)
        qualification.delete()
        return Response(status=status.HTTP_200_OK)


class EmployeeJobPreferenceAPIView(APIView):
    serializer_class=EmployeeJobPreferenceSerializer

    def get(self,request,employee_id,format=None):
        try:
            preferences=EmployeeJobPreference.objects.filter(Employee_ID=employee_id)
            serializer=self.serializer_class(preferences,many=True)
            return Response(serializer.data)
        except EmployeeJobPreference.DoesNotExist:
            return Response(status=status.HTTP_204_NO_CONTENT)
        

    def post(self,request,employee_id,format=None):
        print('test')
        EmployeeJobPreference.objects.filter(Employee_ID=employee_id).delete()
        for d in request.data:
            print(d)
            serializer=self.serializer_class(data=d)
            if serializer.is_valid():
                serializer.save()
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(data=request.data,status=status.HTTP_201_CREATED)
 
class EmployerAPIView(APIView):
    serializer_class = EmployerSerializer

    def get(self, request, format=None):
        employers = Employer.objects.all()
        serializer = self.serializer_class(employers, many=True)

        return Response(serializer.data)

    def post(self, request, format=None):
        try:
            phone=request.data['User_ID']
            employer=Employer.objects.get(User_ID=phone)
            serializer = self.serializer_class(employer, many=False)
            return Response(serializer.data)
        except Employer.DoesNotExist:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.save()
                serialized_data = serializer.data
                return Response(serialized_data, status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmployerDetailAPIView(APIView):
    serializer_class = EmployerSerializer

    def get_object(self, employer_id):
        try:
            employer = Employer.objects.get(EmployerID=employer_id)
            return employer
        except Employer.DoesNotExist:
            raise Http404

    def get(self, request, employer_id, format=None):
        employer = self.get_object(employer_id)
        serializer = self.serializer_class(employer)
        x=serializer.data

        validityDate=pd.to_datetime(x['Validity'])
        now=datetime.now().replace(microsecond=0).replace(tzinfo=validityDate.tzinfo)

        if now>validityDate and (x['Total_Contact_Credits'] or x['Total_Interest_Credits'] or x['Contact_Credits'] or x['Interest_Credits'] or x['Job_Post_Credits'] or x['Total_Job_Post_Credits']):
            employer_serializer = self.serializer_class(employer, data={"Contact_Credits":0,"Interest_Credits":0,"Total_Contact_Credits":0,"Total_Interest_Credits":0,"Total_Job_Post_Credits":0,"Job_Post_Credits":0}, partial=True)
            if employer_serializer.is_valid():
                employer_serializer.save()

        return Response(serializer.data)

    def put(self, request, employer_id, format=None):
        try:
            employer = self.get_object(employer_id)
            serializer = self.serializer_class(employer, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                serialized_data = serializer.data
                return Response(serialized_data, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            raise e

class PaymentEmployeeAPIView(APIView):
    employee_serializer_class = EmployeeSerializer

    def get_employee_by_employee_id(self,Employee_ID):
        try:
            employee=Employee.objects.get(Employee_ID=Employee_ID)
            return employee
        except Employee.DoesNotExist:
            raise Http404

    def post(self, request, format=None):
        serializer = PaymentEmployeeSerializer(data=request.data)
        if serializer.is_valid():
            employeeId=serializer.data['Employee_ID']
            contactCredits=serializer.data['Contact_Credit']
            interestCredits=serializer.data['Interest_Credit']

            employee=self.get_employee_by_employee_id(employeeId)
            employee_serializer = self.employee_serializer_class(employee, many=False)
            serialized_data = employee_serializer.data

            employeeContactCredits=serialized_data['Contact_Credits']
            employeeInterestCredits=serialized_data['Interest_Credits']

            employee_serializer = self.employee_serializer_class(employee, data={"Contact_Credits":employeeContactCredits+contactCredits,"Interest_Credits":employeeInterestCredits+interestCredits}, partial=True)
            if employee_serializer.is_valid():
                employee_serializer.save()
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

    def get_object(self, employee_id):
        try:
            payment_employee = Payment_Employee.objects.filter(Employee_ID=employee_id).order_by('-subscription_end')
            return payment_employee
        except Payment_Employee.DoesNotExist:
            raise Http404

    def get(self, request, employee_id, format=None):
        payment_employee = self.get_object(employee_id)
        serializer = PaymentEmployeeSerializer(payment_employee, many=True)
        serialized_data = serializer.data
        paymentHistory=[]
        for x in serialized_data:
            employee=Employee.objects.get(EmployeeID=x['Employee_ID'])
            emp_serializer = self.employee_serializer_class(employee, many=False)
            x['organization']=emp_serializer.data['Name']
            x['invoice']=generate_invoice(x)
            paymentHistory.append(x)

        return Response(paymentHistory, status=status.HTTP_200_OK)

class PaymentEmployerAPIView(APIView):
    employer_serializer_class = EmployerSerializer

    def get_employer_by_employer_id(self,Employer_ID):
        try:
            employer=Employer.objects.get(Employer_ID=Employer_ID)
            return employer
        except Employer.DoesNotExist:
            raise Http404

    def post(self, request, format=None):
        serializer = PaymentEmployerSerializer(data=request.data)
        if serializer.is_valid():
            employerId=serializer.data['Employer_ID']
            contactCredits=serializer.data['Contact_Credit']
            interestCredits=serializer.data['Interest_Credit']
            jobPostCredits=serializer.data['Job_Post_Credit']

            employer=self.get_employer_by_employer_id(employerId)
            employer_serializer = self.employer_serializer_class(employer, many=False)
            serialized_data = employer_serializer.data

            employerContactCredits=serialized_data['Contact_Credits']
            employerInterestCredits=serialized_data['Interest_Credits']
            employerJobPostCredits=serialized_data['Job_Post_Credits']

            employer_serializer = self.employer_serializer_class(employer, data={"Contact_Credits":employerContactCredits+contactCredits,"Interest_Credits":employerInterestCredits+interestCredits,"Job_Post_Credits":employerJobPostCredits+jobPostCredits}, partial=True)
            if employer_serializer.is_valid():
                employer_serializer.save()
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

            

    def get_object(self, employer_id):
        try:
            payment_employer = Payment_Employer.objects.filter(Employer_ID=employer_id).order_by('-subscription_end')
            return payment_employer
        except Payment_Employer.DoesNotExist:
            raise Http404

    def get(self, request, employer_id, format=None):
        payment_employer = self.get_object(employer_id)
        serializer = PaymentEmployerSerializer(payment_employer, many=True)
        serialized_data = serializer.data
        paymentHistory=[]
        for x in serialized_data:
            employer=Employer.objects.get(EmployerID=x['Employer_ID'])
            empr_serializer = self.employer_serializer_class(employer, many=False)
            x['organization']=empr_serializer.data['Organization']
            x['invoice']=generate_invoice(x)
            paymentHistory.append(x)

        return Response(paymentHistory, status=status.HTTP_200_OK)

class EmployeeToEmployerJobAPIView(APIView):
    serializer_class = EmployeeToEmployerJobSerializer
    employee_serializer_class = EmployeeSerializer
    employer_serializer_class=EmployerSerializer
    job_serializer_class=JobSerializer

    def get_employee_by_employee_id(self,Employee_ID):
        try:
            return Employee.objects.get(EmployeeID=Employee_ID)
        except Employee.DoesNotExist:
            raise Http404
        
    def get_employer_by_employer_id(self,Employer_ID):
        try:
            return Employer.objects.get(EmployerID=Employer_ID)
        except Employer.DoesNotExist:
            raise Http404
        
    def get_job_by_job_id(self,JobID):
        try:
            return Job.objects.get(Job_ID=JobID)
        except Job.DoesNotExist:
            raise Http404

    def get_object_by_job_id(self, Job_ID,Employee_ID):
        try:
            return Employee_To_Employer_Job.objects.filter(Job_ID=Job_ID,Employee_ID=Employee_ID)
        except Employee_To_Employer_Job.DoesNotExist:
            raise Http404

    def get_object_by_employee_id(self, Employee_ID):
        try:
            return Employee_To_Employer_Job.objects.filter(Employee_ID=Employee_ID)
        except Employee_To_Employer_Job.DoesNotExist:
            raise Http404
        
    def get_object_by_employer_id(self, Employer_ID):
        try:
            return Employee_To_Employer_Job.objects.filter(Employer_ID=Employer_ID)
        except Employee_To_Employer_Job.DoesNotExist:
            raise Http404

    def get(self, request, format=None):
        Job_ID = request.query_params.get('job_id')
        Employee_ID = request.query_params.get('employee_id')
        Employer_ID = request.query_params.get('employer_id')

        if Job_ID and Employee_ID:
            employee_to_employer_jobs = self.get_object_by_job_id(Job_ID,Employee_ID)
        elif Employee_ID:
            employee_to_employer_jobs = self.get_object_by_employee_id(Employee_ID)
        elif Employer_ID:
            employee_to_employer_jobs = self.get_object_by_employer_id(Employer_ID)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        empEmpyJobs=[]
        for etej in employee_to_employer_jobs:
            serializer = self.serializer_class(etej, many=False)
            serialized_data = serializer.data
            serialized_data['Organization_Type']=etej.Employer_ID.Organization_Type
            serialized_data['Employer_Name']=etej.Employer_ID.Name
            serialized_data['Employer_Organization']=etej.Employer_ID.Organization
            serialized_data['Employer_Address']=etej.Employer_ID.Address
            serialized_data['Employee_Name']=etej.Employee_ID.Name
            serialized_data['Employee_State_Ut']=etej.Employee_ID.Preferred_State_Ut
            serialized_data['Employee_City']=etej.Employee_ID.Preferred_City
            serialized_data['EmployeeSalary']=etej.Employee_ID.Expected_Salary
            serialized_data['EmployeeSalaryFrequency']=etej.Employee_ID.Salary_Frequency

            jobPreference=EmployeeJobPreference.objects.filter(Employee_ID=etej.Employee_ID).values('Category__Category','User_ID','ID','Employee_ID')
            serialized_data['job_preference']=jobPreference

            empEmpyJobs.append(serialized_data)
        return Response(empEmpyJobs, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        if 'Employee_ID' in request.data:
            employeeId=request.data['Employee_ID']
            employee=self.get_employee_by_employee_id(employeeId)
            employee_serializer = self.employee_serializer_class(employee,many=False)
            employee_serialized_data=employee_serializer.data
            
            if employee_serialized_data is not None and employee_serialized_data['Interest_Credits']>0:
                interestCredits=employee_serialized_data['Interest_Credits']
                employerId=request.data['Employer_ID']
                employer=self.get_employer_by_employer_id(employerId)
                employer_serializer=self.employer_serializer_class(employer,many=False)
                employer_serialized_data=employer_serializer.data

                jobId=request.data['Job_ID']
                job=self.get_job_by_job_id(jobId)
                job_serializer=self.job_serializer_class(job,many=False)
                job_serialized_data=job_serializer.data
                receivedInterests=job_serialized_data['Received_Interests']

                try:
                    Employee_To_Employer_Job.objects.get(Employer_ID=employerId,Employee_ID=employeeId,Job_ID=jobId)
                except Employee_To_Employer_Job.DoesNotExist:
                    serializer = self.serializer_class(data=request.data)
                    if serializer.is_valid():
                        serializer.save()
                        serialized_data = serializer.data
                        
                        employee_serializer = self.employee_serializer_class(employee, data={"Interest_Credits":interestCredits-1}, partial=True)
                        job_serializer=self.job_serializer_class(job,data={"Received_Interests":receivedInterests+1},partial=True)
                        if employee_serializer.is_valid():
                            employee_serializer.save()
                            if job_serializer.is_valid():
                                job_serializer.save()
                            send_notification(employer_serialized_data['User_ID'],"Congratulations, You have received interest from "+employee_serialized_data['Name'])
                            return Response(serialized_data, status=status.HTTP_201_CREATED)
                        return Response(employee_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                return Response(status=status.HTTP_302_FOUND)
            return Response(status=status.HTTP_402_PAYMENT_REQUIRED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

class EmployerToEmployeeJobAPIView(APIView):
    serializer_class = EmployerToEmployeeJobSerializer
    employer_serializer_class = EmployerSerializer
    employee_serializer_class=EmployeeSerializer
    job_serializer_class=JobSerializer

    def get_employer_by_employer_id(self,Employer_ID):
        try:
            return Employer.objects.get(EmployerID=Employer_ID)
        except Employer.DoesNotExist:
            return Http404
        
    def get_employee_by_employee_id(self,Employee_ID):
        try:
            return Employee.objects.get(EmployeeID=Employee_ID)
        except Employee.DoesNotExist:
            return Http404
        
    def get_job_by_job_id(self,Job_ID):
        try:
            return Job.objects.get(Job_ID=Job_ID)
        except Job.DoesNotExist:
            return Http404
        
    def get_object_by_job_id(self, Job_ID,Employer_ID):
        try:
            return Employer_To_Employee_Job.objects.filter(Job_ID=Job_ID,Employer_ID=Employer_ID)
        except Employer_To_Employee_Job.DoesNotExist:
            raise Http404

    def get_object_by_employee_id(self, Employee_ID):
        try:
            return Employer_To_Employee_Job.objects.filter(Employee_ID=Employee_ID)
        except Employer_To_Employee_Job.DoesNotExist:
            raise Http404

    def get_object_by_employer_id(self, Employer_ID):
        try:
            return Employer_To_Employee_Job.objects.filter(Employer_ID=Employer_ID)
        except Employer_To_Employee_Job.DoesNotExist:
            raise Http404

    def get(self, request, format=None):
        job_id = request.query_params.get('job_id')
        employee_id = request.query_params.get('employee_id')
        employer_id = request.query_params.get('employer_id')

        if job_id and employer_id:
            employer_to_employee_jobs = self.get_object_by_job_id(job_id,employer_id)
        elif employee_id:
            employer_to_employee_jobs = self.get_object_by_employee_id(employee_id)
        elif employer_id:
            employer_to_employee_jobs = self.get_object_by_employer_id(employer_id)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        empyEmpJobs=[]
        for etej in employer_to_employee_jobs:
            serializer = self.serializer_class(etej, many=False)
            serialized_data = serializer.data
            serialized_data['Organization_Type']=etej.Employer_ID.Organization_Type
            serialized_data['Employer_Name']=etej.Employer_ID.Name
            serialized_data['Employer_Organization']=etej.Employer_ID.Organization
            serialized_data['Employer_Address']=etej.Employer_ID.Address
            serialized_data['Employee_Name']=etej.Employee_ID.Name
            serialized_data['Employee_State_Ut']=etej.Employee_ID.Preferred_State_Ut
            serialized_data['Employee_City']=etej.Employee_ID.Preferred_City
            serialized_data['EmployeeSalary']=etej.Employee_ID.Expected_Salary
            serialized_data['EmployeeSalaryFrequency']=etej.Employee_ID.Salary_Frequency
            # serialized_data['Job_Shift']=etej.Job_ID.Job_Shift

            jobPreference=EmployeeJobPreference.objects.filter(Employee_ID=etej.Employee_ID).values('Category__Category','User_ID','ID','Employee_ID')
            serialized_data['job_preference']=jobPreference

            empyEmpJobs.append(serialized_data)
        return Response(empyEmpJobs, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        if 'Employer_ID' in request.data:
            employerId=request.data['Employer_ID']
            employer=self.get_employer_by_employer_id(employerId)
            employer_serializer = self.employer_serializer_class(employer,many=False)
            employer_serialized_data=employer_serializer.data
            
            if employer_serialized_data is not None and employer_serialized_data['Interest_Credits']>0:
                interestCredits=employer_serialized_data['Interest_Credits']
                employeeId=request.data['Employee_ID']
                employee=self.get_employee_by_employee_id(employeeId)
                employee_serializer=self.employee_serializer_class(employee,many=False)
                employee_serialized_data=employee_serializer.data

                jobId=request.data['Job_ID']
                job=self.get_job_by_job_id(jobId)
                job_serializer=self.job_serializer_class(job,many=False)
                job_serialized_data=job_serializer.data
                sentInterests=job_serialized_data['Sent_Interests']
                
                try:
                    Employer_To_Employee_Job.objects.get(Employer_ID=employerId,Employee_ID=employeeId,Job_ID=jobId)
                except Employer_To_Employee_Job.DoesNotExist:
                    serializer = self.serializer_class(data=request.data)
                    if serializer.is_valid():
                        serializer.save()
                        serialized_data = serializer.data
                        
                        employer_serializer = self.employer_serializer_class(employer, data={"Interest_Credits":interestCredits-1}, partial=True)
                        job_serializer=self.job_serializer_class(job,data={"Sent_Interests":sentInterests+1},partial=True)
                        if employer_serializer.is_valid():
                            employer_serializer.save()
                            if job_serializer.is_valid():
                                job_serializer.save()
                            send_notification(employee_serialized_data['User_ID'],"Congratulations, You have received interest from "+employer_serialized_data['Name']) 
                            return Response(serialized_data, status=status.HTTP_201_CREATED)
                        return Response(employer_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                return Response(status=status.HTTP_302_FOUND)
            return Response(status=status.HTTP_402_PAYMENT_REQUIRED)
        return Response(status=status.HTTP_400_BAD_REQUEST)



class EmployeeToEmployerCallAPIView(APIView):
    serializer_class = EmployeeToEmployerCallSerializer
    employee_serializer_class = EmployeeSerializer

    def get_employee_by_employee_id(self,Employee_ID):
        try:
            return Employee.objects.get(EmployeeID=Employee_ID)
        except Employee.DoesNotExist:
            raise Http404

    def get_object_by_employer_id(self, Employer_ID):
        try:
            return Employee_To_Employer_Call.objects.filter(Employer_ID=Employer_ID)
        except Employee_To_Employer_Call.DoesNotExist:
            raise Http404
        
    def get_object_by_job_id(self, Job_ID,Employee_ID):
        try:
            return Employee_To_Employer_Call.objects.filter(Job_ID=Job_ID,Employee_ID=Employee_ID)
        except Employee_To_Employer_Call.DoesNotExist:
            raise Http404

    def get_object_by_employee_id(self, Employee_ID):
        try:
            return Employee_To_Employer_Call.objects.filter(Employee_ID=Employee_ID)
        except Employee_To_Employer_Call.DoesNotExist:
            raise Http404

    def get(self, request, format=None):
        Employee_ID = request.query_params.get('employee_id')
        Employer_ID = request.query_params.get('employer_id')
        Job_ID = request.query_params.get('job_id')

        if Employee_ID:
            employee_to_employer_calls = self.get_object_by_employee_id(Employee_ID)
        elif Employer_ID:
            employee_to_employer_calls = self.get_object_by_employer_id(Employer_ID)
        elif Job_ID and Employee_ID:
            employee_to_employer_calls = self.get_object_by_job_id(Job_ID,Employee_ID)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        empEmpyCall=[]
        for etec in employee_to_employer_calls:
            serializer = self.serializer_class(etec, many=False)
            serialized_data = serializer.data
            serialized_data['Job_Shift']=etec.Job_ID.Job_Shift
            serialized_data['Salary_Offered']=etec.Job_ID.Salary_Offered
            serialized_data['Frequency']=etec.Job_ID.Frequency
            empEmpyCall.append(serialized_data)
        return Response(empEmpyCall, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        if 'Employee_ID' in request.data:
            employeeId=request.data['Employee_ID']
            jobId=request.data['Job_ID']
            employee=self.get_employee_by_employee_id(employeeId)
            employee_serializer = self.employee_serializer_class(employee,many=False)
            employee_serialized_data=employee_serializer.data
            
            if employee_serialized_data is not None and employee_serialized_data['Contact_Credits']>0:
                contactCredits=employee_serialized_data['Contact_Credits']
                employerId=request.data['Employer_ID']
                
                try:
                    Employee_To_Employer_Call.objects.get(Employer_ID=employerId,Employee_ID=employeeId,Job_ID=jobId)
                except Employee_To_Employer_Call.DoesNotExist:
                    serializer = self.serializer_class(data=request.data)
                    if serializer.is_valid():
                        serializer.save()
                        serialized_data = serializer.data
                        
                        employee_serializer = self.employee_serializer_class(employee, data={"Contact_Credits":contactCredits-1}, partial=True)
                        if employee_serializer.is_valid():
                            employee_serializer.save()
                            return Response(serialized_data, status=status.HTTP_201_CREATED)
                        return Response(employee_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                return Response(status=status.HTTP_302_FOUND)
            return Response(status=status.HTTP_402_PAYMENT_REQUIRED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

class EmployerToEmployeeCallAPIView(APIView):
    serializer_class = EmployerToEmployeeCallSerializer
    employer_serializer_class = EmployerSerializer
    

    def get_employer_by_employer_id(self,Employer_ID):
        try:
            return Employer.objects.get(EmployerID=Employer_ID)
        except Employer.DoesNotExist:
            return Http404
        
    def get_object_by_job_id(self, Job_ID,Employer_ID):
        try:
            return Employer_To_Employee_Call.objects.filter(Job_ID=Job_ID,Employer_ID=Employer_ID)
        except Employer_To_Employee_Call.DoesNotExist:
            raise Http404

    def get_object_by_employee_id(self, Employee_ID):
        try:
            return Employer_To_Employee_Call.objects.filter(Employee_ID=Employee_ID)
        except Employer_To_Employee_Call.DoesNotExist:
            raise Http404

    def get_object_by_employer_id(self, Employer_ID):
        try:
            return Employer_To_Employee_Call.objects.filter(Employer_ID=Employer_ID)
        except Employer_To_Employee_Call.DoesNotExist:
            raise Http404
        
    def get_object_by_employer_employee_id(self,Employer_ID,Employee_ID):
        try:
            return Employer_To_Employee_Call.objects.filter(Employer_ID=Employer_ID,Employee_ID=Employee_ID)
        except Employer_To_Employee_Call.DoesNotExist:
            raise Http404

    def get(self, request, format=None):
        employee_id = request.query_params.get('employee_id')
        employer_id = request.query_params.get('employer_id')
        job_id=request.query_params.get('job_id')

        if employee_id and employer_id:
            employer_to_employee_jobs = self.get_object_by_employer_employee_id(employer_id,employee_id)
        elif employee_id:
            employer_to_employee_jobs = self.get_object_by_employee_id(employee_id)
        elif employer_id:
            employer_to_employee_jobs = self.get_object_by_employer_id(employer_id)
        elif job_id and employer_id:
            employer_to_employee_jobs=self.get_object_by_job_id(job_id,employer_id)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        empyEmpCall=[]
        for etec in employer_to_employee_jobs:
            serializer = self.serializer_class(etec, many=False)
            serialized_data = serializer.data
            # serialized_data['Job_Profile']=etec.Job_ID.Job_Profile
            # serialized_data['Job_Shift']=etec.Job_ID.Job_Shift
            serialized_data['Employee_Shift']=etec.Employee_ID.Preferred_Shift
            jobPreference=EmployeeJobPreference.objects.filter(Employee_ID=serialized_data['Employee_ID']).values('Category__Category','User_ID','ID','Employee_ID')
            # jobSerializer=self.job_preference_serializer_class(jobPreference,many=True)
            serialized_data['job_preference']=jobPreference
            # serialized_data['']
            empyEmpCall.append(serialized_data)
        return Response(empyEmpCall, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        if 'Employer_ID' in request.data:
            employerId=request.data['Employer_ID']
            employer=self.get_employer_by_employer_id(employerId)
            employer_serializer = self.employer_serializer_class(employer,many=False)
            employer_serialized_data=employer_serializer.data
            
            if employer_serialized_data is not None and employer_serialized_data['Contact_Credits']>0:
                contactCredits=employer_serialized_data['Contact_Credits']
                employeeId=request.data['Employee_ID']
                
                try:
                    Employer_To_Employee_Call.objects.get(Employer_ID=employerId,Employee_ID=employeeId)
                except Employer_To_Employee_Call.DoesNotExist:
                    serializer = self.serializer_class(data=request.data)
                    if serializer.is_valid():
                        serializer.save()
                        serialized_data = serializer.data
                        
                        employer_serializer = self.employer_serializer_class(employer, data={"Contact_Credits":contactCredits-1}, partial=True)
                        if employer_serializer.is_valid():
                            employer_serializer.save()
                            return Response(serialized_data, status=status.HTTP_201_CREATED)
                        return Response(employer_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                return Response(status=status.HTTP_302_FOUND)
            return Response(status=status.HTTP_402_PAYMENT_REQUIRED)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class AvailableCandidatesAPIView(APIView):
    serializer_class=EmployeeSerializer
    job_preference_serializer_class=EmployeeJobPreferenceSerializer
    qualification_serializer_class=EmployeeQualificationSerializer

    def get_object_by_frequency(self, Frequency):
        try:
            return Employee.objects.filter(Salary_Frequency=Frequency,Profile_Completed=True,Approved=True,Active=True)
        except Employee.DoesNotExist:
            raise Http404

    def get(self,request,format=None):
        frequency = request.query_params.get('frequency')

        if frequency:
            employees = self.get_object_by_frequency(frequency)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        

        serializer = self.serializer_class(employees, many=True)
        serialized_data = serializer.data
        newdata=[]
        for x in serialized_data:
            jobPreference=EmployeeJobPreference.objects.filter(Employee_ID=x['EmployeeID']).values('Category__Category','User_ID','ID','Employee_ID')
            # jobSerializer=self.job_preference_serializer_class(jobPreference,many=True)
            x['job_preference']=jobPreference

            qualification=EmployeeQualification.objects.filter(Employee_ID=x['EmployeeID'])
            qualificationSerializer=self.qualification_serializer_class(qualification,many=True)
            x['qualifications']=qualificationSerializer.data

            newdata.append(x)
        return Response(newdata, status=status.HTTP_200_OK)
    

class JobAPIView(APIView):
    serializer_class = JobSerializer
    employer_serializer_class = EmployerSerializer
    

    def get_employer_by_employer_id(self,Employer_ID):
        try:
            return Employer.objects.get(EmployerID=Employer_ID)
        except Employer.DoesNotExist:
            return Http404

    def get(self, request, format=None):
        jobs = Job.objects.filter(Vacancy__gt=0)
        jobData=[]
        for job in jobs:
            serializer = self.serializer_class(job, many=False)
            serialized_data = serializer.data
            serialized_data['Organization_Type']=job.Employer_ID.Organization_Type
            jobData.append(serialized_data)

        return Response(jobData, status=status.HTTP_200_OK)

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            employerId=request.data['Employer_ID']
            employer=self.get_employer_by_employer_id(employerId)
            employer_serializer = self.employer_serializer_class(employer,many=False)
            employer_serialized_data=employer_serializer.data
            
            if employer_serialized_data is not None and employer_serialized_data['Job_Post_Credits']>0:
                jobPostCredits=employer_serialized_data['Job_Post_Credits']
                serializer.save()
                serialized_data = serializer.data

                employer_serializer = self.employer_serializer_class(employer, data={"Job_Post_Credits":jobPostCredits-1}, partial=True)
                if employer_serializer.is_valid():
                    employer_serializer.save()
                    return Response(serialized_data, status=status.HTTP_201_CREATED)
                return Response(employer_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response(status=status.HTTP_402_PAYMENT_REQUIRED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class JobExtendedAPIView(APIView):
    serializer_class = JobSerializer

    def get_job_by_employer_id(self, Employer_ID):
        jobs = Job.objects.filter(Employer_ID=Employer_ID).order_by('-Date')
        return jobs

    def get(self, request, pk=None, format=None):
        if pk:
            jobs = self.get_job_by_employer_id(pk)
            serializer = self.serializer_class(jobs, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk=None, format=None):
        try:
            job = Job.objects.get(Job_ID=pk)
        except Job.DoesNotExist:
            return Response({"error": "Job not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(job, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            serialized_data = serializer.data
            return Response(serialized_data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class JobDeleteAPIView(APIView):
    serializer_class=JobSerializer

    def delete(self,request,pk=None,format=None):
        try:
            job = Job.objects.filter(Job_ID=pk).first()
        except Job.DoesNotExist:
            return Response({"error": "Job not found."}, status=status.HTTP_404_NOT_FOUND)
        
        job.delete()
        return Response(status=status.HTTP_200_OK)

class EmployeeSubscriptionAPIView(APIView):
    serializer_class = EmployeeSubscriptionSerializer

    def get(self, request, format=None):
        subscriptions = EmployeeSubscription.objects.all()
        serializer = self.serializer_class(subscriptions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class EmployerSubscriptionAPIView(APIView):
    serializer_class = EmployerSubscriptionSerializer

    def get(self, request, format=None):
        subscriptions = EmployerSubscription.objects.all()
        serializer = self.serializer_class(subscriptions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class RequestACallAPIView(APIView):
    serializer_class = RequestACallSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            serialized_data = serializer.data
            return Response(serialized_data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ReferredByAPIView(APIView):
    serializer_class = ReferredBySerializer

    def get(self, request, format=None):
        referrals = ReferredBy.objects.all()
        serializer = self.serializer_class(referrals, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class JobCategoryAPIView(APIView):
    serializer_class = JobCategorySerializer

    def get(self, request, format=None):
        categories = JobCategory.objects.all()
        serializer = self.serializer_class(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class HiringTableAPIView(APIView):
    serializer_class = HiringTableSerializer
    job_serializer_class=JobSerializer
    job_otp_serializer_class=JobOtpSerializer
    employee_serializer_class=EmployeeSerializer
    employer_serializer_class=EmployerSerializer

    def get_object(self, employer_id):
        try:
            return HiringTable.objects.filter(Employer_ID=employer_id)
        except HiringTable.DoesNotExist:
            raise Http404
        
    def get_job_otp_by_id(self, employee_id,job_id):
        try:
            return JobOtp.objects.get(Employee_ID=employee_id,Job_ID=job_id)
        except JobOtp.DoesNotExist:
            raise Http404
        
    def get_employee_by_id(self, employee_id):
        try:
            return Employee.objects.get(EmployeeID=employee_id)
        except Employee.DoesNotExist:
            raise Http404
        
    def get_employer_by_id(self, employer_id):
        try:
            return Employer.objects.get(EmployerID=employer_id)
        except Employer.DoesNotExist:
            raise Http404
        
    def get_job_by_id(self, job_id):
        try:
            return Job.objects.get(Job_ID=job_id)
        except Job.DoesNotExist:
            raise Http404

    def get(self, request, employer_id, format=None):
        hiring_entries = self.get_object(employer_id)
        serializer = self.serializer_class(hiring_entries, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


    def post(self, request, format=None):
        if 'Employee_ID' in request.data and 'Job_ID' in request.data and 'Employer_ID' in request.data and 'Otp' in request.data:
            employerId=request.data['Employer_ID']
            employeeId=request.data['Employee_ID']
            jobId=request.data['Job_ID']
            otp=request.data['Otp']

            job_otp=self.get_job_otp_by_id(employeeId,jobId)

            job_otp_serialzer=self.job_otp_serializer_class(job_otp,many=False)
            job_otp_serialized_data=job_otp_serialzer.data

            if job_otp_serialized_data['Otp']==otp:

                employee=self.get_employee_by_id(employeeId)

                employee_serializer = self.employee_serializer_class(employee, many=False)
                employee_serialized_data = employee_serializer.data

                employer=self.get_employer_by_id(employerId)
                employer_serializer=self.employer_serializer_class(employer,many=False)
                employer_serialized_data=employer_serializer.data

                request.data['Candidate_Name']=employee_serialized_data['Name']
                request.data['Aadhar_No']=employee_serialized_data['Aadhar_Number']
                request.data['Contact_No']=employee_serialized_data['Contact_No']

                job=self.get_job_by_id(jobId)

                job_serializer = self.job_serializer_class(job, many=False)
                job_serialized_data = job_serializer.data
                jobVacancy=job_serialized_data['Vacancy']

                request.data['Job_Profile']=job_serialized_data['Job_Profile']
                request.data['Salary']=job_serialized_data['Salary_Offered']
                request.data['Salary_Frequency']=job_serialized_data['Frequency']

                serializer = self.serializer_class(data=request.data)
                job_serializer = self.job_serializer_class(job, data={"Vacancy":jobVacancy-1}, partial=True)
                employee_serializer=self.employee_serializer_class(employee,{"Active":False,"Contact_Credits":0,"Interest_Credits":0,"Total_Contact_Credits":0,"Total_Interest_Credits":0,"Active_Pack":None},partial=True)
                if serializer.is_valid():
                    serializer.save()
                    if job_serializer.is_valid():
                        job_serializer.save()
                    if employee_serializer.is_valid():
                        employee_serializer.save()
                    serialized_data = serializer.data
                    send_notification(employee_serialized_data['User_ID'],"Congratulations, You are hired by "+employer_serialized_data['Name'])
                    return Response(serialized_data, status=status.HTTP_201_CREATED)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(status=status.HTTP_304_NOT_MODIFIED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ContactPhoneList(APIView):
    serializer_class = ContactPhoneSerializer

    def get(self, request, format=None):
        contact_phones = Contact_phone.objects.all()
        serializer = self.serializer_class(contact_phones, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class NotificationAPIView(APIView):
    serializer_class = NotificationSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            serialized_data = serializer.data
            return Response(serialized_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_by_user_id(self, user_id):
        # Retrieve notifications for a specific user by User_ID
        notifications = Notification.objects.filter(User_ID=user_id).order_by('-Notification_Date')
        serializer = self.serializer_class(notifications, many=True)
        return Response(serializer.data)

    def get(self, request, user_id, format=None):
        return self.get_by_user_id(user_id)
    

class JobOtpAPIView(APIView):
    serializer_class = JobOtpSerializer

    def post(self, request, format=None):
        if 'Employee_ID' in request.data and 'Job_ID' in request.data:
            employeeId=request.data['Employee_ID']
            jobId=request.data['Job_ID']
            try:
                JobOtp.objects.get(Employee_ID=employeeId,Job_ID=jobId)
                return Response(status=status.HTTP_208_ALREADY_REPORTED)
            except JobOtp.DoesNotExist:
                otp = random.randint(1000,9999)
                request.data['Otp']=otp
                serializer = self.serializer_class(data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    serialized_data = serializer.data
                    return Response(serialized_data, status=status.HTTP_201_CREATED)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def get_by_employee_job_id(self, employee_id,job_id):
        try:
            jobOtp = JobOtp.objects.get(Employee_ID=employee_id,Job_ID=job_id)
            serializer = self.serializer_class(jobOtp, many=False)
            return Response(serializer.data)
        except:
            raise Http404

    def get(self, request, employee_id,job_id, format=None):
        return self.get_by_employee_job_id(employee_id,job_id)



class CashFreeAPIView(APIView):
    # Cashfree.XClientId = "204074922efba9680cf55759fd470402"
    # Cashfree.XClientSecret = "cfsk_ma_prod_1d6417d85d089115bdb49bdf494789d0_7ec0c7d1"
    # Cashfree.XEnvironment = Cashfree.XSandbox
    # x_api_version = "2023-08-01"

    serializer_class=TransactionSerializer
    employee_serializer_class=EmployeeSerializer
    employer_serializer_class=EmployerSerializer
    employee_subscription_serializer_class=EmployeeSubscriptionSerializer
    employer_subscription_serializer_class=EmployerSubscriptionSerializer


    def get_employee_subscription_by_id(self, plan_id):
        try:
            return EmployeeSubscription.objects.get(Plan_ID=plan_id)
        except EmployeeSubscription.DoesNotExist:
            raise Http404
        
    def get_employer_subscription_by_id(self, plan_id):
        try:
            return EmployerSubscription.objects.get(Plan_ID=plan_id)
        except EmployerSubscription.DoesNotExist:
            raise Http404

    def get_employee_by_id(self, employee_id):
        try:
            return Employee.objects.get(EmployeeID=employee_id)
        except Employee.DoesNotExist:
            raise Http404
        
    def get_transaction_by_id(self, oid):
        try:
            return Transaction.objects.get(OID=oid)
        except Transaction.DoesNotExist:
            raise Http404
        
    def get_employer_by_id(self, employer_id):
        try:
            return Employer.objects.get(EmployerID=employer_id)
        except Employer.DoesNotExist:
            raise Http404

    def create_order(self,obj):
            url = 'https://sandbox.cashfree.com/pg/orders'
            data = {
                    "order_amount": obj['Amount'],
                    "order_currency": "INR",
                    "customer_details": {
                        "customer_id": obj['User_ID'],
                        "customer_phone": obj['User_ID']
                    },
                    "order_meta": { 
                        "return_url": "https://b8af79f41056.eu.ngrok.io?order_id=order_123"
                    }
                }
            headers = {'Content-Type': 'application/json',
                       'Accept':'application/json',
                       'X-Client-Secret':'fece89c0a54020a331ab9f651677f7b201e6ada3',
                       'X-Client-Id':'155361abf2179feae793b46601163551',
                       'x-api-version':'2023-08-01'}
            
            try:
                r = requests.post(url, data=json.dumps(data), headers=headers)

                api_response = r.json()     

                if 'order_status' in api_response and api_response['order_status']=='ACTIVE':
                    cfOrderId=api_response['cf_order_id']
                    orderId=api_response['order_id']
                    sessionId = api_response['payment_session_id']

                    obj['CfOrderId']=cfOrderId
                    obj['Order_ID']=orderId
                    obj['Session_ID']=sessionId

                    serializer = self.serializer_class(data=obj)
                    if serializer.is_valid():
                        serializer.save()
                        serialized_data = serializer.data
                        return Response(serialized_data, status=status.HTTP_201_CREATED)
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                return Response(status=status.HTTP_403_FORBIDDEN)
            except Exception as e:
                raise Response(e,status=status.HTTP_400_BAD_REQUEST)

    def post(self,request,format=None):
        if ('Employer_ID' in request.data or 'Employee_ID' in request.data) and 'Plan_ID' in request.data:
            type='Employer'
            userId=''
            EmployeeId=''
            EmployerId=''
            
            if 'Employee_ID' in request.data :
                EmployeeId=request.data['Employee_ID']
                print(EmployeeId)
                employee=self.get_employee_by_id(request.data['Employee_ID'])
                employeeSubscription=self.get_employee_subscription_by_id(request.data['Plan_ID'])

                employee_serializer=self.employee_serializer_class(employee,many=False)
                employee_serialized_data=employee_serializer.data

                employee_subscription_serializer=self.employee_subscription_serializer_class(employeeSubscription,many=False)
                employee_subscription_serialized_data=employee_subscription_serializer.data

                type='Employee'
                amount=employee_subscription_serialized_data['Discounted_Price']
                userId=employee_serialized_data['User_ID']
            else:
                EmployerId=request.data['Employer_ID']
                employer=self.get_employer_by_id(request.data['Employer_ID'])
                employerSubscription=self.get_employer_subscription_by_id(request.data['Plan_ID'])

                employer_serializer=self.employer_serializer_class(employer,many=False)
                employer_serialized_data=employer_serializer.data

                employer_subscription_serializer=self.employer_subscription_serializer_class(employerSubscription,many=False)
                employer_subscription_serialized_data=employer_subscription_serializer.data

                amount=employer_subscription_serialized_data['Discounted_Price']
                userId=employer_serialized_data['User_ID']

            amount = str(round(amount, 2))
            obj={
                'Amount':amount,
                'User_ID':userId,
                'Employee_ID':EmployeeId,
                'Employer_ID':EmployerId,
                'Type':type,
                'Plan_ID':request.data['Plan_ID'],
                'Status':'Pending'
            }

            return self.create_order(obj)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    

    def get(self,request,oid,format=None):
        transaction=self.get_transaction_by_id(oid)

        transaction_serializer=self.serializer_class(transaction,many=False)
        transaction_serialized_data=transaction_serializer.data

        if transaction_serialized_data['Status']=='Pending':
            orderId=transaction_serialized_data['Order_ID']

            url = 'https://sandbox.cashfree.com/pg/orders/'+orderId
            headers = {'Content-Type': 'application/json',
                       'Accept':'application/json',
                       'X-Client-Secret':'fece89c0a54020a331ab9f651677f7b201e6ada3',
                       'X-Client-Id':'155361abf2179feae793b46601163551',
                       'x-api-version':'2023-08-01'}
            
            try:
                r = requests.get(url, headers=headers)

                api_response = r.json()

                if 'order_status' in api_response and api_response['order_status']=='ACTIVE':
                    return Response(status=status.HTTP_304_NOT_MODIFIED)
                elif api_response['order_status']=='PAID':

                    current_dateTime = datetime.now()

                    if transaction_serialized_data['Type']=='Employee':

                        employeeId=transaction_serialized_data['Employee_ID']
                        planId=transaction_serialized_data['Plan_ID']

                        employee=self.get_employee_by_id(employeeId)
                        employee_serializer = self.employee_serializer_class(employee, many=False)
                        serialized_data = employee_serializer.data

                        employeeName=serialized_data['Name']
                        employeeAddress=serialized_data['City']+', '+serialized_data['State_Ut']

                        plan=self.get_employee_subscription_by_id(planId)
                        plan_serializer=self.employee_subscription_serializer_class(plan,many=False)
                        plan_serialized_data=plan_serializer.data

                        end_dateTime=current_dateTime + timedelta(days=plan_serialized_data['Validity_In_Days'])

                        requestData={
                            'inv_number':transaction_serialized_data['OID'],
                            'user_name':employeeName,
                            'name':employeeName,
                            'address':employeeAddress,
                            'subscription_name':plan_serialized_data['Plan_Name'],
                            'subscription_start':current_dateTime,
                            'subscription_end':end_dateTime,
                            'list_price':plan_serialized_data['Price'],
                            'discount':plan_serialized_data['Price']-plan_serialized_data['Discounted_Price'],
                            'amount':plan_serialized_data['Discounted_Price'],
                            'invoice_total':plan_serialized_data['Discounted_Price'],
                            'Employee_ID':employeeId,
                            'Contact_Credit':plan_serialized_data['Contact_Credit'],
                            'Interest_Credit':plan_serialized_data['Interest_Credit']
                        }


                        serializer = PaymentEmployeeSerializer(data=requestData)
                        if serializer.is_valid():
                            contactCredits=serializer.validated_data['Contact_Credit']
                            interestCredits=serializer.validated_data['Interest_Credit']

                            employeeContactCredits=serialized_data['Contact_Credits']
                            employeeInterestCredits=serialized_data['Interest_Credits']
                            employeeStatus=serialized_data['Approved']
                   
                            employee_serializer = self.employee_serializer_class(employee, data={"Active":employeeStatus,"Contact_Credits":employeeContactCredits+contactCredits,"Interest_Credits":employeeInterestCredits+interestCredits,"Total_Contact_Credits":employeeContactCredits+contactCredits,"Total_Interest_Credits":employeeInterestCredits+interestCredits,'Active_Pack':planId,'Validity':end_dateTime}, partial=True)
                            if employee_serializer.is_valid():
                                employee_serializer.save()
                                serializer.save()
                                payment_serialized_data=serializer.data
                                transaction_serializer = self.serializer_class(transaction, data={"Status":"Success"}, partial=True)
                                if transaction_serializer.is_valid():
                                    transaction_serializer.save()
                                
                                transaction=self.get_transaction_by_id(oid)

                                transaction_serializer=self.serializer_class(transaction,many=False)
                                transaction_serialized_data=transaction_serializer.data
                                transaction_serialized_data['payment_id']=payment_serialized_data['Order_ID']

                                # send_notification(serialized_data['User_ID'],"Your subscription payment for "+plan_serialized_data['Plan_Name']+" is successful")

                                return Response(transaction_serialized_data, status=status.HTTP_200_OK)
                            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
                    else:

                        employerId=transaction_serialized_data['Employer_ID']
                        planId=transaction_serialized_data['Plan_ID']

                        employer=self.get_employer_by_id(employerId)
                        employer_serializer = self.employer_serializer_class(employer, many=False)
                        serialized_data = employer_serializer.data

                        employerName=serialized_data['Name']
                        employerAddress=serialized_data['City']+', '+serialized_data['State_Ut']

                        plan=self.get_employer_subscription_by_id(planId)
                        plan_serializer=self.employer_subscription_serializer_class(plan,many=False)
                        plan_serialized_data=plan_serializer.data

                        end_dateTime=current_dateTime + timedelta(days=plan_serialized_data['Validity_in_days'])

                        requestData={
                            'inv_number':transaction_serialized_data['OID'],
                            'user_name':employerName,
                            'name':employerName,
                            'address':employerAddress,
                            'subscription_name':plan_serialized_data['Plan_Name'],
                            'subscription_start':current_dateTime,
                            'subscription_end':end_dateTime,
                            'list_price':plan_serialized_data['Price'],
                            'discount':plan_serialized_data['Price']-plan_serialized_data['Discounted_Price'],
                            'amount':plan_serialized_data['Discounted_Price'],
                            'invoice_total':plan_serialized_data['Discounted_Price'],
                            'Employer_ID':employerId,
                            'Contact_Credit':plan_serialized_data['Contact_Credit'],
                            'Interest_Credit':plan_serialized_data['Interest_Credit'],
                            'Job_Post_Credit':plan_serialized_data['Job_Post_Credit']
                        }

                        serializer = PaymentEmployerSerializer(data=requestData)
                        if serializer.is_valid():
                            contactCredits=serializer.validated_data['Contact_Credit']
                            interestCredits=serializer.validated_data['Interest_Credit']
                            jobPostCredits=serializer.validated_data['Job_Post_Credit']

                            employerContactCredits=serialized_data['Contact_Credits']
                            employerInterestCredits=serialized_data['Interest_Credits']
                            employerJobPostCredits=serialized_data['Job_Post_Credits']

                            employer_serializer = self.employer_serializer_class(employer, data={"Contact_Credits":employerContactCredits+contactCredits,"Interest_Credits":employerInterestCredits+interestCredits,"Job_Post_Credits":employerJobPostCredits+jobPostCredits,"Total_Contact_Credits":employerContactCredits+contactCredits,"Total_Interest_Credits":employerInterestCredits+interestCredits,"Total_Job_Post_Credits":employerJobPostCredits+jobPostCredits,'Active_Pack':planId,'Validity':end_dateTime}, partial=True)
                            if employer_serializer.is_valid():
                                employer_serializer.save()
                                serializer.save()
                                payment_serialized_data=serializer.data

                                transaction_serializer = self.serializer_class(transaction, data={"Status":"Success"}, partial=True)
                                if transaction_serializer.is_valid():
                                    transaction_serializer.save()
                                
                                transaction=self.get_transaction_by_id(oid)

                                transaction_serializer=self.serializer_class(transaction,many=False)
                                transaction_serialized_data=transaction_serializer.data
                                transaction_serialized_data['payment_id']=payment_serialized_data['Order_ID']
                                                                
                                # send_notification(serialized_data['User_ID'],"Your subscription payment for "+plan_serialized_data['Plan_Name']+" is successful")
                                
                                return Response(transaction_serialized_data, status=status.HTTP_200_OK)
                            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                raise e
                    
            else:
                transaction_serializer = self.serializer_class(transaction, data={"Status":"Failed"}, partial=True)
                if transaction_serializer.is_valid():
                    transaction_serializer.save()
                
                transaction=self.get_transaction_by_id(oid)

                transaction_serializer=self.serializer_class(transaction,many=False)
                transaction_serialized_data=transaction_serializer.data
                return Response(transaction_serialized_data, status=status.HTTP_200_OK)
        else:
            transaction_serializer=self.serializer_class(transaction,many=False)
            transaction_serialized_data=transaction_serializer.data
            return Response(transaction_serialized_data, status=status.HTTP_200_OK)
