from collections import defaultdict
from zlapp.zlshenpi.all import *

def choose_func_zlshenpi(quyu):
   roads={
       "zlshenpi_anhuisheng":ext_anhuisheng,
       "zlshenpi_beijingshi":ext_beijingshi,
       "zlshenpi_fujiansheng":ext_fujiansheng,
       "zlshenpi_gansusheng":ext_gansusheng,
       "zlshenpi_guangdongsheng":ext_guangdongsheng,
       "zlshenpi_hebeisheng":ext_hebeisheng,
       "zlshenpi_heilongjiangsheng":ext_heilongjiangsheng,
       "zlshenpi_henansheng":ext_henansheng,
       "zlshenpi_hubeisheng":ext_hubeisheng,
       "zlshenpi_hunansheng":ext_hunansheng,
       "zlshenpi_jiangxisheng":ext_jiangxisheng,
       "zlshenpi_jilinsheng":ext_jilinsheng,
       "zlshenpi_neimenggusheng":ext_neimenggusheng,
       "zlshenpi_ningxiasheng":ext_ningxiasheng,
       "zlshenpi_qinghaisheng":ext_qinghaisheng,
       "zlshenpi_shanxisheng":ext_shanxisheng,
       "zlshenpi_shanxisheng1":ext_shanxisheng1,
       "zlshenpi_sichuansheng":ext_sichuansheng,
       "zlshenpi_xiamenshi":ext_xiamenshi,
       "zlshenpi_xinjiangsheng":ext_xinjiangsheng,
       "zlshenpi_yunnansheng":ext_yunnansheng,
       "zlshenpi_zhejiangsheng":ext_zhejiangsheng,
       }
   a=defaultdict(lambda :None)
   a.update(roads)
   return a[quyu]