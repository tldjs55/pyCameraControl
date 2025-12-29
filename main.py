#!/usr/bin/env python3
"""
pyCameraControl Interface
Requirements:
pip install gphoto2 pillow
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import queue
import os
import time
from datetime import datetime
from PIL import Image, ImageTk
import gphoto2 as gp
import logging

class CameraControlPro:
    def __init__(self):
        # 初始化主視窗
        self.root = tk.Tk()
        self.root.title("pyCameraControl")
        self.root.geometry("1200x820")
        self.root.configure(bg='#f8f9fa')
        self.root.resizable(True, True)
        
        # 相機相關變數
        self.camera = None
        self.context = gp.Context()
        self.connected = False
        self.camera_model = ""
        self.setting_in_progress = False  # 標記設定是否正在進行中
        
        # 通訊佇列
        self.photo_queue = queue.Queue()
        self.status_queue = queue.Queue()
        self.capture_queue = queue.Queue()  # 新增拍攝任務佇列
        
        # 設定變數
        self.save_directory = "./photos"
        self.setup_variables()
        
        # 建立介面
        self.create_main_layout()
        self.setup_logging()
        self.check_queues()
        
    def setup_variables(self):
        """初始化所有變數"""
        # 相機設定變數
        self.iso_var = tk.StringVar(value="")
        self.aperture_var = tk.StringVar(value="")
        self.shutter_var = tk.StringVar(value="")
        self.white_balance_var = tk.StringVar(value="")
        self.image_quality_var = tk.StringVar(value="")
        self.exposure_compensation_var = tk.StringVar(value="")
        self.metering_mode_var = tk.StringVar(value="")
        self.focus_mode_var = tk.StringVar(value="")
        
        # 拍攝設定變數
        self.burst_count_var = tk.StringVar(value="1")
        self.interval_var = tk.StringVar(value="0")
        self.capture_mode_var = tk.StringVar(value="single")
        
        # 檔案管理變數
        self.save_path_var = tk.StringVar(value=self.save_directory)
        self.filename_prefix_var = tk.StringVar(value="IMG")
        
        # 拍攝目標變數
        self.capture_target_var = tk.StringVar(value="")
        
        # 快門速度對應表（顯示值 -> 原始值）
        self.shutter_speed_map = {}
        
        
    def setup_logging(self):
        """設定日誌記錄"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
    def create_main_layout(self):
        """建立主要布局結構"""
        # 建立主要容器
        main_container = tk.Frame(self.root, bg='#f8f9fa')
        main_container.pack(fill='both', expand=True, padx=15, pady=15)
        
        # 頂部標題欄
        self.create_header(main_container)
        
        # 主要內容區域 - 使用Grid布局
        content_frame = tk.Frame(main_container, bg='#f8f9fa')
        content_frame.pack(fill='both', expand=True, pady=(15, 0))
        
        # 配置Grid權重
        content_frame.grid_columnconfigure(0, weight=1)  # 左欄
        content_frame.grid_columnconfigure(1, weight=1)  # 中欄
        content_frame.grid_columnconfigure(2, weight=2)  # 右欄 (預覽區域較大)
        content_frame.grid_rowconfigure(0, weight=1)
        
        # 左欄：相機連接與設定
        self.create_camera_section(content_frame)
        
        # 中欄：拍攝控制
        self.create_capture_section(content_frame)
        
        # 右欄：預覽與檔案管理
        self.create_preview_section(content_frame)
        
        
    def create_header(self, parent):
        """建立頂部標題欄"""
        header_frame = tk.Frame(parent, bg='#ffffff', relief='solid', bd=1)
        header_frame.pack(fill='x', pady=(0, 15))
        
        # 左側標題
        title_frame = tk.Frame(header_frame, bg='#ffffff')
        title_frame.pack(side='left', padx=20, pady=15)
        
        title_label = tk.Label(
            title_frame,
            text="RATC pyCameraControl",
            font=('Arial', 18, 'bold'),
            bg='#ffffff',
            fg='#2c3e50'
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            title_frame,
            text="photography control interface",
            font=('Arial', 10),
            bg='#ffffff',
            fg='#7f8c8d'
        )
        subtitle_label.pack()
        
        # 右側連接狀態
        status_frame = tk.Frame(header_frame, bg='#ffffff')
        status_frame.pack(side='right', padx=20, pady=15)
        
        tk.Label(
            status_frame,
            text="Connection Status:",
            font=('Arial', 10, 'bold'),
            bg='#ffffff',
            fg='#2c3e50'
        ).pack(side='left', padx=(0, 10))
        
        self.connection_status = tk.Label(
            status_frame,
            text="● Disconnected",
            font=('Arial', 10, 'bold'),
            bg='#ffffff',
            fg='#e74c3c'
        )
        self.connection_status.pack(side='left')
        
    def create_camera_section(self, parent):
        """建立相機連接與設定區域"""
        # 主容器
        camera_frame = tk.Frame(parent, bg='#ffffff', relief='solid', bd=1)
        camera_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 8))
        
        # === 1. 相機連接區塊 ===
        connection_block = self.create_section_block(camera_frame, "Camera Connection")
        
        # 相機資訊顯示
        self.camera_info_frame = tk.Frame(connection_block, bg='#ffffff')
        self.camera_info_frame.pack(fill='x', pady=(0, 15))
        
        self.camera_info_label = tk.Label(
            self.camera_info_frame,
            text="No camera connected",
            font=('Arial', 10),
            bg='#ffffff',
            fg='#7f8c8d',
            wraplength=280
        )
        self.camera_info_label.pack()
        
        # 連接按鈕
        self.connect_button = tk.Button(
            connection_block,
            text="Connect Camera",
            command=self.toggle_connection,
            font=('Arial', 11, 'bold'),
            bg='#e9ecef',
            fg='#495057',
            relief='flat',
            padx=30,
            pady=8,
            cursor='hand2'
        )
        self.connect_button.pack(fill='x', pady=(0, 10))
        
        # 相機設定按鈕
        self.settings_button = tk.Button(
            connection_block,
            text="Show Camera Settings",
            command=self.show_camera_settings,
            font=('Arial', 10),
            bg='#e9ecef',
            fg='#495057',
            relief='flat',
            padx=20,
            pady=6,
            cursor='hand2',
            state='disabled'
        )
        self.settings_button.pack(fill='x')
        
        # === 2. 曝光設定區塊 ===
        exposure_block = self.create_section_block(camera_frame, "Exposure Settings")
        
        # ISO設定
        iso_frame = self.create_setting_row(exposure_block, "ISO")
        self.iso_combo = ttk.Combobox(
            iso_frame,
            textvariable=self.iso_var,
            values=[],
            state="readonly",
            width=12
        )
        self.iso_combo.pack(side='right')
        self.iso_combo.bind('<<ComboboxSelected>>', lambda e: self.root.after_idle(lambda: self.on_setting_change('iso', self.iso_var.get())))
        
        # 光圈設定
        aperture_frame = self.create_setting_row(exposure_block, "Aperture")
        self.aperture_combo = ttk.Combobox(
            aperture_frame,
            textvariable=self.aperture_var,
            values=[],
            state="readonly",
            width=12
        )
        self.aperture_combo.pack(side='right')
        self.aperture_combo.bind('<<ComboboxSelected>>', lambda e: self.root.after_idle(lambda: self.on_setting_change('f-number', self.aperture_var.get())))
        
        # 快門速度設定
        shutter_frame = self.create_setting_row(exposure_block, "Shutter Speed")
        self.shutter_combo = ttk.Combobox(
            shutter_frame,
            textvariable=self.shutter_var,
            values=[],
            state="readonly",
            width=12
        )
        self.shutter_combo.pack(side='right')
        self.shutter_combo.bind('<<ComboboxSelected>>', lambda e: self.root.after_idle(lambda: self.on_setting_change('shutterspeed', self.shutter_var.get())))
        
        # === 3. 相機設定區塊 ===
        settings_block = self.create_section_block(camera_frame, "Camera Settings")
        
        # 白平衡設定
        wb_frame = self.create_setting_row(settings_block, "White Balance")
        self.wb_combo = ttk.Combobox(
            wb_frame,
            textvariable=self.white_balance_var,
            values=[],
            state="readonly",
            width=12
        )
        self.wb_combo.pack(side='right')
        self.wb_combo.bind('<<ComboboxSelected>>', lambda e: self.root.after_idle(lambda: self.on_setting_change('whitebalance', self.white_balance_var.get())))
        
        # 影像品質設定
        quality_frame = self.create_setting_row(settings_block, "Image Quality")
        self.quality_combo = ttk.Combobox(
            quality_frame,
            textvariable=self.image_quality_var,
            values=[],
            state="readonly",
            width=12
        )
        self.quality_combo.pack(side='right')
        self.quality_combo.bind('<<ComboboxSelected>>', lambda e: self.root.after_idle(lambda: self.on_setting_change('imagequality', self.image_quality_var.get())))
        
        # 曝光補償設定
        exp_comp_frame = self.create_setting_row(settings_block, "Exposure Compensation")
        self.exp_comp_combo = ttk.Combobox(
            exp_comp_frame,
            textvariable=self.exposure_compensation_var,
            values=[],
            state="readonly",
            width=12
        )
        self.exp_comp_combo.pack(side='right')
        self.exp_comp_combo.bind('<<ComboboxSelected>>', lambda e: self.root.after_idle(lambda: self.on_setting_change('exposurecompensation', self.exposure_compensation_var.get())))
        
        # 注意：測光模式和對焦模式的支援因相機而異
        # 建議使用時先用 gphoto2 --list-config 確認支援的參數
        
        # 測光模式設定
        metering_frame = self.create_setting_row(settings_block, "Metering Mode")
        self.metering_combo = ttk.Combobox(
            metering_frame,
            textvariable=self.metering_mode_var,
            values=[],
            state="readonly",
            width=12
        )
        self.metering_combo.pack(side='right')
        self.metering_combo.bind('<<ComboboxSelected>>', lambda e: self.root.after_idle(lambda: self.on_setting_change('meteringmode', self.metering_mode_var.get())))
        
        # 對焦模式設定
        focus_frame = self.create_setting_row(settings_block, "Focus Mode")
        self.focus_combo = ttk.Combobox(
            focus_frame,
            textvariable=self.focus_mode_var,
            values=[],
            state="readonly",
            width=12
        )
        self.focus_combo.pack(side='right')
        self.focus_combo.bind('<<ComboboxSelected>>', lambda e: self.root.after_idle(lambda: self.on_setting_change('focusmode', self.focus_mode_var.get())))
        
        # 拍攝目標設定（SD卡 vs 記憶體）
        target_frame = self.create_setting_row(settings_block, "Capture Target")
        self.target_combo = ttk.Combobox(
            target_frame,
            textvariable=self.capture_target_var,
            values=[],
            state="readonly",
            width=12
        )
        self.target_combo.pack(side='right')
        self.target_combo.bind('<<ComboboxSelected>>', lambda e: self.root.after_idle(lambda: self.on_setting_change('capturetarget', self.capture_target_var.get())))
        
    def create_capture_section(self, parent):
        """建立拍攝控制區域"""
        # 主容器
        capture_frame = tk.Frame(parent, bg='#ffffff', relief='solid', bd=1)
        capture_frame.grid(row=0, column=1, sticky='nsew', padx=8)
        
        # === 1. 拍攝控制區塊 ===
        control_block = self.create_section_block(capture_frame, "Capture Control")
        
        # 主要拍攝按鈕
        self.capture_button = tk.Button(
            control_block,
            text="CAPTURE",
            command=self.capture_photo,
            font=('Arial', 16, 'bold'),
            bg='#e9ecef',
            fg='#495057',
            relief='flat',
            padx=40,
            pady=20,
            cursor='hand2',
            state='disabled'
        )
        self.capture_button.pack(fill='x', pady=(0, 15))
        
        
        # === 2. 拍攝模式區塊 ===
        mode_block = self.create_section_block(capture_frame, "Capture Modes")
        
        # 拍攝模式選擇
        mode_frame = tk.Frame(mode_block, bg='#ffffff')
        mode_frame.pack(fill='x', pady=(0, 15))
        
        modes = [("Single Shot", "single"), ("Burst Mode", "burst")]
        
        for i, (text, value) in enumerate(modes):
            rb = tk.Radiobutton(
                mode_frame,
                text=text,
                variable=self.capture_mode_var,
                value=value,
                font=('Arial', 10),
                bg='#ffffff',
                fg='#2c3e50',
                selectcolor='#3498db',
                command=self.on_mode_change
            )
            rb.pack(anchor='w', pady=2)
        
        # === 3. 拍攝參數區塊 ===
        params_block = self.create_section_block(capture_frame, "Capture Parameters")
        
        # 連拍數量
        burst_frame = self.create_setting_row(params_block, "Burst Count")
        burst_spinbox = tk.Spinbox(
            burst_frame,
            from_=1,
            to=999,
            textvariable=self.burst_count_var,
            width=10,
            font=('Arial', 10)
        )
        burst_spinbox.pack(side='right')
        
        # 間隔時間
        interval_frame = self.create_setting_row(params_block, "Interval (sec)")
        interval_spinbox = tk.Spinbox(
            interval_frame,
            from_=0,
            to=3600,
            textvariable=self.interval_var,
            width=10,
            font=('Arial', 10)
        )
        interval_spinbox.pack(side='right')
        
        # === 4. 拍攝狀態區塊 ===
        status_block = self.create_section_block(capture_frame, "Capture Status")
        
        self.capture_status_label = tk.Label(
            status_block,
            text="Ready to capture",
            font=('Arial', 10),
            bg='#ffffff',
            fg='#27ae60',
            wraplength=250
        )
        self.capture_status_label.pack(pady=10)
        
        # 進度條
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            status_block,
            variable=self.progress_var,
            maximum=100
        )
        self.progress_bar.pack(fill='x', pady=5)
        
    def create_preview_section(self, parent):
        """建立預覽與檔案管理區域"""
        # 主容器
        preview_frame = tk.Frame(parent, bg='#ffffff', relief='solid', bd=1)
        preview_frame.grid(row=0, column=2, sticky='nsew', padx=(8, 0))
        
        # === 1. 預覽區塊 ===
        preview_block = self.create_section_block(preview_frame, "Image Preview", expand=True)
        
        # 預覽畫布
        self.preview_canvas = tk.Canvas(
            preview_block,
            bg='#ecf0f1',
            relief='sunken',
            bd=1,
            highlightthickness=0
        )
        self.preview_canvas.pack(fill='both', expand=True, pady=(0, 15))
        
        # === 2. 檔案管理區塊 ===
        file_block = self.create_section_block(preview_frame, "File Management")
        
        # 儲存路徑設定
        path_label_frame = tk.Frame(file_block, bg='#ffffff')
        path_label_frame.pack(fill='x', pady=(0, 5))
        
        tk.Label(
            path_label_frame,
            text="Save Location:",
            font=('Arial', 10, 'bold'),
            bg='#ffffff',
            fg='#2c3e50'
        ).pack(anchor='w')
        
        path_frame = tk.Frame(file_block, bg='#ffffff')
        path_frame.pack(fill='x', pady=(0, 15))
        
        self.path_entry = tk.Entry(
            path_frame,
            textvariable=self.save_path_var,
            font=('Arial', 9),
            relief='solid',
            bd=1
        )
        self.path_entry.pack(side='left', fill='x', expand=True, padx=(0, 5))
        
        browse_button = tk.Button(
            path_frame,
            text="Browse",
            command=self.browse_directory,
            font=('Arial', 9),
            bg='#e9ecef',
            fg='#495057',
            relief='flat',
            padx=15,
            pady=2,
            cursor='hand2'
        )
        browse_button.pack(side='right')
        
        # 檔名前綴設定
        prefix_frame = self.create_setting_row(file_block, "Filename Prefix")
        prefix_entry = tk.Entry(
            prefix_frame,
            textvariable=self.filename_prefix_var,
            width=12,
            font=('Arial', 9),
            relief='solid',
            bd=1
        )
        prefix_entry.pack(side='right')
        
        # 檔案操作按鈕
        file_actions = tk.Frame(file_block, bg='#ffffff')
        file_actions.pack(fill='x', pady=(15, 0))
        
        tk.Button(
            file_actions,
            text="Open Folder",
            command=self.open_photo_folder,
            font=('Arial', 10),
            bg='#e9ecef',
            fg='#495057',
            relief='flat',
            padx=15,
            pady=8,
            cursor='hand2'
        ).pack(fill='x', pady=(0, 5))
        
        tk.Button(
            file_actions,
            text="Delete Last Photo",
            command=self.delete_last_photo,
            font=('Arial', 10),
            bg='#e9ecef',
            fg='#495057',
            relief='flat',
            padx=15,
            pady=8,
            cursor='hand2'
        ).pack(fill='x')
        
        
    def create_section_block(self, parent, title, expand=False):
        """建立區段區塊"""
        # 外框容器
        container = tk.Frame(parent, bg='#ffffff')
        if expand:
            container.pack(fill='both', expand=True, padx=15, pady=(15, 10))
        else:
            container.pack(fill='x', padx=15, pady=(15, 10))
        
        # 標題
        title_label = tk.Label(
            container,
            text=title,
            font=('Arial', 12, 'bold'),
            bg='#ffffff',
            fg='#2c3e50'
        )
        title_label.pack(anchor='w', pady=(0, 10))
        
        # 分隔線
        separator = tk.Frame(container, height=1, bg='#ecf0f1')
        separator.pack(fill='x', pady=(0, 15))
        
        # 內容區域
        content_frame = tk.Frame(container, bg='#ffffff')
        if expand:
            content_frame.pack(fill='both', expand=True)
        else:
            content_frame.pack(fill='x')
        
        return content_frame
        
    def create_setting_row(self, parent, label_text):
        """建立設定行"""
        frame = tk.Frame(parent, bg='#ffffff')
        frame.pack(fill='x', pady=5)
        
        label = tk.Label(
            frame,
            text=label_text + ":",
            font=('Arial', 10),
            bg='#ffffff',
            fg='#2c3e50'
        )
        label.pack(side='left')
        
        return frame
    
    def find_camera_setting(self, config, setting_names, prefix="", seen_paths=None):
        """遞歸尋找相機設定"""
        if seen_paths is None:
            seen_paths = set()
        
        for i in range(config.count_children()):
            try:
                child = config.get_child(i)
                child_name = child.get_name()
                full_path = f"{prefix}/{child_name}" if prefix else child_name
                
                # 避免重複處理
                if full_path in seen_paths:
                    continue
                seen_paths.add(full_path)
                
                # 檢查是否是我們要找的設定
                if child_name in setting_names:
                    try:
                        # 驗證這個設定是否有選項
                        if child.count_choices() > 0:
                            return (full_path, child)
                    except:
                        pass
                
                # 如果有子設定，遞歸搜尋
                if child.count_children() > 0:
                    result = self.find_camera_setting(child, setting_names, full_path, seen_paths)
                    if result:
                        return result
                        
            except:
                continue
        
        return None
        
    def check_camera_capabilities(self):
        """檢查相機支援的設定能力"""
        if not self.camera:
            return
            
        try:
            config = self.camera.get_config(self.context)
            
            # 檢查白平衡設定
            try:
                wb_config = config.get_child_by_name('whitebalance')
                wb_choices = []
                for i in range(wb_config.count_choices()):
                    wb_choices.append(wb_config.get_choice(i))
                
                # 更新白平衡選項
                if wb_choices:
                    self.root.after_idle(lambda: self.update_wb_choices(wb_choices))
                    self.status_queue.put(f"Found {len(wb_choices)} white balance options")
                    
            except gp.GPhoto2Error:
                pass  # 相機不支援此設定
            
            # 檢查ISO設定
            try:
                iso_config = config.get_child_by_name('iso')
                iso_choices = []
                current_iso = iso_config.get_value()
                for i in range(iso_config.count_choices()):
                    iso_choices.append(iso_config.get_choice(i))
                
                # 更新ISO選項
                if iso_choices:
                    self.root.after_idle(lambda choices=iso_choices, current=current_iso: self.update_iso_choices(choices, current))
                    
            except gp.GPhoto2Error:
                pass
                
            # 檢查光圈設定
            try:
                aperture_config = config.get_child_by_name('f-number')
                aperture_choices = []
                current_aperture = aperture_config.get_value()
                for i in range(aperture_config.count_choices()):
                    aperture_choices.append(aperture_config.get_choice(i))
                
                # 更新光圈選項
                if aperture_choices:
                    self.root.after_idle(lambda choices=aperture_choices, current=current_aperture: self.update_aperture_choices(choices, current))
                    
            except gp.GPhoto2Error:
                pass
                
            # 檢查快門速度設定
            try:
                shutter_config = config.get_child_by_name('shutterspeed')
                shutter_choices = []
                current_shutter = shutter_config.get_value()  # 獲取當前值
                for i in range(shutter_config.count_choices()):
                    shutter_choices.append(shutter_config.get_choice(i))
                
                # 更新快門速度選項
                if shutter_choices:
                    self.root.after_idle(lambda choices=shutter_choices, current=current_shutter: self.update_shutter_choices(choices, current))
                    
            except gp.GPhoto2Error:
                pass
                
            # 檢查影像品質設定
            try:
                quality_config = config.get_child_by_name('imagequality')
                quality_choices = []
                for i in range(quality_config.count_choices()):
                    quality_choices.append(quality_config.get_choice(i))
                
                # 更新影像品質選項
                if quality_choices:
                    self.root.after_idle(lambda: self.update_quality_choices(quality_choices))
                    
            except gp.GPhoto2Error:
                pass
                
            # 檢查曝光補償設定
            try:
                exp_comp_config = config.get_child_by_name('exposurecompensation')
                exp_comp_choices = []
                for i in range(exp_comp_config.count_choices()):
                    exp_comp_choices.append(exp_comp_config.get_choice(i))
                
                # 更新曝光補償選項
                if exp_comp_choices:
                    self.root.after_idle(lambda: self.update_exp_comp_choices(exp_comp_choices))
                    
            except gp.GPhoto2Error:
                pass
                
            # 檢查測光模式設定
            try:
                metering_config = config.get_child_by_name('meteringmode')
                metering_choices = []
                for i in range(metering_config.count_choices()):
                    metering_choices.append(metering_config.get_choice(i))
                
                # 更新測光模式選項
                if metering_choices:
                    self.root.after_idle(lambda: self.update_metering_choices(metering_choices))
                    
            except gp.GPhoto2Error:
                pass
                
            # 檢查對焦模式設定
            try:
                focus_config = config.get_child_by_name('focusmode')
                focus_choices = []
                for i in range(focus_config.count_choices()):
                    focus_choices.append(focus_config.get_choice(i))
                
                # 更新對焦模式選項
                if focus_choices:
                    self.root.after_idle(lambda: self.update_focus_choices(focus_choices))
                    
            except gp.GPhoto2Error:
                pass
                
            # 檢查拍攝目標設定
            try:
                target_config = config.get_child_by_name('capturetarget')
                target_choices = []
                current_target = target_config.get_value()
                for i in range(target_config.count_choices()):
                    target_choices.append(target_config.get_choice(i))
                
                # 更新拍攝目標選項
                if target_choices:
                    self.root.after_idle(lambda choices=target_choices, current=current_target: self.update_capture_target_choices(choices, current))
                    self.status_queue.put(f"Found capture targets: {', '.join(target_choices)}")
                    
            except gp.GPhoto2Error:
                self.status_queue.put("Camera doesn't support capture target selection")
                
        except Exception as e:
            self.status_queue.put(f"Capability check failed: {str(e)}")
    
    def update_wb_choices(self, choices):
        """更新白平衡選項"""
        self.wb_combo['values'] = choices
        if choices and self.white_balance_var.get() not in choices:
            self.white_balance_var.set(choices[0])
    
    def update_iso_choices(self, choices, current_value=None):
        """更新ISO選項"""
        self.iso_combo['values'] = choices
        if current_value and current_value in choices:
            self.iso_var.set(current_value)
        elif choices:
            self.iso_var.set(choices[0])
    
    def update_aperture_choices(self, choices, current_value=None):
        """更新光圈選項"""
        self.aperture_combo['values'] = choices
        if current_value and current_value in choices:
            self.aperture_var.set(current_value)
        elif choices:
            self.aperture_var.set(choices[0])
    
    def update_shutter_choices(self, choices, current_value=None):
        """更新快門速度選項"""
        # 清空之前的對應表
        self.shutter_speed_map = {}
        
        # 轉換選項為攝影格式並建立對應表
        display_choices = []
        for original_value in choices:
            display_value = self.convert_shutter_speed_to_display(original_value)
            display_choices.append(display_value)
            self.shutter_speed_map[display_value] = original_value
        
        self.shutter_combo['values'] = display_choices
        
        # 設定當前值
        if current_value and current_value in choices:
            # 使用相機的當前快門速度
            current_display = self.convert_shutter_speed_to_display(current_value)
            self.shutter_var.set(current_display)
        elif choices:
            # 如果沒有當前值，使用第一個選項
            first_display = self.convert_shutter_speed_to_display(choices[0])
            self.shutter_var.set(first_display)
    
    def update_quality_choices(self, choices):
        """更新影像品質選項"""
        self.quality_combo['values'] = choices
        if choices and self.image_quality_var.get() not in choices:
            self.image_quality_var.set(choices[0])
    
    def update_exp_comp_choices(self, choices):
        """更新曝光補償選項"""
        self.exp_comp_combo['values'] = choices
        if choices and self.exposure_compensation_var.get() not in choices:
            self.exposure_compensation_var.set(choices[0])
    
    def update_metering_choices(self, choices):
        """更新測光模式選項"""
        self.metering_combo['values'] = choices
        if choices and self.metering_mode_var.get() not in choices:
            self.metering_mode_var.set(choices[0])
    
    def update_focus_choices(self, choices):
        """更新對焦模式選項"""
        self.focus_combo['values'] = choices
        if choices and self.focus_mode_var.get() not in choices:
            self.focus_mode_var.set(choices[0])
    
    def update_capture_target_choices(self, choices, current_value):
        """更新拍攝目標選項"""
        self.target_combo['values'] = choices
        self.capture_target_var.set(current_value)
    
    def convert_shutter_speed_to_display(self, gphoto_value):
        """將 gPhoto2 快門速度格式轉換為攝影格式顯示"""
        try:
            # 處理常見的 gPhoto2 快門速度格式
            value_str = str(gphoto_value).strip()
            
            # 如果已經是分數格式，直接返回
            if '/' in value_str:
                return value_str
            
            # 如果是特殊值，直接返回
            if value_str.lower() in ['bulb', 'sync', 'time']:
                return value_str
                
            # 處理帶有 "s" 後綴的格式（如 "0.0001s"）
            if value_str.endswith('s'):
                try:
                    seconds = float(value_str[:-1])  # 移除 "s" 後轉換
                except ValueError:
                    return value_str
            else:
                # 嘗試直接轉換為浮點數
                try:
                    seconds = float(value_str)
                except ValueError:
                    return value_str
            
            # 大於等於1秒的快門速度
            if seconds >= 1:
                return f"{int(seconds)}\"" if seconds == int(seconds) else f"{seconds:.1f}\""
            
            # 小於1秒的快門速度轉換為分數
            if seconds > 0:
                # 計算分母
                denominator = round(1 / seconds)
                return f"1/{denominator}"
            
            return value_str
            
        except Exception:
            return str(gphoto_value)
    
    def convert_display_to_shutter_speed(self, display_value):
        """將攝影格式顯示轉換回 gPhoto2 快門速度格式"""
        try:
            value_str = str(display_value).strip()
            
            # 如果是特殊值，直接返回
            if value_str.lower() in ['bulb', 'sync', 'time']:
                return value_str
            
            # 如果是秒數格式 (如 '2"' 或 '2.5"')
            if value_str.endswith('"'):
                seconds_str = value_str[:-1]
                return f"{seconds_str}s"
            
            # 如果是分數格式 (如 "1/125")
            if '/' in value_str:
                parts = value_str.split('/')
                if len(parts) == 2:
                    try:
                        numerator = float(parts[0])
                        denominator = float(parts[1])
                        result = numerator / denominator
                        return f"{result}s"
                    except ValueError:
                        pass
            
            return value_str
            
        except Exception:
            return str(display_value)
    
    def setup_tethered_mode(self):
        """設定tethered拍攝模式（無SD卡直接傳輸）"""
        if not self.camera:
            return
            
        try:
            config = self.camera.get_config(self.context)
            
            # 嘗試設定捕獲目標為記憶體/電腦
            try:
                capturetarget = config.get_child_by_name('capturetarget')
                current_value = capturetarget.get_value()
                
                # 尋找適合的tethered模式選項
                tethered_options = []
                for i in range(capturetarget.count_choices()):
                    choice = capturetarget.get_choice(i)
                    choice_lower = choice.lower()
                    if any(keyword in choice_lower for keyword in ['ram', 'memory', 'internal', 'pc', 'computer']):
                        tethered_options.append(choice)
                
                if tethered_options:
                    # 使用第一個找到的tethered選項
                    capturetarget.set_value(tethered_options[0])
                    self.camera.set_config(config, self.context)
                    self.status_queue.put(f"Tethered mode enabled: {tethered_options[0]}")
                else:
                    # 顯示所有可用選項
                    all_choices = []
                    for i in range(capturetarget.count_choices()):
                        all_choices.append(capturetarget.get_choice(i))
                    self.status_queue.put(f"Available capture targets: {', '.join(all_choices)}")
                    
            except gp.GPhoto2Error:
                # 相機不支援capturetarget設定
                self.status_queue.put("Camera doesn't support capture target setting")
                
        except Exception as e:
            self.status_queue.put(f"Tethered setup failed: {str(e)}")
    
    def show_camera_settings(self):
        """顯示相機支援的所有設定"""
        if not self.connected:
            messagebox.showinfo("Info", "Please connect camera first")
            return
            
        def show_settings_thread():
            try:
                config = self.camera.get_config(self.context)
                settings_info = self.get_all_camera_settings(config)
                
                
                # 建立新視窗顯示設定
                self.root.after_idle(lambda: self.display_settings_window(settings_info))
                
            except Exception as e:
                self.status_queue.put(f"error:Failed to get camera settings: {str(e)}")
        
        threading.Thread(target=show_settings_thread, daemon=True).start()
    
    def get_all_camera_settings(self, config, prefix="", level=0, seen_paths=None):
        """遞歸獲取所有相機設定，避免重複"""
        if seen_paths is None:
            seen_paths = set()
            
        settings = []
        
        for i in range(config.count_children()):
            child = config.get_child(i)
            child_name = child.get_name()
            full_name = f"{prefix}/{child_name}" if prefix else child_name
            
            # 檢查是否已經處理過這個路徑
            if full_name in seen_paths:
                continue
            seen_paths.add(full_name)
            
            try:
                if child.count_children() > 0:
                    # 如果有子設定，遞歸獲取
                    sub_settings = self.get_all_camera_settings(child, full_name, level + 1, seen_paths)
                    settings.extend(sub_settings)
                else:
                    # 葉節點，獲取設定值
                    try:
                        setting_type = child.get_type()
                        current_value = child.get_value()
                        
                        # 獲取可選值
                        choices = []
                        try:
                            if hasattr(child, 'count_choices') and child.count_choices() > 0:
                                for j in range(child.count_choices()):
                                    choice = child.get_choice(j)
                                    if choice not in choices:  # 避免重複選項
                                        choices.append(choice)
                        except:
                            pass  # 有些設定沒有選項
                        
                        settings.append({
                            'name': child_name,
                            'full_name': full_name,
                            'type': str(setting_type),
                            'current_value': str(current_value),
                            'choices': choices,
                            'level': level
                        })
                    except Exception as e:
                        # 如果無法獲取設定值，至少記錄設定名稱
                        settings.append({
                            'name': child_name,
                            'full_name': full_name,
                            'type': 'Unknown',
                            'current_value': f'Error: {str(e)}',
                            'choices': [],
                            'level': level
                        })
            except Exception:
                continue
                
        return settings
    
    def display_settings_window(self, settings):
        """顯示設定視窗"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title(f"Camera Settings - {self.camera_model}")
        settings_window.geometry("800x600")
        settings_window.configure(bg='#f8f9fa')
        
        # 建立滾動框架
        canvas = tk.Canvas(settings_window, bg='#f8f9fa')
        scrollbar = ttk.Scrollbar(settings_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#f8f9fa')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 標題
        title_label = tk.Label(
            scrollable_frame,
            text=f"Available Settings for {self.camera_model}",
            font=('Arial', 14, 'bold'),
            bg='#f8f9fa',
            fg='#2c3e50'
        )
        title_label.pack(pady=10)
        
        # 設定列表 - 顯示所有層級的設定
        if not settings:
            no_settings_label = tk.Label(
                scrollable_frame,
                text="No camera settings found or camera not properly connected",
                font=('Arial', 12),
                bg='#f8f9fa',
                fg='#e74c3c'
            )
            no_settings_label.pack(pady=20)
        
        for setting in settings:
            # 計算縮排（根據層級）
            indent = "  " * setting['level']
            
            setting_frame = tk.Frame(scrollable_frame, bg='#ffffff', relief='solid', bd=1)
            setting_frame.pack(fill='x', padx=10, pady=2)
                
            # 設定名稱（加入層級縮排）
            name_label = tk.Label(
                setting_frame,
                text=f"{indent}{setting['name']}:",
                font=('Arial', 10, 'bold'),
                bg='#ffffff',
                fg='#2c3e50'
            )
            name_label.pack(anchor='w', padx=10, pady=(5, 0))
                
            # 當前值
            value_label = tk.Label(
                setting_frame,
                text=f"Current: {setting['current_value']}",
                font=('Arial', 9),
                bg='#ffffff',
                fg='#27ae60'
            )
            value_label.pack(anchor='w', padx=20)
            
            # 可選值
            if setting['choices']:
                choices_text = ", ".join(setting['choices'][:10])  # 限制顯示前10個選項
                if len(setting['choices']) > 10:
                    choices_text += f"... (+{len(setting['choices']) - 10} more)"
                
                choices_label = tk.Label(
                    setting_frame,
                    text=f"Options: {choices_text}",
                    font=('Arial', 8),
                    bg='#ffffff',
                    fg='#7f8c8d',
                    wraplength=700
                )
                choices_label.pack(anchor='w', padx=20, pady=(0, 5))
        
        # 佈局滾動組件
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        
    def toggle_connection(self):
        """切換相機連接狀態"""
        if not self.connected:
            self.connect_camera()
        else:
            self.disconnect_camera()
            
    def connect_camera(self):
        """連接相機"""
        def connect_thread():
            try:
                self.status_queue.put("Searching for camera...")
                
                # 檢測相機
                camera_list = gp.check_result(gp.gp_camera_autodetect())
                if not camera_list:
                    self.status_queue.put("error:No camera found. Please check connection.")
                    return
                    
                self.camera = gp.Camera()
                self.camera.init(self.context)
                
                # 獲取相機資訊
                abilities = self.camera.get_abilities()
                self.camera_model = abilities.model
                
                # 檢查相機支援的設定
                self.check_camera_capabilities()
                
                self.status_queue.put(f"connected:{self.camera_model}")
                
            except gp.GPhoto2Error as e:
                self.status_queue.put(f"error:Connection failed: {str(e)}")
                
        threading.Thread(target=connect_thread, daemon=True).start()
        
    def disconnect_camera(self):
        """斷開相機連接"""
        if self.camera:
            try:
                self.camera.exit(self.context)
                self.camera = None
                self.connected = False
                
                # 更新UI
                self.connection_status.configure(text="● Disconnected", fg='#e74c3c')
                self.connect_button.configure(text="Connect Camera", bg='#e9ecef', fg='#495057')
                self.settings_button.configure(state='disabled')
                self.capture_button.configure(state='disabled')
                self.camera_info_label.configure(text="No camera connected")
                self.update_status("Camera disconnected")
                
            except Exception as e:
                self.update_status(f"Disconnect error: {str(e)}")
                
    def capture_photo(self):
        """拍攝照片"""
        if not self.connected:
            messagebox.showerror("Error", "Please connect camera first")
            return
        
        if self.setting_in_progress:
            messagebox.showinfo("Info", "Camera settings are being updated. Please wait a moment and try again.")
            return
        
        # 將拍攝任務加入佇列
        capture_task = {
            'mode': self.capture_mode_var.get(),
            'burst_count': self.burst_count_var.get(),
            'interval': self.interval_var.get(),
            'save_path': self.save_path_var.get(),
            'filename_prefix': self.filename_prefix_var.get()
        }
        self.capture_queue.put(capture_task)
        
    def process_capture_queue(self):
        """處理拍攝佇列中的任務"""
        try:
            if not self.capture_queue.empty():
                task = self.capture_queue.get_nowait()
                self.execute_capture_task(task)
        except queue.Empty:
            pass
            
    def execute_capture_task(self, task):
        """執行拍攝任務"""
        try:
            # 檢查相機連接狀態
            if not self.camera:
                self.status_queue.put("error:Camera not connected")
                return
            
            # 檢查相機是否仍然可用
            try:
                self.camera.get_config(self.context)
            except:
                self.status_queue.put("error:Camera connection lost")
                return
            
            # 從任務中獲取參數
            mode = task['mode']
            try:
                burst_count = max(1, int(task['burst_count'] or "1"))
                interval_time = max(0, float(task['interval'] or "0"))
            except ValueError:
                burst_count = 1
                interval_time = 0
            save_path = task['save_path']
            prefix = task['filename_prefix']
            
            if not os.path.exists(save_path):
                os.makedirs(save_path)
                
            total_shots = burst_count if mode == "burst" else 1
            
            for i in range(total_shots):
                progress = (i + 1) / total_shots * 100
                self.status_queue.put(f"progress:{progress}")
                
                if total_shots > 1:
                    self.status_queue.put(f"Capturing {i+1}/{total_shots}...")
                else:
                    self.status_queue.put("Capturing...")
                
                # 生成檔名
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                if total_shots > 1:
                    filename = f"{prefix}_{timestamp}_{i+1:03d}.jpg"
                else:
                    filename = f"{prefix}_{timestamp}.jpg"
                
                target_path = os.path.join(save_path, filename)
                
                # 拍攝照片 - 嘗試強制拍攝
                file_path = self.camera.capture(gp.GP_CAPTURE_IMAGE, self.context)
                
                camera_file = gp.CameraFile()  # 預先建立 CameraFile 物件
                self.camera.file_get(
                    file_path.folder, file_path.name,
                    gp.GP_FILE_TYPE_NORMAL, camera_file, self.context  # 將 camera_file 作為 in/out 參數傳入
                )
                camera_file.save(target_path)  # 使用傳入的物件儲存

                # 刪除相機中的檔案以釋放記憶體
                try:
                    self.camera.file_delete(file_path.folder, file_path.name, self.context)
                except:
                    pass  # 有些相機不支援刪除，忽略錯誤
                
                # 確認檔案已儲存
                if os.path.exists(target_path):
                    self.photo_queue.put(target_path)
                else:
                    self.status_queue.put(f"error:Failed to save photo: {filename}")
                
                # 間隔等待
                if i < total_shots - 1:
                    if mode == "interval" and interval_time > 0:
                        time.sleep(interval_time)
                    elif total_shots > 1:
                        time.sleep(0.5)  # 連拍間隔
                    
            self.status_queue.put(f"Captured {total_shots} photo(s)")
            self.status_queue.put("progress:0")  # 重置進度條
            
        except gp.GPhoto2Error as e:
            try:
                error_msg = gp.check_result(e.code) if hasattr(e, 'code') else str(e)
            except:
                error_msg = f"GPhoto2 Error: {e}"
            self.status_queue.put(f"error:Camera capture failed: {error_msg}")
            self.status_queue.put("progress:0")
        except Exception as e:
            self.status_queue.put(f"error:Capture failed: {str(e)}")
            self.status_queue.put("progress:0")
        
    def on_setting_change(self, setting_name, value):
        """處理設定變更"""
        if self.connected:
            self.setting_in_progress = True  # 標記設定開始
            # 快門速度需要特殊處理：將顯示值轉換為原始值
            if setting_name == 'shutterspeed' and value in self.shutter_speed_map:
                original_value = self.shutter_speed_map[value]
                self.update_status(f"Setting {setting_name} to {value} ({original_value})...")
                threading.Thread(
                    target=lambda name=setting_name, val=original_value: self.set_camera_setting(name, val),
                    daemon=True
                ).start()
            else:
                self.update_status(f"Setting {setting_name} to {value}...")
                threading.Thread(
                    target=lambda name=setting_name, val=value: self.set_camera_setting(name, val),
                    daemon=True
                ).start()
        else:
            self.update_status(f"{setting_name} will be set when camera connects")
            
    def on_mode_change(self):
        """處理拍攝模式變更"""
        mode = self.capture_mode_var.get()
        mode_text = {
            "single": "Single shot mode selected",
            "burst": "Burst mode selected"
        }
        self.capture_status_label.configure(text=mode_text.get(mode, "Unknown mode"))
    
        
    def set_camera_setting(self, setting_name, value):
        """設定相機參數"""
        if not self.camera:
            self.setting_in_progress = False  # 清除設定進行中標記
            return
            
        try:
            config = self.camera.get_config(self.context)
            setting = config.get_child_by_name(setting_name)
            setting.set_value(str(value))
            self.camera.set_config(config, self.context)
            self.status_queue.put(f"✓ {setting_name}: {value}")
            logging.info(f"Camera setting applied: {setting_name} = {value}")
            
        except gp.GPhoto2Error as e:
            self.status_queue.put(f"error:Setting {setting_name} failed: {str(e)}")
        except Exception as e:
            self.status_queue.put(f"error:Failed to set {setting_name}: {str(e)}")
            logging.error(f"Setting {setting_name} failed: {str(e)}")
        finally:
            # 無論成功或失敗，都清除設定進行中標記
            self.setting_in_progress = False
    
    def navigate_to_setting(self, config, full_path):
        """根據完整路徑導航到設定"""
        try:
            parts = full_path.split('/')
            current = config
            
            for i, part in enumerate(parts):
                if part:  # 忽略空字串
                    try:
                        current = current.get_child_by_name(part)
                    except gp.GPhoto2Error as e:
                        self.status_queue.put(f"Failed to navigate to '{part}' in path '{full_path}' at step {i}: {str(e)}")
                        return None
                        
            return current
        except Exception as e:
            self.status_queue.put(f"Navigation error for {full_path}: {str(e)}")
            return None
            
    
    def load_preview_image(self, image_path):
        """載入預覽圖片 - 使用相對置中"""
        try:
            with Image.open(image_path) as img:
                # 取得當前畫布大小
                self.preview_canvas.update()
                canvas_width = self.preview_canvas.winfo_width()
                canvas_height = self.preview_canvas.winfo_height()
                
                if canvas_width <= 1 or canvas_height <= 1:
                    self.root.after(100, lambda: self.load_preview_image(image_path))
                    return
                
                # 計算最適合的縮放比例
                img_width, img_height = img.size
                padding = 20
                scale = min(
                    (canvas_width - padding) / img_width,
                    (canvas_height - padding) / img_height,
                    1.0  # 不放大，只縮小
                )
                
                new_width = int(img_width * scale)
                new_height = int(img_height * scale)
                
                # 縮放圖片
                img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img_resized)
                
                # 清除畫布
                self.preview_canvas.delete("all")
                
                # 使用相對座標置中 (0.5 = 50% = 中心)
                self.preview_canvas.create_image(
                    canvas_width * 0.5,  # X座標：畫布寬度的50%
                    canvas_height * 0.5,  # Y座標：畫布高度的50%
                    image=photo, 
                    anchor='center',
                    tags='preview_image'
                )
                
                # 保持圖片引用
                self.preview_canvas.image = photo
                
                # 綁定畫布大小變更事件來重新置中
                self.preview_canvas.bind('<Configure>', lambda e: self.recenter_image())
                
        except Exception as e:
            self.update_status(f"Preview load failed: {str(e)}")
    
    def recenter_image(self):
        """重新置中預覽圖片"""
        try:
            # 獲取目前的預覽圖片物件
            items = self.preview_canvas.find_withtag('preview_image')
            if items:
                # 獲取新的畫布大小
                canvas_width = self.preview_canvas.winfo_width()
                canvas_height = self.preview_canvas.winfo_height()
                
                # 更新圖片位置到新的中心點
                self.preview_canvas.coords(
                    items[0],
                    canvas_width * 0.5,
                    canvas_height * 0.5
                )
        except Exception:
            pass  # 忽略重新置中時的錯誤
            
    def browse_directory(self):
        """瀏覽目錄"""
        directory = filedialog.askdirectory(
            title="Select photo save directory",
            initialdir=self.save_directory
        )
        if directory:
            self.save_path_var.set(directory)
            self.save_directory = directory
            
    def open_photo_folder(self):
        """開啟照片資料夾"""
        save_path = self.save_path_var.get()
        if os.path.exists(save_path):
            os.system(f'open "{save_path}"')
        else:
            messagebox.showwarning("Warning", "Photo folder does not exist")
    
    def delete_last_photo(self):
        """刪除最後一張拍攝的照片"""
        save_path = self.save_path_var.get()
        if not os.path.exists(save_path):
            messagebox.showwarning("Warning", "Photo folder does not exist")
            return
            
        try:
            # 獲取資料夾中所有 jpg 檔案，按修改時間排序
            jpg_files = []
            for filename in os.listdir(save_path):
                if filename.lower().endswith(('.jpg', '.jpeg')):
                    filepath = os.path.join(save_path, filename)
                    if os.path.isfile(filepath):
                        jpg_files.append(filepath)
            
            if not jpg_files:
                messagebox.showinfo("Info", "No photos found in the save folder")
                return
            
            # 按修改時間排序，最新的在最後
            jpg_files.sort(key=lambda x: os.path.getmtime(x))
            latest_photo = jpg_files[-1]
            
            # 確認刪除
            filename = os.path.basename(latest_photo)
            result = messagebox.askyesno(
                "Confirm Delete", 
                f"Are you sure you want to delete the last photo?\n\n{filename}"
            )
            
            if result:
                os.remove(latest_photo)
                self.update_status(f"Deleted: {filename}")
                
                # 清除預覽圖片如果刪除的是當前顯示的圖片
                self.preview_canvas.delete("all")
                
                # 如果還有其他照片，顯示倒數第二張
                if len(jpg_files) > 1:
                    second_latest = jpg_files[-2]
                    self.load_preview_image(second_latest)
                    
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete photo: {str(e)}")
            
    def update_status(self, message):
        """更新狀態"""
        self.capture_status_label.configure(text=message)
        
    def check_queues(self):
        """檢查佇列訊息"""
        # 檢查拍攝佇列
        self.process_capture_queue()
        
        # 檢查狀態佇列
        try:
            while True:
                message = self.status_queue.get_nowait()
                
                if message.startswith("connected:"):
                    model = message.split(":", 1)[1]
                    self.connected = True
                    self.connection_status.configure(text="● Connected", fg='#27ae60')
                    self.connect_button.configure(text="Disconnect Camera", bg='#e9ecef', fg='#495057')
                    self.settings_button.configure(state='normal')
                    self.capture_button.configure(state='normal')
                    self.camera_info_label.configure(text=f"Connected: {model}")
                    self.update_status(f"Connected to {model}")
                    
                elif message.startswith("progress:"):
                    progress = float(message.split(":", 1)[1])
                    self.progress_var.set(progress)
                    
                elif message.startswith("error:"):
                    error_msg = message.split(":", 1)[1]
                    self.update_status(error_msg)
                    messagebox.showerror("Error", error_msg)
                    
                else:
                    self.update_status(message)
                    
        except queue.Empty:
            pass
            
        # 檢查照片佇列
        try:
            while True:
                photo_path = self.photo_queue.get_nowait()
                self.load_preview_image(photo_path)
                
        except queue.Empty:
            pass
            
        self.root.after(50, self.check_queues)
        
    def run(self):
        """啟動應用程式"""
        self.root.mainloop()

def main():
    app = CameraControlPro()
    app.run()

if __name__ == "__main__":
    main()