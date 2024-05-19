from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from django.contrib.auth.models import User
from base.models import UserProfile
from base.models import Mood, UserDetail, Habit, UserActivity, Medication, HabitRecord
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password, ValidationError

from base.recommender import get_hobbies

from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator

class SignUpSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required = True,
        validators = [UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(
        write_only = True,
        required = True,
        validators = [validate_password]
    )
    password2 = serializers.CharField(
        write_only = True,
        required = True
    )

    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email', 'first_name', 'last_name')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields don't match."})
        
        return attrs
    
    def create(self, validated_data):
        user = User.objects.create(
            username = validated_data['username'],
            email = validated_data['email'],
            first_name = validated_data['first_name'],
            last_name = validated_data['last_name'],
        )

        user.set_password(validated_data['password'])
        user.save()

        return user
    
class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name']

class ProfileSerializer(ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['profilePic','phoneNum', 'streak', 'completedIA', 'lastAssessment']

class UserDetailsSerializer(serializers.Serializer):
    user = UserSerializer()
    profile = ProfileSerializer()

class ProfilePicSerializer(ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['profilePic']

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
       
    def validate_old_password(self, value):
        #user = self.context['request'].user
        user = self.context['user']
        if not user.check_password(value):
            raise serializers.ValidationError("Incorrect old password.")
        
        return value
        
    def validate_new_password(self, value):
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(e)

        return value
    
class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ResetPasswordSetSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        password = data.get('password')
        token = self.context.get('kwargs').get('token')
        encoded_pk = self.context.get('kwargs').get('encoded_pk')

        pk = urlsafe_base64_decode(encoded_pk).decode()
        
        user = User.objects.get(pk=pk)

        if not PasswordResetTokenGenerator().check_token(user, token):
            raise serializers.ValidationError("Token invalid.")
        
        user.set_password(password)
        user.save()
        return data


class MoodSerializer(ModelSerializer):
    class Meta:
        model = Mood
        fields = ['user', 'date', 'time', 'result']


class GetHobbiesSerializer(serializers.Serializer):
    type = serializers.CharField(required=True)
    

class UserDetailSerializer(ModelSerializer):
    class Meta:
        model = UserDetail
        fields = '__all__'

class HabitSerializer(ModelSerializer):
    class Meta:
        model = Habit
        fields = '__all__'



class UserActivitySerializer(ModelSerializer):
    class Meta:
        model = UserActivity  
        fields = ['date', 'habit1', 'habit2', 'habit3', 'habit4', 'habit5']


class MedicationSerializer(ModelSerializer):
    class Meta:
        model = Medication
        fields = ['medname', 'dosage', 'frequency', 'time']

class HabitRecordSerializer(ModelSerializer):
    class Meta:
        model = HabitRecord
        fields = '__all__'