import gzip
import glob
import requests
import json
import stanza
import csv
from bs4 import BeautifulSoup
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from . models import ReviewData, Category, Reviewer, Images, ProductModel

# stanza.download()
nlp = stanza.Pipeline(lang='en', processors='tokenize,sentiment')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0',
    'Accept-Language': 'en-US, en;q=0.5'
}



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
            print("==>",d)
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
        if i and z < 50:
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
                get_data.append({'Rating': review.rating, 'Review': review.reviewText, 'status': review.status, "reviewTime": review.reviewTime})
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



@csrf_exempt
def get_reviews(request):
    search = request.POST["search"]
    search_query = search.replace(' ', '+')
    base_url = 'https://www.amazon.ae/s?k={0}'.format(search_query)

    items = []
    for i in range(1, 2):
        print('Processing {0}...'.format(base_url + '&page={0}'.format(i)))
        response = requests.get(base_url + '&page={0}'.format(i), headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')

        results = soup.find_all('div', {'class': 's-result-item', 'data-component-type': 's-search-result'})

        for result in results[:10]:
            product_name = result.h2.text

            try:
                rating = result.find('i', {'class': 'a-icon'}).text
                rating_count = result.find_all('span', {'aria-label': True})[1].text
            except AttributeError:
                continue

            try:
                price1 = result.find('span', {'class': 'a-price-whole'}).text
                price2 = result.find('span', {'class': 'a-price-fraction'}).text
                price = price1 + price2
                product_url = 'https://amazon.ae' + result.h2.a['href']
                response1 = requests.get(product_url, headers=headers)
                soup1 = BeautifulSoup(response1.content, 'html.parser')
                image = soup1.select("#landingImage")
                image_url =""
                if image:
                    image_url = image[0]["src"]
                results1 = soup1.find_all("div", attrs={"class": "a-row a-spacing-none"})
                review_data = []
                for result1 in results1:
                    name = result1.select(".a-profile-name")
                    time1 = result1.find_all("span", attrs={"class": "a-size-base a-color-secondary review-date"})
                    review_d = result1.find_all("div", attrs={"class": "a-expander-content reviewText review-text-content a-expander-partial-collapse-content"})
                    if name and time1 and review_d:
                        status = analysis(review_d[0].text)
                        review_data.append({"reviwer": name[0].text, "Time": time1[0].text, "review": review_d[0].text, "status": status})
                items.append({"product_url": product_url, "product_name": product_name, "image_url": image_url, "rating": rating, "rating_count": rating_count, "price": price, "review_data": review_data})
            except AttributeError:
                continue
    return JsonResponse({'get_json': items})