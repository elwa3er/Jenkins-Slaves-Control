import jenkins
import os
import requests
import json
from xml.etree import ElementTree
from lxml import html
from requests_html import HTMLSession


import feedparser
from requests.auth import HTTPBasicAuth
server = jenkins.Jenkins("http://192.168.20.208/", username="kelwaer", password="KELTechnica2020//")
a=server.get_node_info("Athens")
jobs=server.get_jobs()
'''for job in jobs:
    #print(job)
    print("-------------------------------------------------------------------------------------")
    builds=server.get_job_info(job["name"])['builds']
    for build in builds:
        #print(server.get_build_info(job["name"],build['number']))
        try:
            x=dict(server.get_build_env_vars(job["name"],build['number'])['envMap'])
            for env_key in x.keys():
                print(str(env_key)+":"+str(x[env_key]))
        except Exception as e:
            print(e)
            continue
        break
    break'''

builds=server.get_job_info("I020_U006_2107_A260_10_15_XX_TE_run")['builds']
for build in builds:
    #print(server.get_build_info(job["name"],build['number']))
    try:
        x=server.get_build_console_output("I020_U006_2107_A260_10_15_XX_TE_run", build['number'])
        x=x.split("\n")
        matching = [s for s in x if "Running on" in s]
        bts=matching[0].split(" ")[2]
        print("I020_U006_2107_A260_10_15_XX_TE_run",build['number'],bts)

        '''x=dict(server.get_build_env_vars("I020_U006_2107_A260_10_15_XX_TE_run",build['number'])['envMap'])
        for env_key in x.keys():
            print(str(env_key)+":"+str(x[env_key]))'''
    except Exception as e:
        print(e)
        continue


