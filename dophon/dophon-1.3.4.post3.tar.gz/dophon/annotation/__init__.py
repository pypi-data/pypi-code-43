# coding: utf-8
from dophon.annotation import AutoWired
from dophon.annotation import response, request
from dophon.annotation.AutoWired import *
from dophon.annotation.description import *
from dophon.annotation.request import BaseHandler

"""
注解集合(部分)
author:CallMeE
date:2018-06-01


"""
__all__ = [
    'ResponseBody',
    'ResponseTemplate',
    'AutoParam',
    'FullParam',
    'RequestMapping',
    'GetRoute',
    'PostRoute',
    'Get',
    'Post',
    'AutoWired',
    'AsResBody',
    'AsResTemp',
    'AsArgs',
    'AsJson',
    'AsFile',
    'BeanConfig',
    'bean',
    'Bean',
    'Desc',
    'DefBean',
    'res',
    'req',
    'BaseHandler'
]

AutoWired = AutoWired

ResponseBody = AsResBody = response.response_body

ResponseTemplate = AsResTemp = response.response_template

AutoParam = AsArgs = request.auto_param

FullParam = AsJson = request.full_param

FileParam = AsFile = request.file_param

BeanConfig = AutoWired.BeanConfig

bean = AutoWired.bean

Bean = AutoWired.Bean

RequestMapping = request.request_mapping

GetRoute = request.get_route

PostRoute = request.post_route

Get = request.get

Post = request.post

Desc = desc

DefBean = DefBean

res = response

req = request