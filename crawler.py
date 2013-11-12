#coding=utf8
import urllib2, random
import os, time

user_agents = ['Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20130406 Firefox/23.0', \
        'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:18.0) Gecko/20100101 Firefox/18.0', \
        'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/533+ \
        (KHTML, like Gecko) Element Browser 5.0', \
        'IBM WebExplorer /v0.94', 'Galaxy/1.0 [en] (Mac OS X 10.5.6; U; en)', \
        'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)', \
        'Opera/9.80 (Windows NT 6.0) Presto/2.12.388 Version/12.14', \
        'Mozilla/5.0 (iPad; CPU OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) \
        Version/6.0 Mobile/10A5355d Safari/8536.25', \
        'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) \
        Chrome/28.0.1468.0 Safari/537.36', \
        'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0; TheWorld)']

timeout = 10

def crawl(url, use_proxy=False):
    #queryStr = urllib2.quote(queryStr)
    index = random.randint(0, 9)
    #import pdb;pdb.set_trace();
    if use_proxy:
    	proxy_handler = urllib2.ProxyHandler({"http":'127.0.0.1:8087', "https":'127.0.0.1:8087'})
    	opener = urllib2.build_opener(proxy_handler)
    	opener.addheaders = [('User-agent', user_agents[index])]
    	urllib2.install_opener(opener)

    print 'url is ', url
    request = urllib2.Request(url)
    user_agent = user_agents[index]
    request.add_header('User-agent', user_agent)
    try:
        response = urllib2.urlopen(request, timeout=timeout)
        code = response.getcode()
        if code not in (200, 201, 202, 302, 304):
            return '', False, code

        html = response.read()
        return html, True, code
    except Exception as e:
        return '', False, None


def save_list(filename, rlist):
    fw = open(filename, 'w+')
    fw.write('\n'.join(rlist))
    fw.close()

def save_error_line(line):
	error_lines = open('error_urls.txt', 'r').readlines()
	error_lines = set([l.strip() for l in error_lines])
	error_lines.add(line)
	save_list('error_urls.txt', list(error_lines))

links_dir = 'links10-20'

def crawl_by_person():
	'''
		根据links里的30个目录，每个目录下的全部文件中的所有url进行爬取，爬取一个后停止5s
	'''
	retry = 0
	total = 0
	success_num = 0
	failed_num = 0
	for dir_ in os.listdir(links_dir):
		if int(dir_) < 1 or int(dir_) > 30:
			continue
		urls_dir = '%s/%s' % (links_dir, dir_)
		files = os.listdir(urls_dir)
		for f in files:
			if not f.endswith('.txt'):
				continue
			try:
				parts = f.split('.')
				base_save_dir = 'htmls/person%s/' % dir_
				if not os.path.isdir(base_save_dir):
					os.mkdir(base_save_dir)
				save_dir = 'htmls/person%s/%s' % (dir_, parts[0])
				if not os.path.isdir(save_dir):
					os.mkdir(save_dir)
				links_file = '%s/%s/%s' % (links_dir, dir_, f)
				lines = open(links_file, 'r').readlines()
				for i, url in enumerate(lines):
					if '.pdf' in url:
						continue
					successed_urls = open('successed_urls.txt', 'r').readlines()
					successed_urls = [l.strip() for l in successed_urls]
					error_urls = open('error_urls.txt', 'r').readlines()
					error_urls = [l.strip().split('\t') for l in error_urls if l]
					error_urls = [r[1] for r in error_urls if r]
					crawled_urls = set(successed_urls + error_urls)
					url = url.strip()
					wfilename = '%s/%s.html' % (save_dir, str(i+1))
					try:
						if url in crawled_urls:
							print '%s has been crawled!' % url
							continue
						if not url:
							continue
						start = time.time()
						print 'crawl person %s, filename %s, %s' % (dir_, links_file, url)
						total += 1
						html, is_successed, code = crawl(url)
                                                print 'code %s is_successed %s' % (code, is_successed)
						if not is_successed:
							html, is_successed, code = crawl(url, use_proxy=True)
                                                print 'code %s is_successed %s--use proxy' % (code, is_successed)
						if is_successed:
							fw = open(wfilename, 'w+')
							fw.write(html)
							fw.close()
							successed_urls.append(url)
							save_list('successed_urls.txt', successed_urls)
							success_num += 1
							print 'succesed, html file saved in %s, cost %.2fs, %s/%s\n' % (wfilename, time.time() - start, success_num, total)
							retry = 0
						else:
							error_line = '%s/%s\t%s' % (save_dir, str(i+1), url)
							save_error_line(error_line)
							failed_num += 0
						time.sleep(2)
					except Exception as e:
						print 'error occured: %s, filename %s, %s url\n' % (e, links_file, i+1)
						failed_num += 1
						import traceback
						traceback.print_exc()
						error_line = '%s/%s\t%s' % (save_dir, str(i+1), url)
						save_error_line(error_line)
						time.sleep(3)
						retry += 1
			except Exception as e:
				import traceback
				traceback.print_exc()
				print 'error occured: %s, in file %s' % (e, f)
				time.sleep(5)
				continue

def crawl_error_list():
    lines = open('error_error_queries.txt')
    total = 0
    for cnt, l in enumerate(lines):
        successed_queries = open('error_error_successed_queries.txt', 'r+').readlines()
        successed_queries = [q.strip() for q in successed_queries]
        wfilename = l.strip()
        try:
            if wfilename in successed_queries:
                print '%s has been crawled!' % wfilename
                continue
            parts = wfilename.split('/')
            query_num = parts[1]
            index = int(parts[2].split('_')[0])
            query_lines = open('query/%s.txt' % query_num, 'r').readlines()
            error_query = query_lines[index-1]
            start = time.time()
            print 'search %s error query %s' % (cnt+1, wfilename)
            html = search(error_query)
            #import pdb;pdb.set_trace()
            fw = open(wfilename, 'w+')
            fw.write(html)
            fw.close()
            successed_queries.append(wfilename)
            save_list('error_successed_queries.txt', successed_queries)
            total += 1
            print 'succesed, html file saved in %s, cost %.2fs, total %s\n' % (wfilename, time.time() - start, total)
            time.sleep(30)
        except Exception as e:
            print 'error occured: %s, %s\n' % (e, l.strip())
            error_queries = open('error_error_queries2.txt', 'r').readlines()
            error_queries = set([l.strip() for l in error_queries])
            error_queries.add(wfilename)
            save_list('error_error_queries.txt', list(error_queries))
            time.sleep(3600 * 2)

def test_crawl():
    url = 'http://orca.cf.ac.uk/view/types/article.html'
    print crawl(url, use_proxy=True)
    print crawl(url)
    


if __name__ == '__main__':
    #html = search('china USA')
    #fw = open('test_google.com', 'w+')
    #fw.write(html)
    #fw.close()
    #search_by_person()
    #crawl_error_list()
    crawl_by_person()
    #test_crawl()
