#!/usr/bin/env python3
"""
Windows Camera Backend for pyCameraControl
Uses digiCamControl Remote Utility for camera control on Windows platform.
Requires the main digiCamControl application to be running and camera connected.
"""

import subprocess
import os
import time
from datetime import datetime
import locale


class DigiCamControlBackend:
	"""Windows camera backend using digiCamControl Remote Utility"""
	
	def __init__(self):
		# Common digiCamControl Remote Utility installation paths
		self.possible_paths = [
			"C:/Program Files (x86)/digiCamControl/CameraControlRemoteCmd.exe",
			"C:/Program Files/digiCamControl/CameraControlRemoteCmd.exe",
			"CameraControlRemoteCmd.exe"  # If in PATH
		]
		self.dcc_path = None
		self.connected = False
		self.camera_model = ""
		
		# Find digiCamControl Remote Utility installation
		self._find_dcc_installation()
	
	def _find_dcc_installation(self):
		"""Find digiCamControl Remote Utility installation path"""
		for path in self.possible_paths:
			if os.path.exists(path):
				self.dcc_path = path
				return
				
		# Try to find in PATH
		try:
			result = subprocess.run(
				["where", "CameraControlRemoteCmd.exe"], 
				capture_output=True, 
				text=True, 
				shell=True,
				timeout=10
			)
			if result.returncode == 0:
				self.dcc_path = result.stdout.strip().split('\n')[0]
				return
		except:
			pass
		
		raise FileNotFoundError(
			"digiCamControl Remote Utility not found. Please install digiCamControl from "
			"http://digicamcontrol.com/ and ensure CameraControlRemoteCmd.exe is accessible. "
			"Also, ensure the main digiCamControl application is running."
		)
	
	def _run_dcc_command(self, *args, timeout=30):
		"""Run digiCamControl Remote command with error handling"""
		if not self.dcc_path:
			raise RuntimeError("digiCamControl Remote not found")
		
		cmd = [self.dcc_path, "/c"] + list(args)
		
		try:
			# Use system locale encoding or utf-8 as fallback
			encoding = locale.getpreferredencoding() or 'utf-8'
			result = subprocess.run(
				cmd, 
				capture_output=True, 
				text=True, 
				encoding=encoding,
				errors='replace', 
				timeout=timeout,
				shell=False
			)
			print(f"Debug: Command {' '.join(cmd)} result: returncode={result.returncode}, stdout={result.stdout}, stderr={result.stderr}")
			return result
		except subprocess.TimeoutExpired:
			raise RuntimeError(f"Command timed out: {' '.join(cmd)}")
		except Exception as e:
			raise RuntimeError(f"Command failed: {e}")
	
	def connect_camera(self):
		"""Connect to camera (check if camera is available)"""
		try:
			# Check if cameras are available
			result = self._run_dcc_command("list", "cameras")

			if result.returncode == 0 and result.stdout:
				stdout = result.stdout.strip()
				# Check if the response contains error message
				if ":;response:error;" in stdout:
					if "no camera is connected" in stdout:
						return False, "No camera is connected"
					else:
						return False, "Camera connection error"

				# Check if we have a camera list response
				if ":;response:[" in stdout and "];" in stdout:
					# Extract camera ID from response like ":;response:["6241310"];"
					start = stdout.find(":;response:[") + len(":;response:[")
					end = stdout.find("];", start)
					if start < end:
						camera_id = stdout[start:end].strip('"')
						self.camera_model = f"Camera {camera_id}"
						self.connected = True
						return True, self.camera_model

				return False, "No cameras found"
			else:
				error_msg = result.stderr.strip() if result.stderr else "Connection failed"
				return False, error_msg

		except Exception as e:
			return False, f"Connection error: {str(e)}"
	
	def disconnect_camera(self):
		"""Disconnect from camera (placeholder, as remote doesn't explicitly disconnect)"""
		try:
			self.connected = False
			self.camera_model = ""
			return True
		except Exception as e:
			self.connected = False
			return False
	
	def is_connected(self):
		"""Check if camera is connected"""
		return self.connected
	
	def capture_photo(self, save_path, filename_prefix="IMG"):
		"""Capture photo"""
		try:
			# Ensure save directory exists
			os.makedirs(save_path, exist_ok=True)
			
			# Generate filename with timestamp
			timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
			filename = f"{filename_prefix}_{timestamp}"
			
			# Set the capture folder
			self._run_dcc_command("set", "session.folder", save_path)
			
			# Set filename template
			self._run_dcc_command("set", "session.filenametemplate", filename)
			
			# Capture photo
			result = self._run_dcc_command("capture")
			
			if result.returncode == 0:
				# Find the captured file
				possible_extensions = ['.jpg', '.jpeg', '.cr2', '.cr3', '.nef', '.arw', '.dng']
				captured_file = None
				
				for ext in possible_extensions:
					test_path = os.path.join(save_path, filename + ext)
					if os.path.exists(test_path):
						captured_file = test_path
						break
				
				if not captured_file:
					# Look for any recently created file in the directory
					try:
						files = [f for f in os.listdir(save_path) if f.startswith(filename)]
						if files:
							captured_file = os.path.join(save_path, files[0])
					except:
						pass
				
				if captured_file and os.path.exists(captured_file):
					return True, captured_file, "Photo captured successfully"
				else:
					return True, None, "Photo captured but file location unknown"
			else:
				error_msg = result.stderr.strip() if result.stderr else "Capture command failed"
				return False, None, f"Capture failed: {error_msg}"
				
		except Exception as e:
			return False, None, f"Capture error: {str(e)}"
	
	def burst_capture(self, save_path, filename_prefix, count, interval=0):
		"""Capture multiple photos in burst mode"""
		captured_files = []
		
		try:
			os.makedirs(save_path, exist_ok=True)
			
			# Set the capture folder
			self._run_dcc_command("set", "session.folder", save_path)
			
			for i in range(count):
				# Generate unique filename for each shot
				timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
				filename = f"{filename_prefix}_burst_{i+1:03d}_{timestamp}"
				
				# Set filename template
				self._run_dcc_command("set", "session.filenametemplate", filename)
				
				# Capture photo
				result = self._run_dcc_command("capture")
				
				if result.returncode == 0:
					# Find the captured file
					possible_extensions = ['.jpg', '.jpeg', '.cr2', '.cr3', '.nef', '.arw', '.dng']
					captured_file = None
					
					for ext in possible_extensions:
						test_path = os.path.join(save_path, filename + ext)
						if os.path.exists(test_path):
							captured_file = test_path
							break
					
					if captured_file:
						captured_files.append(captured_file)
					
					# Wait between captures if interval specified
					if interval > 0 and i < count - 1:
						time.sleep(interval)
					elif i < count - 1:
						time.sleep(0.5)  # Minimum delay between shots
				else:
					error_msg = result.stderr.strip() if result.stderr else f"Capture {i+1} failed"
					return False, captured_files, f"Burst capture failed at photo {i+1}: {error_msg}"
			
			return True, captured_files, f"Successfully captured {len(captured_files)} photos"
			
		except Exception as e:
			return False, captured_files, f"Burst capture error: {str(e)}"
	
	def get_camera_info(self):
		"""Get basic camera information"""
		try:
			info = {}

			if self.connected:
				info['model'] = self.camera_model
				info['status'] = "Connected"
			else:
				info['model'] = "No camera"
				info['status'] = "Not connected"

			return info

		except Exception as e:
			return {'error': str(e)}


# Example usage and testing
if __name__ == "__main__":
	try:
		backend = DigiCamControlBackend()
		print(f"digiCamControl Remote found at: {backend.dcc_path}")
		
		# Test connection
		success, result = backend.connect_camera()
		if success:
			print(f"Connected to: {result}")
			
			# Test camera info
			info = backend.get_camera_info()
			print("Camera info:")
			for key, value in info.items():
				print(f"  {key}: {value}")
			
			# Test capture
			print("Testing photo capture...")
			success, filepath, message = backend.capture_photo("C:/Users/seant/Pictures/photo")
			print(f"Capture result: {message}")
			if filepath:
				print(f"Photo saved to: {filepath}")
			
			backend.disconnect_camera()
			print("Disconnected successfully")
		else:
			print(f"Connection failed: {result}")
			
	except Exception as e:
		print(f"Error: {e}")
		print("Make sure digiCamControl is installed, running, and a camera is connected.")