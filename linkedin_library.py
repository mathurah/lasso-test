import html
import json
import math
import time
import datetime

import requests

LINK_PREFIX = 'https://www.linkedin.com/sales/people/'
SLEEP = 10

BLANK_PROFILEf_PIC = 'https://writedirection.com/website/wp-content/uploads/2016/09/blank-profile-picture-973460_960_720.png'
NON_TARGET = ['clerk', 'accounting', 'writer', 'assistant', 'operations', 'picker', 'sourcer', 'vendor', 'ambassador', 'associate', 'representative', 'coordinator', 'community', 'administrator', 'quality',
              'contract', 'driver', 'account executive', 'deliverer', 'account manager', 'advisor', 'analyst', 'intern',
              'consultant', 'contract', 'adviser']
NEW_TITLE = ['founder', 'executive', 'technology']
target_companies = ['Lyft',
                    'Looker',
                    'GitHub',
                    'Plaid',
                    'DataDog',
                    'Uber',
                    'Glossier',
                    'Chime',
                    'Stripe',
                    'Airbnb',
                    'Notion',
                    'Figma',
                    'AirTable',
                    'Slack',
                    'Snowflake',
                    'Affirm',
                    'Flexport',
                    'Hashicorp',
                    'Atlassian',
                    'Segment',
                    'Faire',
                    'Netflix',
                    'Google',
                    'UiPath',
                    'Roblox',
                    'Databricks',
                    'Robinhood',
                    'Instacart',
                    'Postmates',
                    'Doordash',
                    'Epic Games',
                    'Twitch',
                    'Checkout.com',
                    'Grab',
                    'Coinbase',
                    'Discord',
                    'Automation Anywhere',
                    'Zoom',
                    'Amazon',
                    'Tesla',
                    'Microsoft',
                    'Snap',
                    'Canva',
                    'GitLab',
                    'Splunk',
                    'Sumo Logic',
                    'Kong',
                    'Harness',
                    'LaunchDarkly',
                    'TripActions',
                    'Gusto',
                    'AppZen',
                    'Procore',
                    'Zapier',
                    'Calendly',
                    'GoPuff',
                    'Niantic',
                    'Toast',
                    'Brex',
                    'SoFi',
                    'FreshWorks',
                    'Rubrik',
                    'Blend',
                    'Reddit',
                    'Confluent',
                    'Houzz',
                    'Convoy',
                    'Quora',
                    'Snyk',
                    'Cohesity',
                    'Coursera',
                    'Duolingo',
                    'Crowdstrike',
                    'Gong',
                    'Hopin',
                    'Webflow',
                    'Braze',
                    'Calm',
                    'Monday.com',
                    'Grammarly',
                    'Checkr',
                    'ZocDoc',
                    'Buzzfeed',
                    'SquareSpace',
                    'Opendoor',
                    'Opentable',
                    'Yelp',
                    'Workato',
                    'ServiceTitan',
                    'Verkada',
                    'DarkTrace',
                    'Auth0',
                    'Okta',
                    'Postman',
                    'Away',
                    'Grove Collaborative',
                    'Thumbtack',
                    'Sonder',
                    'Lookout',
                    'Superhuman',
                    'Quizlet',
                    'Docker',
                    'Sisense',
                    'Sysdig',
                    'Intercom',
                    'Course Hero',
                    'SalesLoft',
                    'KeepTruckin',
                    'BigID',
                    'Classpass',
                    'Amplitude',
                    'Facebook',
                    'Cisco',
                    'Dropbox',
                    'Box',
                    'Evernote',
                    'Eventbrite',
                    'LinkedIn',
                    'Medium',
                    'MongoDB',
                    'Retool',
                    'SecurityScorecard',
                    'Unity',
                    'VMWare',
                    'Twilio',
                    'Pillpack',
                    'Adobe',
                    'Shopify',
                    'Step',
                    'Better',
                    'Lemonade',
                    'Brex',
                    'Current',
                    'Root',
                    'Cash App'
                    ]


def create_date(user, d):
    return datetime.date(d.get('year'), d.get('month', 1), d.get('day', 1)).isoformat()


class LeadData:
    def __init__(self, name, summary, current_pos, current_company, current_company_start,
                 sales_nav_url, target, target_pos, target_pos_start, target_pos_end, image_url):
        self.name = name
        self.linked_in_summary = summary
        self.current_position = current_pos
        self.current_company = current_company
        self.current_position_start = current_company_start
        self.sales_nav_url = sales_nav_url
        self.target_company_position = target_pos
        self.target_company = target
        self.target_company_position_start = target_pos_start
        self.target_company_position_end = target_pos_end
        self.image_url = image_url


class Query:
    def __init__(self, headers, cookies):
        self.headers = headers
        self.cookies = cookies
        self.dropped_count = 0

    def make_search_request(self, start):
        time.sleep(SLEEP)
        resp = requests.get('https://www.linkedin.com/sales-api/salesApiLeadSearch?q=savedSearchId&start='+str(start)+'&count=25&savedSearchId=50520885&trackingParam=(sessionId:Bwt%2B5hw%2BSZO405wH8cTVZA%3D%3D)&decorationId=com.linkedin.sales.deco.desktop.searchv2.LeadSearchResult-7',
                            headers=self.headers, cookies=self.cookies)
        return html.unescape(resp.text)

    @staticmethod
    def get_target_company_info(past_positions):
        target_company_start = None
        target_company_end = None
        target_company_pos = None
        target_company_pos = None
        for position in past_positions:
            company = position['companyName'].upper()
            is_target = [x for x in map(
                str.upper, target_companies) if x in company] != []
            if is_target:
                return (position['companyName'],
                        position['title'],
                        position['startedOn'],
                        position['endedOn'])
        return None, None, None, None

    def career_filter(self, target_comp, target_title, current_role):
        target_check = True
        current_check = False

        if not target_title or not current_role:
            return False

        for prof in NON_TARGET:
            if prof in target_title.lower():
                target_check = False

        for prof in NEW_TITLE:
            if prof in current_role.lower():
                current_check = True

        return target_comp and target_check and current_check

    def format_lead(self, user):
        name = user['fullName']
        try:
            (target_comp, target_title, target_start,
             target_end) = self.get_target_company_info(user['pastPositions'])
            print("-----" + user['currentPositions'])
            current_company = user['currentPositions'][0]['companyName'] if user['currentPositions'] else return current_role = user['currentPositions'][0]['title']

            if not self.career_filter(target_comp, target_title, current_role):
                print('Dropped ', name, ' Current Role:', current_role, " Target Comp: ",
                      target_comp, ' Target Title: ', target_title)
                self.dropped_count += 1
                print(self.dropped_count)
                return None
            current_start = user['currentPositions'][0]['startedOn']
            sales_nav = LINK_PREFIX + user['entityUrn'].split('(')[1][:-1]
            summary = user.get('summary').replace(
                "\x00", "\uFFFD") if 'summary' in user else "No summary"
            image_url = None
            if 'profilePictureDisplayImage' in user:
                image_url = user['profilePictureDisplayImage']['rootUrl'] \
                    + user['profilePictureDisplayImage']['artifacts'][1]['fileIdentifyingUrlPathSegment']
            else:
                image_url = BLANK_PROFILE_PIC
            return LeadData(name, summary, current_role, current_company, create_date(user, current_start), sales_nav,
                            target_comp, target_title, create_date(
                                user, target_start), create_date(user, target_end),
                            image_url)
        except KeyError:
            return None

    def extract_results_json(self, response):
        #ind = response.rfind("{\"metadata")
        #response = response[ind:]
        #end = response.find('</')
        try:
            results = json.loads(response)
        except:
            return [], -1

        # normalize users
        users = []
        if 'elements' in results:
            for e in results['elements']:
                try:
                    user = self.format_lead(e)
                except KeyError:
                    user = None
                if user:
                    users.append(vars(user))
        else:
            return [], 0
        # calculate pages
        paging = results['paging']
        total_elem = paging['total']
        page_count = paging['count']
        pages = math.ceil(total_elem / page_count)
        return users, pages

    def pull_results(self):
        response = self.make_search_request(0)
        users, pages = self.extract_results_json(response)
        total_users = []
        for i in range(1, pages):
            start = 25*i
            response = self.make_search_request(start)
            users, _ = self.extract_results_json(response)
            total_users += users
            print(len(total_users), self.dropped_count)
        return total_users
