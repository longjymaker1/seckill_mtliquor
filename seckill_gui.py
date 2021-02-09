# -*- coding:utf-8 -*-

import tkinter as tk


class SeckillGui:
    """创建秒杀gui"""
    def __init__(self):
        self.win = tk.Tk()
        self.win.title("mt抢购")
        self.win.geometry("900x800+500+500")

    def foo(self):
        """test"""
        print('test')

    def get_jd_config(self):
        """获取京东配置信息"""
        print('JD_configs')

    def myMenu(self):
        """创建菜单栏
        菜单栏有更改config信息功能，关闭功能
        """
        menubar = tk.Menu(self.win)

        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label='退出', command=self.win.quit)
        menubar.add_cascade(label='文件', menu=filemenu)

        configmenu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label='配置信息', menu=configmenu)
        edit_config_menu = tk.Menu(configmenu)
        configmenu.add_cascade(label='查看/修改配置信息', menu=edit_config_menu, underline=0)
        edit_config_menu.add_command(label='京东', command=self.get_jd_config)

        helpmenu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label='帮助', menu=helpmenu)
        return menubar

    def mySeckillWebSelect(self):
        """抢购网站选择
        选择网站复选框，京东、天猫、品多多、苏宁
        """
        pass

    def eid_fp_Config(self):
        """config信息
        展示当前config信息, 主要是eid, fp信息
        """
        eid_label = tk.Label(self.win, text="eid", bg="blue", font=("黑体", 12), width=15)
        eid_label.place(x=20, y=40)

        fp_label = tk.Label(self.win, text='fp', bg="blue", font=("黑体", 12), width=15)
        fp_label.place(x=20, y=80)

    def myQrCode(self):
        """展示二维码
        可以切换京东、天猫、拼多多、苏宁登陆二维码和小程序关注二维码
        """
        pass

    def myReserve(self):
        """预约按钮
        预约入口
        """

    def mySeckill(self):
        """抢购按钮
        抢购入口
        """
        pass

    def mySeckillLog(self):
        """日志输出
        查看当前日志，方便了解当前的状态
        """
        pass

    def gui_run(self):
        """运行gui"""

        self.eid_fp_Config()
        self.win.config(menu=self.myMenu())
        self.win.mainloop()


if __name__ == '__main__':
    sgui = SeckillGui()
    sgui.gui_run()
