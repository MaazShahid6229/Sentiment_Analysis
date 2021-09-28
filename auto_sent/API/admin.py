from django.contrib import admin
from . models import ReviewData, Category, ProductModel, Reviewer, Images

# Register your models here.
admin.site.register(ReviewData)
admin.site.register(Category)
admin.site.register(ProductModel)
admin.site.register(Reviewer)
admin.site.register(Images)


