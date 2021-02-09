# -*- encoding: utf-8 -*-

from tkinter import *
from tkinter import messagebox
from tkinter import simpledialog
from tkinter import filedialog



def ui_process():
    """gui"""
    root = Tk()
    root.geometry("800x800+500+500")

    # 标签
    L_title = Label(root, text='测试标题0')
    L_title.config(font='Helvetica -15 bold', fg='blue')
    L_title.place(x=150, y=20, anchor="center")
    L_author = Label(root, text='作者:longjy')
    L_author.config(font="Helvetica -15 bold", fg='blue')
    L_author.place(x=250, y=380)

    # 按钮
    B_0 = Button(root, text="对话框", command=CreatDialog)
    B_0.place(x=90, y=200)
    B_1 = Button(root, text="确定", command=print)
    B_1.place(x=200, y=200)
    B_ok = Button(root, text='创建', command=lambda:button_process(root))
    B_ok.place(x=250, y=200)
    B_no = Button(root, text='取消')
    B_no.place(x=300, y=200)

    # 单选按钮
    v = IntVar()
    R_one = Radiobutton(
        root,
        text='One',
        variable=v,
        value=1,
        command=lambda:Print_b(1).place(x=60, y=150)
    )

    R_two = Radiobutton(
        root,
        text='two',
        variable=v,
        value=2,
        command=lambda:Print_b(2)
    )

    # 滑块
    W = Scale(
        root,
        from_=0,
        orient=HORIZONTAL  # HORIZONTAL 横向, 默认纵向
    )
    W.place(x=50, y=300)
    print(W.get())  # 获取滑块值

    # 菜单栏
    menu = Menu(root)
    filemenu = Menu(menu, tearoff=0)
    filemenu.add_command(label="Open", command=OpenFile)
    filemenu.add_command(label="Save", command=SaveFile)
    filemenu.add_separator()  # 分割线
    filemenu.add_command(label="Exit", command=root.quit)
    filemenu.add_cascade(label="File", menu=filemenu)
    root.config(menu=menu)

    mainloop()


def CreatDialog():
    """创建输入框"""
    world = simpledialog.askstring('Python Tkinter', 'Input String', initialvalue='Python3')
    print(world)


def button_process(root):
    messagebox.askokcancel("Python Tkinter", "确认创建窗口?")
    messagebox.askquestion("Python Tkinter", "确认创建窗口?")
    messagebox.askyesno("Python Tkinter", "是否创建窗口")
    messagebox.showerror("Python Tkinter", "未知错误")
    messagebox.showinfo("Python Tkinter", "hello world")
    messagebox.showwarning("Python Tkinter", "我擦")
    root1 = Toplevel(root)  # 创建子窗口


def Print_b(mes):
    print(mes)


def OpenFile():
    f = filedialog.askopenfilename(title='打开文件',
                                   filetypes=[('Python', '*py *.pyw'),('All File', '*')])
    print(f)

def SaveFile():
    f = filedialog.asksaveasfilename(title='保存文件',
                                     initialdir='/home/longjy',
                                     initialfile='hello.py'
                                     )








if __name__ == '__main__':
    print("开始")
    ui_process()



