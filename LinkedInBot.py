import time
import configparser
import json
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd

#Resume Path here
resume = "Resume Path"
# "https://www.linkedin.com/jobs/search/?geoId=103644278&keywords=software%20engineer%20entry%20level"
# "https://www.linkedin.com/jobs/search/?geoId=103644278&keywords=software%20engineer%20entry%20level&start=25"
# "https://www.linkedin.com/jobs/search/?geoId=103644278&keywords=software%20engineer%20entry%20level&start=50"


class LinkedInBot:
    def __init__(self, username, password):
        self.driver = webdriver.Chrome("Driver\chromedriver.exe")
        self.base_url = ('https://www.linkedin.com/')
        self.login_url = self.base_url + '/login'
        self.username = username
        self.password = password

    def _nav(self, url):
        self.driver.get(url)
        time.sleep(3)

    def Login(self,username,password):
        print("Now Logging in..")
        self._nav(self.login_url)
        self.driver.find_element_by_id('username').send_keys(username)
        self.driver.find_element_by_id('password').send_keys(password)
        self.driver.find_element_by_xpath("//button[contains(text(), 'Sign in')]").click()

    def Search(self, job):
        print("Searching for job, location, and position level..")
        job_search = self.driver.find_element_by_class_name('search-global-typeahead__input')
        job_search.click()
        job_search.send_keys(job)
        job_search.send_keys(Keys.ENTER)

        time.sleep(3)

        job_search_button = self.driver.find_element_by_link_text('See all job results')
        job_search_button.click()
    
    def Filter(self):
        print("Applying Filters..")
        time.sleep(2)
        job_filter = self.driver.find_element_by_xpath("/html/body/div[7]/div[3]/div[3]/section/div/div/div/div[2]/button")
        job_filter.click()

        job_filter = self.driver.find_element_by_xpath("/html/body/div[4]/div/div/div[2]/ul/li[7]/div/ul/li[1]/label")
        job_filter.click()

        job_filter = self.driver.find_element_by_xpath("/html/body/div[4]/div/div/div[3]/div/button[2]")
        time.sleep(2) 
        job_filter.click()

    def Find_Jobs(self):
        print("Searching..")
        time.sleep(1)
        results = self.driver.find_element_by_class_name("display-flex.t-12.t-black--light.t-normal")
        results_int = int(results.text.split(' ',1)[0].replace(",",""))
        print(results_int)

        time.sleep(2)
        current_page = self.driver.current_url
        new_results = self.driver.find_elements_by_class_name("jobs-search-results__list-item.occludable-update.p0.relative.ember-view")

        for result in new_results:
            hover = ActionChains(self.driver).move_to_element(result)
            hover.perform()
            titles = result.find_elements_by_class_name("disabled.ember-view.job-card-container__link.job-card-list__title")
            for title in titles:
                self.Submit_Application(title)
            
            #number of page check
            if results_int > 24:
                time.sleep(2)
                find_pages = self.driver.find_elements_by_class_name("artdeco-pagination__indicator.artdeco-pagination__indicator--number.ember-view")
                total_pages = find_pages[len(find_pages) - 1].text
                total_pages_int = int(re.sub(r"[^\d.]", "", total_pages))
                
                get_last_page = self.driver.find_element_by_xpath("//button[@aria-label='Page "+str(total_pages_int)+"']")
                get_last_page.send_keys(Keys.RETURN)
                time.sleep(1)
                last_page = self.driver.current_url
                total_jobs = int(last_page.split('start=',1)[1])

                for page_number in range(25,total_jobs+25,25):
                    self.driver.get(current_page+"&start="+str(page_number))
                    time.sleep(1)
                    results_ext = self.driver.find_elements_by_class_name("jobs-search-results__list-item.occludable-update.p0.relative.ember-view")
                    for result in results_ext:
                        hover = ActionChains(self.driver).move_to_element(result)
                        hover.perform()
                        titles_ext = result.find_elements_by_class_name("disabled.ember-view.job-card-container__link.job-card-list__title")
                        for title_ext in titles_ext:
                            self.Submit_Application(title_ext)
                else:
                    self.close_session()

    
    def Submit_Application(self, job_offer):
            Jobs = []
            print("Currently applying to", job_offer.text)
            job_offer.click()
            time.sleep(2)

            #Click on Easy Apply(Submit Only)
            try:
                easy_apply = self.driver.find_element_by_xpath("/html/body/div[7]/div[3]/div[3]/div/div/section[2]/div/div/div[1]/div/div[1]/div/div/div[2]/div[2]/div[1]/div[1]/div/button")
                easy_apply.click()
            except NoSuchElementException:
                print('Job already Applied to. Continuing onto next Job..')
                pass
            time.sleep(1)

            try:
                time.sleep(2)
                job_title = job_offer.text
                job_items = {
                    'Title' : job_title
                }
                Jobs.append(job_items)
                df = pd.DataFrame(Jobs)
                submit = self.driver.find_element_by_xpath("/html/body/div[4]/div/div/div[2]/div/form/footer/div[3]/button")
                # phone_enter = self.driver.find_element_by_xpath("/html/body/div[4]/div/div/div[2]/div/form/div/div[1]/div[3]/div[2]/div/div/input")
                # resume_form = self.driver.find_element_by_xpath("/html/body/div[4]/div/div/div[2]/div/form/div/div[2]/div/div/div[2]/label").click()
                time.sleep(2)
                # phone_enter.clear()
                # phone_enter.send_keys(phone)
                # time.sleep(2)
                # resume_form.send_keys(resume)
                # time.sleep(10)
                submit.click()
                time.sleep(2)
                xpath = "/html/body/div[4]/div/div/button";
                confirm_and_exit = self.driver.find_element_by_xpath(xpath).send_keys(Keys.ENTER)
                confirm_and_exit = self.driver.find_element_by_xpath(xpath).send_keys(Keys.ENTER)
                time.sleep(2)
                confirm_and_exit.send_keys(Keys.ENTER)            
                print(df)

            except NoSuchElementException:
                print("Too many steps, moving on to next job..")
                time.sleep(2)
                try:
                    exit = self.driver.find_element_by_xpath("/html/body/div[4]/div/div/button")
                    exit.send_keys(Keys.ENTER)
                    time.sleep(2)
                    exit_confirm = self.driver.find_element_by_xpath("/html/body/div[4]/div[2]/div/div[3]/button[2]").send_keys(Keys.ENTER)
                    time.sleep(1)
                except NoSuchElementException:
                    pass
                    
    def CloseOut(self):
        print("Job Search and Apply Complete")
        self.driver.close()


if __name__ == '__main__':

    config=configparser.ConfigParser()
    config.read('Config\Config.ini')

    username = config['CREDS']['USERNAME']
    password = config['CREDS']['PASSWORD']
    job = config['CREDS']['JOB-LOC-EXPLVL']
    # phone = config['CREDS']['PHONE']


    bot = LinkedInBot(username, password)
    bot.Login(username, password)
    bot.Search(job)
    bot.Filter()
    bot.Find_Jobs()
    bot.Submit_Application()
    bot.CloseOut()
    # bot.Apply()