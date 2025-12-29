#!/usr/bin/env python3
"""
pyCameraControl Interface - Windows Version
Requirements:
pip install pillow
Install digiCamControl from http://digicamcontrol.com/
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import queue
import os
from PIL import Image, ImageTk
import logging

# Import our camera backend
from camera_backends import DigiCamControlBackend


class CameraControlWindows:
	def __init__(self):
		# 初始化主視窗
		self.root = tk.Tk()
		self.root.title("pyCameraControl - Windows")
		self.root.geometry("1200x820")
		self.root.configure(bg='#f8f9fa')
		self.root.resizable(True, True)
		
		# 相機後端
		try:
			self.camera_backend = DigiCamControlBackend()
		except Exception as e:
			messagebox.showerror("Error", f"Failed to initialize camera backend: {e}")
			self.root.destroy()
			return
		
		# 相機相關變數
		self.connected = False
		self.camera_model = ""
		
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
		# 拍攝設定變數
		self.burst_count_var = tk.StringVar(value="1")
		self.interval_var = tk.StringVar(value="0")
		self.capture_mode_var = tk.StringVar(value="single")

		# 檔案管理變數
		self.save_path_var = tk.StringVar(value=self.save_directory)
		self.filename_prefix_var = tk.StringVar(value="IMG")
		
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
			text="pyCameraControl - Windows",
			font=('Arial', 18, 'bold'),
			bg='#ffffff',
			fg='#2c3e50'
		)
		title_label.pack()
		
		subtitle_label = tk.Label(
			title_frame,
			text="photography control interface with digiCamControl",
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
		"""建立相機連接區域"""
		# 主容器
		camera_frame = tk.Frame(parent, bg='#ffffff', relief='solid', bd=1)
		camera_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 8))

		# 相機連接區塊
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
		self.preview_canvas.pack(fill='both', expand=True)
		
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
				
				success, result = self.camera_backend.connect_camera()
				
				if success:
					self.status_queue.put(f"connected:{result}")
				else:
					self.status_queue.put(f"error:{result}")
					
			except Exception as e:
				self.status_queue.put(f"error:Connection failed: {str(e)}")
				
		threading.Thread(target=connect_thread, daemon=True).start()
		
	def disconnect_camera(self):
		"""斷開相機連接"""
		try:
			success = self.camera_backend.disconnect_camera()
			if success:
				self.connected = False
				
				# 更新UI
				self.connection_status.configure(text="● Disconnected", fg='#e74c3c')
				self.connect_button.configure(text="Connect Camera", bg='#e9ecef', fg='#495057')
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
				threading.Thread(target=lambda: self.execute_capture_task(task), daemon=True).start()
		except queue.Empty:
			pass
			
	def execute_capture_task(self, task):
		"""執行拍攝任務"""
		try:
			# 檢查相機連接狀態
			if not self.connected:
				self.status_queue.put("error:Camera not connected")
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
			
			if mode == "burst" and burst_count > 1:
				# 連拍模式
				self.status_queue.put(f"Starting burst capture ({burst_count} photos)")
				
				success, files, message = self.camera_backend.burst_capture(
					save_path, prefix, burst_count, interval_time
				)
				
				if success:
					self.status_queue.put(f"Burst complete: {len(files)} photos")
					# 顯示最後一張照片
					if files:
						self.photo_queue.put(files[-1])
				else:
					self.status_queue.put(f"error:{message}")
			
			else:
				# 單張拍攝
				if mode == "interval" and interval_time > 0:
					self.status_queue.put(f"Interval mode: capturing every {interval_time} seconds")
				else:
					self.status_queue.put("Capturing...")
				
				success, filepath, message = self.camera_backend.capture_photo(save_path, prefix)
				
				if success:
					self.status_queue.put("Photo captured successfully")
					if filepath:
						self.photo_queue.put(filepath)
				else:
					self.status_queue.put(f"error:{message}")
			
			self.status_queue.put("progress:0")  # 重置進度條
			
		except Exception as e:
			self.status_queue.put(f"error:Capture failed: {str(e)}")
			self.status_queue.put("progress:0")
		

	
	def on_mode_change(self):
		"""處理拍攝模式變更"""
		mode = self.capture_mode_var.get()
		mode_text = {
			"single": "Single shot mode selected",
			"burst": "Burst mode selected"
		}
		self.capture_status_label.configure(text=mode_text.get(mode, "Unknown mode"))
	
	
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

	def delete_last_photo(self):
		"""刪除最後一張拍攝的照片"""
		save_path = self.save_path_var.get()
		if not os.path.exists(save_path):
			messagebox.showwarning("Warning", "Photo folder does not exist")
			return
			
		try:
			# 獲取資料夾中所有圖片檔案，按修改時間排序
			image_extensions = ('.jpg', '.jpeg', '.cr2', '.cr3', '.nef', '.arw', '.dng', '.png', '.tiff')
			image_files = []
			for filename in os.listdir(save_path):
				if filename.lower().endswith(image_extensions):
					filepath = os.path.join(save_path, filename)
					if os.path.isfile(filepath):
						image_files.append(filepath)
			
			if not image_files:
				messagebox.showinfo("Info", "No photos found in the save folder")
				return
			
			# 按修改時間排序，最新的在最後
			image_files.sort(key=lambda x: os.path.getmtime(x))
			latest_photo = image_files[-1]
			
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
				if len(image_files) > 1:
					second_latest = image_files[-2]
					self.load_preview_image(second_latest)
					
		except Exception as e:
			messagebox.showerror("Error", f"Failed to delete photo: {str(e)}")
			
	def open_photo_folder(self):
		"""開啟照片資料夾"""
		save_path = self.save_path_var.get()
		if os.path.exists(save_path):
			os.startfile(save_path)  # Windows specific
		else:
			messagebox.showwarning("Warning", "Photo folder does not exist")
			
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
					self.camera_model = model
					self.connection_status.configure(text="● Connected", fg='#27ae60')
					self.connect_button.configure(text="Disconnect Camera", bg='#e9ecef', fg='#495057')
					self.capture_button.configure(state='normal')
					self.camera_info_label.configure(text=f"Connected: {model}")
					self.update_status(f"Connected to {model}")
					
				elif message.startswith("progress:"):
					progress = float(message.split(":", 1)[1])
					self.progress_var.set(progress)
					
				elif message.startswith("error:"):
					error_msg = message.split(":", 1)[1]
					self.update_status(error_msg)
					# 重置连接状态
					if "Connection failed" in error_msg or "No camera" in error_msg or "Camera connection error" in error_msg:
						self.connected = False
						self.connection_status.configure(text="● Disconnected", fg='#e74c3c')
						self.connect_button.configure(text="Connect Camera", bg='#e9ecef', fg='#495057')
						self.capture_button.configure(state='disabled')
						self.camera_info_label.configure(text="No camera connected")
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
	try:
		app = CameraControlWindows()
		app.run()
	except Exception as e:
		print(f"Failed to start application: {e}")
		input("Press Enter to exit...")


if __name__ == "__main__":
	main()