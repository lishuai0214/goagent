#!/usr/bin/env python
# coding:utf-8

import sys
import os
import re
import getpass
import socket

def println(s, file=sys.stderr):
    assert type(s) is type(u'')
    file.write(s.encode(sys.getfilesystemencoding(), 'replace') + os.linesep)
#连接本地的代理服务器，因为google不能直接连接，也就没法部署软件
try:
    socket.create_connection(('127.0.0.1', 8087), timeout=1).close()
    os.environ['HTTPS_PROXY'] = '127.0.0.1:8087'
except socket.error:
    println(u'警告：建议先启动 goagent 客户端或者 VPN 然后再上传，如果您的 VPN 已经打开的话，请按回车键继续。')
    raw_input()

sys.modules.pop('google', None)
sys.path.insert(0, os.path.abspath(os.path.join(__file__, '../google_appengine.zip')))

import mimetypes
mimetypes._winreg = None

# urllib2 是python标准库中的 HTTP 客户端库
import urllib2
#fancy_urllib google_appengine.zip中的库
import fancy_urllib
fancy_urllib.FancyHTTPSHandler = urllib2.HTTPSHandler

_realgetpass = getpass.getpass
def getpass_getpass(prompt='Password:', stream=None):
    try:
        import msvcrt
    except ImportError:
        return _realgetpass(prompt, stream)
    password = ''
    sys.stdout.write(prompt)
    while True:
        ch = msvcrt.getch()
        if ch == '\b':#退格键，使密码后退一个
            if password:
                password = password[:-1]#密码去掉一个字符
                sys.stdout.write('\b \b')#输出一个退格一个空格再输出一个退格，模拟退格删除动作
            else:
                continue
        elif ch == '\r':#'\r'是回车键，密码输入完毕后按下的确定键
            sys.stdout.write(os.linesep)#os.linesep字符串给出当前平台使用的行终止符。例如，Windows使用'\r\n'，Linux使用'\n'而Mac使用'\r'。
            return password
        else:
            password += ch#每输入一个字符密码加一个字符
            sys.stdout.write('*')#模拟密码的*号
getpass.getpass = getpass_getpass


from google.appengine.tools import appengine_rpc, appcfg
appengine_rpc.HttpRpcServer.DEFAULT_COOKIE_FILE_PATH = './.appcfg_cookies'

#上传代码的主函数
def upload(dirname, appid):
    assert isinstance(dirname, basestring) and isinstance(appid, basestring)
    filename = os.path.join(dirname, 'app.yaml')
    template_filename = os.path.join(dirname, 'app.template.yaml')
    assert os.path.isfile(template_filename), u'%s not exists!' % template_filename
    with open(template_filename, 'rb') as fp:
        yaml = fp.read()
    with open(filename, 'wb') as fp:
        fp.write(re.sub(r'application:\s*\S+', 'application: '+appid, yaml))
    appcfg.main(['appcfg', 'rollback', dirname])
    appcfg.main(['appcfg', 'update', dirname])

#主函数
def main():
    appids = raw_input('APPID:')
    if not re.match(r'[0-9a-zA-Z\-|]+', appids):
        println(u'错误的 appid 格式，请登录 http://appengine.google.com 查看您的 appid!')
        sys.exit(-1)
    if any(x in appids.lower() for x in ('ios', 'android', 'mobile')):
        println(u'appid 不能包含 ios/android/mobile 等字样。')
        sys.exit(-1)
    os.chdir(os.path.abspath(os.path.dirname(__file__)))
    try:
        os.remove(appengine_rpc.HttpRpcServer.DEFAULT_COOKIE_FILE_PATH)
    except OSError:
        pass
    for appid in appids.split('|'):
        upload('gae', appid)
    try:
        os.remove(appengine_rpc.HttpRpcServer.DEFAULT_COOKIE_FILE_PATH)
    except OSError:
        pass


if __name__ == '__main__':
    println(u'''\
===============================================================
 GoAgent服务端部署程序, 开始上传 gae 应用文件夹
 Linux/Mac 用户, 请使用 python uploader.py 来上传应用
===============================================================

请输入您的appid, 多个appid请用|号隔开
注意：appid 请勿包含 ios/android/mobile 等字样，否则可能被某些网站识别成移动设备。
        '''.strip())
    main()
    println(os.linesep + u'上传成功，请不要忘记编辑proxy.ini把你的appid填进去，谢谢。按回车键退出程序。')
    raw_input()
