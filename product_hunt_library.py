import json
from datetime import date, timedelta

import requests

import constants


class ProductLead:

    def __init__(self, name, desc, link, num_votes, num_comments, image_url):
        self.name = name
        self.description = desc
        self.product_hunt_link = link
        self.num_upvotes = num_votes
        self.num_comments = num_comments
        self.image_url = image_url


class Query:

    def __init__(self, num_days_back, topN):
        self.num_days_back = num_days_back
        self.topN = topN

    @staticmethod
    def format_lead(raw_lead):
        name = raw_lead['name']
        description = raw_lead['tagline']
        link = raw_lead['url']
        upvotes = raw_lead['votesCount']
        num_comments = raw_lead['comments']['totalCount']
        image_url = raw_lead['thumbnail']['url']
        return vars(ProductLead(name, description, link, upvotes, num_comments, image_url))

    def get_data(self):
        after = (date.today() - timedelta(days=self.num_days_back)).strftime("%Y-%m-%d")
        query = {"query": """
                     {
          posts(order: VOTES, postedAfter: \"""" + after + """\") {
            edges {
              node {
                name
                comments {
                  totalCount,
                }
                url
                topics {
                  edges {
                    node {
                      name
                    }
                  }
                }
                votesCount
                thumbnail {
          url
          type
        }
                tagline
                createdAt
              }
            }
          }
        } """}

        today_posts = requests.post(constants.API_URL,
                                    headers=constants.PH_HEADERS,
                                    data=json.dumps(query))

        today_posts = today_posts.json()
        top_n_exclusive = self.topN+1
        return today_posts['data']['posts']['edges'][:top_n_exclusive]

    def pull_leads(self):
        leads = self.get_data()
        return [Query.format_lead(x['node']) for x in leads]


