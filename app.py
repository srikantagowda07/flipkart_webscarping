import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS, cross_origin
import requests
from bs4 import BeautifulSoup
from urllib.request import urlopen as uReq
import logging
import pymongo
import csv

logging.basicConfig(filename="scrapper.log", level=logging.INFO)
app = Flask(__name__)


def createCsv(data_list):
    csv_file = 'output.csv'
    with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
      fieldnames = ['Review', 'Rating', 'Person Name', 'Title']
      writer = csv.DictWriter(file, fieldnames=fieldnames)
      if file.tell() == 0:
        writer.writeheader()
      writer.writerows(data_list)
    print(f'Data has been written to {csv_file}.')
    
def createList(soup, tag, className):
        element = soup.find_all(tag, class_=className)
        List = []
        for index,div in enumerate(element):
          text = div.get_text(strip=True)
          List.append(text)
          if len(List) >= 10:
                break;    
        return List   


@app.route("/", methods=['GET'])
def homepage():
    return render_template("index.html")


@app.route("/flipkart", methods=['GET'])
def FlipKart():
    return render_template("flipkart.html")

 # flip-kart
@app.route("/flipkart", methods=['POST', 'GET'])
def flipkartApi():
     if request.method == 'POST':
        try:
                link = request.form['content'].replace(" ", "")
                save_directory = "data/"
                if not os.path.exists(save_directory):
                        os.makedirs(save_directory)
                  # fake user agent to avoid getting blocked by Google
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}
                response = requests.get(f"{link}")
                soup=BeautifulSoup(response.content, "html.parser")
                personNameList=createList(soup, "p", "_2sc7ZR _2V5EHH");
                titleList=createList(soup, "p", "_2-N8zT");
                ratingList=createList(soup, "div", "_3LWZlK _1BLPMq");
                reviewList=createList(soup, "div", "t-ZTKy");
                payload = []
                smallest = min([len(personNameList), len(titleList), len(ratingList) , len(reviewList)])
                for x in range(smallest):
                        data = {
                                "Review":  reviewList[x] ,
                                "Rating": ratingList[x],
                                "Person Name":  personNameList[x],
                                "Title": titleList[x],
                        }
                        payload.append(data)
                else:
                        for data in payload:
                                createCsv([data])
                return render_template('flipkart.html')
        except Exception as e:
                    logging.info(e)
                    return 'something is wrong'
     else:
             return render_template('flipkart.html')
     

@app.route("/review" , methods = ['POST' , 'GET'])
def index():
    if request.method == 'POST':
                try:
                    # query to search for images
                    query = request.form['content'].replace(" ","")

                            # directory to store downloaded images
                    save_directory = "images/"

                            # create the directory if it doesn't exist
                    if not os.path.exists(save_directory):
                        os.makedirs(save_directory)



                            # fake user agent to avoid getting blocked by Google
                    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}

                            # fetch the search results page
                    # response = requests.get(f"https://www.google.com/search?q={query}&sxsrf=AJOqlzUuff1RXi2mm8I_OqOwT9VjfIDL7w:1676996143273&source=lnms&tbm=isch&sa=X&ved=2ahUKEwiq-qK7gaf9AhXUgVYBHYReAfYQ_AUoA3oECAEQBQ&biw=1920&bih=937&dpr=1#imgrc=1th7VhSesfMJ4M")
                    response = requests.get(f"https://www.google.com/search?q={query}&sxsrf=AJOqlzUuff1RXi2mm8I_OqOwT9VjfIDL7w:1676996143273&source=lnms&tbm=isch&sa=X&ved=2ahUKEwiq-qK7gaf9AhXUgVYBHYReAfYQ_AUoA3oECAEQBQ&biw=1920&bih=937&dpr=1#imgrc=1th7VhSesfMJ4M")

                            # parse the HTML using BeautifulSoup
                    soup = BeautifulSoup(response.content, "html.parser")

                            # find all img tags
                    image_tags = soup.find_all("img")

                            # download each image and save it to the specified directory
                    del image_tags[0]
                    img_data=[]
                    for index,image_tag in enumerate(image_tags):
                                # get the image source URL
                                image_url = image_tag['src']
                                #print(image_url)
                                
                                # send a request to the image URL and save the image
                                image_data = requests.get(image_url).content
                                mydict={"Index":index,"Image":image_data}
                                img_data.append(mydict)
                                with open(os.path.join(save_directory, f"{query}_{image_tags.index(image_tag)}.jpg"), "wb") as f:
                                    f.write(image_data)
                #     client = pymongo.MongoClient("mongodb+srv://snshrivas:Snshrivas@cluster0.ln0bt5m.mongodb.net/?retryWrites=true&w=majority")
                #     db = client['image_scrap']
                #     review_col = db['image_scrap_data']
                #     review_col.insert_many(img_data)          

                    return "image loaded"
                except Exception as e:
                    logging.info(e)
                    return 'something is wrong'
            # return render_template('results.html')

    else:
        return render_template('index.html')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)
