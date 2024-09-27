

import os
import sys
current = os.path.dirname(os.path.realpath(__file__))
subparent = os.path.dirname(current)
parent = os.path.dirname(subparent)
root =   os.path.dirname(parent)
sys.path.append(subparent)
sys.path.append(parent)
sys.path.append(root)
from datetime import datetime
import requests
from common.gs import write_dataframe_to_sheet
import re
import pandas as pd
from time import sleep

class SeekJobListing:
    def __init__(self, title, company_location, department, job_type, salary_range, email, phone, ads_link, ads_posted_date, raw_text):
        self.title = title
        self.company_location = company_location
        self.department = department
        self.job_type = job_type
        self.salary_range = salary_range
        self.email = email
        self.phone = phone
        self.ads_link = ads_link
        self.ads_posted_date = ads_posted_date
        self.raw_text = raw_text

    def __str__(self):
        return f"Job Listing: {self.title} at {self.company_location}"

    def display_info(self):
        print(f"Title: {self.title}")
        print(f"Company Location: {self.company_location}")
        print(f"Department: {self.department}")
        print(f"Job Type: {self.job_type}")
        print(f"Salary Range: {self.salary_range}")
        print(f"Email: {self.email}")
        print(f"Phone: {self.phone}")
        print(f"Ads Link: {self.ads_link}")
        print(f"Ads Posted Date: {self.ads_posted_date}")
        print(f"Raw Text: {self.raw_text[:100]}...") 
class Scaping:
    
    def __init__(self):
        self.listError=[]
        self.website = 'https://www.seek.com.au'
        self.s = requests.Session()
    def safeGet(self,dictionary, *keys, default=None):
        for key in keys:
            if isinstance(dictionary, dict):
                dictionary = dictionary.get(key, {})
            elif isinstance(dictionary, list) and isinstance(key, int):
                if 0 <= key < len(dictionary):
                    dictionary = dictionary[key]
                else:
                    return default
            else:
                return default
        return dictionary if dictionary != {} else default

    def get_first_classification_label(self,job_data):
        classifications = job_data.get('classifications', [])
        if classifications and isinstance(classifications, list) and len(classifications) > 0:
            return classifications[0].get('label', "Department not specified")
        return "Department not specified"
    def getPages(self,page=1):
        url = f"{self.website}/api/chalice-search/v4/search?siteKey=AU-Main&sourcesystem=houston&userqueryid=1d2b93395fa16d62e149572444733805-3816116&userid=1ad0f857-940d-4839-884e-354bd976a872&usersessionid=1ad0f857-940d-4839-884e-354bd976a872&eventCaptureSessionId=1ad0f857-940d-4839-884e-354bd976a872&where=All+Australia&page={page}&seekSelectAllPages=true&keywords=Accountant&classification=1200&pageSize=40&include=seodata&locale=en-AU&solId=720f1f0a-030e-4378-b5ea-9a51b5b620b5"
        payload = {}
        headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'priority': 'u=0, i',
        'sec-ch-ua': '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        }
        try:
            response = requests.request("GET", url, headers=headers, data=payload)
            return response.json()
        except Exception as e:
            self.listError.append(url)
            print (e)
            print ("Error" + url +"\n")
        return {}
    def getDetail(self,jobId=79053918):
        url = f"{self.website}/graphql"
        payload = "{\"query\":\"query jobDetails($jobId: ID!, $jobDetailsViewedCorrelationId: String!, $sessionId: String!, $zone: Zone!, $locale: Locale!, $languageCode: LanguageCodeIso!, $countryCode: CountryCodeIso2!, $timezone: Timezone!) {\\n  jobDetails(\\n    id: $jobId\\n    tracking: {channel: \\\"WEB\\\", jobDetailsViewedCorrelationId: $jobDetailsViewedCorrelationId, sessionId: $sessionId}\\n  ) {\\n    job {\\n      sourceZone\\n      tracking {\\n        adProductType\\n        classificationInfo {\\n          classificationId\\n          classification\\n          subClassificationId\\n          subClassification\\n          __typename\\n        }\\n        hasRoleRequirements\\n        isPrivateAdvertiser\\n        locationInfo {\\n          area\\n          location\\n          locationIds\\n          __typename\\n        }\\n        workTypeIds\\n        postedTime\\n        __typename\\n      }\\n      id\\n      title\\n      phoneNumber\\n      isExpired\\n      expiresAt {\\n        dateTimeUtc\\n        __typename\\n      }\\n      isLinkOut\\n      contactMatches {\\n        type\\n        value\\n        __typename\\n      }\\n      isVerified\\n      abstract\\n      content(platform: WEB)\\n      status\\n      listedAt {\\n        label(context: JOB_POSTED, length: SHORT, timezone: $timezone, locale: $locale)\\n        dateTimeUtc\\n        __typename\\n      }\\n      salary {\\n        currencyLabel(zone: $zone)\\n        label\\n        __typename\\n      }\\n      shareLink(platform: WEB, zone: $zone, locale: $locale)\\n      workTypes {\\n        label(locale: $locale)\\n        __typename\\n      }\\n      advertiser {\\n        id\\n        name(locale: $locale)\\n        isVerified\\n        registrationDate {\\n          dateTimeUtc\\n          __typename\\n        }\\n        __typename\\n      }\\n      location {\\n        label(locale: $locale, type: LONG)\\n        __typename\\n      }\\n      classifications {\\n        label(languageCode: $languageCode)\\n        __typename\\n      }\\n      products {\\n        branding {\\n          id\\n          cover {\\n            url\\n            __typename\\n          }\\n          thumbnailCover: cover(isThumbnail: true) {\\n            url\\n            __typename\\n          }\\n          logo {\\n            url\\n            __typename\\n          }\\n          __typename\\n        }\\n        bullets\\n        questionnaire {\\n          questions\\n          __typename\\n        }\\n        video {\\n          url\\n          position\\n          __typename\\n        }\\n        __typename\\n      }\\n      __typename\\n    }\\n    companyProfile(zone: $zone) {\\n      id\\n      name\\n      companyNameSlug\\n      shouldDisplayReviews\\n      branding {\\n        logo\\n        __typename\\n      }\\n      overview {\\n        description {\\n          paragraphs\\n          __typename\\n        }\\n        industry\\n        size {\\n          description\\n          __typename\\n        }\\n        website {\\n          url\\n          __typename\\n        }\\n        __typename\\n      }\\n      reviewsSummary {\\n        overallRating {\\n          numberOfReviews {\\n            value\\n            __typename\\n          }\\n          value\\n          __typename\\n        }\\n        __typename\\n      }\\n      perksAndBenefits {\\n        title\\n        __typename\\n      }\\n      __typename\\n    }\\n    companySearchUrl(zone: $zone, languageCode: $languageCode)\\n    learningInsights(platform: WEB, zone: $zone, locale: $locale) {\\n      analytics\\n      content\\n      __typename\\n    }\\n    companyTags {\\n      key(languageCode: $languageCode)\\n      value\\n      __typename\\n    }\\n    restrictedApplication(countryCode: $countryCode) {\\n      label(locale: $locale)\\n      __typename\\n    }\\n    sourcr {\\n      image\\n      imageMobile\\n      link\\n      __typename\\n    }\\n    gfjInfo {\\n      location {\\n        countryCode\\n        country(locale: $locale)\\n        suburb(locale: $locale)\\n        region(locale: $locale)\\n        state(locale: $locale)\\n        postcode\\n        __typename\\n      }\\n      workTypes {\\n        label\\n        __typename\\n      }\\n      __typename\\n    }\\n    __typename\\n  }\\n}\\n\",\"variables\":{\"jobId\":\""+str(jobId)+"\",\"jobDetailsViewedCorrelationId\":\"58ad64b3-e268-4467-b90d-5bb1a4b57680\",\"sessionId\":\"1ad0f857-940d-4839-884e-354bd976a872\",\"zone\":\"anz-1\",\"locale\":\"en-AU\",\"languageCode\":\"en\",\"countryCode\":\"AU\",\"timezone\":\"Asia/Bangkok\"}}"
        headers = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'no-cache',
        'content-type': 'application/json',
        'origin': 'https://www.seek.com.au',
        'pragma': 'no-cache',
        'priority': 'u=1, i',
        'sec-ch-ua': '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'seek-request-brand': 'seek',
        'seek-request-country': 'AU',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
        'x-seek-site': 'chalice'
        }
        try:
            response = requests.request("POST", url, headers=headers, data=payload)
            return response.json()
        except Exception as e:
            self.listError.append(url)
            print (e)
            print ("Error" + url +"\n")
        return {}
        # print (response.text)
    def cleanText(self,text):
    # Remove HTML tags
        clean = re.sub('<[^<]+?>', '', text)
        # Remove newlines and carriage returns
        clean = re.sub('[\n\r]+', ' ', clean)
        # Replace multiple spaces with a single space
        clean = re.sub(r'\s+', ' ', clean)
        return clean.strip()
    def createRow(self,json_data):
        job_data = json_data['data']['jobDetails']['job']

        job_df = pd.DataFrame([{
            'title': self.safeGet(job_data, 'title', default=""),
            'company_name': self.safeGet(job_data, 'advertiser', 'name', default=""),   
            'company_location': self.safeGet(job_data, 'location', 'label', default=""),
            'department': self.safeGet(job_data, 'classifications', 0, 'label', default=""),
            'job_type': self.safeGet(job_data, 'workTypes', 'label', default=""),
            'salary_range': self.safeGet(job_data, 'salary', 'label', default=""),
            'email': next((contact['value'] for contact in job_data.get('contactMatches', []) if contact['type'] == 'Email'), ""),
            'phone': next((contact['value'] for contact in job_data.get('contactMatches', []) if contact['type'] == 'Phone'), ""),
            'ads_link': self.safeGet(job_data, 'shareLink', default=""),
            'ads_posted_date': datetime.fromisoformat(self.safeGet(job_data, 'listedAt', 'dateTimeUtc', default="2024-09-24T07:33:02.261Z").replace('Z', '+00:00')).strftime('%Y-%m-%d'),
            'raw_text': self.cleanText(self.safeGet(job_data, 'content', default=""))
        }])
        return job_df
    def main(self):
        dataPages=[]
        all_jobs_df = pd.DataFrame()
        for page in range(1,3):
            print ("page index "+str(page))
            page=self.getPages(page)
            if 'data' in page:
                dataPages=dataPages+page['data']
            sleep(2)
        jodIds=[]
        print (len(dataPages))
        for item in dataPages:
            if (item['id'] not in jodIds):
                jodIds.append(item['id'])
        print (len(jodIds))
        for item in jodIds[:]:
            print (item)
            detail=self.getDetail(item)
            if 'data' in detail:
                job_df = self.createRow(detail)
                all_jobs_df = pd.concat([all_jobs_df, job_df], ignore_index=True)
            sleep(2)
        current_time = datetime.now()
        sheet_name = current_time.strftime('%d-%m-%y %H:%M')
        sheet_seek = os.environ.get(f'sheet_seek')
        print (len(all_jobs_df))
        write_dataframe_to_sheet(all_jobs_df, sheet_name,sheet_seek)



if __name__ == "__main__":
    Scaping().main()

    # json_data = json.loads('''{"data":{"jobDetails":{"job":{"sourceZone":"anz-1","tracking":{"adProductType":"Branded","classificationInfo":{"classificationId":"1200","classification":"Accounting","subClassificationId":"6151","subClassification":"Financial Accounting & Reporting","__typename":"JobTrackingClassificationInfo"},"hasRoleRequirements":true,"isPrivateAdvertiser":false,"locationInfo":{"area":"Fremantle & Southern Suburbs","location":"Perth","locationIds":["5050"],"__typename":"JobTrackingLocationInfo"},"workTypeIds":"242","postedTime":"24m ago","__typename":"JobTracking"},"id":"79053918","title":"Financial and Management Accountant","phoneNumber":null,"isExpired":false,"expiresAt":{"dateTimeUtc":"2024-10-24T12:59:59.999Z","__typename":"SeekDateTime"},"isLinkOut":false,"contactMatches":[{"type":"Email","value":"gharris@harc.net.au","__typename":"ContactMatches"},{"type":"Phone","value":"0408 905 057","__typename":"ContactMatches"}],"isVerified":true,"abstract":"Full responsibility for the accounting and financial and management reporting functions in a fast growing company.","content":"<p>Our client is a well established and successful provider of services and products to the resource and construction sectors.   </p><p>The consistent double digit growth of the company now sees them expanding their facilities in the industrial area of Perth's southern suburbs.  The Directors wish to support this ongoing growth through the appointment of a Financial and Management Accountant.  </p><p>The Financial and Management Accountant will take <i>hands-on </i>responsibility for the accounting and management reporting functions and report to the Managing Director. The role is supported at transactional level by a small accounts and bookkeeping team.</p><p>Overarching outcomes of the position are the control of costs and financial management of operations, financial reporting, capital control and management of the accounting team.  </p><p>Importantly, the Financial Accountant and Management will need to demonstrate superior written and interpersonal communication skills.  Equally, an ability to confidently engage with internal staff and external service providers is essential for this position.</p><p>Specific responsibilities of the Financial and Management Accountant follow;</p><ul><li>Effective, timely, accurate and clear management reporting</li><li>Cashflow monitoring and reporting</li><li>Monthly financial statements preparation</li><li>Hands-on creditor and debtor processing and management</li><li>Payroll processing</li><li>Work in progress job cost control and reporting</li><li>BAS returns</li><li>ASIC compliance</li><li>Tax compliance (in conjunction with the external tax accountant)</li><li>Project analysis as directed by the executive team</li></ul><p>It is expected the appointee will have <strong>CA or CPA qualifications </strong>and a <strong>minimum six years</strong> of experience in a professional accounting practice in audit or tax and business services.  Alternatively, a broad knowledge of accounting standards and financial accounting experience in a job costing, construction or manufacturing organisation will be an appropriate career background.</p><p>Should you exhibit the above attributes, qualifications and experience and have the inherent energy to assume financial and accounting responsibility in a fast-growing company then we would encourage your expression of interest. </p><p>Please apply via Seek or contact Geoffrey Harris CA at gharris@harc.net.au or 0408 905 057.</p>","status":"Active","listedAt":{"label":"24m ago","dateTimeUtc":"2024-09-24T07:33:02.261Z","__typename":"SeekDateTime"},"salary":{"currencyLabel":null,"label":"$130,000 – $140,000 (plus super and parking)","__typename":"JobSalary"},"shareLink":"https://www.seek.com.au/job/79053918?tracking=SHR-WEB-SharedJob-anz-1","workTypes":{"label":"Full time","__typename":"JobWorkTypes"},"advertiser":{"id":"29803530","name":"Harris Recruitment","isVerified":true,"registrationDate":{"dateTimeUtc":"2013-11-07T06:52:41.257Z","__typename":"SeekDateTime"},"__typename":"Advertiser"},"location":{"label":"Fremantle & Southern Suburbs, Perth WA","__typename":"LocationInfo"},"classifications":[{"label":"Financial Accounting & Reporting (Accounting)","__typename":"ClassificationInfo"}],"products":{"branding":{"id":"de70cf42-7166-11f4-d188-8aadca6f84bd.1","cover":null,"thumbnailCover":null,"logo":{"url":"https://image-service-cdn.seek.com.au/2d17fdf8aff2897e2d2cf5d79a8fc70ea909cac5/f3c5292cec0e05e4272d9bf9146f390d366481d0","__typename":"JobProductBrandingImage"},"__typename":"JobProductBranding"},"bullets":["Expanding company in the resources and construction sectors","Career step from professional practice or step up within commerce","Integrated financial, cost and management reporting"],"questionnaire":{"questions":["How many years' experience do you have as a Financial and Management Accountant?","How many years of accounting experience do you have?","Which of the following statements best describes your right to work in Australia?"],"__typename":"JobQuestionnaire"},"video":null,"__typename":"JobProducts"},"__typename":"Job"},"companyProfile":null,"companySearchUrl":"https://www.seek.com.au/Harris-Recruitment-jobs/at-this-company","learningInsights":{"analytics":{"title":"Course Directory homepage","landingPage":"CD Home","bannerName":"DefaultSearchToCD","resultType":"DefaultSearchToCD:financial-and-management-accountant","entity":"course","encoded":"title:Course Directory homepage;landingPage:CD Home;bannerName:DefaultSearchToCD;resultType:DefaultSearchToCD:financial-and-management-accountant;entity:course"},"content":"<style>\n  /* capsize font, don't change */\n  .capsize-heading4 {\n    font-size: 20px;\n    line-height: 24.66px;\n    display: block;\n    font-weight: 500;\n  }\n\n  .capsize-heading4::before {\n    content: '';\n    margin-bottom: -0.225em;\n    display: table;\n  }\n\n  .capsize-heading4::after {\n    content: '';\n    margin-top: -0.225em;\n    display: table;\n  }\n\n  .capsize-standardText {\n    font-size: 16px;\n    line-height: 24.528px;\n    display: block;\n  }\n\n  .capsize-standardText::before {\n    content: '';\n    margin-bottom: -0.375em;\n    display: table;\n  }\n\n  .capsize-standardText::after {\n    content: '';\n    margin-top: -0.375em;\n    display: table;\n  }\n  /* end of capsize */\n\n  /* LMIS css start here*/\n  .lmis-root {\n    font-family: SeekSans, 'SeekSans Fallback', Arial, sans-serif;\n    color: #2e3849;\n    background-color: #fff;\n    border-radius: 16px;\n  }\n\n  .lmis-description {\n    margin: 24px 0;\n  }\n\n  .lmis-cta {\n    font-weight: 500;\n    text-decoration: none;\n    display: flex;\n    align-items: center;\n    justify-content: center;\n    color: #2e3849;\n    border: 2px solid #2e3849;\n    border-radius: 8px;\n    min-height: 48px;\n  }\n\n  .lmis-cta:hover {\n    background-color: #f4f6fe;\n  }\n\n  .lmis-cta img {\n    margin-left: 4px;\n  }\n\n  @media only screen and (min-width: 740px) {\n    .lmis-cta {\n      max-width: 250px;\n    }\n  }\n\n  @media only screen and (min-width: 992px) {\n    .lmis-root {\n      margin: -16px;\n    }\n  }\n</style>\n\n<div class=\"lmis-root\">\n  <div class=\"capsize-heading4\">Need to upskill?</div>\n  <div class=\"capsize-standardText lmis-description\">\n    Choose from thousands of courses delivered by leaders in education.\n  </div>\n  <a\n    class=\"lmis-cta\"\n    target=\"_blank\"\n    href=\"https://www.seek.com.au/learning/?campaigncode=lrn:skj:sklm:jbd:rhs:dg:btn:resp\"\n  >\n    <span class=\"capsize-standardText\">Find the course for you</span>\n    <img\n      src=\"https://cdn.seeklearning.com.au/media/images/lmis/arrow_right.svg\"\n      alt=\"arrow-right\"\n    />\n  </a>\n</div>\n","__typename":"LearningInsights"},"companyTags":[],"restrictedApplication":{"label":null,"__typename":"JobDetailsRestrictedApplication"},"sourcr":null,"gfjInfo":{"location":{"countryCode":"AU","country":"Australia","suburb":null,"region":null,"state":"Western Australia","postcode":null,"__typename":"GFJLocation"},"workTypes":{"label":["FULL_TIME"],"__typename":"GFJWorkTypes"},"__typename":"GFJInfo"},"__typename":"JobDetails"}}}''')

# Extract relevant data
    # job_data = json_data['data']['jobDetails']['job']
    #a=Scaping().safeGet(job_data, 'classifications', 0, 'label', default="Department not specified")
    #print (a)
    # a=Scaping().getDetail('79047414')
    # job_data = a['data']['jobDetails']['job']
    #print (job_data['classifications'][0]['label'])
    #print (Scaping().safeGet(job_data, 'classifications', 0, 'label', default="Department not specified"))





# def saveFile(fileName):
#     headers    = ['Title','Company Location','Department','Job type','Salary range','Email','Phone','Ads Link','Ads Posted Date','Raw text']
#     workbook_name = fileName
#     if os.path.isfile(workbook_name):
#         wb = load_workbook(workbook_name)
#         page = wb.active
#     else:
#         wb = Workbook()
#         page = wb.active
#         page.title = 'result'
#         page.append(headers) # write the headers to the first line

# for item in jodIds:
#     print (item['id'])

# print (response)
# print(response.text)