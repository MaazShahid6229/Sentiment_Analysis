import gzip
import glob
import requests
import json
import stanza
import csv

from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from . models import ReviewData, Category, Reviewer, Images, ProductModel

# stanza.download()
nlp = stanza.Pipeline(lang='en', processors='tokenize,sentiment')


def index(request):
    return render(request, "API.html")


def meta(request):

    for file in glob.glob('meta_data/*'):
        print(file)
        data1 = []
        with gzip.open(file) as f:
            for y in f:
                data1.append(json.loads(y.strip()))
        i = 1

        for d in data1:
            try:
                cat,_ = Category.objects.get_or_create(cat_name=d['main_cat'])
                ProductModel.objects.get_or_create(cats=cat, title=d['title'], description=d['description'],
                                                   asin=d['asin'])
                prod = ProductModel.objects.get(asin=d['asin'])
                Images.objects.get_or_create(prods=prod, image_high=d['imageURLHighRes'],
                                             image_low=d['imageURL'])
                print(i)
                i = i+1
            except Exception as e:
                print(e)
        print(len(data1))
    return HttpResponse("This is getting data from dataset meta data and store it into the DataBase")


def reviews(request):

    for file in glob.glob('json_files/*'):
        data2 = []
        with gzip.open(file) as f2:
            for y in f2:
                data2.append(json.loads(y.strip()))
        i = 1

        for d in data2:
            try:
                prod = ProductModel.objects.get(asin=d['asin'])
                status = analysis(d['reviewText'])
                print(status)
                rev,_ = ReviewData.objects.get_or_create(prods=prod, asin=d['asin'], reviewText=d['reviewText'],
                                                         summary=d['summary'], rating=d['overall'],
                                                         reviewTime=d['reviewTime'], status=status)
                Reviewer.objects.get_or_create(reviewdata=rev, reviewerName=d['reviewerName'],
                                               reviewerID=d['reviewerID'])
                print(i)
                i = i+1
            except Exception as e:
                print(e)
    return HttpResponse("This is getting data from dataset meta data and store it into the DataBase")


@csrf_exempt
def get(request):

    get_json = []
    search = request.POST["search"]

    x = ProductModel.objects.filter(title__contains=search)
    z = 0
    for i in x:
        if i:
            z = z + 1
            get_high_image = []
            get_low_image = []

            all_reviews = ReviewData.objects.filter(prods=i)
            all_images = Images.objects.filter(prods=i)

            for image in all_images:
                get_high_image.append(image.image_high)
                get_low_image.append(image.image_low)
            get_data = []
            for review in all_reviews:
                get_data.append({'Rating': review.rating, 'Review': review.reviewText, 'status': review.status})
            get_json.append({
                'Id': z,
                'asin': i.asin,
                'title': i.title,
                'review_data': get_data,
            })
        else:
            break
    # return render(request, 'response.html', {'get_json': get_json, 'search': search})
    return JsonResponse({'get_json': get_json})


def analysis(review_text):
    sent_res=[]
    x = (nlp(review_text))

    for j, sentence in enumerate(x.sentences):
        sent_res.append(sentence.sentiment)

    z = round(sum(sent_res)/len(sent_res))

    if z == 0:
        return "Negative"
    elif z == 1:
        return "Neutral"
    elif z == 2:
        return "Positive"
    else:
        return "Not Found"
