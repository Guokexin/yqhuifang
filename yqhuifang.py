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

no_use_word = ['额','呃','厄','噢','哦','吾']

chat_word = {'吃饭了吗':'还没呢','饿了吗':'不饿'}

#neg_word = ['不是','不对','没有啊','错','没有',"没去过","不在","回老家"]

#q1_sure = ['是的','是','在深圳','对','对的','没错']
#q1_neg = ['不在','在老家','回老家','旅游','出去了','在外地','不是']

#请问是xxx同事吗,您可以回答是或者不是？
q0_sure =['我就是','对','没错','是的','不错','是我','你说','好','是啊','就是我','我啊怎么了','怎么啦','是','嗯']  
q0_neg =['我是他','我是她','他去','不是','不对','错了','打错','不认识','她走了','他走了','他出去了','她出去了','晚点','不方便','在忙','还没回来','刚走开','刚离开','他现在没空']

#请问您春节期间是在深圳吗？
q1_sure =['是的','是','在深圳','对','对的','没错','一直在深圳','是啊','在啊','肯定']
q1_neg =['不是','不在','旅游','回老家','在老家','出差','在外地','在外面','出去了','没在','去过','去了']

#请问您近期有去过湖北吗？
q2_sure =['去了','去过','有呀','有啊','有','是的','没错','对','在湖北人家里','我在湖北']
q2_neg =['没有','最近没有','现在没有','没','没呀','没啊','不可能','不会','怎么可能','没空去']

#请问您近期有湖北的亲友来访或者接触过湖北过来的人员吗？
q3_sure =['有几个','有一个','有呀','有啊','我亲戚','接触过','最近有','有','好像有']
q3_neg =['没有','没接触过','不认识湖北的','肯定没','朋友','亲戚','邻居']

#请问您最近是否有出现咳嗽、发烧、流鼻涕、头痛乏力、腹泻等症状呢？请回答有或没有
q4_sure =['去了','去过','有呀','有啊','有','去医院','痛','不舒服','有点','全中','全有','咳嗽了','发烧了','腹泻了','头痛了','乏力了','流鼻涕了','拉肚子了','出现发烧']
q4_neg =['没有','健康这呢','没毛病','身体很好','没事','没出现过','肯定没','怎么可能','身体很健康','没生病']


apologies_word = '非常抱歉，打扰了'

answers = {}

original_words = {}

no_stati = [ '不满意','不太满意','非常不满意','太差了','差评','投诉']
soso_stati = ['一般','还行','差不多']
stati = ['满意','非常好','很棒','点赞']

remove_word = ['我想','那个','嗯','哈哈','这个','咨询','一下','呃','吧','哎']

title = ''
mydb = db.DBInfo()
class Request(MyAgi):

    def remove_dirty_word(self, asr_txt):
      for i in remove_word:
        asr_txt = asr_txt.replace(i, '')
      return asr_txt

    @with_goto
    def call_obs(self):
      """ call obs"""
      #step1 check identity
      repeat_num = 0
      voiceTxt = ''
      project_id = 2;
 
      user_name = self.getChannelVariables(["name"])[0]
      phone_no = self.getChannelVariables(['phoneno'])[0]

      #first check id      
      while True:
        #voiceTxt = "您好，这边是深圳电信方案中心工作人员，请问是%s同事吗？您可以回答是或者不是？" % (user_name)
        file = ["/usr/local/soundsStatic/yq_welcome"]
        self.playHints(file)
        voiceTxt = user_name + "同事吗"

        if repeat_num == 0:
          self.SynthAndRecog(voiceTxt);
        elif repeat_num == 1:
          self.PlayRecogVoice("/usr/local/soundsStatic/again")
        elif repeat_num == 2:
          self.PlayRecogVoice("/usr/local/soundsStatic/yesno")

        status = self.getChannelVariables(["RECOG_COMPLETION_CAUSE"])[0]
        asr_txt = self.getChannelVariables(["RECOG_RESULT"])[0]
        asr_txt = self.remove_dirty_word(asr_txt) 
        self.logInfo("SynthAndRecog recog status is %s " % status)

        if (any(name in asr_txt for name in q0_neg)): 
          self.SynthText("非常抱歉，打扰了")
          original_words['请问是xxx同事吗？您可以回答是或者不是？'] = asr_txt;
          answers['请问是xxx同事吗？您可以回答是或者不是？'] = 'B'
          goto .hangup
        elif any(name in asr_txt for name in q0_sure):
          original_words['请问是xxx同事吗？您可以回答是或者不是？'] = asr_txt;
          answers['请问是xxx同事吗？您可以回答是或者不是？'] = 'A'
          break;
        else:
          repeat_num = repeat_num + 1
          if repeat_num == 3:
            original_words['请问是xxx同事吗？您可以回答是或者不是？'] = asr_txt;
            answers['请问是xxx同事吗？您可以回答是或者不是？'] = 'C'
            goto .hangup
            break;
            
          #if repeat_num == 1:
          #  self.PlayRecogVoice("/usr/local/soundsStatic/yesno")
          #if repeat_num == 2:
          #  self.PlayRecogVoice("/usr/local/soundsStatic/tongshi")
          #  self.PlayRecogVoice("/usr/local/soundsStatic/yesno")
          continue
          
      
      #self.SynthText("本次电信对近期新型肺炎疫情做简要回访")        
          
      repeat_num = 0 
      #event check
      while True:
        #voiceTxt = '请问您春节期间是在深圳吗？您可以回答是或者不是？'
        #self.SynthAndRecog(voiceTxt); #
        if repeat_num == 0:
          self.PlayRecogVoice("/usr/local/soundsStatic/cjsz_q1")
        elif repeat_num == 1:
          self.PlayRecogVoice("/usr/local/soundsStatic/again")
        elif repeat_num == 2:
          self.PlayRecogVoice("/usr/local/soundsStatic/yesno")

        status = self.getChannelVariables(["RECOG_COMPLETION_CAUSE"])[0]
        asr_txt = self.getChannelVariables(["RECOG_RESULT"])[0]
        asr_txt = self.remove_dirty_word(asr_txt) 
        self.logInfo("SynthAndRecog recog status is %s " % status)
        if any(name in asr_txt for name in q1_neg):
          answers['请问您春节期间是在深圳吗？您可以回答是或者不是？'] = 'B'
          original_words['请问您春节期间是在深圳吗？您可以回答是或者不是？'] = asr_txt;
          break
        elif any(name in asr_txt for name in q1_sure):
          answers['请问您春节期间是在深圳吗？您可以回答是或者不是？'] = 'A'
          original_words['请问您春节期间是在深圳吗？您可以回答是或者不是？'] = asr_txt;
          break
        else:
          repeat_num = repeat_num + 1
          if repeat_num == 3:
            original_words['请问您春节期间是在深圳吗？您可以回答是或者不是？'] = asr_txt;
            answers['请问您春节期间是在深圳吗？您可以回答是或者不是？'] = 'C'
            break;
          continue

      repeat_num = 0 
      while True:
        #voiceTxt = '请问您近期有去过湖北吗？您可以回答有或者没有？'
        #self.SynthAndRecog(voiceTxt);

        if repeat_num == 0:
          self.PlayRecogVoice("/usr/local/soundsStatic/hb_q2")
        elif repeat_num == 1:
          self.PlayRecogVoice("/usr/local/soundsStatic/again")
        elif repeat_num == 2:
          self.PlayRecogVoice("/usr/local/soundsStatic/haveno")

  
        status = self.getChannelVariables(["RECOG_COMPLETION_CAUSE"])[0]
        asr_txt = self.getChannelVariables(["RECOG_RESULT"])[0]
        asr_txt = self.remove_dirty_word(asr_txt) 
        self.logInfo("SynthAndRecog recog status is %s " % status)
        
        #否定回答
        if any(name in asr_txt for name in q2_neg):
          answers['请问您近期有去过湖北吗？您可以回答有或者没有？'] = 'B'
          original_words['请问您近期有去过湖北吗？您可以回答有或者没有？'] = asr_txt;
          break
        #肯定回答
        elif any(name in asr_txt for name in q2_sure):
          answers['请问您近期有去过湖北吗？您可以回答有或者没有？'] = 'A'
          original_words['请问您近期有去过湖北吗？您可以回答有或者没有？'] = asr_txt;
          break
        else:
          repeat_num = repeat_num + 1
          if repeat_num == 3:
            original_words['请问您近期有去过湖北吗？您可以回答有或者没有？'] = asr_txt;
            answers['请问您近期有去过湖北吗？您可以回答有或者没有？'] = 'C'
            break;
          continue

      repeat_num = 0 
      while True:
        #voiceTxt = '请问您近期有湖北的亲友来访或者接触过湖北过来的人员吗？您可以回答有或者没有？'
        #self.SynthAndRecog(voiceTxt);
        if repeat_num == 0:
          self.PlayRecogVoice("/usr/local/soundsStatic/hb_friend_q3")
        elif repeat_num == 1:
          self.PlayRecogVoice("/usr/local/soundsStatic/again")
        elif repeat_num == 2:
          self.PlayRecogVoice("/usr/local/soundsStatic/haveno")


        status = self.getChannelVariables(["RECOG_COMPLETION_CAUSE"])[0]
        asr_txt = self.getChannelVariables(["RECOG_RESULT"])[0]
        asr_txt = self.remove_dirty_word(asr_txt) 
        self.logInfo("SynthAndRecog recog status is %s " % status)
          
        #否定回答
        if any(name in asr_txt for name in q3_neg):
          answers['请问您近期有湖北的亲友来访或者接触过湖北过来的人员吗？您可以回答有或者没有？'] = 'B'
          original_words['请问您近期有湖北的亲友来访或者接触过湖北过来的人员吗？您可以回答有或者没有？'] = asr_txt;
          break
        #肯定回答
        elif any(name in asr_txt for name in q3_sure):
          answers['请问您近期有湖北的亲友来访或者接触过湖北过来的人员吗？您可以回答有或者没有？'] = 'A'
          original_words['请问您近期有湖北的亲友来访或者接触过湖北过来的人员吗？您可以回答有或者没有？'] = asr_txt;
          break
          
        else:
          repeat_num = repeat_num + 1
          if repeat_num == 3:
            original_words['请问您近期有湖北的亲友来访或者接触过湖北过来的人员吗？您可以回答有或者没有？'] = asr_txt;
            answers['请问您近期有湖北的亲友来访或者接触过湖北过来的人员吗？您可以回答有或者没有？'] = 'C'
            break;
            
          file = ["/usr/local/soundsStatic/again"]
          self.playHints(file) 
          if repeat_num == 1:
            self.PlayRecogVoice("/usr/local/soundsStatic/haveno")
            
          if repeat_num == 2:
            self.PlayRecogVoice("/usr/local/soundsStatic/hb_friend_q3")
            self.PlayRecogVoice("/usr/local/soundsStatic/haveno")
          continue
         
      repeat_num = 0 
      while True:
        voiceTxt = '请问您最近是否有出现咳嗽、发烧、流鼻涕、头痛乏力、腹泻等症状呢？请回答有或没有'
        #self.SynthAndRecog(voiceTxt);
        if repeat_num == 0:
          self.PlayRecogVoice("/usr/local/soundsStatic/health_q4")
        elif repeat_num == 1:
          self.PlayRecogVoice("/usr/local/soundsStatic/again")
        elif repeat_num == 2:
          self.PlayRecogVoice("/usr/local/soundsStatic/haveno")



        status = self.getChannelVariables(["RECOG_COMPLETION_CAUSE"])[0]
        asr_txt = self.getChannelVariables(["RECOG_RESULT"])[0]
        asr_txt = self.remove_dirty_word(asr_txt) 
        self.logInfo("SynthAndRecog recog status is %s " % status)

        #否定回答
        if any(name in asr_txt for name in q4_neg):
          answers['请问您最近是否有出现咳嗽、发烧、流鼻涕、头痛乏力、腹泻等症状呢？请回答有或没有'] = 'B'
          original_words['请问您最近是否有出现咳嗽、发烧、流鼻涕、头痛乏力、腹泻等症状呢？请回答有或没有'] = asr_txt;
          break
        #肯定回答
        elif any(name in asr_txt for name in q4_sure):
          answers['请问您最近是否有出现咳嗽、发烧、流鼻涕、头痛乏力、腹泻等症状呢？请回答有或没有'] = 'A'
          original_words['请问您最近是否有出现咳嗽、发烧、流鼻涕、头痛乏力、腹泻等症状呢？请回答有或没有'] = asr_txt;
          break
        else:
          repeat_num = repeat_num + 1
          if repeat_num == 3:
            original_words['请问您最近是否有出现咳嗽、发烧、流鼻涕、头痛乏力、腹泻等症状呢？请回答有或没有'] = asr_txt;
            answers['请问您最近是否有出现咳嗽、发烧、流鼻涕、头痛乏力、腹泻等症状呢？请回答有或没有'] = 'C'
            break;
          continue
            
     
      #delete_sql = "DELETE from t_1_answer where project_id = %d AND phone = '%s'" % (project_id, '13828282828')
      #self.logInfo(delete_sql)
      #mydb.writeAnswer(delete_sql)  
      call_time = time.strftime("%Y%m%d%H%M%S", time.localtime())      
      self.logInfo("call_time = %s" % call_time)
      
      file = ["/usr/local/soundsStatic/bye"]
      self.playHints(file)
      
      #此处为挂断电话后的点
      label .hangup  
      
      for k in answers:
        a = answers[k]
        text = original_words[k]
        #topicSec  集智平台 题号变量
        topicSec = 0
        qid = 0
        if k == '请问是xxx同事吗？您可以回答是或者不是？':
          qid = 0
          topicSec = 0
        elif k == '请问您春节期间是在深圳吗？您可以回答是或者不是？':
          qid = 1
          topicSec = 1
        elif k == '请问您近期有去过湖北吗？您可以回答有或者没有？':
          qid = 2
          topicSec = 2
        elif k == '请问您近期有湖北的亲友来访或者接触过湖北过来的人员吗？您可以回答有或者没有？':
          qid = 3
          topicSec = 3
        elif k == '请问您最近是否有出现咳嗽、发烧、流鼻涕、头痛乏力、腹泻等症状呢？请回答有或没有':
          qid = 4
          topicSec = 4
        sql = "insert into t_1_answer (project_id, customer_name, phone, topic_seq, option_key,ORIGINAL_WORDS,CALL_TIME) values (%d, '%s', '%s', %d, '%s', '%s', %d)" % (project_id, user_name, phone_no, topicSec, a, text , time.time() )
        self.logInfo(sql)
        mydb.writeAnswer(sql) 
        
      sql = "UPDATE t_1_customer set status = 'Y' where project_id = %d and phone = %s " % (project_id, phone_no) 
      self.logInfo(sql)
      mydb.writeAnswer(sql)  
    
      sql = "UPDATE t_1_customer set CALL_TIME = CALL_TIME + 1 where project_id = %d and phone = %s " % (project_id, phone_no) 
      self.logInfo(sql)
      mydb.writeAnswer(sql) 

      #self.SynthText("本次回访结束，提醒您近期尽量不要出门，保持室内通风，出门戴好口罩，勤洗手，勤消毒，做好防护工作，祝您和家人身体健康！生活愉快！再见！")

      

if __name__ == "__main__":
  try:
    req = Request()
    req.call_obs()
  except:
    req.logException(sys.exc_info())
