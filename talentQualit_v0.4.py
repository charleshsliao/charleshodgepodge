# -*- coding: utf-8 -*-
import argparse
import logging
import os
import sys
import traceback
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

import tornado
import tornado.web

import ujson as json

# pool = ThreadPoolExecutor()  # 涉及额外IO操作时开启

"""
update:
请求参数p中增加"work_desc",类型为map, 示例{"work_desc":{wid1:word_cnt1, wid2:word_cnt2}}
"""

log_path = os.path.abspath(os.path.join(sys.path[0], "../log/cv_quality.log"))
logging.basicConfig(level=logging.INFO,
                    format='%(levelname)s t=%(asctime)s&%(message)s&[line:%(lineno)d]',
                    datefmt='[%Y-%m-%d %H:%M:%S]',
                    filename=log_path,
                    filemode='a')


def load_school_score(default=0):
    sc_path = os.path.abspath(os.path.join(sys.path[0], "../ScoreData/schoolScore.json"))
    with open(sc_path) as ss:
        school_score = json.load(ss)
    return defaultdict(lambda:default, school_score)


def load_company_score(default=0):
    cs_path = os.path.abspath(os.path.join(sys.path[0], "../ScoreData/companyScore.json"))
    with open(cs_path) as cs:
        company_score = json.load(cs)
    return defaultdict(lambda:default, company_score)


def load_company_mapping():
    cm_path = os.path.abspath(os.path.join(sys.path[0], "../ScoreData/companyMapping.json"))
    with open(cm_path) as cm:
        company_score = json.load(cm)
    return company_score


def company_score_all():
    cp_map = load_company_mapping()                     # 公司映射关系{子公司:父公司}
    cp_score = load_company_score()                     # 公司得分(父公司居多)
    return defaultdict(lambda:0, {i:cp_score[cp_map[i]] for i in cp_map})


def check_request(dictobj, *args):
    """
    参数完整性检验, 指定参数为args, 若无缺失则返回参数名和请求头中对应值的dict,
    否则返回缺失参数列表
    """

    parameter_required = {}
    parameter_lost = []

    # request_parameters = json.loads(self.request.body)['request']['p']
    # 检查'p'值的类型,与请求方约定单个请求发送一个dict(map),多个请求将每组请求参数放入一个list中,
    for i in args:
        try:
            parameter_required[i] = dictobj[i]    # 在参数p中指定所需参数
        except:
            parameter_lost.append(i)
    if any(parameter_lost):          # 有参数缺失
        parameter_required.update({'err':'缺失参数{}'.format(parameter_lost)})

    return parameter_required


class TalentQualityHandler(tornado.web.RequestHandler):
    """
    人才质量打分服务step:
    1.参数完整性检验,参数完整则返回{参数名称:参数}字典,否则返回缺失列表参数,通过check_request方法实现;
    2.打分计算,通过quality_score方法实现;
    3.响应请求,返回json.
    """
    # _thread_pool = pool                       # 涉及额外IO操作时开启
    school_score = load_school_score(0.04)      # 学校分数默认值
    company_score = company_score_all()         # 涵盖所有公司的得分,若表中无相应公司ID则得分默认值为0
    degree_map = {'0': 0, '1': 0.6, '2': 0.8, '3': 0.8, '4': 0.1, '6': 0.8, '10': 0.8, '86': 0,
                  '87': 0, '89': 0, '90': 0, '91': 0, '92': 0.3, '94': 0.8, '95': 0.8, '99': 0}
    degree_score = defaultdict(int, degree_map)
    necessary_parameters = ('cvid', 'degreeid', 'schoolid', 'corpid', 'workexpyears', 'skills', 'work_desc') # 必须参数


    def check_request(self, *args):
        """
        参数完整性检验, 指定参数为args, 若无缺失则返回参数名和请求头中对应值的dict,
        否则返回缺失参数列表
        """
        return check_request(json.loads(self.request.body)['request']['p'], *args)


    # @tornado.concurrent.run_on_executor(executor="_thread_pool")      # 涉及额外IO操作时开启
    def quality_score(self, debug=False, **kwargs):
        """
        计算质量得分
        """
        results = {}
        results['cvid'] = int(kwargs['cvid'])
        degree_resp = self.degree_score[kwargs['degreeid']]
        if kwargs['schoolid'] == []:
            school_resp = 0
        else:
            school_resp = max([self.school_score[sc] for sc in kwargs['schoolid']])
        workexp = float(kwargs['workexpyears'])

        if workexp == 0 and not int(len(kwargs['corpid'])) :            # 工作年限为0且公司id为0则认定为应届生(请求参数中公司id未知则为0)
            score = 0.6 * school_resp + 0.4 * degree_resp
            results['score_detail'] = {'schoolScore':school_resp, 'degreeScore':degree_resp, 'corpScore':'应届生', 'workExpScore':'应届生'}
        else: # 非应届生
            if 0 <= workexp < 1:
                work_resp = 0.3
            elif 1 <= workexp < 3:
                work_resp = 0.6
            elif 3 <= workexp < 5:
                work_resp = 0.8
            elif 5 <= workexp < 10:
                work_resp = 0.9
            else:
                work_resp = 0.8

            if len(kwargs['corpid']) == 0:
                company_resp = 0
            else:
                company_resp = max([self.company_score[i] for i in kwargs['corpid']])   # 请求参数必须含有corpid,目前调用不含此参数

            if school_resp > 0.04 and degree_resp == self.degree_score['4']:
                score = 0.15 * school_resp + 0.2 * degree_resp + 0.3 * company_resp + 0.4 * work_resp   #工作0.2->0.4
            else:
                score = 0.3 * school_resp + 0.2 * degree_resp + 0.3 * company_resp + 0.4 * work_resp    #工作0.2->0.4
            results['score_detail'] = {'schoolScore':school_resp, 'degreeScore':degree_resp, 'corpScore':company_resp, 'workExpScore':work_resp}

            # 根据简历中工作描述的详细情况酌情对任一描述字数均不大于45个字的简历分数进行惩罚
            if kwargs['work_desc'] == {}:
                score -= 0.1
            else:
                try:
                    max_desc = max([int(i) for i in kwargs['work_desc'].values()])  # 请求格式{'p':{work_desc:{wid:len(description)}}}
                except ValueError:
                    max_desc = max([len(i) for i in kwargs['work_desc'].values()])  # 避免传入明文的情况
                except:
                    logging.info(traceback.format_exc())
                if max_desc < 45:
                    score -= 0.1

        results['score'] = score + 0.001 # 0区分是否返回成功

        if not debug:
            results.pop('score_detail')
        return results


    def gen_response(self):
        response = {}
        response['response'] = {}
        response['header'] = {"local_ip":"192.168.8.76","uid":"111","user_ip":"192.168.8.76","product":"cv_quality","appid":"16","user":"algo_platform"}

        parameters = self.check_request(*self.necessary_parameters)
        if 'err' not in parameters:
            score_resp = self.quality_score(**parameters)
            response['response']['results'] = score_resp
            response['response']['err_no'] = '0'
            response['response']['err_msg'] = ''
        else:
            response['response']['results'] = {'cvid': parameters['cvid'], 'score': 0}
            response['response']['err_no'] = '1'
            response['response']['err_msg'] = parameters['err']

        return response


    @tornado.gen.coroutine
    def post(self):
        """
        响应post请求.
        """
        self.finish(self.gen_response())


class TalentQualityHandlerBatch(TalentQualityHandler):
    """
    批处理请求
    """
    def check_request_batch(self, *args):
        """
        检查参数列表
        """
        request_parameters = json.loads(self.request.body)['request']['p'] # 列表[{p1},...{pn}]
        return [check_request(rp, *args) for rp in request_parameters] # 请求参数列表中不需要再load


    def gen_response(self, request_p):
        """
        重载父类的gen_response方法, 复用父类quality_score方法,用于批量处理请求参数
        """
        result = {}
        score_resp = self.quality_score(**request_p) # {cvid:123, score:0.96}
        if 'err' not in request_p:
            result.update({score_resp['cvid']:{'score':score_resp['score']}})
        else:
            result.update({score_resp['cvid']:{'score':0}}) # 简历ID不能缺失
        return result


    def gen_response_batch(self):
        results = {}
        results['response'] = {}
        results['header'] = {"local_ip":"192.168.8.76","uid":"111","user_ip":"192.168.8.76","product":"cv_quality","appid":"16","user":"algo_platform"}
        self.request_list = self.check_request_batch(*self.necessary_parameters)
        score_resp_batch = {}
        for i in [self.gen_response(p) for p in self.request_list]:
            score_resp_batch.update(i) # {id:{score:0.96}}
        if all([score_resp_batch[cv]['score'] for cv in score_resp_batch]):
            results['response']['err_no'] = '0'
            results['response']['err_msg'] = ''
        else:
            results['response']['err_no'] = '1'
            results['response']['err_msg'] = '简历ID{}未计算得分'.format([cv for cv in score_resp_batch['response']['results'] if score_resp_batch['response']['results'][cv]['score']==0])
        results['response']['results'] = score_resp_batch
        # print(res)
        return results


    @tornado.gen.coroutine
    def post(self):
        """
        批量返回计算结果
        """
        try:
            self.finish(self.gen_response_batch())
        except:
            logging.debug(traceback.format_exc())
            print(traceback.format_exc())


def make_app():
    return tornado.web.Application([
        (r"/", TalentQualityHandler),
        (r"/batch", TalentQualityHandlerBatch)
    ], debug=False)



def main():
    logging.info('程序启动')
    app = make_app()
    parser = argparse.ArgumentParser()
    arggroup = parser.add_mutually_exclusive_group()                                    # 指定互斥的命令行参数以获取程序监听端口信息
    arggroup.add_argument("-l", '--LocalTest', help="本地测试", action='store_true')
    arggroup.add_argument("-t", '--Test',      help="测试环境", action='store_true')
    arggroup.add_argument("-o", '--OneLine',   help="线上服务", action='store_true')
    arggroup.add_argument("-d", '--Develop',   help="开发环境", action='store_true')
    args = parser.parse_args()

    if args.OneLine:
        sockets = tornado.netutil.bind_sockets(port=51618, address='192.168.8.76')
    elif args.Develop:
        sockets = tornado.netutil.bind_sockets(port=51615, address='192.168.1.111')
    elif args.Test:
        sockets = tornado.netutil.bind_sockets(port=51615, address='10.9.10.10')
    elif args.LocalTest:
        sockets = tornado.netutil.bind_sockets(8888)
    else:                                                                               # 不指定命令行参数则报错,程序终止
        parser.error('请指定运行环境: -l或--LocalTest ->本地测试(使用localhost); -o或--OneLine ->线上服务; -t或--Test -> 测试环境; -d或--Develop ->开发环境')

    tornado.process.fork_processes(0)
    server = tornado.httpserver.HTTPServer(app)
    server.add_sockets(sockets)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
