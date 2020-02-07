#!/usr/bin/env python2
# coding=utf-8
# -*- coding:UTF-8 -*-

import json
import requests;
import sys,os,re,time,random
import urllib,xml.sax
from utility.myAgi import MyAgi,MyAgiException
#import utility.db
import db
import string
import xml.etree.ElementTree as ET
import httplib
import urllib
import urllib2
import time
from urllib import urlencode
from urllib import quote
import hashlib
from hashlib import md5
import re
from goto import with_goto
reload(sys)
sys.setdefaultencoding('utf8')



obs_dict = { '出险的赔款是否已经收到':'O', '赔款的效率是否满意':'O','对本次赔款的服务是否满意':'O'}
#拒绝接收近类
refuse_word = ['没空','没时间','再忙','忙','等会','不行','不方便','打错了','搞错了','有点事'] 
#
repeat_word = ['说什么','没听清','再说','说啥','信号不好','信号太差了']

certain_word = ['我是','对的','对','是的','是','可以','行','OK','没问题','问吧' ,'有']

chat_word = {'吃饭了吗':'还没呢','饿了吗':'不饿'}

neg_word = ['不是','不对','没有啊','错','没有',"没去过","不在","回老家"]

apologies_word = '非常抱歉，打扰了'

answers = {}

original_words = {}

no_stati = [ '不满意','不太满意','非常不满意','太差了','差评','投诉']
soso_stati = ['一般','还行','差不多']
stati = ['满意','非常好','很棒','点赞']

title = ''
mydb = db.DBInfo()
class Request(MyAgi):


    @with_goto
    def call_obs(self):
      """ call obs"""
      #step1 check identity
      repeat_num = 0
      voiceTxt = ''
      project_id = 2;
 
      #first check id      
      while True:
        user_name = self.getChannelVariables(["name"])[0]
	phone_no = self.getChannelVariables(['phoneno'])[0]
        voiceTxt = "您好，这边是深圳电信方案中心工作人员，请问是%s同事吗？" % (user_name)
        #self.SynthText(voiceTxt)
        file = ["/usr/local/soundsStatic/yq_welcome"]
        self.playHints(file)
        voiceTxt = user_name + "同事吗"
        self.SynthAndRecog(voiceTxt);
        #self.SynthText(user_name+"同事吗?")
        #self.PlayRecogVoice("/usr/local/soundsStatic/tongshi")
        #voiceTxt = "%s同事吗?" % user_name
        status = self.getChannelVariables(["RECOG_COMPLETION_CAUSE"])[0]
        asr_txt = self.getChannelVariables(["RECOG_RESULT"])[0]
        
        self.logInfo("SynthAndRecog recog status is %s " % status)
        if (asr_txt.find('不是')>=0):
          self.SynthText("对不起，打扰了。")
          original_words['请问是xxx同事吗？'] = asr_txt;
          answers['请问是xxx同事吗？'] = 'B'
	  goto .hangup
        elif (any(name in asr_txt for name in refuse_word)): 
          self.SynthText("非常抱歉，打扰了")
          original_words['请问是xxx同事吗？'] = asr_txt;
          answers['请问是xxx同事吗？'] = 'B'
	  goto .hangup
        elif any(name in asr_txt for name in certain_word):
          original_words['请问是xxx同事吗？'] = asr_txt;
          answers['请问是xxx同事吗？'] = 'A'
	  # check id pass
          break;
        else:
          voiceTxt = "对不起，请您再说一遍？"
          repeat_num = repeat_num + 1
          if repeat_num >= 2:
            original_words['请问是xxx同事吗？'] = asr_txt;
            answers['请问是xxx同事吗？'] = 'B'
	    goto .hangup
          continue
      
      #self.SynthText("本次电信对近期新型肺炎疫情做简要回访")        
          
      repeat_num = 0 
      #event check
      while True:
        voiceTxt = '请问您春节期间是在深圳吗？'
        #self.SynthAndRecog(voiceTxt); #
        self.PlayRecogVoice("/usr/local/soundsStatic/cjsz_q1")
        status = self.getChannelVariables(["RECOG_COMPLETION_CAUSE"])[0]
        asr_txt = self.getChannelVariables(["RECOG_RESULT"])[0]
        self.logInfo("SynthAndRecog recog status is %s " % status)
        if any(name in asr_txt for name in certain_word):
          answers['请问您春节期间是在深圳吗？'] = 'A'
          original_words['请问您春节期间是在深圳吗？'] = asr_txt;
          break
        elif any(name in asr_txt for name in neg_word):
          answers['请问您春节期间是在深圳吗？'] = 'B'
          original_words['请问您春节期间是在深圳吗？'] = asr_txt;
          break
        else:
          voiceTxt = "对不起，请您再说一遍？"
          repeat_num = repeat_num + 1
          if repeat_num >= 2:
            original_words['请问您春节期间是在深圳吗？'] = asr_txt;
            answers['请问您春节期间是在深圳吗？'] = 'C'
            break;
            #goto .hangup
          continue

      repeat_num = 0 
      while True:
        voiceTxt = '请问您近期有去过湖北吗？'

        self.PlayRecogVoice("/usr/local/soundsStatic/hb_q2")
        #self.SynthAndRecog(voiceTxt);
        status = self.getChannelVariables(["RECOG_COMPLETION_CAUSE"])[0]
        asr_txt = self.getChannelVariables(["RECOG_RESULT"])[0]
        self.logInfo("SynthAndRecog recog status is %s " % status)
        
        #否定回答
        if any(name in asr_txt for name in neg_word):
          answers['请问您近期有去过湖北吗？'] = 'B'
          original_words['请问您近期有去过湖北吗？'] = asr_txt;
          break
        #肯定回答
        elif any(name in asr_txt for name in certain_word):
          answers['请问您近期有去过湖北吗？'] = 'A'
          original_words['请问您近期有去过湖北吗？'] = asr_txt;
          break
        else:
          voiceTxt = "对不起，请您再说一遍？"
          repeat_num = repeat_num + 1
          if repeat_num >= 2:
            original_words['请问您近期有去过湖北吗？'] = asr_txt;
            answers['请问您近期有去过湖北吗？'] = 'C'
            break;
            #goto .hangup
          continue

      repeat_num = 0 
      while True:
        voiceTxt = '请问您近期有湖北的亲友来访或者接触过湖北过来的人员吗？'
        self.PlayRecogVoice("/usr/local/soundsStatic/hb_friend_q3")
        #self.SynthAndRecog(voiceTxt);
        status = self.getChannelVariables(["RECOG_COMPLETION_CAUSE"])[0]
        asr_txt = self.getChannelVariables(["RECOG_RESULT"])[0]
        self.logInfo("SynthAndRecog recog status is %s " % status)
          
        #否定回答
        if any(name in asr_txt for name in neg_word):
          answers['请问您近期有湖北的亲友来访或者接触过湖北过来的人员吗？'] = 'B'
          original_words['请问您近期有湖北的亲友来访或者接触过湖北过来的人员吗？'] = asr_txt;
          break
        #肯定回答
        elif any(name in asr_txt for name in certain_word):
          answers['请问您近期有湖北的亲友来访或者接触过湖北过来的人员吗？'] = 'A'
          original_words['请问您近期有湖北的亲友来访或者接触过湖北过来的人员吗？'] = asr_txt;
          break
          
        else:
          self.SynthText("对不起，请您再说一遍？")
          repeat_num = repeat_num + 1
          if repeat_num >= 2:
            original_words['请问您近期有湖北的亲友来访或者接触过湖北过来的人员吗？'] = asr_txt;
            answers['请问您近期有湖北的亲友来访或者接触过湖北过来的人员吗？'] = 'C'
            break;
            #goto .hangup
          continue
         
      repeat_num = 0 
      while True:
        voiceTxt = '请问您最近是否有出现咳嗽、发烧、流鼻涕、头痛乏力、腹泻等症状呢？请回答有或没有'
        #self.SynthAndRecog(voiceTxt);
        self.PlayRecogVoice("/usr/local/soundsStatic/health_q4")
        status = self.getChannelVariables(["RECOG_COMPLETION_CAUSE"])[0]
        asr_txt = self.getChannelVariables(["RECOG_RESULT"])[0]
        self.logInfo("SynthAndRecog recog status is %s " % status)

        #否定回答
        if any(name in asr_txt for name in neg_word):
          answers['请问您最近是否有出现咳嗽、发烧、流鼻涕、头痛乏力、腹泻等症状呢？请回答有或没有'] = 'B'
          original_words['请问您最近是否有出现咳嗽、发烧、流鼻涕、头痛乏力、腹泻等症状呢？请回答有或没有'] = asr_txt;
          break
        #肯定回答
        elif any(name in asr_txt for name in certain_word):
          answers['请问您最近是否有出现咳嗽、发烧、流鼻涕、头痛乏力、腹泻等症状呢？请回答有或没有'] = 'A'
          original_words['请问您最近是否有出现咳嗽、发烧、流鼻涕、头痛乏力、腹泻等症状呢？请回答有或没有'] = asr_txt;
          break
        else:
          self.SynthText("对不起，请您再说一遍？")
          repeat_num = repeat_num + 1
          if repeat_num >= 2:
            original_words['请问您最近是否有出现咳嗽、发烧、流鼻涕、头痛乏力、腹泻等症状呢？请回答有或没有'] = asr_txt;
            answers['请问您最近是否有出现咳嗽、发烧、流鼻涕、头痛乏力、腹泻等症状呢？请回答有或没有'] = 'C'
            break
            #goto .hangup
          continue 
            
     
      #delete_sql = "DELETE from t_1_answer where project_id = %d AND phone = '%s'" % (project_id, '13828282828')
      #self.logInfo(delete_sql)
      #mydb.writeAnswer(delete_sql)  
      call_time = time.strftime("%Y%m%d%H%M%S", time.localtime())      
      self.logInfo("call_time = %s" % call_time)
      for k in answers:
        a = answers[k]
        text = original_words[k]
        #topicSec  集智平台 题号变量
        topicSec = 0
        qid = 0
	if k == '请问是xxx同事吗？':
	  qid = 0
	  topicSec = 0
	elif k == '请问您春节期间是在深圳吗？':
          qid = 1
          topicSec = 1
        elif k == '请问您近期有去过湖北吗？':
          qid = 2
          topicSec = 2
        elif k == '请问您近期有湖北的亲友来访或者接触过湖北过来的人员吗？':
          qid = 3
          topicSec = 3
        elif k == '请问您最近是否有出现咳嗽、发烧、流鼻涕、头痛乏力、腹泻等症状呢？请回答有或没有':
          qid = 4
          topicSec = 4
        sql = "insert into t_1_answer (project_id, customer_name, phone, topic_seq, option_key,ORIGINAL_WORDS,CALL_TIME) values (%d, '%s', '%s', %d, '%s', '%s', %d)" % (project_id, user_name, phone_no, topicSec, a, text , time.time() )
        self.logInfo(sql)
	mydb.writeAnswer(sql) 

      file = ["/usr/local/soundsStatic/bye"]
      self.playHints(file)
 
      #self.SynthText("本次回访结束，提醒您近期尽量不要出门，保持室内通风，出门戴好口罩，勤洗手，勤消毒，做好防护工作，祝您和家人身体健康！生活愉快！再见！")

      label .hangup  

if __name__ == "__main__":
  try:
    req = Request()
    req.call_obs()
  except:
    req.logException(sys.exc_info())
