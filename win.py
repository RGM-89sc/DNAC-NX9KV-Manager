# -*- coding: utf-8 -*-

# 添加设备的时候假定用户输入的设备名称对于dnac和nx9kv都是唯一的标识，但还未实现逻辑上对设备名称的查重
# 当设备列表只有一个设备并删除后，设备列表为空但是Combobox中选中的元素文本不清空

import tkinter as tk
from tkinter import ttk
import sys
import os
import json

# Get the absolute path for the directory where this file is located "here"
here = os.path.abspath(os.path.dirname(__file__))

# Get the absolute path for the project / repository root
project_root = os.path.abspath(os.path.join(here, "../"))

# Extend the system path to include the project root and import the env files
sys.path.insert(0, project_root)

from device_model.dnac import DNAC
from device_model.nx9kv import Nx9kv

config = {
    'devices_config': {
        'dnac': [],
        'nx9kv': [],
    }
}

current_device = {}

# 创建窗口
window = tk.Tk()

window.title('DNAC&NX9KV Manager')

# 设定窗口的大小(长 * 宽)
window.geometry('700x600')

comvalue = tk.StringVar()  # 窗体自带的文本，新建一个值
devices_comboxlist = ttk.Combobox(window, textvariable=comvalue)  # 初始化

all_devices = config['devices_config']['dnac'] + config['devices_config']['nx9kv']
devices_comboxlist["values"] = [device['device_name'] for device in all_devices]


# nx9kv控制面板的组件开始######################################################################
nx9kv_control_cli_type_combobox = ttk.Combobox(window, textvariable=tk.StringVar())
nx9kv_control_cli_type_combobox["values"] = ['cli_show', 'cli_show_array', 'cli_show_ascii', 'cli_conf', 'bash']
nx9kv_control_cli_type_combobox.current(0)

nx9kv_control_label2 = tk.Label(window, text='返回结果：')
nx9kv_control_res_text_yScroll = tk.Scrollbar(window)
nx9kv_control_res_text_xScroll = tk.Scrollbar(window, orient=tk.HORIZONTAL)
nx9kv_control_res_text = tk.Text(window, width=50, height=10,
                                 yscrollcommand=nx9kv_control_res_text_yScroll.set,
                                 xscrollcommand=nx9kv_control_res_text_xScroll.set, wrap='none')
nx9kv_control_res_text_yScroll.config(command=nx9kv_control_res_text.yview)
nx9kv_control_res_text_xScroll.config(command=nx9kv_control_res_text.xview)


def exec_nx9kv_cli():
    global current_device
    nx9kv_control_res_text.delete('1.0', 'end')
    cli = nx9kv_control_cli_input.get('1.0', 'end')
    res = current_device['instance'].cli(nx9kv_control_cli_type_combobox.get(), cli.strip('\n'))
    nx9kv_control_res_text.insert('end', res)


nx9kv_control_label1 = tk.Label(window, text='CLI Command：')
nx9kv_control_cli_input = tk.Text(window, width=50, height=4)

nx9kv_control_button1 = tk.Button(window, text=' 执 行 ', command=exec_nx9kv_cli)
# nx9kv控制面板的组件结束########################################################################


# dnac控制面板的组件开始#########################################################################
dnac_control_label2 = tk.Label(window, text='返回结果：')
dnac_control_res_text_yScroll = tk.Scrollbar(window)
dnac_control_res_text_xScroll = tk.Scrollbar(window, orient=tk.HORIZONTAL)
dnac_control_res_text = tk.Text(window, width=50, height=10,
                                 yscrollcommand=dnac_control_res_text_yScroll.set,
                                 xscrollcommand=dnac_control_res_text_xScroll.set, wrap='none')
dnac_control_res_text_yScroll.config(command=dnac_control_res_text.yview)
dnac_control_res_text_xScroll.config(command=dnac_control_res_text.xview)


def get_url_for_dnac():
    global current_device
    dnac_control_res_text.delete('1.0', 'end')
    url = dnac_control_url_input.get('1.0', 'end')
    res = current_device['instance'].get_url(url.strip('\n'))
    dnac_control_res_text.insert('end', json.dumps(res, indent=2))


dnac_control_label1 = tk.Label(window, text='Url：')
dnac_control_url_input = tk.Text(window, width=50, height=4)

dnac_control_button1 = tk.Button(window, text=' 执 行 ', command=get_url_for_dnac)
# dnac控制面板的组件结束########################################################################


def delete_device():
    global config
    global all_devices
    global devices_comboxlist
    new_dnac_devices_list = []
    new_nx9kv_devices_list = []
    current_device_name = devices_comboxlist.get()
    for device in all_devices:
        if device['device_type'] == 'dnac':
            if device['device_name'] != current_device_name:
                new_dnac_devices_list.append(device)
        if device['device_type'] == 'nx9kv':
            if device['device_name'] != current_device_name:
                new_nx9kv_devices_list.append(device)
    config['devices_config']['dnac'] = new_dnac_devices_list
    config['devices_config']['nx9kv'] = new_nx9kv_devices_list

    all_devices = config['devices_config']['dnac'] + config['devices_config']['nx9kv']
    devices_comboxlist["values"] = [device['device_name'] for device in all_devices]
    try:
        devices_comboxlist.current(0)  # 选择第一个
        select_device()
    except Exception:
        pass


def select_device(*args):
    global all_devices
    global current_device
    global devices_comboxlist
    current_device_name = devices_comboxlist.get()
    for device in all_devices:
        if device['device_name'] == current_device_name:
            device_type = device['device_type']
            current_device = {
                'type': device_type,
                'instance': DNAC(device) if device_type == 'dnac' else (Nx9kv(device) if device_type == 'nx9kv' else None)
            }
            if device_type == 'dnac':
                dnac_control_label1.place(x=20, y=80)
                dnac_control_url_input.place(x=20, y=100)
                dnac_control_label2.place(x=20, y=220)
                dnac_control_button1.place(x=20, y=160)
                dnac_control_res_text_yScroll.place(x=375, y=240)
                dnac_control_res_text_xScroll.place(x=20, y=375)
                dnac_control_res_text.place(x=20, y=240)

                nx9kv_control_label1.place_forget()
                nx9kv_control_cli_input.place_forget()
                nx9kv_control_button1.place_forget()
                nx9kv_control_label2.place_forget()
                nx9kv_control_res_text_yScroll.place_forget()
                nx9kv_control_res_text_xScroll.place_forget()
                nx9kv_control_res_text.place_forget()
                nx9kv_control_cli_type_combobox.place_forget()
            if device_type == 'nx9kv':
                dnac_control_label1.place_forget()
                dnac_control_url_input.place_forget()
                dnac_control_label2.place_forget()
                dnac_control_button1.place_forget()
                dnac_control_res_text_yScroll.place_forget()
                dnac_control_res_text_xScroll.place_forget()
                dnac_control_res_text.place_forget()

                nx9kv_control_label1.place(x=20, y=80)
                nx9kv_control_cli_input.place(x=20, y=100)
                nx9kv_control_cli_type_combobox.place(x=20, y=165)
                nx9kv_control_button1.place(x=200, y=160)
                nx9kv_control_label2.place(x=20, y=220)
                nx9kv_control_res_text_yScroll.place(x=375, y=240)
                nx9kv_control_res_text_xScroll.place(x=20, y=300)
                nx9kv_control_res_text.place(x=20, y=240)
            return


try:
    devices_comboxlist.current(0)  # 选择第一个
    select_device()
except Exception:
    pass


devices_comboxlist.bind("<<ComboboxSelected>>", select_device)
tk.Label(window, text='选择设备：').place(x=20, y=20)
devices_comboxlist.place(x=140, y=20)
tk.Button(window, text='删除设备', command=delete_device).place(x=350, y=15)


def open_add_dnac_win():
    global window
    add_dnac_win = tk.Toplevel(window)
    add_dnac_win.geometry('500x400')
    add_dnac_win.title('添加设备(DNAC)')

    name = tk.StringVar()
    name.set('dnac')
    tk.Label(add_dnac_win, text='Device Name:').place(x=20, y=20)
    entry_name = tk.Entry(add_dnac_win, textvariable=name)
    entry_name.place(x=140, y=20)

    host = tk.StringVar()
    host.set('sandboxdnac.cisco.com')  # 将最初显示定为'sandboxdnac.cisco.com'
    tk.Label(add_dnac_win, text='Host:').place(x=20, y=60)
    entry_host = tk.Entry(add_dnac_win, textvariable=host)
    entry_host.place(x=140, y=60)

    port = tk.StringVar()
    port.set('443')
    tk.Label(add_dnac_win, text='Port:').place(x=20, y=100)
    entry_port = tk.Entry(add_dnac_win, textvariable=port)
    entry_port.place(x=140, y=100)

    username = tk.StringVar()
    username.set('devnetuser')
    tk.Label(add_dnac_win, text='Username:').place(x=20, y=140)
    entry_username = tk.Entry(add_dnac_win, textvariable=username)
    entry_username.place(x=140, y=140)

    password = tk.StringVar()
    password.set('Cisco123!')
    tk.Label(add_dnac_win, text='Password:').place(x=20, y=180)
    entry_password = tk.Entry(add_dnac_win, textvariable=password)
    entry_password.place(x=140, y=180)

    def cancel():
        add_dnac_win.destroy()

    def confirm():
        global config
        global devices_comboxlist
        global all_devices
        config['devices_config']['dnac'].append({
            'device_name': entry_name.get(),
            'device_type': 'dnac',
            'protocol': 'https',
            'host': entry_host.get(),
            'port': int(entry_port.get()),
            'username': entry_username.get(),
            'password': entry_password.get(),
            'proxy': {
                'proxy_settings': {
                    'httpProxyHost': '',
                    'httpsProxyHost': '',
                    'httpProxyPort': '',
                    'httpsProxyPort': '',
                    'httpNonProxyHosts': '',
                },
                'username': '',
                'password': ''
            }
        })

        devices_old_len = len(all_devices)
        all_devices = config['devices_config']['dnac'] + config['devices_config']['nx9kv']
        devices_comboxlist["values"] = [device['device_name'] for device in all_devices]
        if devices_old_len == 0 and len(all_devices) == 1:  # 如果当前是第一次添加设备
            try:
                devices_comboxlist.current(0)  # 选择第一个
                select_device()
            except Exception:
                pass

        add_dnac_win.destroy()

    tk.Button(add_dnac_win, text=' 取 消 ', command=cancel).place(x=140, y=220)
    tk.Button(add_dnac_win, text=' 确 认 ', command=confirm).place(x=200, y=220)


def open_add_nx9kv_win():
    global window
    add_nx9kv_win = tk.Toplevel(window)
    add_nx9kv_win.geometry('500x400')
    add_nx9kv_win.title('添加设备(NX9KV)')

    name = tk.StringVar()
    name.set('nx9kv1')
    tk.Label(add_nx9kv_win, text='Device Name:').place(x=20, y=20)
    entry_name = tk.Entry(add_nx9kv_win, textvariable=name)
    entry_name.place(x=140, y=20)

    host = tk.StringVar()
    host.set('sbx-nxos-mgmt.cisco.com')
    tk.Label(add_nx9kv_win, text='Host:').place(x=20, y=60)
    entry_host = tk.Entry(add_nx9kv_win, textvariable=host)
    entry_host.place(x=140, y=60)

    username = tk.StringVar()
    username.set('admin')
    tk.Label(add_nx9kv_win, text='Username:').place(x=20, y=100)
    entry_username = tk.Entry(add_nx9kv_win, textvariable=username)
    entry_username.place(x=140, y=100)

    password = tk.StringVar()
    password.set('Admin_1234!')
    tk.Label(add_nx9kv_win, text='Password:').place(x=20, y=140)
    entry_password = tk.Entry(add_nx9kv_win, textvariable=password)
    entry_password.place(x=140, y=140)

    def cancel():
        add_nx9kv_win.destroy()

    def confirm():
        global config
        global all_devices
        config['devices_config']['nx9kv'].append({
            'device_name': entry_name.get(),
            'device_type': 'nx9kv',
            'protocol': 'https',
            'host': entry_host.get(),
            'aaa_attributes': {
                'name': entry_username.get(),
                'pwd': entry_password.get()
            }
        })

        devices_old_len = len(all_devices)
        all_devices = config['devices_config']['dnac'] + config['devices_config']['nx9kv']
        devices_comboxlist["values"] = [device['device_name'] for device in all_devices]
        if devices_old_len == 0 and len(all_devices) == 1:  # 如果当前是第一次添加设备
            try:
                devices_comboxlist.current(0)  # 选择第一个
                select_device()
            except Exception:
                pass

        add_nx9kv_win.destroy()

    tk.Button(add_nx9kv_win, text=' 取 消 ', command=cancel).place(x=140, y=180)
    tk.Button(add_nx9kv_win, text=' 确 认 ', command=confirm).place(x=200, y=180)


# 创建一个菜单栏
menubar = tk.Menu(window)
filemenu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label='设备', menu=filemenu)
filemenu.add_command(label='添加设备(DNAC)', command=open_add_dnac_win)
filemenu.add_command(label='添加设备(NX9KV)', command=open_add_nx9kv_win)
window.config(menu=menubar)

# 主窗口循环显示
window.mainloop()
