import json
import locale
import os
import sys
from array import array
from warnings import catch_warnings

from numpy.matlib import empty

current = os.path.dirname(os.path.realpath(__file__))
subparent = os.path.dirname(current)
parent = os.path.dirname(subparent)
root =   os.path.dirname(parent)
sys.path.append(subparent)
sys.path.append(parent)
sys.path.append(root)
from datetime import datetime
import requests
from common.gs import write_dataframe_to_sheet, write_data_to_sheet, open_worksheet
import re
import pandas as pd
from time import sleep

class GlassdoorJobListing:
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
        self.website = 'https://www.glassdoor.com.au'
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

    def getListJobs(self, keyword, originalPageUrl, seoFriendlyUrlInput, pageNumber=1, pageCursor = None):
        url = self.website + "/graph"
        payload = json.dumps([
            {
                "operationName": "JobSearchResultsQuery",
                "variables": {
                    "excludeJobListingIds": [],
                    "filterParams": [],
                    "keyword": keyword,
                    "locationId": 16,
                    "locationType": "COUNTRY",
                    "numJobsToShow": 30,
                    "originalPageUrl": originalPageUrl,
                    "parameterUrlInput": "IL.0,9_IN16_KO10,20",
                    "pageType": "SERP",
                    "queryString": "",
                    "seoFriendlyUrlInput": seoFriendlyUrlInput,
                    "seoUrl": True,
                    "includeIndeedJobAttributes": True,
                    "pageCursor": pageCursor,
                    "pageNumber": pageNumber
                },
                "query": "query JobSearchResultsQuery($excludeJobListingIds: [Long!], $filterParams: [FilterParams], $keyword: String, $locationId: Int, $locationType: LocationTypeEnum, $numJobsToShow: Int!, $originalPageUrl: String, $pageCursor: String, $pageNumber: Int, $pageType: PageTypeEnum, $parameterUrlInput: String, $queryString: String, $seoFriendlyUrlInput: String, $seoUrl: Boolean, $includeIndeedJobAttributes: Boolean) {\n  jobListings(\n    contextHolder: {queryString: $queryString, pageTypeEnum: $pageType, searchParams: {excludeJobListingIds: $excludeJobListingIds, filterParams: $filterParams, keyword: $keyword, locationId: $locationId, locationType: $locationType, numPerPage: $numJobsToShow, pageCursor: $pageCursor, pageNumber: $pageNumber, originalPageUrl: $originalPageUrl, seoFriendlyUrlInput: $seoFriendlyUrlInput, parameterUrlInput: $parameterUrlInput, seoUrl: $seoUrl, searchType: SR, includeIndeedJobAttributes: $includeIndeedJobAttributes}}\n  ) {\n    companyFilterOptions {\n      id\n      shortName\n      __typename\n    }\n    filterOptions\n    indeedCtk\n    jobListings {\n      ...JobView\n      __typename\n    }\n    jobListingSeoLinks {\n      linkItems {\n        position\n        url\n        __typename\n      }\n      __typename\n    }\n    jobSearchTrackingKey\n    jobsPageSeoData {\n      pageMetaDescription\n      pageTitle\n      __typename\n    }\n    paginationCursors {\n      cursor\n      pageNumber\n      __typename\n    }\n    indexablePageForSeo\n    searchResultsMetadata {\n      searchCriteria {\n        implicitLocation {\n          id\n          localizedDisplayName\n          type\n          __typename\n        }\n        keyword\n        location {\n          id\n          shortName\n          localizedShortName\n          localizedDisplayName\n          type\n          __typename\n        }\n        __typename\n      }\n      footerVO {\n        countryMenu {\n          childNavigationLinks {\n            id\n            link\n            textKey\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n      helpCenterDomain\n      helpCenterLocale\n      jobAlert {\n        jobAlertId\n        __typename\n      }\n      jobSerpFaq {\n        questions {\n          answer\n          question\n          __typename\n        }\n        __typename\n      }\n      jobSerpJobOutlook {\n        occupation\n        paragraph\n        heading\n        __typename\n      }\n      showMachineReadableJobs\n      __typename\n    }\n    serpSeoLinksVO {\n      relatedJobTitlesResults\n      searchedJobTitle\n      searchedKeyword\n      searchedLocationIdAsString\n      searchedLocationSeoName\n      searchedLocationType\n      topCityIdsToNameResults {\n        key\n        value\n        __typename\n      }\n      topEmployerIdsToNameResults {\n        key\n        value\n        __typename\n      }\n      topEmployerNameResults\n      topOccupationResults\n      __typename\n    }\n    totalJobsCount\n    __typename\n  }\n}\n\nfragment JobView on JobListingSearchResult {\n  jobview {\n    header {\n      indeedJobAttribute {\n        skills\n        extractedJobAttributes {\n          key\n          value\n          __typename\n        }\n        __typename\n      }\n      adOrderId\n      advertiserType\n      ageInDays\n      divisionEmployerName\n      easyApply\n      employer {\n        id\n        name\n        shortName\n        __typename\n      }\n      expired\n      organic\n      employerNameFromSearch\n      goc\n      gocConfidence\n      gocId\n      isSponsoredJob\n      isSponsoredEmployer\n      jobCountryId\n      jobLink\n      jobResultTrackingKey\n      normalizedJobTitle\n      jobTitleText\n      locationName\n      locationType\n      locId\n      needsCommission\n      payCurrency\n      payPeriod\n      payPeriodAdjustedPay {\n        p10\n        p50\n        p90\n        __typename\n      }\n      rating\n      salarySource\n      savedJobId\n      seoJobLink\n      __typename\n    }\n    job {\n      descriptionFragmentsText\n      importConfigId\n      jobTitleId\n      jobTitleText\n      listingId\n      __typename\n    }\n    jobListingAdminDetails {\n      cpcVal\n      importConfigId\n      jobListingId\n      jobSourceId\n      userEligibleForAdminJobDetails\n      __typename\n    }\n    overview {\n      shortName\n      squareLogoUrl\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n"
            }
        ])
        headers = {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9,vi;q=0.8',
            'apollographql-client-name': 'job-search-next',
            'apollographql-client-version': '7.77.2-hotfix-7-77-2-performance.3',
            'cache-control': 'no-cache',
            'content-type': 'application/json',
            'cookie': 'gdId=1e5ab43d-69cb-4ed7-b378-136f80c7f8f7; rl_page_init_referrer=RudderEncrypt%3AU2FsdGVkX1%2B%2FKMRkCa2T7OxZ%2BAjhoJ%2B%2FCbG%2BrHLrIaA%3D; rl_page_init_referring_domain=RudderEncrypt%3AU2FsdGVkX19ZGO7W69dqd8fo0NxR7R4zRTvHi%2Boi7%2BA%3D; GSESSIONID=undefined; _optionalConsent=true; _gcl_au=1.1.114906139.1727322048; __pdst=f136f3363e064aa0894d62a8c67606ed; _fbp=fb.2.1727322048541.98386705973576795; _tt_enable_cookie=1; _ttp=XgD0ibFWeUuMjSEqp7DLc0trL4w; _pin_unauth=dWlkPU5tTTJZalkxT0dJdFpqZ3hOQzAwT0RaaUxUZ3dZek10TjJVMllqTmtNVE5pWW1Zdw; _rdt_uuid=1727322048211.d7290527-1e00-4c79-88a0-0fd0e1b11e92; _derived_epik=dj0yJnU9cUJPc1BxRzJrU3NNak9vR0dRUTQ0YUtsMkhZZnlvdzYmbj0xVHU1dVZQcXZzVlpuZzktNWpSR1d3Jm09MSZ0PUFBQUFBR2IwMV9RJnJtPTEmcnQ9QUFBQUFHYjAxX1Emc3A9Mg; indeedCtk=1i8m6ng66iq5f801; _cfuvid=T.hTsNvnRSGUBR9iAW8EXFygPU4VnGIMR7PHfdqsUC4-1727345107423-0.0.1.1-604800000; asst=1727345109.0; rsSessionId=1727345145016; JSESSIONID=2EE5E480EEF250A07022522367FA8FE3; cass=0; __cf_bm=0UCsViTnwQ4W0mwF._iuQxJCCTBffj1aghHIIWs2JOI-1727348013-1.0.1.1-5ZdFyzCEVMgg52y7UDaYYGriRry4J_iC3y73cCuxLsjj6fSz9eEb13oNkNo3K7xaC595WjulcD.0wFXVPvNW6A; gdsid=1727345153575:1727348071031:3B14F8980B1AC70A905C6B3139884573; cf_clearance=5IlEPNm7W9RVJwtJXhBj56GaHqTXZ4SKW_1HlcxENP4-1727348075-1.2.1.1-LGKSf.Yb7FnZiYXfgPIHxKLIFkAC7LKsXprot5NjAzPJc.rA00G2q.wYYrhUy_gQ3NiBJqmcAxXZJDEskHOaPhpczr19xdOJ.vS5N2NQWJ._I91kt.JJXiZQhbPLc_8GAoJWm1TbJo1iqj69JLyHJKOOGOB9_ug01eqQEoJe0.SNbdYY8_FafCbbc9g2HhJfs4wTWok3T6yq9SmrUJACAwowg7sDnWdR5fwAoV9LkjR1OYieOy1CXT26LFvO993WQQ87.OQzAHiIqAzOwIsXmDw3hxKjHm9s5HH13XK9SSTKAMRvRmn22k8XEHNy9hAr_FPU4gR4dyZnBf2q1bbdjFCuHD4xLgv1suDZujQJeXGByNoKJFWAiiwZq8.G_Kvg; rl_user_id=RudderEncrypt%3AU2FsdGVkX1%2Bkc2ikaTmd6zrpRtbDhIj2O%2FyvsGtf7tY%3D; rl_trait=RudderEncrypt%3AU2FsdGVkX19fm2NM9ui9VJC9x4MMoK71L%2F7IZnSCqis%3D; rl_group_id=RudderEncrypt%3AU2FsdGVkX1%2FYeUG5MRjJNxpLuHWKvRCE89%2FzNhlJq2I%3D; rl_group_trait=RudderEncrypt%3AU2FsdGVkX19qi%2FYmswB6eeUR2hcqrTYd%2F%2FbIpiyJGFA%3D; OptanonConsent=isGpcEnabled=0&datestamp=Thu+Sep+26+2024+17%3A58%3A05+GMT%2B0700+(Indochina+Time)&version=202407.2.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=c112a181-a131-4c27-9223-361abcea654c&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0003%3A1%2CC0002%3A1%2CC0004%3A1%2CC0017%3A1&AwaitingReconsent=false; AWSALB=RD9lBP6uf2Y7MmJq0L32+TtJ/pI9paVz7/Z5cJEKdbCg3uMUsV63ALAPN2boEn/7x6Pi87HwFWyALJforeG37aQvSIK5OSZJZ9sqdlZMxFJ8ro5FDDLeX5zGdvje; AWSALBCORS=RD9lBP6uf2Y7MmJq0L32+TtJ/pI9paVz7/Z5cJEKdbCg3uMUsV63ALAPN2boEn/7x6Pi87HwFWyALJforeG37aQvSIK5OSZJZ9sqdlZMxFJ8ro5FDDLeX5zGdvje; rl_anonymous_id=RudderEncrypt%3AU2FsdGVkX1%2FUefLSdQX1u0GyARj3Bk4zbtn%2F2OXs6w%2F9WMyZrxX99p82YgZTg0I4tMCPca0ZhVLUT84vnJTtxQ%3D%3D; rsReferrerData=%7B%22currentPageRollup%22%3A%22%2Fjob%2Fjobs-srch%22%2C%22previousPageRollup%22%3A%22%2Fjob-listing%2Fjv%22%2C%22currentPageAbstract%22%3A%22%2FJob%2F%5BOCC%5D-jobs-SRCH_%5BPRM%5D.htm%22%2C%22previousPageAbstract%22%3A%22%2Fjob-listing%2F%5BOCC%5D-%5BEMP%5D-JV_%5BPRM%5D.htm%22%2C%22currentPageFull%22%3A%22https%3A%2F%2Fwww.glassdoor.com.au%2FJob%2Faustralia-accountant-jobs-SRCH_IL.0%2C9_IN16_KO10%2C20.htm%22%2C%22previousPageFull%22%3A%22https%3A%2F%2Fwww.glassdoor.com.au%2Fjob-listing%2Fjunior-accountant-malabar-foods-JV_IC2256890_KO0%2C17_KE18%2C31.htm%3Fjl%3D1009315512558%26cs%3D1_b7f1c355%26s%3D58%26t%3DSR%26pos%3D101%26src%3DGD_JOB_AD%26guid%3D000001922df938929102dea7e3ba7740%26jobListingId%3D1009315512558%26ea%3D1%26ao%3D1136043%26vt%3Dw%26jrtk%3D5-pdx1-0-1i8mvie6oi0hp800-b0ccd711f4e947e0%26cb%3D1727348160950%26ctt%3D1727348282097%22%7D; _dd_s=rum=0&expire=1727349882711; rl_session=RudderEncrypt%3AU2FsdGVkX1%2BQmo9Uihv6lCe6tV%2B%2BO0bph6f1dT3Sh%2FTAFPpTairPADkRHf%2FnAi75MSrNKr4xdC3swICG0QHp9FFiL7BxZyCFPUcE%2FYnkmC%2FAPf6azpW2RqkU5Q0p%2Ffi%2BlQWhd2nGHoe8VvTGxsxnVA%3D%3D; cdArr=101; __cf_bm=GSUc8XDKgypktj2hqI8_Ws7tMszrCEcf8BWrtPOjAC0-1727349853-1.0.1.1-hm6CqbDSjU614eWdLaeky6XJzrFljanQCirFQhYngo5ccjjtd6XYXZ_JvgMlZ2RGpNDBpQFaJGX.FfFhQ3gGyw; asst=1727345109.0; gdsid=1727345153575:1727349852733:B3B07F5AF0BEF468DD22FACF7882DFBC',
            'gd-csrf-token': 'LjwCtuoj3ZfE2-3baddeaw:PL5bFRsfqSX5A4uKQyKalHV4b5oUjCKwSM58g5xWhdOihjrr6V_bnOa2Bzo_MYQ-EttLm8LLCkfBDuWVWfrR6A:pRVeBLp105LaVoNi87DByDY86BcYE-_541xZT7Rx-4I',
            'origin': 'https://www.glassdoor.com.au',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://www.glassdoor.com.au/',
            'sec-ch-ua': '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
            'x-gd-job-page': 'serp'
        }
        try:
            response = requests.request("POST", url, headers=headers, data=payload)
            return response.json()
        except Exception as e:
            self.listError.append(url)
            print(e)
            print("Error" + url + "\n")
        return {}

    def getDetail(self,jobId=1009432955313):
        url = f"{self.website}/graph"
        payload = json.dumps([
            {
                "operationName": "JobDetailQuery",
                "variables": {
                    "enableReviewSummary": True,
                    "jl": jobId,
                    "queryString": "pos=102&ao=1136043&s=58&guid=000001922de8803789a974d0bfa51853&src=GD_JOB_AD&t=SR&vt=w&ea=1&cs=1_c24d1e09&cb=1727347065212&jobListingId=1009432955313&jrtk=5-pdx1-0-1i8muh04niq7p800-cc6ccf45ac4ac0af",
                    "pageTypeEnum": "SERP",
                    "countryId": 16
                },
                "query": "query JobDetailQuery($jl: Long!, $queryString: String, $enableReviewSummary: Boolean!, $pageTypeEnum: PageTypeEnum, $countryId: Int) {\n  jobview: jobView(\n    listingId: $jl\n    contextHolder: {queryString: $queryString, pageTypeEnum: $pageTypeEnum}\n  ) {\n    ...DetailFragment\n    employerReviewSummary @include(if: $enableReviewSummary) {\n      reviewSummary {\n        highlightSummary {\n          sentiment\n          sentence\n          categoryReviewCount\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment DetailFragment on JobView {\n  employerBenefits {\n    benefitsOverview {\n      benefitsHighlights {\n        benefit {\n          commentCount\n          icon\n          name\n          __typename\n        }\n        highlightPhrase\n        __typename\n      }\n      overallBenefitRating\n      employerBenefitSummary {\n        comment\n        __typename\n      }\n      __typename\n    }\n    benefitReviews {\n      benefitComments {\n        id\n        comment\n        __typename\n      }\n      cityName\n      createDate\n      currentJob\n      rating\n      stateName\n      userEnteredJobTitle\n      __typename\n    }\n    numReviews\n    __typename\n  }\n  employerContent {\n    featuredVideoLink\n    managedContent {\n      id\n      type\n      title\n      body\n      captions\n      photos\n      videos\n      __typename\n    }\n    diversityContent {\n      goals {\n        id\n        workPopulation\n        underRepresentedGroup\n        currentMetrics\n        currentMetricsDate\n        representationGoalMetrics\n        representationGoalMetricsDate\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  employerAttributes {\n    attributes {\n      attributeName\n      attributeValue\n      __typename\n    }\n    __typename\n  }\n  gaTrackerData {\n    jobViewDisplayTimeMillis\n    requiresTracking\n    pageRequestGuid\n    searchTypeCode\n    trackingUrl\n    __typename\n  }\n  header {\n    jobLink\n    adOrderId\n    advertiserType\n    ageInDays\n    applicationId\n    appliedDate\n    applyUrl\n    applyButtonDisabled\n    divisionEmployerName\n    easyApply\n    easyApplyMethod\n    employerNameFromSearch\n    employer {\n      activeStatus\n      bestProfile {\n        id\n        __typename\n      }\n      id\n      name\n      shortName\n      size\n      squareLogoUrl\n      __typename\n    }\n    expired\n    goc\n    hideCEOInfo\n    indeedApplyMetadata\n    indeedJobAttribute {\n      education\n      skills\n      educationLabel\n      skillsLabel\n      yearsOfExperienceLabel\n      __typename\n    }\n    isIndexableJobViewPage\n    isSponsoredJob\n    isSponsoredEmployer\n    jobTitleText\n    jobType\n    jobTypeKeys\n    jobCountryId\n    jobResultTrackingKey\n    locId\n    locationName\n    locationType\n    needsCommission\n    normalizedJobTitle\n    organic\n    payCurrency\n    payPeriod\n    payPeriodAdjustedPay {\n      p10\n      p50\n      p90\n      __typename\n    }\n    rating\n    remoteWorkTypes\n    salarySource\n    savedJobId\n    seoJobLink\n    serpUrlForJobListing\n    sgocId\n    categoryMgocId\n    __typename\n  }\n  job {\n    description\n    discoverDate\n    eolHashCode\n    importConfigId\n    jobReqId\n    jobSource\n    jobTitleId\n    jobTitleText\n    listingId\n    __typename\n  }\n  jobListingAdminDetails {\n    adOrderId\n    cpcVal\n    importConfigId\n    jobListingId\n    jobSourceId\n    userEligibleForAdminJobDetails\n    __typename\n  }\n  map {\n    address\n    cityName\n    country\n    employer {\n      id\n      name\n      __typename\n    }\n    lat\n    lng\n    locationName\n    postalCode\n    stateName\n    __typename\n  }\n  overview {\n    ceo(countryId: $countryId) {\n      name\n      photoUrl\n      __typename\n    }\n    id\n    name\n    shortName\n    squareLogoUrl\n    headquarters\n    links {\n      overviewUrl\n      benefitsUrl\n      photosUrl\n      reviewsUrl\n      salariesUrl\n      __typename\n    }\n    primaryIndustry {\n      industryId\n      industryName\n      sectorName\n      sectorId\n      __typename\n    }\n    ratings {\n      overallRating\n      ceoRating\n      ceoRatingsCount\n      recommendToFriendRating\n      compensationAndBenefitsRating\n      cultureAndValuesRating\n      careerOpportunitiesRating\n      seniorManagementRating\n      workLifeBalanceRating\n      __typename\n    }\n    revenue\n    size\n    sizeCategory\n    type\n    website\n    yearFounded\n    __typename\n  }\n  photos {\n    photos {\n      caption\n      photoId\n      photoId2x\n      photoLink\n      photoUrl\n      photoUrl2x\n      __typename\n    }\n    __typename\n  }\n  reviews {\n    reviews {\n      advice\n      cons\n      countHelpful\n      employerResponses {\n        response\n        responseDateTime\n        userJobTitle\n        __typename\n      }\n      employmentStatus\n      featured\n      isCurrentJob\n      jobTitle {\n        text\n        __typename\n      }\n      lengthOfEmployment\n      pros\n      ratingBusinessOutlook\n      ratingCareerOpportunities\n      ratingCeo\n      ratingCompensationAndBenefits\n      ratingCultureAndValues\n      ratingOverall\n      ratingRecommendToFriend\n      ratingSeniorLeadership\n      ratingWorkLifeBalance\n      reviewDateTime\n      reviewId\n      summary\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n"
            }
        ])
        headers = {
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.9,vi;q=0.8',
            'apollographql-client-name': 'job-search-next',
            'apollographql-client-version': '7.77.2-hotfix-7-77-2-performance.3',
            'cache-control': 'no-cache',
            'content-type': 'application/json',
            'cookie': 'gdId=1e5ab43d-69cb-4ed7-b378-136f80c7f8f7; rl_page_init_referrer=RudderEncrypt%3AU2FsdGVkX1%2B%2FKMRkCa2T7OxZ%2BAjhoJ%2B%2FCbG%2BrHLrIaA%3D; rl_page_init_referring_domain=RudderEncrypt%3AU2FsdGVkX19ZGO7W69dqd8fo0NxR7R4zRTvHi%2Boi7%2BA%3D; GSESSIONID=undefined; _optionalConsent=true; _gcl_au=1.1.114906139.1727322048; __pdst=f136f3363e064aa0894d62a8c67606ed; _fbp=fb.2.1727322048541.98386705973576795; _tt_enable_cookie=1; _ttp=XgD0ibFWeUuMjSEqp7DLc0trL4w; _pin_unauth=dWlkPU5tTTJZalkxT0dJdFpqZ3hOQzAwT0RaaUxUZ3dZek10TjJVMllqTmtNVE5pWW1Zdw; _rdt_uuid=1727322048211.d7290527-1e00-4c79-88a0-0fd0e1b11e92; _derived_epik=dj0yJnU9cUJPc1BxRzJrU3NNak9vR0dRUTQ0YUtsMkhZZnlvdzYmbj0xVHU1dVZQcXZzVlpuZzktNWpSR1d3Jm09MSZ0PUFBQUFBR2IwMV9RJnJtPTEmcnQ9QUFBQUFHYjAxX1Emc3A9Mg; indeedCtk=1i8m6ng66iq5f801; _cfuvid=T.hTsNvnRSGUBR9iAW8EXFygPU4VnGIMR7PHfdqsUC4-1727345107423-0.0.1.1-604800000; asst=1727345109.0; rsSessionId=1727345145016; rsReferrerData=%7B%22currentPageRollup%22%3A%22%2Fjob%2Fjobs-srch%22%2C%22previousPageRollup%22%3A%22%2Fjob%2Fjobs-srch%22%2C%22currentPageAbstract%22%3A%22%2FJob%2F%5BOCC%5D-jobs-SRCH_%5BPRM%5D.htm%22%2C%22previousPageAbstract%22%3A%22%2FJob%2F%5BOCC%5D-jobs-SRCH_%5BPRM%5D.htm%22%2C%22currentPageFull%22%3A%22https%3A%2F%2Fwww.glassdoor.com.au%2FJob%2Faustralia-accountant-jobs-SRCH_IL.0%2C9_IN16_KO10%2C20.htm%22%2C%22previousPageFull%22%3A%22https%3A%2F%2Fwww.glassdoor.com.au%2FJob%2Faustralia-accountant-jobs-SRCH_IL.0%2C9_IN16_KO10%2C20.htm%22%7D; AWSALB=yLjW8gyoA5QjNPZgbmU01L2rMgd6qNb/BWuHe6LqRtfj3YE68wrlzykn7rJ5Iw6j57LUw4RMwEjiDpJ2HpLmaGKW5GRjN5kj9EP3UKRV5pANko0kTZc9LJ3bXy91; AWSALBCORS=yLjW8gyoA5QjNPZgbmU01L2rMgd6qNb/BWuHe6LqRtfj3YE68wrlzykn7rJ5Iw6j57LUw4RMwEjiDpJ2HpLmaGKW5GRjN5kj9EP3UKRV5pANko0kTZc9LJ3bXy91; JSESSIONID=2EE5E480EEF250A07022522367FA8FE3; cass=0; gdsid=1727345153575:1727347064864:E9C00341826FDF0707BF134BEC8FAFCF; bs=WN2cjm3PVlqhfZiaOsIpMA:OLvgP05LNIjyw7AW6UayN0xhT-HzpdDEOX0kxkDtdTZ9kdjiIQ1LXFKQWwANHC5zYPFCYVN4bnIdQVHNa5ph79JewsES2ch3bcVRUF6J2so:DR_S_i0tAIk1z8YAyB9MtoZ3GcPyfK0ro10tg1m2QKE; __cf_bm=ZNHx_B08gIyCZiv9V3nvFzYrIfepQot8S6.x42xzutY-1727347065-1.0.1.1-F0PkOJq0pi3CfhDTGhh.d1Rgh9v8pfFdKyflhm5MUXRuTmw4Qj81kc2Mwc.0wGEXd3k2ds9ZJugMXoOT2R.9sg; rl_user_id=RudderEncrypt%3AU2FsdGVkX18L89P%2FJ2MVB%2FFCB40ArdZDtZ18iag4Zf4%3D; rl_trait=RudderEncrypt%3AU2FsdGVkX1%2BsjSKAdrM7r7EBtWjccO%2Fu9aT1TpRrBt8%3D; rl_group_id=RudderEncrypt%3AU2FsdGVkX1%2FtzBqpByJhbdAOIfubu%2F7QRiv5bNUgtXc%3D; rl_group_trait=RudderEncrypt%3AU2FsdGVkX18q2wGVj3UBZcXmFqWLTQJS31b8Hkg3tUQ%3D; cf_clearance=j.1AtHB1zH00ZXe.DLXw46ImNe4.YIpW20NfgqTMUYg-1727347070-1.2.1.1-CDJ1njMQtVC2phDROuOFm1xnfDpbDYjWSbbe7Z5nYdfH_bfZpVy0smOqfJ7XHF53Lci.fpXE2uevUjYvcQbKGublf8diukiujskcXJlrsF.59UoC_dr3bNpzOI4IzEVThZtx4QWKM1ksReZT_nuvnbgmVhRuoATBmDMZ9SYqCY3zN8uGuYdPEx4jIoOcDTSjTQhJICWrWs.r4M2d9y800xX99hxVvVoF5jjPkCCrI7VR2GnWbYcYFezSaLQ_kfybSBtxs4Bwe5rvl0xytgHEhRp7syTHA1trOKJ.BiLN.VoX2zWQEywxiI8Zqn9AcpbaLbWits1t2XWoUurD7PKc1M45OnMILWVqC3Z9p7SQPJjXqERoqFfUAa05X.fYq9H6; OptanonConsent=isGpcEnabled=0&datestamp=Thu+Sep+26+2024+17%3A37%3A51+GMT%2B0700+(Indochina+Time)&version=202407.2.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=c112a181-a131-4c27-9223-361abcea654c&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0003%3A1%2CC0002%3A1%2CC0004%3A1%2CC0017%3A1&AwaitingReconsent=false; rl_anonymous_id=RudderEncrypt%3AU2FsdGVkX19zrFqc2KCYoeUWVrRMRsl9VmrBv%2FfEf1EpsRb%2Bs3flV09ADc%2FWo380%2Bzv746ipzERyp%2BKdmzfM6Q%3D%3D; _dd_s=rum=0&expire=1727347981371; rl_session=RudderEncrypt%3AU2FsdGVkX182t%2BbwBrtst0UtMKcSzs4Txj4vZ5TjMTl9GwgFKSdtgjo1oecMuCtAa2GOV7fIke%2FYHHQk73vjn06%2Fzxcc0KsjUVaCQai5FWc60xCc1dTklGmq7F%2FQ2BjRm7JlEOqxQcR4rpOPKICh2w%3D%3D; cdArr=101; __cf_bm=Odd9kiWZzZJX0IC42C.XtqWpu7wX9sPSKrg6etGz20A-1727348351-1.0.1.1-AHZWXxlx.WIig3fekiCD_1zqE4M4xWWNTMEihLjxlswcevI_RdCNmfmCFub3NYp83dEz0K4qf_2Ck2zqxsI9lQ; asst=1727345109.0; gdsid=1727345153575:1727348351309:C756B8677D2C45E0593BBC9F55D38778',
            'gd-csrf-token': 'XNd2BlqnMQmgivmz77fo2Q:C0O85q7PC6Ic7cJA7NF4OdCLhfnc3EjG3QmQsWcpBsqC0nQZAqoJ6k69grjFZ9QnpJu_d8L6Z82QKmMJ-G5BJw:SHsB8HHz0V9feTqGChcq27ObCzTkMvRmi65s_vJFrb8',
            'origin': 'https://www.glassdoor.com.au',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://www.glassdoor.com.au/',
            'sec-ch-ua': '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
            'x-gd-job-page': 'serp'
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

    def checkEmpty(self, str):
        if str is None:
            return True
        if str == '':
            return True
        if str == ' ':
            return True
        return False

    def strReturnNotNone(self, str):
        if str is None:
            return "null"
        return str

    def salary(self, salary_str1, salary_str2):
        # Set the locale to default 'C' locale
        locale.setlocale(locale.LC_ALL, 'C')
        # Format a number as a currency string using defined function
        if self.checkEmpty(salary_str1):
            salary_str1 = 0
        if self.checkEmpty(salary_str2):
            salary_str2 = 0

        GFG1 = '${:,.2f}'.format(float(salary_str1))
        GFG2 = '${:,.2f}'.format(float(salary_str2))
        if GFG1 >= GFG2:
            return GFG1
        else:
            return GFG1 + " - " + GFG2

    def reValidString(self, value):
        # print value
        if value is not None:
            value = value.replace('[', '').replace(']', '')
            value = value.replace("'", "")
            value = value.replace('-', ' ')
        return value

    def createRow(self,json_data):
        job_data = json_data['data']['jobview']['job']
        job_header = json_data['data']['jobview']['header']
        jobType = self.safeGet(job_header, 'jobType', default="")
        jobTypeTemp = jobType
        if jobType is array:
            jobTypeTemp = self.reValidString(', '.join(jobType))
        else:
            jobTypeTemp = self.reValidString(str(jobType))
        salary1 = self.safeGet(job_header, 'payPeriodAdjustedPay', 'p10', default="")
        salary2 = self.safeGet(job_header, 'payPeriodAdjustedPay', 'p90', default="")
        job_df = pd.DataFrame([{
            'title': self.strReturnNotNone(self.safeGet(job_data, 'jobTitleText', default="")),
            'company_name': self.strReturnNotNone(self.safeGet(job_header, 'employerNameFromSearch', default="")),
            'company_location': self.strReturnNotNone(self.safeGet(job_header, 'locationName', default="")),
            'department': self.strReturnNotNone(self.safeGet(job_data, 'classifications', 0, 'label', default="")),
            'job_type': self.strReturnNotNone(jobTypeTemp),
            'salary_range': self.strReturnNotNone(self.salary(salary1, salary2)),
            'email': "null",
            'phone': "null",
            'ads_link': self.strReturnNotNone(self.safeGet(job_header, 'seoJobLink', default="")),
            'ads_posted_date': self.strReturnNotNone(datetime.fromisoformat(self.safeGet(job_data, 'discoverDate', default="2024-09-24T07:33:02.261Z").replace('Z', '+00:00')).strftime('%Y-%m-%d')),
            'raw_text': self.strReturnNotNone(self.cleanText(self.safeGet(job_data, 'description', default="")))
        }])
        return job_df

    def addJobId(self, jodIds, page):
        jobListings = page[0]['data']['jobListings']
        if jobListings is not None:
             # has job add jobID
            listJobViews = page[0]['data']['jobListings']['jobListings']
            for jobView in listJobViews:
                jobId = jobView['jobview']['job']['listingId']
                # print(jobId)
                if jobId not in jodIds:
                    jodIds.append(jobId)
                else:
                    print(f"job id in list : {jobId}")

    def main(self):
        # list_data = Scaping().getDetail()
        # print(' '.join([]))
        list_input_datas = [
            {
                "originalPageUrl":"https://www.glassdoor.com.au/Job/australia-cpa-jobs-SRCH_IL.0,9_IN16_KO10,13.htm",
                "seoFriendlyUrlInput":"australia-cpa-jobs",
                "keyword":"cpa"
            },
            {
                "originalPageUrl": "https://www.glassdoor.com.au/Job/australia-accountant-jobs-SRCH_IL.0,9_IN16_KO10,20.htm",
                "seoFriendlyUrlInput": "australia-accountant-jobs",
                "keyword": "accountant"
            },
            {
                "originalPageUrl": "https://www.glassdoor.com.au/Job/australia-accounting-firm-jobs-SRCH_IL.0,9_IN16_KO10,25.htm",
                "seoFriendlyUrlInput": "australia-accounting-firm-jobs",
                "keyword": "accounting firm"
            }
        ]
        listJobViews=[]
        jodIds = []

        all_jobs_df = pd.DataFrame()
        for data in list_input_datas: # paging next
            pageNumber = 1
            print("Page Number : " + str(pageNumber))
            # get page 1
            page = self.getListJobs(data["keyword"], data["originalPageUrl"], data["seoFriendlyUrlInput"])
            # add job ids for page 1
            self.addJobId(jodIds, page)
            # get paging number and cursor (con tro page)
            paginationCursors = page[0]['data']['jobListings']['paginationCursors']
            for PaginationCursor in paginationCursors:
                # print(PaginationCursor)
                pageNumber += 1
                print("Page Number : " + str(pageNumber))
                # get page 1
                page = self.getListJobs(data["keyword"], data["originalPageUrl"], data["seoFriendlyUrlInput"],PaginationCursor["pageNumber"],PaginationCursor["cursor"])
                # add job ids for page 1
                self.addJobId(jodIds, page)

        print (len(jodIds))
        current_time = datetime.now()
        # create new sheet or clear if sheet is existed
        sheet_name = "GlassdoorJobListing_" + current_time.strftime('%d-%m-%y')
        sheet_seek = os.environ.get(f'sheet_glassdoor')
        print(len(all_jobs_df))
        worksheet = open_worksheet(sheet_name, sheet_seek)

        for idJob in jodIds[:]:
            print (idJob)
            detail = self.getDetail(idJob)
            # print(detail)
            dataDetail = detail[0]
            if 'data' in dataDetail:
                job_df = self.createRow(dataDetail)
                print("=======================")
                print(job_df)
                all_jobs_df = pd.concat([all_jobs_df, job_df], ignore_index=True)
                # sleep(4)
                write_data_to_sheet(all_jobs_df,worksheet=worksheet)


        # test_df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
        # write_dataframe_to_sheet(test_df, 'GlassdoorJobListing', '1CTWgP_59_HHDEOOEyJuEHyQCcrBWw95QraUptvePtk0')




if __name__ == "__main__":
    Scaping().main()
    # list_data = Scaping().getListJobs()
    # print(list_data)
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