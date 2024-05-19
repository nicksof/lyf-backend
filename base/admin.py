from django.contrib import admin
from .models import UserProfile
from .models import Mood
from .models import UserDetail, UserActivity, Habit, HabitRecord
from .models import Medication

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(Mood)
admin.site.register(UserDetail)
admin.site.register(Habit)
admin.site.register(UserActivity)
admin.site.register(Medication)
admin.site.register(HabitRecord)
