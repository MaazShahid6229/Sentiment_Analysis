from django.db import models


class Category(models.Model):
    cat_name = models.CharField(max_length=50, default="", null=True)

    def __str__(self):
        return self.cat_name


class ProductModel(models.Model):
    title = models.CharField(max_length=1000, default="", null=True)
    description = models.TextField(default="", null=True)
    asin = models.CharField(max_length=15, default="", null=True)
    cats = models.ForeignKey(Category, on_delete=models.CASCADE, default="", null=True)

    def __str__(self):
        return self.asin


class Images(models.Model):
    image_high = models.CharField(max_length=1000, default="", null=True)
    image_low = models.CharField(max_length=1000, default="", null=True)
    prods = models.ForeignKey(ProductModel, on_delete=models.CASCADE, default="", null=True)


class ReviewData(models.Model):

    asin = models.CharField(max_length=10, default="", null=True)
    reviewText = models.TextField(default="", null=True)
    status = models.CharField(max_length=100, default="", null=True)
    summary = models.CharField(max_length=1000, default="", null=True)
    reviewTime = models.CharField(max_length=50, default="", null=True)
    rating = models.DecimalField(max_digits=

                                 3, decimal_places=2, default=0.0)
    prods = models.ForeignKey(ProductModel, on_delete=models.CASCADE, default="", null=True)

    def __str__(self):
        return self.summary


class Reviewer(models.Model):
    reviewerName = models.CharField(max_length=1000, default="", null=True)
    reviewerID = models.CharField(max_length=15, default="", null=True)
    reviewdata = models.ForeignKey(ReviewData, on_delete=models.CASCADE, default="", null=True)

    def __str__(self):
        return self.reviewerName
