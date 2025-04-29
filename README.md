# short_link
You can use this script to create your own link shortener.
## to run project 
````
docker build -t url-shortener .
````
````
docker run -d -p 8080:8080 -v ./data:/app --name shortener url-shortener
````
