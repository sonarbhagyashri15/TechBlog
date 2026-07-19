from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")

db = client["TechBlogDB"]

blogs_collection = db["blogs"]