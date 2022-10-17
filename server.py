import string
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
import requests

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
BASE_URL = "https://api.github.com"
origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class repo_star_data(BaseModel):
    org: str

def sort_by_stars(list):
    return list['stars']

@app.post("/repos")
def main(data: repo_star_data ):
    page_number = 1
    resp = []
    while True:
        url = BASE_URL + "/orgs/" + data.org + "/repos" + "?page=" + str(page_number)
        org_repos = requests.get(url).json()
        if len(org_repos) == 0:
            break
        for repo in org_repos:
            resp.append({"name":repo['name'],"stars":repo['stargazers_count']}.copy())
        page_number += 1
    resp.sort(key=sort_by_stars, reverse=True)
    json_compatible_item_data = jsonable_encoder({"results":resp[:min(10,len(resp))]})
    return JSONResponse(content=json_compatible_item_data)



class repo_commit_data(BaseModel):
    org: str
    repo : str
    start_date : str
    end_date : str

@app.post("/commit-history")
def main(data: repo_commit_data ):
    page_number = 1
    resp = []
    while True:
        url = BASE_URL + "/repos/" + data.org + "/" + data.repo + "/commits?since=" + data.start_date + "&until=" + data.end_date + "&page=" + str(page_number) + "&per_page=100"
        commits = requests.get(url).json()
        if len(commits) == 0:
            break
        for commit in commits:
            date = commit['commit']['author']['date'][:10]
            commit_message = commit['commit']['message']
            author = commit['commit']['author']['name']
            url = commit['html_url']
            resp.append({"date":date,"commit_message":commit_message,"commit_author":author,"commit_url":url}.copy())
        page_number += 1
    
    json_compatible_item_data = jsonable_encoder({"results":resp})
    return JSONResponse(content=json_compatible_item_data)
