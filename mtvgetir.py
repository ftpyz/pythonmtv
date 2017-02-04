# -*- coding:utf-8 -*-
import os,sys,decimal,django

from pyquery import PyQuery as pq
import unirest
from backend.models import *

class MtvGetir(object):
   def __init__(self,plaka,tescil,vergino):
       self.plaka=plaka
       self.tescil=tescil
       self.vergino=vergino
       self.url="https://intvd.gib.gov.tr/internetvd/dispatch2"

   def getGibData(self):
       self.response=unirest.post(self.url,
                        headers={
                                      "Accept": "*/*",
                                      "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                                      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36",
                                      "X-Requested-With": "XMLHttpRequest"
                        },
                        params={
                            "cmd":"IVD_MOTOP_DETAY_CARI",
                            "plaka": self.plaka,
                            "ozelPlaka": "0",
                            "vkno":self.vergino,
                            "tescilTarihiGun": '%02d' % self.tescil.day,
                            "tescilTarihiAy": '%02d' % self.tescil.month,
                            "tescilTarihiYil":self.tescil.year,
                            "LANG":"tr",
                            "tckno":"",
                            "TOKEN":" ",
                        }
                    )
       return self.response

   def getMTV(self):
       self.getGibData()
       if self.response.code == 200 and self.response.raw_body.find("SERVERERROR") == -1:
           data=pq(self.response.raw_body)
           plaka = data(".bigform_container table").eq(1).find("tr").eq(1).find("td").eq(1).text()
           if plaka==self.plaka:
               #plaka kontrolu yapılyor
               donem = data("#formMTV .gradient_table tr").eq(2).find("td").eq(3).text()
               if self.response.raw_body.find("Cari Döneme Ait Motorlu Taşıtlar Vergisi Borcunuz Bulunmamaktadır.") == -1:
                   #mtv varsa
                   try:
                       gecikme = float(data("#formMTV .gradient_table tr").eq(2).find("td").eq(7).text().replace(".","").replace(",","."))
                       tutar = float(data("#formMTV .gradient_table tr").eq(2).find("td").eq(8).text().replace(".","").replace(",","."))
                       return {"plaka":plaka,"donem":donem,"tutar":tutar,"gecikme":gecikme}
                   except:
                       return False
               else:
                   #mtv yoksa
                   return {"plaka": plaka, "donem": donem, "tutar": float(0.0), "gecikme": float(0.0)}
           else:
               return False
       else:
           raise Exception(u"Arac bulunamadi")
#a=MtvGetir("plaka",datetime.datetime(year=2015,day=20,month=8),"vergino").getMTV() #mtv yok
