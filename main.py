#!/usr/bin/env python
#@encoding: utf-8
#@author zhoufanglong ${date} ${time}

import requests
from util import *
import os
import time

MAN_URL = 'http://erlang.org/doc/man/'
script_dir = os.path.split(os.path.realpath(__file__))[0]
doc_dir = os.path.join(script_dir, "doc")
chm_dir = os.path.join(script_dir, "chm")
if not os.path.isdir(doc_dir):
	os.makedirs(doc_dir, exist_ok=True)
if not os.path.isdir(chm_dir):
	os.makedirs(chm_dir, exist_ok=True)
SEP = '@@@'	

name = 'Erlang Manual'

project_template = '''\
[OPTIONS]
Binary TOC=No
Binary Index=No
Compiled file=%(outname)s.chm
Contents file=%(outname)s.hhc
Default Window=%(outname)s
Default topic=%(index)s
Display compile progress=No
Full text search stop list file=%(outname)s.stp
Full-text search=Yes
Index file=%(outname)s.hhk
Language=%(lcid)#x
Title=%(title)s

[WINDOWS]
%(outname)s="%(title)s","%(outname)s.hhc","%(outname)s.hhk",\
"%(index)s","%(index)s",,,,,0x63520,220,0x10384e,[0,0,1024,768],,,,,,,0

[FILES]
'''		
contents_header = '''\
<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML//EN">
<HTML>
<HEAD>
<meta name="GENERATOR" content="Microsoft&reg; HTML Help Workshop 4.1">
<!-- Sitemap 1.0 -->
</HEAD><BODY>
<OBJECT type="text/site properties">
        <param name="Window Styles" value="0x801227">
        <param name="ImageType" value="Folder">
</OBJECT>
<UL>
'''
object_sitemap = '''\
<OBJECT type="text/sitemap">
    <param name="Name" value="%s">
    <param name="Local" value="%s">
</OBJECT>
'''
object_sitemap_folder = '''\
<OBJECT type="text/sitemap">
    <param name="Name" value="%s">
</OBJECT>
'''
object_index_folder = '''\
<OBJECT type="text/sitemap">
    <param name="Name" value="%s">
    <param name="See Also" value="%s">
</OBJECT>
'''

def opt_make_htmlhelp_prj():
	make_htmlhelp(chm_dir, name)

def count_start_tab(_str):
	n = 0
	for i in _str:
		if i == '\t':
			n+=1
		else:
			break
	return n

def parse_cata(lines):
	cata = []	
	for line in lines:
		arr = line.split(SEP)
		print(arr)
		cata.append([count_start_tab(line), arr[0], arr[1]])
	return cata

def add_prefix(_str, prefix):
	_list = []
	for line in _str.splitlines():
		_list.append(prefix+line)
	return NEW_LINE.join(_list)

def make_htmlhelp(_dir, name):	
	encoding = 'gbk'
	text = project_template % {'outname': name,
                                        'title': name,
                                        'version': '1.0',
                                        'project': name,
                                        'lcid': 0x804,
                                        'index': 'erlang.html'}
	text += NEW_LINE
	length = len(_dir)
	_list = []
	for root, dirs, files in os.walk(_dir):
		for file in files:
			if file.startswith(name):
				continue
			path = os.path.join(root, file)
			_list.append(path[length+1:].replace('\\','/'))
	text += NEW_LINE.join(_list)
	path = os.path.join(_dir,name+".hhp")
	write_file(path, text, encoding)
	
	text = contents_header
	path = os.path.join(_dir, "cata.txt")
	_str = read_file(path, encoding)
	lines = _str.splitlines()
	cata = parse_cata(lines)
	cata_len = len(cata)
	if cata_len==0 or cata[0][0]!=0:
		raise
	for i in range(0, cata_len):
		item = cata[i]
		level = item[0]
		prefix = '\t'*level
		obj = '<LI>'
		obj += object_sitemap % (item[1].strip(), item[2])
		obj = add_prefix(obj, prefix)
		text += obj
		text += NEW_LINE
		if i+1 != cata_len:
			next_item = cata[i+1]
			next_level = next_item[0]
			if level < next_level:
				if next_level-level!=1:
					raise
				text += prefix+'<UL>'+NEW_LINE
			elif level>next_level:
				for j in range(0, level-next_level):
					text+= '\t'*(level-j-1)+'</UL>'+NEW_LINE

	last_level = cata[-1][0]
	for j in range(0, last_level):
		text+= '\t'*(last_level-j-1)+'</UL>'+NEW_LINE
	text += '</UL></BODY></HTML>'
	path = os.path.join(_dir,name+".hhc")
	write_file(path, text, encoding)
	
	text = contents_header
	for i in range(0, cata_len):
		item = cata[i]
		text +='<LI>'
		text += object_sitemap % (item[1], item[2])
		text += NEW_LINE
	text += '</UL></BODY></HTML>'
	path = os.path.join(_dir,name+".hhk")
	write_file(path, text, encoding)

def opt_build_htmlhelp_prj():
	path = os.path.join(chm_dir, name+".hhp")
	script="""
@echo off
set path=C:\Program Files (x86)\HTML Help Workshop;%path%
hhc "{0}"
pause
""".format(path)
	run_scripts(script)
	
def opt_fetch_doc_html():
	r = requests.get(MAN_URL)
	_str = r.text
	table = find_str_in(_str, 0, "man-index", "</table>")
	elems = find_str_list_in(table, 0, "<a ", "</a>")
	links = []
	for elem in elems:
		elem += "<a"
		href = find_str_in(elem, 0, 'href="', '"')
		title = find_str_in(elem, 0, '>', '<a')
		if not href.startswith('../'):
			links.append([join_url(MAN_URL, href), title])
	links.append('http://erlang.org/doc/otp_doc.css')
	for link in links:
		url = link[0]
		path = os.path.join(doc_dir, get_url_filename(url))
		if not os.path.isfile(path):
			try:
				r = requests.get(url, timeout=30)
				print(url)
				write_bytes(path, r.content)
			except:
				time.sleep(3)

def parse_resouce(_str):
	urls = []
	css = find_str_list_in(_str, 0, "<link", ">")
	for item in css:
		src = find_str_in(item, 0, 'href="', '"')
		if src:
			urls.append(src)
	scripts = find_str_list_in(_str, 0, "<script", ">")
	for item in scripts:
		src = find_str_in(item, 0, 'src="', '"')
		if src:
			urls.append(src)
	return urls

def opt_handle_html():
	cata = []
	for file in os.listdir(doc_dir):
		print(file)
		path = os.path.join(doc_dir, file)
		_str = read_file(path)
		pos1 = _str.find('<div id="container">')
		pos2 = _str.find('<div id="content">', pos1)
		container = _str[pos1:pos2]	
		_str = _str[0:pos1]+_str[pos2:]
		links = find_str_list_in(container, 0, '<a ', '</a>')
		cata.append(get_filename(file)+SEP+file)
		for elem in links:
			elem += "<a"
			href = find_str_in(elem, 0, 'href="', '"')
			title = find_str_in(elem, 0, '>', '<a')
			title = title.strip()
			if href.startswith(file+"#"):
				cata.append('\t'+title+SEP+href)
		_list = parse_resouce(_str)
		for l in _list:
			link = join_url(MAN_URL, l)
			filename = "_res"+get_url_path(link).replace('/','_')
			path = os.path.join(chm_dir, filename)
			if not os.path.isfile(path):
				r = requests.get(link)
				write_bytes(path, r.content)
			_str = _str.replace(l, filename)
		_str = _str.replace('urchinTracker();','')
		path = os.path.join(chm_dir, file)
		write_file(path, _str)
	path = os.path.join(chm_dir, "cata.txt")
	write_file(path, NEW_LINE.join(cata))

	for file in os.listdir(chm_dir):
		if file.startswith('_res'):
			path = os.path.join(chm_dir, file)
			if file == '_res_doc_otp_doc.css':
				content = read_file(path)
				content = content.replace('margin-left: 340px;','')
				write_file(path, content)
			elif file.endswith('.js'):
				write_file(path, '')
		

def _opt_test():
	url = join_url(MAN_URL, '../../../../doc/js/highlight.js')
	print(url)

if __name__ == '__main__':
	select_opt(globals())
