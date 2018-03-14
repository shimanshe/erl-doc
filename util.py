
PREV_PAGE = 'previous page'
NEXT_PAGE = 'next page'

NEW_LINE = '\n'
import subprocess
import tempfile
import os
from urllib.parse import urlparse


def select_input_return(opts,top=0,comment_callback=None):
	opts = list(opts)
	page = 0
	while True:
		sels = opts
		if top>0 and len(opts)>top:
			tp = len(opts)//top
			if len(opts) %top!=0:
				tp+=1
			sels = opts[page*top:(page+1)*top]
			print(str(tp)+','+str(page))
			if page!=0:
				sels.append(PREV_PAGE)
			if page != tp-1:
				sels.append(NEXT_PAGE)
		i = 1
		for name in sels:
			if comment_callback:
				name = comment_callback(name)
			if name:
				print(str(i) + "."+name)
			i+=1
		print()
		s = input('Please select:')
		if not s:
			return None,False
		else:
			try:
				sel = sels[int(s)-1]
				if sel == PREV_PAGE:
					page-=1
					continue
				elif sel == NEXT_PAGE:
					page+=1
					continue
				else:
					return sel,True
			except:
				return s, False
		
	
def select_input(opts,top=0):
	str,result = select_input_return(opts,top)  
	return str

def select_opt(d,prefix='opt_'):
	opts = []
	length = len(prefix)
	for k,v in d.items():
		if k.startswith(prefix):
			opts.append(k[length:])
	opts.sort()
	opt = ''
	if len(opts)==1:
		opt = opts[0]
	else:
		opt = select_input(opts)
	if opt:
		d[prefix+opt]()
	else:
		print('no or not select opt method')	

def find_str_list_in(str, start, search1, search2=None):
	l = []
	while True:
		s, pos = _find_str_in(str, start, search1, search2)
		if pos == -1:
			break
		start = pos+len(search2)
		l.append(s)
	return l

def find_str_in(s, start, search1, search2=None):
	s, pos = _find_str_in(s, start, search1, search2)
	return s

def find_str_in2(s, start, search1, search2=None):
	return _find_str_in(s, start, search1, search2)

def _find_str_in(s, start, search1, search2=None):
	if not search2:
		search2 = search1
	pos = s.find(search1, start)
	if pos == -1:
		return None,-1
	end = s.find(search2, pos+len(search1))
	if end == -1:
		return None,-1
	return s[pos+len(search1):end], end

def get_url_root(url):
	pos = url.find('//')
	if pos == -1:
		pos = 0
	else:
		pos += 2
	pos = url.find('/', pos)
	if pos == -1:
		pos = len(url)
	url = url[0:pos]
	if not url.endswith('/'):
		url += '/'
	return url


def get_url_path(url):
	o = urlparse(url)
	return o.path

def get_url_filename(url):
	pos = url.find('?')
	if pos != -1:
		url = url[0:pos]
	pos = url.rfind('/')
	return url[pos+1:]

def get_url_dir(url):
	if not url.endswith('/'):
		pos = url.rfind('/')
		if pos != -1:
			url = url[0:pos+1]
	return url

def get_parent_url(url):
	root_path = get_url_root(url)
	if url.endswith('/'):
		url = url[0:-1]
	pos = url.rfind('/')
	parent_url = url[0:pos+1]
	if len(parent_url) < len(root_path):
		return root_path
	else:
		return parent_url

def join_url(url, path):
	if path.startswith('http://') or path.startswith('https://'):
		return path
	if path.startswith('/'):
		url = get_url_root(url)
		path = path[1:]
	else:
		url = get_url_dir(url)
		while True:
			if path.startswith('./'):
				path = path[2:]
			elif path.startswith('../'):
				url = get_parent_url(url)
				path = path[3:]
			else:
				break
	if not url.endswith('/'):
		url += '/'
	return url + path

def write_bytes(path, bytes):
	f = open(path, 'wb')
	f.write(bytes)
	f.close()

def read_file(path, encoding='utf-8'):
	try:
		f = open(path,'r',encoding=encoding, errors="ignore")
		content = f.read()
		f.close()
		return content
	except:
		return None

def get_filename(file):
	filename, ext = filename_ext(file)
	return filename

def filename_ext(filename):
	pos = filename.rfind('.')
	if pos == -1:
		return filename,''
	else:
		return filename[0:pos],filename[pos+1:]

def write_file(path, content,encoding='utf-8', log=False):
	f = open(path,'w',encoding=encoding,errors='ignore')
	f.write(content)
	f.close()
	if log:
		print("write file: "+path)
		
def run_scripts(script,timeout=None):
	tmpdir = tempfile.gettempdir() 
	path = os.path.join(tmpdir,'scripts.bat')
	write_file(path,script,encoding='gbk')
	run_cmd('start cmd /c {0}'.format(path),timeout=timeout)
	
def run_cmd_console(cmd):
	run_cmd('start cmd /k '+cmd)
	
def run_cmd(cmd,timeout=None):
	result = run_cmd_result(cmd, timeout=timeout)
	if result:
		print(result)
	
def run_cmd_result(cmd, timeout=None):
	try:
		print("run cmd:{0}".format(cmd))
	except:
		print_e()
	try:
		p = subprocess.check_output(
			cmd,
			stderr=subprocess.STDOUT,
			shell=True,
			timeout=timeout)
	except subprocess.CalledProcessError as e:
		print(e.returncode)
		print(e.output.decode('gbk','ignore'))
		return ''
	except subprocess.TimeoutExpired as e:
		return ''
	else:
		return (p.decode('gbk','ignore'))