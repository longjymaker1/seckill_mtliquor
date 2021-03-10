# -*- coding:utf-8 -*-

import tkinter as tk


def tmp():
    print('123')


class SeckillGui:
    """创建秒杀gui"""
    def __init__(self):
        self.win = tk.Tk()
        self.win.title("mt抢购")
        self.win.geometry("700x500+300+80")

    def get_config(self, web):
        """获取配置信息"""
        print('test')

    def cat_web_config(self, web):
        """获取平台(京东、天猫、拼多多、苏宁)配置信息"""
        print('cat', web)

    def edit_web_config(self, web):
        """修改平台(京东、天猫、拼多多、苏宁)配置信息"""
        print('edit', web)

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
        cat_config_menu = tk.Menu(configmenu)
        configmenu.add_cascade(label='查看配置信息',
                               menu=cat_config_menu,
                               underline=0)
        cat_config_menu.add_command(label='京东',
                                    command=lambda: self.cat_web_config('jd'))
        cat_config_menu.add_command(label='天猫',
                                    command=lambda: self.cat_web_config('tm'))
        cat_config_menu.add_command(label='拼多多',
                                    command=lambda: self.cat_web_config('pdd'))
        cat_config_menu.add_command(label='苏宁',
                                    command=lambda: self.cat_web_config('sn'))
        cat_config_menu.add_command(
            label='eid & fp', command=lambda: self.cat_web_config('eid_fp'))

        edit_config_menu = tk.Menu(configmenu)
        configmenu.add_cascade(label='修改配置信息',
                               menu=edit_config_menu,
                               underline=0)
        edit_config_menu.add_command(
            label='京东', command=lambda: self.edit_web_config('jd'))
        edit_config_menu.add_command(
            label='天猫', command=lambda: self.edit_web_config('tm'))
        edit_config_menu.add_command(
            label='拼多多', command=lambda: self.edit_web_config('pdd'))
        edit_config_menu.add_command(
            label='苏宁', command=lambda: self.edit_web_config('sn'))
        edit_config_menu.add_command(
            label='eid & fp', command=lambda: self.edit_web_config('eid_fp'))

        helpmenu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label='帮助', menu=helpmenu)
        return menubar

    def web_selection(self):
        if self.isjd.get():
            print("选择京东")
        else:
            print("删除京东")

        if self.istm.get():
            print("选择天猫")
        else:
            print("删除天猫")

        if self.ispdd.get():
            print("选择品多多")
        else:
            print("删除品多多")

        if self.issn.get():
            print("选择苏宁")
        else:
            print("删除苏宁")

    def mySeckillWebSelect(self):
        """抢购网站选择
        选择网站复选框，京东、天猫、品多多、苏宁
        """
        l = tk.Label(self.win, text='选择平台', font=("黑体", 9))
        l.place(x=20, y=3)
        self.isjd = tk.BooleanVar()
        self.istm = tk.BooleanVar()
        self.ispdd = tk.BooleanVar()
        self.issn = tk.BooleanVar()
        b_jd = tk.Checkbutton(self.win,
                              text='京东',
                              variable=self.isjd,
                              onvalue=True,
                              offvalue=False,
                              command=self.web_selection)
        b_tm = tk.Checkbutton(self.win,
                              text='天猫',
                              variable=self.istm,
                              onvalue=True,
                              offvalue=False,
                              command=self.web_selection)
        b_pdd = tk.Checkbutton(self.win,
                               text='拼多多',
                               variable=self.ispdd,
                               onvalue=True,
                               offvalue=False,
                               command=self.web_selection)
        b_sn = tk.Checkbutton(self.win,
                              text='苏宁',
                              variable=self.issn,
                              onvalue=True,
                              offvalue=False,
                              command=self.web_selection)
        b_jd.place(x=20, y=25)
        b_tm.place(x=80, y=25)
        b_pdd.place(x=130, y=25)
        b_sn.place(x=200, y=25)

    def eid_fp_Config(self):
        """config信息
        展示当前config信息, 主要是eid, fp信息
        """
        eid_label = tk.Label(self.win,
                             text="eid",
                             bg="blue",
                             font=("黑体", 12),
                             width=5)
        eid_label.place(x=20, y=65)

        fp_label = tk.Label(self.win,
                            text='fp',
                            bg="blue",
                            font=("黑体", 12),
                            width=5)
        fp_label.place(x=20, y=90)

    def myQrCode(self):
        """展示二维码
        可以切换京东、天猫、拼多多、苏宁登陆二维码和小程序关注二维码
        """
        pass

    def myReserve(self):
        """预约按钮
        预约入口
        """
        res_button = tk.Button(self.win, text='预约', font=("黑体", 12), command=tmp)
        res_button.place(x=20, y=180)

    def mySeckill(self):
        """抢购按钮
        抢购入口
        """
        kill_button = tk.Button(self.win, text='抢购', font=("黑体", 12), command=tmp)
        kill_button.place(x=20, y=215)

    def mySeckillLog(self):
        """日志输出
        查看当前日志，方便了解当前的状态
        """
        pass

    def gui_run(self):
        """运行gui"""
        self.eid_fp_Config()
        self.mySeckillWebSelect()
        self.myReserve()
        self.mySeckill()
        self.win.config(menu=self.myMenu())
        self.win.mainloop()


if __name__ == '__main__':
    sgui = SeckillGui()
    sgui.gui_run()
