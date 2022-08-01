import requests
from bs4 import BeautifulSoup
import json
import time

'''
    请初始化jit账号密码，
    本脚本是根据上一次填报信息进行打卡，所以你至少要有一条填报记录
'''


class HealthReport:
    login_dict = {  # 请初始化账号密码
        'username': 'test',
        'password': 'demo',
    }
    s = requests.session()  # 开启会话
    login_url = "http://authserver.jit.edu.cn/authserver/login?service=http%3A%2F%2Fehall.jit.edu.cn%2Flogin%3Fservice%3Dhttp%3A%2F%2Fehall.jit.edu.cn%2Fnew%2Findex.html"
    login_text = ''
    report_url = 'http://ehallapp.jit.edu.cn/qljfwapp/sys/lwJitHealthInfoDailyClock/modules/healthClock' \
                 '/T_HEALTH_DAILY_INFO_SAVE.do'
    last_report = {}
    report_data = {}

    #   别寻思了，我是启动入口，调我吧
    def start(self):
        if self.login():
            if self.getTodayHasReport():
                self.report()
        self.logout()

    def login(self):
        # 解析
        print(self.login_dict['username'] + ":")
        self.login_text = self.s.get(self.login_url).text  # 获取登陆参数
        self.parseValue()
        # 登陆
        code = self.s.post(self.login_url, self.login_dict).text
        if code.find("å½éå"):
            self.s.get("http://ehallapp.jit.edu.cn/qljfwapp/sys/lwJitHealthInfoDailyClock/index.do")  # 获权
            print("\t登陆成功！")
            return True
        print("\t登陆失败！")
        return False

    def parseValue(self):  # 解析参数
        login_value = self.login_text[3158:3530]
        soup = BeautifulSoup(login_value, "lxml")
        for link in soup.find_all('input'):
            key = link.get('name')
            val = link.get('value')
            self.login_dict[key] = val

    def getTodayHasReport(self):
        report_info_str = self.s.post(
            "http://ehallapp.jit.edu.cn/qljfwapp/sys/lwJitHealthInfoDailyClock/modules/healthClock"
            "/getTodayHasReported.do",
            {'pageNumber': 1}).text
        report_info_json = json.loads(report_info_str)
        last_report = report_info_json['datas']['getTodayHasReported']['rows']
        if not last_report:
            print("\t这家伙今日没打卡，即将进行打卡")
            return True
        print("\t今日已打卡！")
        return False

    def report(self):
        if self.getDailyReports():
            return False

        CREATED_AT = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        NEED_CHECKIN_DATE = time.strftime('%Y-%m-%d', time.localtime(time.time()))
        self.report_data = self.last_report
        self.report_data['FILL_TIME'] = CREATED_AT  # 填报时间
        self.report_data['NEED_CHECKIN_DATE'] = NEED_CHECKIN_DATE  # 应填日期
        self.report_data['CREATED_AT'] = CREATED_AT  # 创建时间
        st = self.s.post(self.report_url, self.report_data).text
        if st.find('VE":1'):
            print("\t打卡成功！")
            return True
        print("\t打卡失败!,请手动打卡")
        return False

    def getDailyReports(self):
        reports = self.s.post(
            "http://ehallapp.jit.edu.cn/qljfwapp/sys/lwJitHealthInfoDailyClock/modules/healthClock/getMyDailyReportDatas.do").text
        reports = json.loads(reports)
        if not reports['datas']['getMyDailyReportDatas']['rows']:
            print("\t这家伙太懒了，一次也没打卡，程序崩溃了！！！！")
            return True
        last_report = reports['datas']['getMyDailyReportDatas']['rows'][-1]
        print(last_report)
        self.last_report = last_report

    def logout(self):
        self.s.get("http://ehall.jit.edu.cn/logout?service=http://ehall.jit.edu.cn/new/index.html")
        self.s.close()
        print("\t已登出!!!")


demo = HealthReport()
demo.start()
