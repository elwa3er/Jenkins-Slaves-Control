import jenkins
from datetime import datetime,timedelta
import pandas as pd
import time
import requests
from requests.auth import HTTPBasicAuth
import json
import os,sys
from texttable import Texttable
import argparse

def getDuration(job,build):
    response = requests.get("http://192.168.20.208/blue/rest/organizations/jenkins/pipelines/"+job+"/runs/"+str(build)+"/steps/",auth=HTTPBasicAuth('qqtechInfra', 'Technica11'))
    rep = json.loads(response.content)
    duration=0
    for r in rep:
        duration += float(int(r["durationInMillis"]) / 1000)
    return duration
def getBuilds(job):
    response = requests.get("http://192.168.20.208/job/" + str(job) + "/api/json/",auth=HTTPBasicAuth('qqtechInfra', 'Technica11'))
    rep = json.loads(response.content)
    builds=[]
    for r in rep["builds"]:
        builds.append(r["number"])
    # duration = time.strftime('%H:%M:%S', time.gmtime(duration))
    return builds

def checkDateRange(s,e,job):
    response = requests.get("http://192.168.20.208/job/"+str(job)+"/api/json?tree=builds[id,timestamp,result,duration]",auth=HTTPBasicAuth('qqtechInfra', 'Technica11'))
    rep = json.loads(response.content)
    date = 0
    build_ids = []
    build_date=[]
    if "builds" in rep:
        for r in rep["builds"]:
            date = float(int(r["timestamp"]) / 1000)
            date = datetime.utcfromtimestamp(date)
            if datetime.strptime(date.strftime("%Y-%m-%d"), "%Y-%m-%d") >= s and datetime.strptime(date.strftime("%Y-%m-%d"), "%Y-%m-%d")<=e:
                build_ids.append(int(r["id"]))
                build_date.append(datetime.strptime(date.strftime("%Y-%m-%d"), "%Y-%m-%d"))
    return build_ids,build_date

def compute(start_date,end_date,blist):
    bts_list=[]
    for i in blist[0].split(" "):
        bts_list.append(i)
    bts_desc=[]
    for b in bts_list:
        response = requests.get("http://192.168.20.208/computer/Athens/api/json?pretty=true",auth=HTTPBasicAuth('qqtechInfra', 'Technica11'))
        rep = json.loads(response.content)
        bts_desc.append(rep["description"])

    filters=['run']
    total_time=[]
    for b in bts_list:
        total_time.append(0)
    server = jenkins.Jenkins("http://192.168.20.208/", username="qqtechInfra", password="Technica11")
    Jobs=server.get_all_jobs()
    All_Jobs=Jobs
    print("Number of jobs on 208 to be parsed is  "+str(len(All_Jobs))+" among "+str(server.jobs_count()))
    i=0
    to_Excel=[]
    All_Jobs=All_Jobs[189:191]

    for job in All_Jobs:
        i+=1
        lb=[]
        ld=[]
        try:

            try:
                lb,ld=checkDateRange(start_date,end_date,str(job["fullname"]))
            except:
                lb, ld = checkDateRange(start_date, end_date, str(job["name"]))
            if len(lb)>0:
                print("Job number " + str(i) + " : " + job["name"])
                #if build_date >= start_date:
                b=0
                for build in lb:
                    to_ex=[]
                    bts=""
                    b+=1
                    try:
                        #infos = dict(server.get_build_info(job["fullname"], build["number"]))
                        #infos = dict(server.get_build_info(job["fullname"], build))
                        '''timestamp = infos['timestamp']
                        timestamp = timestamp / 1000  # The timestamp returned by Jenkins api is in miliseconds
                        build_date = datetime.utcfromtimestamp(timestamp)'''
                        #if build_date >= start_date and build_date <= end_date:
                        y = server.get_build_console_output(job["fullname"], build)
                        x = y.split("\n")
                        matching = [s for s in x if "Running on" in s]
                        matching1 = [s for s in x if "Building remotely on" in s]
                        if len(matching)>0 or len(matching1)>0:
                            if len(matching)>0 and matching[0]!="":
                                bts = matching[0].split(" ")[2]
                            else:
                                bts = matching1[0].split(" ")[3]
                            if bts in bts_list:
                                duration=getDuration(job["fullname"],build)
                                vb=float(total_time.__getitem__(bts_list.index(bts)))+ duration
                                desc=bts_desc.__getitem__(bts_list.index(bts))

                                total_time.__setitem__(bts_list.index(bts),vb)

                                to_ex.append(bts)
                                to_ex.append(desc)
                                to_ex.append(str(job["name"]))
                                to_ex.append(build)
                                to_ex.append(datetime.strftime(ld.__getitem__(b-1),"%Y-%m-%d"))
                                to_ex.append(duration)
                                to_Excel.append(to_ex)

                    except Exception as e:
                        continue
        except Exception as ee:
            continue
    tb = Texttable()
    tbbt=[["BTS","ELAPSED TIME"]]
    for i in bts_list:
        ind=bts_list.index(i)
        tt=total_time.__getitem__(ind)
        tbbt.append([str(i),timedelta(seconds=tt)])

    tb.add_rows(tbbt)
    print(tb.draw())
    if len(to_Excel)>0:
        df=pd.DataFrame(to_Excel,columns=["BTS Name","BTS Description","Job Name","Build N°","Date","Duration"],  index=False)
        print(df)
        df.to_excel('BTS_Trend.xlsx',sheet_name="BTS_Trend_"+str(start_date)+"_"+str(end_date))

    return "ok"
def previous_week_range(date):
    start_date = date + timedelta(-date.weekday(), weeks=-1)
    end_date = date + timedelta(-date.weekday() - 1)
    return start_date, end_date

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    #parser.add_argument('--bts',type=list)
    parser.add_argument('--bts', nargs='+')
    parser.add_argument('--sdate')
    parser.add_argument('--endDate')
    s=parser.parse_args()._get_kwargs()[2][1]
    e=parser.parse_args()._get_kwargs()[1][1]
    b=parser.parse_args()._get_kwargs()[0][1]
    s=datetime.strptime(s,'%Y-%m-%d')
    e=datetime.strptime(e,'%Y-%m-%d')
    compute(s,e,b)
