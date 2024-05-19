import io
import numpy as np

from datetime import datetime

from PIL import Image

from django.http import JsonResponse
from django.contrib.auth.models import User

from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.urls import reverse

from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import UserDetailSerializer, ProfileSerializer, ProfilePicSerializer, ChangePasswordSerializer
from .serializers import MoodSerializer
from .serializers import GetHobbiesSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import SignUpSerializer
from . import serializers
from base.models import UserProfile, Mood, UserDetail, UserActivity, Habit, Medication, HabitRecord

from keras.utils import img_to_array
from keras.models import load_model

from base.recommender import get_hobbies, get_recommendations
from base.habitrecommender import get_habits

from django_rest_passwordreset.views import ResetPasswordConfirm, ResetPasswordRequestToken
from django.core.mail import send_mail, EmailMultiAlternatives
from django.shortcuts import render, redirect
from django.template.loader import render_to_string, get_template
from django.template import Context

from paddleocr import PaddleOCR


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        token['email'] = user.email
        token['firstname'] = user.first_name
        token['completedIA'] = user.userprofile.completedIA
        # ...

        return token
    
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer



class SignUpView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = SignUpSerializer

    #return Response(serializer_class.validated_data)

@permission_classes([IsAuthenticated])
@api_view(['PATCH'])
def updateProfile(request):
    
    user = request.user
    profile_instance = user.userprofile
    serializer = ProfileSerializer(profile_instance, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getRoutes(request):
    routes = [
        'GET /api',
        'GET /api/users',
        'GET /api/final',
    ]
    return Response(routes)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getProfile(request):
    user = request.user
    user_profile = UserProfile.objects.get(user=user)
    serializer = ProfileSerializer(user_profile)
    #serializer = UserDetailsSerializer({'user': user, 'profile': user_profile})
    return Response(serializer.data)

class UpdateProfilePic(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        profile_instance = request.user.userprofile
        serializer = ProfilePicSerializer(profile_instance, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def removeProfilePic(request):
    profile_instance = request.user.userprofile
    profile_instance.profilePic = None
    profile_instance.save()

    serializer = ProfileSerializer(profile_instance)

    return Response(serializer.data, status=status.HTTP_200_OK)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def changePassword(request):
    if request.method == 'POST':
        #name = 'hehec'
        user = request.user
        serializer = ChangePasswordSerializer(data=request.data, context={'user': user})
        if serializer.is_valid():
            #if user.check_password(serializer.validated_data.get('old_password')):
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({'message': "Password updated successfully."}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
class ResetPassword(generics.GenericAPIView):
    serializer_class = serializers.ResetPasswordSerializer 

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            email = serializer.data['email']
            user = User.objects.filter(email=email).first() #first

            if user:
                encoded_pk = urlsafe_base64_encode(force_bytes(user.pk))       
                token = PasswordResetTokenGenerator().make_token(user)

                reset_url = reverse(
                    'reset_password',
                    kwargs={'encoded_pk':encoded_pk, 'token':token}
                )

                reset_link = f"http://127.0.0.1:8000{reset_url}"

                message = f'Here is the link to reset your password:\n{reset_link}'
                #html_content = render_to_string('email/password_reset_email.html', {'reset_link':reset_link},)
                htmlc = render_to_string('email/password_reset_email.html', {'reset_link': reset_link, 'name': user.first_name})
                textc = render_to_string('email/password_reset_email.txt', {'reset_link': reset_link, 'name': user.first_name})
                send_mail(
                    "Password Reset",
                    message,
                    "lyfstyleapp@gmail.com",
                    [email], 
                    html_message=htmlc,
                                   
                )
                
                
                
                #msg = EmailMultiAlternatives(
                #    "Password Reset",
                #    textc,
                #    #f'Here is the link to reset your password:\n{reset_link}',
                #    "lyfstyleapp@gmail.com",
                #    [email], 
                #)
                #msg.attach_alternative(htmlc, "text/html")
                #msg.send()

                return Response({'email': "Reset password email sent."}, status=status.HTTP_200_OK)
            else:
                return Response({'email': "Email address is not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
def reset_password_page(request, token, encoded_pk):
    return render(request, 'reset_password_page.html', {'token':token, 'encoded_pk':encoded_pk})

class ResetPasswordSet(generics.GenericAPIView):
    serializer_class = serializers.ResetPasswordSetSerializer

    def patch(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'kwargs':kwargs})

        serializer.is_valid()

        return Response({'message': "All good"})

def resetPasswordPage(request, token, encoded_pk):
    pk = urlsafe_base64_decode(encoded_pk).decode()
    user = User.objects.get(pk=pk)

    if user and PasswordResetTokenGenerator().check_token(user, token):
        if request.method == 'POST':
            new_password = request.POST.get('password')
            user.set_password(new_password)
            user.save()
            return redirect('password_reset_complete')
        else:
            context = {'token': token, 'encoded_pk': encoded_pk}
            return render(request, 'reset_password_page.html', context)
    else:
        return render(request, 'link_expired.html')
        
def passwordResetComplete(request):
    return render(request, 'password_reset_complete.html')

class EvaluateMoodView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = MultiPartParser, FormParser

    def post(self, request, *args, **kwargs):
        image_file = request.FILES.get('image')
        eval_date = request.data.get('date')
        eval_time = request.data.get('time')

        if image_file:
            user = request.user
            image = Image.open(io.BytesIO(image_file.read()))
            image = image.resize((224,224))
            #image = image.convert('L')
            
            img_arr = img_to_array(image)/255
            in_arr = np.array([img_arr])

            model = load_model('best_model.h5')

            moods = {0: 'Good', 1: 'Neutral', 2: 'Poor'}

            ind = np.argmax(model.predict(in_arr))
            mood = moods[ind]

            mood_record = Mood.objects.create(
                user = request.user,
                date = eval_date,
                time = eval_time,
                result = mood
            )

            serializer = MoodSerializer(mood_record)
            
            user_activity = UserActivity.objects.filter(user=request.user, date=eval_date)

            if user_activity.exists():
                user_activity.date = eval_date
            else: 
                UserActivity.objects.create(
                    user = user,
                    date = eval_date,
                    mood = True
                )            
                user.userprofile.streak += 1
                user.userprofile.save()   

            if (mood == 'Poor'):
                hobbies = [
                    user.userdetail.hobby1,
                    user.userdetail.hobby2,
                    user.userdetail.hobby3,
                    user.userdetail.hobby4,
                ]
                recommendations = get_recommendations(hobbies)

                response = {
                    'record': serializer.data,
                    'recommendations': recommendations
                }
            
            else:
                response = {
                    'record': serializer.data
                }

            return JsonResponse(response)
        
        return Response({'error': "No image detected."})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getMoodRecords(request):
    user = request.user
    mood_records = user.mood_set.all().order_by('-id')
    serializer = MoodSerializer(mood_records, many=True)
    return Response(serializer.data)


class GetHobbies(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        #serializer = GetHobbiesSerializer(data=request.data)
        
        #if serializer.is_valid():
        type = request.data.get('type', None)
        hobbies = get_hobbies(type)

        return Response({'hobbies': hobbies}, status=status.HTTP_200_OK)

        #return Response({'message': serializer.errors})
    

class UpdateUserDetails(APIView):
    permission_classes = [IsAuthenticated]
    def patch(self, request, *args, **kwargs):
        user = request.user
        try :
            user_detail = UserDetail.objects.get(user=user)
        except UserDetail.DoesNotExist:
            user_detail = UserDetail(user=user)
            user_detail.save()

        serializer = UserDetailSerializer(user_detail, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()

            try:
                habits = Habit.objects.get(user=user)
            except Habit.DoesNotExist:
                habits = Habit(user=user)
                habits.save()


            if serializer.data['answer1'] is not None:
                habits.habit1 = get_habits(serializer.data['answer1'])
            if serializer.data['answer2'] is not None:
                habits.habit2 = get_habits(serializer.data['answer2'])
            if serializer.data['answer3'] is not None:
                habits.habit3 = get_habits(serializer.data['answer3'])
            if serializer.data['answer4'] is not None:
                habits.habit4 = get_habits(serializer.data['answer4'])
            if serializer.data['answer5'] is not None:
                habits.habit5 = get_habits(serializer.data['answer5'])

            habits.save()   
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GetHabits(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        user = request.user
        habits = Habit.objects.get(user=user)       

        serializer = serializers.HabitSerializer(habits)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
        
class UpdateUserActivity(APIView):
    permission_classes = [IsAuthenticated]
    def patch(self, request, *args, **kwargs):
        user = request.user
        date = request.data.get('date')

        try:
            record = UserActivity.objects.get(user=user, date=date)
        except UserActivity.DoesNotExist:
            record = UserActivity(user=user)
            record.save()
            user.userprofile.streak += 1
            user.userprofile.save()

        serializer = serializers.UserActivitySerializer(record, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()

            

            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class GetUserActivity(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        user = request.user
        date = request.data.get('date')
        
        try:
            record = UserActivity.objects.get(user=user, date=date)
        except UserActivity.DoesNotExist:
            record = UserActivity(user=user, date=date)

        serializer = serializers.UserActivitySerializer(record)

        return Response(serializer.data, status=status.HTTP_200_OK)
    

        

@api_view(['GET'])
def getRecommendations(request):

    user = User.objects.get(username='bingusb')
    hobbies = [
        user.userdetail.hobby1,
        user.userdetail.hobby2,
        user.userdetail.hobby3,
        user.userdetail.hobby4
    ]

    recommendations = get_recommendations(hobbies)

    return Response({'recommendations': recommendations})

class AddMedicine(APIView):
    permission_classes = [IsAuthenticated]
    def patch(self, request, *args, **kwargs):
        user = request.user
        date = request.data.get('expiry')
        date_obj = datetime.fromisoformat(date)
        medicine = Medication(user=user, expiry=date_obj)
        
        serializer = serializers.MedicationSerializer(medicine, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetMedications(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        user = request.user
        date = request.data.get('date')

        date_obj = datetime.fromisoformat(date)

        expired_medications = Medication.objects.filter(user=user, expiry__lt=date_obj)

        if expired_medications:
            expired_medications.delete()


        medications = user.medication_set.all().order_by('-id')

        serializer = serializers.MedicationSerializer(medications, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    

class AddHabitRecord(APIView):
    permission_classes = [IsAuthenticated]
    def patch(self, request, *args, **kwargs):
        user = request.user
        date = request.data.get('date')
        habit = request.data.get('habit')
        
        
        habit_record = HabitRecord.objects.filter(user=user, date=date, habit=habit).first()

        if habit_record:
            return Response({'message': "Existant"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            habit_record = HabitRecord(
                user = user               
            )
            serializer = serializers.HabitRecordSerializer(habit_record, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()

                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else: 
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        
class GetHabitRecords(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        user = request.user
        habit_records = user.habitrecord_set.all().order_by('-id')
        serializer = serializers.HabitRecordSerializer(habit_records, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
                  



# @parser_classes([MultiPartParser, FormParser, FileUploadParser])
# class OCRView(APIView):
#     parser_classes = MultiPartParser, FormParser
#     def post(self, request, format=None):
#         # Assuming the uploaded image is in a form with name 'image'
#         uploaded_image = request.FILES.get("image")

#         if uploaded_image:
#             image = Image.open(io.BytesIO(uploaded_image.read()))
#             image = image.resize((224,224))

#         # if not uploaded_image:
#         #     return Response(
#         #         {"error": "Image file not provided"}, status=status.HTTP_400_BAD_REQUEST
#         #     )

#         # # Save the image to a temporary location
#         # with open("image", "wb") as temp_image:
#         #     for chunk in uploaded_image.chunks():
#         #         temp_image.write(chunk)

#         # Perform OCR on the image
#         ocr_result = perform_ocr(image)

#         # Serialize the OCR result
#         serializer = OCRResultSerializer({"lines": ocr_result})

#         # Return the serialized result as JSON
#         return JsonResponse(serializer.data)
        
class OCRView(APIView):
    def post(self, request, *args, **kwargs):
        ocr = PaddleOCR(lang="en")
        image_files = request.FILES.get('images')

        if image_files:
            user = request.user
            image_data = image_files.read()  # Read image data as bytes
            result = ocr.ocr(image_data)

            medicine_names = ["Buspirone", "Acetaminophen", "Ibuprofen", "Aspirin", "Naproxen", "Doxycycline", "Histamine", "Piriton", "Prednisolone", "Metoprolol", "Hydrocodone", "Acetaminophone"]

            recognized_medicine_names = []

            for line in result:
                for word in line:
                    text = word[1][0]  

                    # Split the text by whitespace to extract individual words
                    words = text.split()
                    print(words)

                    for word in words:
                        for name in medicine_names:
                            if name.lower() == word.lower():
                                recognized_medicine_names.append(name)
                                break  
                    else:
                        continue 
                    break  

            return JsonResponse({'results': recognized_medicine_names}, status=200)

        return JsonResponse({'error': 'No image provided'}, status=400)


