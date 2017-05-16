# coding:utf-8
import os
import urllib2
from bs4 import BeautifulSoup
import json
from skimage import io
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties

Keys        = [u'笔仙',u'碟仙',u'筷仙',u'镜仙']
none_img    = 'https://img3.doubanio.com/f/movie/b6dc761f5e4cf04032faa969826986efbecd54bb/pics/movie/movie_default_small.png'
report_name = 'x-xian_movies.png'
json_name   = 'x-xian_movies.json'
repo_url    = 'https://github.com/pengzhxyz/X-xian-movies'
movies = []

def find_xian_from_page(url, key):
    content = urllib2.urlopen(url).read()
    global movies
    soup = BeautifulSoup(content)
    trs = soup.find_all('tr',{'class':'item'})
    for tr in trs:
        movie = dict()
        movie['title'] = tr.find('img')['alt']
        if movie['title'].count(key)==0:
            continue
        movie['poster'] = tr.find('img')['src']
        movie['url'] = tr.find('a',{'class':'nbg'})['href']
        if tr.find('span', {'class':'rating_nums'}):
            movie['rating'] = tr.find('span', {'class':'rating_nums'}).text
        else:
            movie['rating'] = None
        movies.append(movie)
    next = soup.find('span',{'class':'next'})
    if next and next.find('a'):
        nexturl = next.find('a')['href']
        find_xian_from_page(nexturl, key)

def xian_movies(keys):
    for key in keys:
        url = 'https://movie.douban.com/subject_search?search_text=%s' % key.encode('utf8')
        find_xian_from_page(url, key)


def vis_square(data):
    """Take an array of shape (n, height, width) or (n, height, width, 3)
       and visualize each (height, width) thing in a grid of size approx. sqrt(n) by sqrt(n)"""
    # normalize data for display
    data = (data - data.min()) / (data.max() - data.min())

    # force the number of filters to be square
    n = int(np.ceil(np.sqrt(data.shape[0])))
    padding = (((0, n ** 2 - data.shape[0]),
                (0, 0), (0, 0))  # add some space between filters
               + ((0, 0),) * (data.ndim - 3))  # don't pad the last dimension (if there is one)
    data = np.pad(data, padding, mode='constant', constant_values=1)  # pad with ones (white)

    # tile the filters into an image
    data = data.reshape((n, n) + data.shape[1:]).transpose((0, 2, 1, 3) + tuple(range(4, data.ndim + 1)))
    data = data.reshape((n * data.shape[1], n * data.shape[3]) + data.shape[4:])
    return data

def plot_report():
    movies_p = filter(lambda x:x['poster']!=none_img, movies)
    movies_p = movies_p[:25] # only plot 25 posters
    img_shape = io.imread(movies_p[0]['poster']).shape
    (h,w,c) = img_shape
    imgs_data = np.zeros((len(movies_p),)+(img_shape))
    for m_i, m in enumerate(movies_p):
        imgs_data[m_i] = io.imread(m['poster'])
    imgs_data = vis_square(imgs_data)
    plt.imshow(imgs_data)
    font = FontProperties(fname=r"C:\\WINDOWS\\Fonts\\msyh.ttc", size=14)
    plt.text(imgs_data.shape[1] // 2, imgs_data.shape[0] + 50 ,
             u'%d部 X-仙电影 平均分  %0.1f'% (len(movies), avg_rating()),
             horizontalalignment='center', fontproperties=font)
    for m_i, m in enumerate(movies):
        rating = str(m['rating']) if m['rating'] else u'评分不足'
        plt.text(imgs_data.shape[1]//2, imgs_data.shape[0]+ 60 + (m_i+1)*40,
                 m['title']+'  '+rating,horizontalalignment='center', fontproperties=font)
    plt.text(imgs_data.shape[1] // 2, imgs_data.shape[0] + 60 + (len(movies)+1) * 40 + 10,
             u'评分来自：豆瓣电影', horizontalalignment='center', fontproperties=font)
    plt.text(imgs_data.shape[1] // 2, imgs_data.shape[0] + 50 + (len(movies)+1)* 40 + 100,
             '@ %s'%repo_url, horizontalalignment='center')
    plt.axis('off')
    plt.savefig(report_name, bbox_inches='tight',pad_inches=0)
    # plt.show()

def avg_rating():
    n = 0
    rating = 0
    for m in movies:
        if m['rating']:
            n += 1
            rating += float(m['rating'])
    return rating/n


if __name__=='__main__':
    print 'Starting find X-xian movies...'
    if not os.path.exists(json_name):
        xian_movies(Keys)
        with open(json_name,'w') as f:
            f.write(json.dumps(movies))
    else:
        print 'Loading x-xian movies from %s' % json_name
        with open(json_name) as f:
            movies = json.load(f)
    movies = sorted(movies,lambda x,y:1 if x['rating'] else -1,reverse=True)
    plot_report()
    print 'Found %d xian movies, avg rating: %0.1f' % (len(movies), avg_rating())
    print 'Report has saved in %s!'%report_name
    r = raw_input('Press any key to exit...')