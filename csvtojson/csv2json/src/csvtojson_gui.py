import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import csv
import json
import os
import datetime
from collections import defaultdict
import glob
import pickle

class CsvToJsonGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("CSV to JSON Converter")
        self.csv_data = []
        self.headers = []
        self.entries = [] # will check later either to remove or not for memory optimization
        self.file_path = None
        self.row_vars = [] # will check later either to remove or not for memory optimization
        # OFF for a while undo/redo stacks
        #self.undo_stack = []
        #self.redo_stack = []
        #self.max_undo_stack = 50 # limit undo history
        self.state_file = "csv_editor_state.pkl" # Add state file path
        self.deleted_columns = set() # Add delete column tracking
        # Add virtual scrolling variables
        self.visible_rows = 30  # Number of visible rows
        self.top_row = 0       # First visible row index
        self.entry_pool = []   # Reusable entry widgets

        # --- Parameter input fields ---
        param_frame = tk.Frame(root)
        param_frame.pack(pady=5, fill=tk.X)
        
        self.url_var = tk.StringVar()
        self.sensor_file_var = tk.StringVar()
        self.weather_file_var = tk.StringVar()
        self.start_date_var = tk.StringVar()
        self.obs_days_var = tk.StringVar()
        self.obs_hour_var = tk.StringVar()
        self.tank_var = tk.StringVar()
        self.exp_name_var = tk.StringVar()

        tk.Label(param_frame, text="URL/Local File Link:").grid(row=0, column=0, sticky='e')
        tk.Entry(param_frame, textvariable=self.url_var, width=40).grid(row=0, column=1, sticky='w', padx=2)
        tk.Label(param_frame, text="Sensor CSV File:").grid(row=0, column=2, sticky='e')
        tk.Entry(param_frame, textvariable=self.sensor_file_var, width=20).grid(row=0, column=3, sticky='w', padx=2)
        tk.Label(param_frame, text="Weather CSV File:").grid(row=0, column=4, sticky='e')
        tk.Entry(param_frame, textvariable=self.weather_file_var, width=20).grid(row=0, column=5, sticky='w', padx=2)

        tk.Label(param_frame, text="Start Date:").grid(row=1, column=0, sticky='e')
        tk.Entry(param_frame, textvariable=self.start_date_var, width=15).grid(row=1, column=1, sticky='w', padx=2)
        tk.Label(param_frame, text="Observation Days:").grid(row=1, column=2, sticky='e')
        tk.Entry(param_frame, textvariable=self.obs_days_var, width=10).grid(row=1, column=3, sticky='w', padx=2)
        tk.Label(param_frame, text="Observation Hour:").grid(row=1, column=4, sticky='e')
        tk.Entry(param_frame, textvariable=self.obs_hour_var, width=10).grid(row=1, column=5, sticky='w', padx=2)

        tk.Label(param_frame, text="Tank(range: 1-20):").grid(row=2, column=0, sticky='e')
        tk.Entry(param_frame, textvariable=self.tank_var, width=10).grid(row=2, column=1, sticky='w', padx=2)
        tk.Label(param_frame, text="Experiment Name:").grid(row=2, column=2, sticky='e')
        tk.Entry(param_frame, textvariable=self.exp_name_var, width=20).grid(row=2, column=3, sticky='w', padx=2)

        # --- Main control buttons ---
        button_frame = tk.Frame(root)
        button_frame.pack(pady=5)
        self.upload_btn = tk.Button(button_frame, text="Upload local CSV file", command=self.load_csv)
        self.upload_btn.pack(side=tk.LEFT, padx=5)
        self.read_btn = tk.Button(button_frame, text="Read CSV", command=self.read_csv_files)
        self.read_btn.pack(side=tk.LEFT, padx=5)
        self.save_btn = tk.Button(button_frame, text="Save CSV", command=self.save_csv)
        self.save_btn.pack(side=tk.LEFT, padx=5)
        self.convert_btn = tk.Button(button_frame, text="Convert to JSON", command=self.show_json_window)
        self.convert_btn.pack(side=tk.LEFT, padx=5)
        self.add_row_btn = tk.Button(button_frame, text="Add Row", command=self.add_row, bg='lightblue')
        self.add_row_btn.pack(side=tk.LEFT, padx=5)
        self.add_row_btn = tk.Button(button_frame, text="Add Column", command=self.add_column, bg='lightgreen')
        self.add_row_btn.pack(side=tk.LEFT, padx=5)
        
        # Add restore deleted column button
        #self.restore_btn = tk.Button(button_frame, text="Restore Deleted Column", command=self.restore_deleted_columns, bg='lightyellow')
        #self.restore_btn.pack(side=tk.LEFT, padx=5)
        
        # Add undo/redo buttons
        #self.undo_btn = tk.Button(button_frame, text="Undo", command = self.undo, state = tk.DISABLED)
        #self.undo_btn.pack(side=tk.LEFT, padx=5)
        #self.redo_btn = tk.Button(button_frame, text="Redo", command=self.redo, state=tk.DISABLED)
        #self.redo_btn.pack(side=tk.LEFT, padx=5)
        
        # File selection and control frame (legacy, can be removed or kept for manual file selection)
        # controls_frame = tk.Frame(root)
        # controls_frame.pack(pady=10)
        # self.select_btn = tk.Button(controls_frame, text="Select CSV File", command=self.load_csv)
        # self.select_btn.pack(side=tk.LEFT, padx=5)
        # self.show_json_btn = tk.Button(controls_frame, text="Show JSON Window", command=self.show_json_window)
        # self.show_json_btn.pack(side=tk.LEFT, padx=5)
        
        #Create main container frame
        self.main_container = tk.Frame(root)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        #create canvas for scroallable area
        self.canvas = tk.Canvas(self.main_container, bg='white')
        
        #Create vertical for scrollable area
        self.v_scrollbar = ttk.Scrollbar(self.main_container, orient="vertical", command=self.canvas.yview)
        self.v_scrollbar.pack(side="right", fill="y")

        # Remove horizontal scrollbar
        # self.h_scrollbar = ttk.Scrollbar(self.main_container, orient="horizontal", command=self.canvas.xview)
        # self.h_scrollbar.pack(side="right", fill="x")
        
        #pack canvas
        self.canvas.pack(side="left", fill="both", expand=True)
        
        #Configure canvas scrollbars
        self.canvas.configure(yscrollcommand = self.v_scrollbar.set)  # Remove xscrollcommand
        
        
        # Frame for dynamic entries (this will be placed inside canvas)
        self.entries_frame = tk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.entries_frame, anchor="nw")
        
        # Bind events for scrolling
        self.entries_frame.bind('<Configure>', self.on_frame_configure)
        self.canvas.bind('<Configure>', self.on_canvas_configure)

        # Bind mouse wheel events only to the canvas and main container
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)  # Windows
        self.canvas.bind("<Button-4>", self.on_mousewheel)    # Linux
        self.canvas.bind("<Button-5>", self.on_mousewheel)    # Linux
        self.main_container.bind("<MouseWheel>", self.on_mousewheel)  # Windows
        self.main_container.bind("<Button-4>", self.on_mousewheel)    # Linux
        self.main_container.bind("<Button-5>", self.on_mousewheel)    # Linux

        # Create the JSON output window as a separate window
        self.json_window = None  # Initialize as None
        self.create_json_window()
        
        # Load save state on startup
        self.load_state()
        
        # Bind keyboard shortcuts for undo/redo
        # self.root.bind ('<Control-z>', lambda e: self.undo())
        # self.root.bind ('<Control-y>', lambda e: self.redo())
        
    def save_state(self):
        """Save current state to file"""
        try:
            state = {
                'headers':self.headers,
                'csv_data': self.csv_data,
                'deleted_columns': self.deleted_columns,
                  'file_path': self.file_path,
                'params': {
                    'url': self.url_var.get(),
                    'sensor_file': self.sensor_file_var.get(),
                    'weather_file': self.weather_file_var.get(),
                    'start_date': self.start_date_var.get(),
                    'obs_days': self.obs_days_var.get(),
                    'obs_hour': self.obs_hour_var.get(),
                    'tank': self.tank_var.get(),
                    'exp_name': self.exp_name_var.get()
                }
            }
            with open(self.state_file, 'wb') as f:
                pickle.dump(state, f)
        except Exception as e:
            print(f"Error saving state: {e}") 
            
    def restore_deleted_columns(self):
        """Show dialog to restore deleted columns"""
        if not self.deleted_columns:
            messagebox.showinfo("Info", "No deleted columns to restore.")
            return
    
        # Create dialog window
        dialog = tk.Toplevel(self.root)
        dialog.title("Restore Deleted Columns")
        dialog.geometry("300x400")
    
        # Create listbox to show deleted columns
        tk.Label(dialog, text="Select columns to restore:").pack(pady=5)
    
        listbox = tk.Listbox(dialog, selectmode=tk.MULTIPLE)
        listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    
        # Populate listbox with deleted columns
        for col in sorted(self.deleted_columns):
            listbox.insert(tk.END, col)
    
        def restore_selected():
            selected_indices = listbox.curselection()
            if not selected_indices:
                messagebox.showwarning("Warning", "No columns selected.")
                return
                
            for index in selected_indices:
                column_name = listbox.get(index)
                # Add back to headers
                self.headers.append(column_name)
                # Add empty values to all rows
                for row in self.csv_data:
                    row[column_name] = ""
                # Remove from deleted set
                self.deleted_columns.discard(column_name)
            
            self.save_state()
            self.display_entries()
            dialog.destroy()
            messagebox.showinfo("Success", f"Restored {len(selected_indices)} column(s).")
        
        tk.Button(dialog, text="Restore Selected", command=restore_selected).pack(pady=10)
        tk.Button(dialog, text="Cancel", command=dialog.destroy).pack()

    def display_entries(self):
        # Clear previous widgets
        for widget in self.entries_frame.winfo_children():
            widget.destroy()
        
        self.top_row = 0
        if not self.headers:
            return
        self.entries = []
        self.row_vars = []
        self.header_vars = []

        # Add delete row button column header
        tk.Label(self.entries_frame, text="", width=5, bg='lightgray').grid(row=0, column=0, padx=2, pady=2)

        # Show editable headers with delete buttons
        for idx, header in enumerate(self.headers):
            header_frame = tk.Frame(self.entries_frame)
            header_frame.grid(row=0, column=idx+1, padx=2, pady=2, sticky='ew')
            
            header_var = tk.StringVar(value=header)
            header_entry = tk.Entry(header_frame, textvariable=header_var,
                                    width=15, bg='lightblue', font=('Arial', 9, 'bold'),
                                    relief=tk.RIDGE)
            header_entry.pack(side=tk.LEFT)
            
            # Delete column button
            delete_btn = tk.Button(header_frame, text="×", fg='red', 
                                 command=lambda h=header: self.confirm_delete_column(h),
                                 width=2, height=1)
            delete_btn.pack(side=tk.LEFT)
            
            # Bind header edit
            header_entry.bind('<FocusOut>', lambda e, i=idx, v=header_var: self.on_header_edit(i, v))
            header_entry.bind('<Return>', lambda e, i=idx, v=header_var: self.on_header_edit(i, v))
            self.header_vars.append(header_var)
        
        # Show all rows with delete buttons
        for row_idx, row in enumerate(self.csv_data):
            # Delete row button
            delete_row_btn = tk.Button(self.entries_frame, text="×", fg='red',
                                     command=lambda r=row_idx: self.confirm_delete_row(r),
                                     width=3, height=1)
            delete_row_btn.grid(row=row_idx+1, column=0, padx=2, pady=2)
            
            row_var = []
            for col_idx, header in enumerate(self.headers):
                var = tk.StringVar(value=row.get(header, ""))
                entry = tk.Entry(self.entries_frame, textvariable=var, width=15)
                entry.grid(row=row_idx+1, column=col_idx+1, padx=2, pady=2, sticky='ew')
                var.trace_add("write", self.live_update)
                row_var.append(var)
            self.row_vars.append(row_var)

        # Configure grid weights
        for i in range(len(self.headers)+1):
            self.entries_frame.grid_columnconfigure(i, weight=1)
            
        # Update scroll region
        self.root.after(100, self.update_scroll_region)
        self.live_update()
    
    def confirm_delete_column(self, column_name):
        """Show confirmation dialog before deleting column"""
        response = messagebox.askyesno("Confirm Delete", 
                                     f"Are you sure you want to delete column '{column_name}'?\n\n"
                                     "You can restore it later from 'Restore Deleted Columns'.")
        if response:
            self.delete_column(column_name)
            
    def confirm_delete_row(self, row_index):
        """Show confirmation dialog before deleting row"""
        response = messagebox.askyesno("Confirm Delete", 
                                     f"Are you sure you want to delete row {row_index + 1}?\n\n"
                                     "This action cannot be undone.")
        if response:
            self.delete_row(row_index)

    # ... (rest of the methods remain the same, just add self.save_state() calls after any data modification)
    
    def add_column(self):
        import tkinter.simpledialog
        col_name = tkinter.simpledialog.askstring("Add Column", "Enter new column name:")
        if not col_name:
            return
        col_name = col_name.strip()
        if not col_name or col_name in self.headers:
            messagebox.showerror("Error", "Invalid or duplicate column name.")
            return
        
        self.headers.append(col_name)
        for row in self.csv_data:
            row[col_name] = ""
            
        if hasattr(self, 'all_csv_data'):
            for row in self.all_csv_data:
                row[col_name] = ""
                
        self.save_state()  # Save state after adding column
        self.display_entries()
        self.live_update()
        
    def add_row(self):
        if not self.headers:
            messagebox.showwarning("Warning", "No headers defined. Please load a CSV file.")
            return
        
        new_row = {header: "" for header in self.headers}
        self.csv_data.append(new_row)
        
        if hasattr(self, 'all_csv_data'):
            self.all_csv_data.append(new_row.copy())
            
        self.save_state()  # Save state after adding row
        self.display_entries()
        self.live_update()

    # Include all other methods from the original code...
    # (I'm showing key methods here, but all original methods should be included)

    
    def create_json_window(self):
        # Check if window already exists and is still valid
        if self.json_window is not None:
            try:
                # Check if window still exists
                self.json_window.winfo_exists()
                return  # Window already exists, don't create a new one
            except tk.TclError:
                # Window was destroyed, we can create a new one
                pass
         
        
        self.json_window = tk.Toplevel(self.root)
        self.json_window.title("Live JSON Output")
        self.json_window.geometry("600x400")
        
        # Handle window close event
        self.json_window.protocol("WM_DELETE_WINDOW", self.on_json_window_close)
        
        #Create frame for JSON text with scrollbars
        json_frame = tk.Frame(self.json_window)
        json_frame.pack(fill = tk.BOTH, expand=True, padx=10, pady=10)
        
        #Create text widget
        self.json_text = tk.Text(json_frame, height=15, width=80, wrap=tk.NONE)
        
        #Create scrollbars for JSON text
        json_v_scrollbar = ttk.Scrollbar(json_frame, orient="vertical", command=self.json_text.yview)
        json_h_scrollbar = ttk.Scrollbar(json_frame, orient="horizontal", command=self.json_text.xview)
        
        #Configure text widget scrollbars
        self.json_text.configure(yscrollcommand=json_v_scrollbar.set, xscrollcommand=json_h_scrollbar.set)
        
        #Pack Scrollbars and text widget
        json_v_scrollbar.pack(side="right", fill="y")
        json_h_scrollbar.pack(side="bottom", fill="x")
        self.json_text.pack(side="left", fill=tk.BOTH, expand=True)
    
    def show_json_window(self):
        # Show or bring focus to JSON window
        if self.json_window is None:
            self.create_json_window()
            # Update with current data
            self.live_update()
        else:
            try:
                # Bring window to front
                self.json_window.lift()
                self.json_window.focus_force()
            except tk.TclError:
                # Window was destroyed, create a new one
                self.json_window = None
                self.create_json_window()
                self.live_update()

    def on_json_window_close(self):
        # Handle when user closes the JSON window
        self.json_window.destroy()
        self.json_window = None
            
    def on_frame_configure(self, event):
        #Update scroll region when the frame changes size
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
    def on_canvas_configure(self, event):
        #Update the canvas window width to match canvas width
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width=canvas_width)
        
        # Adjust visible rows based on window height
        if hasattr(self, 'visible_rows'):
            canvas_height = event.height
            row_height = 25  # Approximate height of each row
            new_visible_rows = max(10, min(50, (canvas_height - 50) // row_height))
        
            if new_visible_rows != self.visible_rows:
                self.visible_rows = new_visible_rows
                self.display_entries()

        
    def on_mousewheel(self, event):
        """Handles mouse wheel scrolling by calling the main on_scroll method."""
        # For Windows, event.delta is positive for scrolling up.
        if event.delta:
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        # For Linux, event.num is 4 for scrolling up.
        elif event.num == 4:
            self.canvas.yview_scroll(-1, 'units') # Scroll up
        elif event.num == 5:
            self.canvas.yview_scroll(-1, 'units') # Scroll down
   

    def _read_csv_with_auto_delimiter(self, file_path):
        # Try to auto-detect delimiter
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            sample = csvfile.read(2048)
            csvfile.seek(0)
            sniffer = csv.Sniffer()
            try:
                dialect = sniffer.sniff(sample)
            except Exception:
                dialect = csv.excel  # fallback to default
            reader = csv.DictReader(csvfile, dialect=dialect)
            headers = reader.fieldnames
            data = list(reader)
        return headers, data

    def load_csv(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV Files", "*.csv")],
            title="Select a CSV file"
        )
        if not file_path:
            return
        self.file_path = file_path
        try:
            self.headers, self.all_csv_data = self._read_csv_with_auto_delimiter(file_path)
            self.csv_data = [row.copy() for row in self.all_csv_data]
            self._convert_timestamp_column()
            self._normalize_date_column()
            self.filter_by_date_and_time()
            self.display_entries()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load CSV: {e}")

    def read_csv_files(self):
        """Read multiple CSV files based on date range"""
        dir_path = self.url_var.get().strip()
        sensor_file_pattern = self.sensor_file_var.get().strip()
        weather_file_pattern = self.weather_file_var.get().strip()
        start_date_str = self.start_date_var.get().strip()
        obs_days_str = self.obs_days_var.get().strip()
    
        if not dir_path:
            messagebox.showerror("Error", "Please specify the directory path in 'URL/Local File Link'.")
            return
        
        if not start_date_str:
            messagebox.showerror("Error", "Please specify a start date.")
            return
        
        try:
            start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d")
        except ValueError:
            try:
                start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                messagebox.showerror("Error", "Start Date must be in YYYY-MM-DD format.")
                return
    
        obs_days = int(obs_days_str) if obs_days_str.isdigit() else 1
    
        # Collect all data from multiple files
        all_data = []
        all_weather_data = []
        headers_set = set()
    
        # Load data for each day in the range
        for day_offset in range(obs_days):
            current_date = start_date + datetime.timedelta(days=day_offset)
            date_str = current_date.strftime("%Y%m%d")

            # Load sensor data
            if sensor_file_pattern:
                # Replace date placeholder if exists
                sensor_file = sensor_file_pattern.replace("YYYYMMDD", date_str)
                # If no placeholder, try to find file with date pattern
                if sensor_file == sensor_file_pattern:
                    # Look for files matching pattern like 20250623v1.csv
                    pattern = f"{date_str}*.csv"
                    files = glob.glob(os.path.join(dir_path, pattern))
                    sensor_files = [f for f in files if "Weather" not in f]
                    if sensor_files:
                        sensor_file = os.path.basename(sensor_files[0])
            
                sensor_path = os.path.join(dir_path, sensor_file)
                if os.path.exists(sensor_path):
                    try:
                        headers, data = self._read_csv_with_auto_delimiter(sensor_path)
                        headers_set.update(headers)
                        all_data.extend(data)
                        print(f"Loaded {len(data)} rows from {sensor_file}")
                    except Exception as e:
                        print(f"Error loading {sensor_file}: {e}")
        
            # Load weather data
            if weather_file_pattern:
                weather_file = weather_file_pattern.replace("YYYYMMDD", date_str)
                if weather_file == weather_file_pattern:
                    # Look for weather files
                    weather_file = f"{date_str}Weather.csv"
            
                weather_path = os.path.join(dir_path, weather_file)
                if os.path.exists(weather_path):
                    try:
                        w_headers, w_data = self._read_csv_with_auto_delimiter(weather_path)
                        all_weather_data.extend(w_data)
                        print(f"Loaded {len(w_data)} weather rows from {weather_file}")
                    except Exception as e:
                        print(f"Error loading {weather_file}: {e}")
    
        if not all_data:
            messagebox.showwarning("No Data", "No data files found for the specified date range.")
            return
    
        # Merge weather data if available
        if all_weather_data:
            # Create a timestamp-based lookup for weather data
            weather_lookup = {}
            for w_row in all_weather_data:
                ts = w_row.get('timestamp', '')
                if ts:
                    weather_lookup[ts] = w_row
        
            # Merge weather data into sensor data
            for row in all_data:
                ts = row.get('timestamp', '')
                if ts and ts in weather_lookup:
                    # Add weather columns to sensor data
                    weather_row = weather_lookup[ts]
                    for key, value in weather_row.items():
                        if key != 'timestamp':  # Don't duplicate timestamp
                            row[f'Weather_{key}'] = value
                            headers_set.add(f'Weather_{key}')
    
        self.headers = sorted(list(headers_set))
        self.all_csv_data = all_data
        self.csv_data = [row.copy() for row in self.all_csv_data]
    
        # Convert timestamps and normalize dates
        self._convert_timestamp_column()
        self._normalize_date_column()
    
        # Apply hourly averaging if specified
        obs_hour_str = self.obs_hour_var.get().strip()
        if obs_hour_str and obs_hour_str.isdigit():
            self.apply_hourly_averaging(int(obs_hour_str))
    
        self.display_entries()
        messagebox.showinfo("Success", f"Loaded {len(self.csv_data)} total rows from {obs_days} day(s)")

    def apply_hourly_averaging(self, hours):
        """Average data over specified hour intervals"""
        if not self.csv_data or 'date' not in self.headers:
            return
    
        # Group data by time intervals
        grouped_data = defaultdict(list)
    
        for row in self.csv_data:
            date_str = row.get('date', '').strip()
            if not date_str:
                continue
            
            try:
                dt = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                # Round down to nearest interval
                interval_start = dt.replace(minute=0, second=0)
                interval_hour = (interval_start.hour // hours) * hours
                interval_start = interval_start.replace(hour=interval_hour)
            
                key = interval_start.strftime("%Y-%m-%d %H:%M:%S")
                grouped_data[key].append(row)
            except ValueError:
                continue
    
        # Calculate averages for each group
        averaged_data = []
        numeric_columns = []
    
        # Identify numeric columns
        for header in self.headers:
            if header not in ['date', 'timestamp']:
                # Check if column contains numeric data
                is_numeric = True
                for row in self.csv_data[:10]:  # Check first 10 rows
                    val = row.get(header, '')
                    if val and val.strip():
                        try:
                            float(val)
                        except ValueError:
                            is_numeric = False
                            break
                if is_numeric:
                    numeric_columns.append(header)
    
        # Calculate averages
        for interval, rows in sorted(grouped_data.items()):
            avg_row = {'date': interval}
        
            # For numeric columns, calculate average
            for col in numeric_columns:
                values = []
                for row in rows:
                    val = row.get(col, '')
                    if val and val.strip():
                        try:
                            values.append(float(val))
                        except ValueError:
                            pass
            
                if values:
                    avg_row[col] = f"{sum(values) / len(values):.2f}"
                else:
                    avg_row[col] = ''
        
            # For non-numeric columns, take the first value
            for col in self.headers:
                if col not in numeric_columns and col not in avg_row:
                    avg_row[col] = rows[0].get(col, '') if rows else ''
        
            averaged_data.append(avg_row)
    
        self.csv_data = averaged_data
        print(f"Averaged {len(self.all_csv_data)} rows into {len(averaged_data)} {hours}-hour intervals")

    def display_entries(self):
        # Clear previous widgets
        for widget in self.entries_frame.winfo_children():
            widget.destroy()
        
        self.top_row = 0
        if not self.headers:
            return
        self.entries = []
        self.row_vars = []
        self.header_vars = [] # Fixed from headers_vars

        # Show editable headers
        for idx, header in enumerate(self.headers):
            header_var = tk.StringVar(value=header)
            header_entry = tk.Entry(self.entries_frame, textvariable=header_var,
                                    width=15, bg='lightblue', font=('Arial', 9, 'bold'),
                                    relief=tk.RIDGE)
            header_entry.grid(row=0, column=idx, padx=2, pady=2, sticky='ew')
            #Bind header edit
            header_entry.bind('<FocusOut>', lambda e, i=idx, v=header_var: self.on_header_edit(i, v))
            header_entry.bind('<Return>', lambda e, i=idx, v=header_var: self.on_header_edit(i, v))
            self.header_vars.append(header_var)
        
        # Show all rows for editing
        for row_idx, row in enumerate(self.csv_data):
            row_var = []
            for col_idx, header in enumerate(self.headers):
                var = tk.StringVar(value=row.get(header, ""))
                entry = tk.Entry(self.entries_frame, textvariable=var, width=15)
                entry.grid(row=row_idx+1, column=col_idx, padx=2, pady=2, sticky='ew')
                var.trace_add("write", self.live_update)
                row_var.append(var)
            self.row_vars.append(row_var)

        # COMMENT FOR TESTING
        #self.create_entry_pool()
        #self.update_virtual_display()
        #self.update_scrollbar()

        #Configure grid weights for proper resizing
        for i in range(len(self.headers)):
            self.entries_frame.grid_columnconfigure(i, weight=1)
        #Configure virtual scrolling
        #self.setup_virtual_display - it said it need to remorve
        #Update scroll region
        self.root.after(100, self.update_scroll_region)
        self.live_update()
    
    def create_entry_pool(self):
        """Create a fixed pool of widgets for visible rows"""
        # Clear any previous widgets
        for widget in self.entries_frame.winfo_children():
            widget.destroy()
        self.entry_pool = []
        
        for idx, header in enumerate(self.headers):
            header_label = tk.Label(self.entries_frame, text=header, relief=tk.RIDGE, width=15, bg='lightgray', font=('Arial', 9, 'bold'))
            header_label.grid(row=0, column=idx, padx=2, pady=2, sticky='ew')
            
        for i in range(self.visible_rows):
            row_widgets = []
            for col_idx, header in enumerate(self.headers):
                var = tk.StringVar()
                entry = tk.Entry(self.entries_frame, textvariable=var, width=15)
                entry.grid(row=i+1, column=col_idx, padx=2, pady=2, sticky='ew')
                
                #Use a lambda to capture the current row and column index
                var.trace_add("write", lambda *args, r=i, c=col_idx: self.on_cell_edit(r, c))
                row_widgets.append((entry, var))
            self.entry_pool.append(row_widgets)
        
            
    def update_virtual_display(self):
        """Updates the pooled widgets with the correct slice of data."""
        total_rows = len(self.csv_data)
    
        for pool_row_idx in range(self.visible_rows):
            data_row_idx = self.top_row + pool_row_idx

            for pool_col_idx, (entry, var) in enumerate(self.entry_pool[pool_row_idx]):
                if data_row_idx < total_rows:
                    header = self.headers[pool_col_idx]
                    value = self.csv_data[data_row_idx].get(header, "")
                    var.set(value)
                    entry.config(state='normal')
                else:
                # This is a blank row beyond the end of the data, so clear and disable it
                    var.set("")
                    entry.config(state='disabled')
                    
    def on_cell_edit(self, pool_row_idx, col_idx):
        """Called when a cell's content is changed."""
        data_row_idx = self.top_row + pool_row_idx
    
        if data_row_idx < len(self.csv_data):
            header = self.headers[col_idx]
            # Get the new value from the corresponding StringVar
            new_value = self.entry_pool[pool_row_idx][col_idx][1].get()
            old_value = self.csv_data[data_row_idx].get(header, '')
        
            if new_value != old_value:
                # Save state before change
                self.save_state(f"Edit cell [{data_row_idx},{col_idx}]")
                self.csv_data[data_row_idx][header] = new_value
            
        self.live_update() # Update the JSON view if open
        
#    def on_scroll(self, *args):
#        """Handles the movement of the scrollbar."""
#        command = args[0]
#        if command == 'moveto':
#            fraction = float(args[1])
#            total_rows = len(self.csv_data)
#            max_top = max(0, total_rows - self.visible_rows)
#            self.top_row = int(fraction * max_top)
#        elif command == 'scroll':
#            delta = int(args[1])
#            total_rows = len(self.csv_data)
#            max_top = max(0, total_rows - self.visible_rows)
#            self.top_row = max(0, min(max_top, self.top_row + delta))
#
#        self.update_scrollbar()
#        self.update_virtual_display()
    
    def update_scrollbar(self):
        """Updates the scrollbar's position and size."""
        total_rows = len(self.csv_data)
        if total_rows <= self.visible_rows:
            self.v_scrollbar.set(0, 1)
        else:
            # Calculate the position and size of the scrollbar thumb
            first = self.top_row / total_rows
            last = (self.top_row + self.visible_rows) / total_rows
            self.v_scrollbar.set(first, last)
                        
    def on_virtual_cell_edit(self, event, widget_row, col):
        """Handle cell edit in virtual scrolling"""
        entry = event.widget
        data_row = getattr(entry, 'data_row', self.top_row + widget_row)
    
        if data_row < len(self.csv_data):
            header = self.headers[col]
            new_value = entry.get()
            self.csv_data[data_row][header] = new_value
        
            # Update live JSON if needed
            self.live_update()

    def setup_virtual_scrolling(self):
        """Setup scrollbar for virtual scrolling"""
        total_rows = len(self.csv_data)
    
        # Reconfigure the existing scrollbar
        self.v_scrollbar.config(command=self.on_virtual_scroll)
        self.update_scrollbar_position()
    
        # Bind additional events
        self.canvas.bind_all("<MouseWheel>", self.on_virtual_mousewheel)
        self.canvas.bind_all("<Button-4>", self.on_virtual_mousewheel)
        self.canvas.bind_all("<Button-5>", self.on_virtual_mousewheel)

    def on_virtual_scroll(self, *args):
        """Handle scrollbar movement for virtual scrolling"""
        total_rows = len(self.csv_data)
    
        if args[0] == 'moveto':
            # Calculate new top row from scrollbar position
            position = float(args[1])
            max_top = max(0, total_rows - self.visible_rows)
            self.top_row = int(position * max_top)
            self.update_virtual_display()
        
        elif args[0] == 'scroll':
            units = int(args[1])
            if args[2] == 'units':
                self.scroll_by_rows(units)
            else:  # pages
                self.scroll_by_rows(units * self.visible_rows)

    def scroll_by_rows(self, rows):
        """Scroll by specified number of rows"""
        total_rows = len(self.csv_data)
        max_top = max(0, total_rows - self.visible_rows)
    
        self.top_row = max(0, min(max_top, self.top_row + rows))
        self.update_virtual_display()
        self.update_scrollbar_position()

    def update_scrollbar_position(self):
        """Update scrollbar thumb position and size"""
        total_rows = len(self.csv_data)
        if total_rows <= self.visible_rows:
            self.v_scrollbar.set(0, 1)
        else:
        # Calculate position
            max_top = max(1, total_rows - self.visible_rows)
            first = self.top_row / max_top
        # Calculate size
            size = self.visible_rows / total_rows
            last = first + size
            self.v_scrollbar.set(first, min(1.0, last))

    def on_virtual_mousewheel(self, event):
        """Handle mouse wheel for virtual scrolling"""
        # Check if mouse is over the canvas area
        widget = self.root.winfo_containing(event.x_root, event.y_root)
        if widget == self or widget in self.canvas.winfo_children():
            if event.num == 4 or event.delta > 0:
                self.scroll_by_rows(-3)
            elif event.num == 5 or event.delta < 0:
                self.scroll_by_rows(3)
            return "break"

    def add_column(self):
        # Prompt for new column name
        import tkinter.simpledialog
        col_name = tkinter.simpledialog.askstring("Add Column", "Enter new column name:")
        if not col_name:
            return
        col_name = col_name.strip()
        if not col_name or col_name in self.headers:
            messagebox.showerror("Error", "Invalid or duplicate column name.")
            return
        # Save state before adding column
        # self.save_state(f"Add column: {col_name}")
        self.headers.append(col_name)
        for row in self.csv_data:
            row[col_name] = ""
            
        if hasattr(self, 'all_csv_data'):
            for row in self.all_csv_data:
                row[col_name] = ""
        self.display_entries()
        self.live_update

    def add_row(self):
        if not self.headers:
            messagebox.showwarning("Warning", "No headers defined. Please load a CSV file.")
            return

        # Save state before adding row
        # self.save_state("Add new row")
        
        # Add new row to data
        new_row = {header: "" for header in self.headers}
        self.csv_data.append(new_row)
    
        # Scroll to show the new row
        total_rows = len(self.csv_data)
        if total_rows > self.visible_rows:
            self.top_row = total_rows - self.visible_rows
            
        if hasattr(self, 'all_csv_data'):
            self.all_csv_data.append(new_row.copy())
            
        # Refresh the display
        self.display_entires()
            
        # Update display
        self.update_virtual_display()
        self.update_scrollbar_position()
    
        # Update live JSON
        self.live_update()
        
        
    def update_scroll_region(self):
        self.entries_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def save_csv(self):
        # Save the current table to CSV
        if not self.headers or not self.csv_data:
            messagebox.showinfo("Info", "No data to save.")
            return
        file_path = self.file_path
        if not file_path:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV Files", "*.csv")],
                title="Save CSV file as"
            )
            if not file_path:
                return
        # Update self.all_csv_data from GUI before saving
        self.update_csv_data_from_gui()
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.headers)
                writer.writeheader()
                for row in self.csv_data:
                    writer.writerow(row)
            messagebox.showinfo("Success", f"CSV saved to {file_path}")
            self.file_path = file_path
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save CSV: {e}")

    def update_csv_data_from_gui(self):
        # Update self.all_csv_data from the current GUI table
        new_data = []
        for row_vars in self.row_vars:
            row_dict = {header: var.get() for header, var in zip(self.headers, row_vars)}
            if any(v.strip() for v in row_dict.values()):
                new_data.append(row_dict)
        self.all_csv_data = new_data
        self.csv_data = [row.copy() for row in self.all_csv_data]
    
    # Add new methods for undo/redo functionality
    def save_state(self, description=""):
        """Save current state to undo stack"""
        state = {
            'headers': self.headers.copy(),
            'csv_data': [row.copy() for row in self.csv_data],
            'description': description
        }
        self.undo_stack.append(state)
    
        # Limit undo stack size
        if len(self.undo_stack) > self.max_undo_stack:
            self.undo_stack.pop(0)
    
        # Clear redo stack when new action is performed
        self.redo_stack.clear()
    
        # Update button states
        self.update_undo_redo_buttons()

    def undo(self):
        """Undo last action"""
        if not self.undo_stack:
            return
    
        # Save current state to redo stack
        current_state = {
            'headers': self.headers.copy(),
            'csv_data': [row.copy() for row in self.csv_data]
        }
        self.redo_stack.append(current_state)
    
        # Restore previous state
        state = self.undo_stack.pop()
        self.headers = state['headers']
        self.csv_data = state['csv_data']
    
        # Refresh display
        self.display_entries()
        self.update_undo_redo_buttons()

    def redo(self):
        """Redo last undone action"""
        if not self.redo_stack:
            return
    
        # Save current state to undo stack
        current_state = {
            'headers': self.headers.copy(),
            'csv_data': [row.copy() for row in self.csv_data]
        }
        self.undo_stack.append(current_state)
    
        # Restore redo state
        state = self.redo_stack.pop()
        self.headers = state['headers']
        self.csv_data = state['csv_data']
    
        # Refresh display
        self.display_entries()
        self.update_undo_redo_buttons()

    def update_undo_redo_buttons(self):
        """Update undo/redo button states"""
        self.undo_btn.config(state=tk.NORMAL if self.undo_stack else tk.DISABLED)
        self.redo_btn.config(state=tk.NORMAL if self.redo_stack else tk.DISABLED)

    def on_header_edit(self, idx, var):
        """Handle header editing"""
        new_header = var.get().strip()
        old_header = self.headers[idx]
    
        if not new_header:
            messagebox.showerror("Error", "Header cannot be empty")
            var.set(old_header)
            return
    
        if new_header != old_header:
            # Check for duplicates
            if new_header in self.headers and self.headers.index(new_header) != idx:
                messagebox.showerror("Error", "Duplicate header name")
                var.set(old_header)
                return
        
            # Save state before change
        self.save_state(f"Edit header: {old_header} → {new_header}")
        
            # Update header
        self.headers[idx] = new_header
        
        # Update data
        for row in self.csv_data:
            if old_header in row:
                row[new_header] = row.pop(old_header)
        
        # Also update all_csv_data if it exists
        if hasattr(self, 'all_csv_data'):
            for row in self.all_csv_data:
                if old_header in row:
                    row[new_header] = row.pop(old_header)
        
        # Refresh display
        self.display_entries()

    def live_update(self, *args):
        # Build data from entry fields
        data = []
        
         # Get all data, not just visible
        for row_idx, row in enumerate(self.csv_data):
            if any(v.strip() for v in row.values()):
                data.append(row)
                
        # Update JSON output in the separate window (if it exists)
        if self.json_window is not None:
            try:
                self.json_window.winfo_exists()
                self.json_text.delete(1.0, tk.END)
                self.json_text.insert(tk.END, json.dumps(data, indent=4, ensure_ascii=False))
            except tk.TclError:
                self.json_window = None
                
        # Auto-save after every edit
        self.update_csv_data_from_gui()
        if self.file_path:
            try:
                with open(self.file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=self.headers)
                    writer.writeheader()
                    for row in self.csv_data:
                        writer.writerow(row)
            except Exception:
                pass

    def _convert_timestamp_column(self):
        # Convert 'timestamp' to 'date' (UTC) and make 'date' the first column
        import datetime
        if not self.csv_data:
            return
        # Find the timestamp column name (case-insensitive)
        timestamp_col = None
        for col in self.headers:
            if col.lower() == 'timestamp' or col.lower().startswith('timestamp'):
                timestamp_col = col
                break
        if not timestamp_col:
            return
        # Remove all 'date' from headers to avoid duplicates
        self.headers = [h for h in self.headers if h.lower() != 'date']
        # Insert 'date' as the first column
        self.headers = ['date'] + [h for h in self.headers]
        for row in self.csv_data:
            ts_val = row.get(timestamp_col, '')
            date_str = ''
            try:
                ts_float = float(ts_val)
                # If timestamp is in ms, convert to seconds
                if ts_float > 1e12:
                    ts_float = ts_float / 1000.0
                dt = datetime.datetime.fromtimestamp(ts_float, datetime.timezone.utc)
                date_str = dt.strftime('%Y-%m-%d %H:%M:%S')
            except Exception:
                date_str = ''
            row['date'] = date_str
        # Ensure every row has a 'date' key
        for row in self.csv_data:
            if 'date' not in row:
                row['date'] = ''
        # Also update all_csv_data if it exists
        if hasattr(self, 'all_csv_data'):
            for row in self.all_csv_data:
                ts_val = row.get(timestamp_col, '')
                date_str = ''
                try:
                    ts_float = float(ts_val)
                    if ts_float > 1e12:
                        ts_float = ts_float / 1000.0
                    dt = datetime.datetime.fromtimestamp(ts_float, datetime.timezone.utc)
                    date_str = dt.strftime('%Y-%m-%d %H:%M:%S')
                except Exception:
                    date_str = ''
                row['date'] = date_str
            for row in self.all_csv_data:
                if 'date' not in row:
                    row['date'] = ''

    def _normalize_date_column(self):
        # Convert 'date' column to 'YYYY-MM-DD HH:MM:SS' if it's a timestamp or scientific notation
        if not self.csv_data or 'date' not in self.headers:
            return
        for row in self.csv_data:
            date_val = row.get('date', '').strip()
            if not date_val:
                continue
            # Try to parse as float (timestamp)
            try:
                # Handle scientific notation and float timestamps
                ts = float(date_val)
                # If it's in ms, convert to seconds
                if ts > 1e12:
                    ts = ts / 1000.0
                dt = datetime.datetime.fromtimestamp(ts)
                row['date'] = dt.strftime('%Y-%m-%d %H:%M:%S')
                continue
            except Exception:
                pass
            # Try to parse as known date string
            for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
                try:
                    dt = datetime.datetime.strptime(date_val, fmt)
                    row['date'] = dt.strftime('%Y-%m-%d %H:%M:%S')
                    break
                except Exception:
                    continue

    def filter_by_date_and_time(self):
        # Only filter if relevant fields are present
        if not hasattr(self, 'all_csv_data') or not self.all_csv_data or 'date' not in self.headers:
            return
        start_date_str = self.start_date_var.get().strip()
        obs_days_str = self.obs_days_var.get().strip()
        obs_hour_str = self.obs_hour_var.get().strip()
        if not start_date_str:
            self.csv_data = [row.copy() for row in self.all_csv_data]
            return  # No filter if no start date
        try:
            start_dt = datetime.datetime.strptime(start_date_str, "%Y-%m-%d")
        except ValueError:
            try:
                start_dt = datetime.datetime.strptime(start_date_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                messagebox.showerror("Error", "Start Date must be in YYYY-MM-DD or YYYY-MM-DD HH:MM:SS format.")
                return
        obs_days = int(obs_days_str) if obs_days_str.isdigit() else 1
        obs_hour = int(obs_hour_str) if obs_hour_str.isdigit() else None
        filtered = []
        for row in self.all_csv_data:
            date_str = row.get('date', '').strip()
            if not date_str:
                continue
            try:
                row_dt = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                try:
                    row_dt = datetime.datetime.strptime(date_str, "%Y-%m-%d")
                except ValueError:
                    continue
            # Date range filter
            if obs_days == 1:
                in_range = row_dt.date() == start_dt.date()
            else:
                end_dt = start_dt + datetime.timedelta(days=obs_days)
                in_range = start_dt <= row_dt < end_dt
            # Hour filter
            if obs_hour is not None:
                in_range = in_range and (row_dt.hour == obs_hour)
            if in_range:
                filtered.append(row.copy())
        if not filtered:
            messagebox.showwarning("No Data", "No rows match the filter. Showing all data.")
            self.csv_data = [row.copy() for row in self.all_csv_data]
        else:
            self.csv_data = filtered
            
    def delete_column(self, column_name):
        """Delete a column and move it to deleted_columns set"""
        if column_name in self.headers:
            self.headers.remove(column_name)
            self.deleted_columns.add(column_name)
        
            # Remove from all data rows
            for row in self.csv_data:
                if column_name in row:
                    del row[column_name]
                
            if hasattr(self, 'all_csv_data'):
                for row in self.all_csv_data:
                    if column_name in row:
                        del row[column_name]
        
            self.save_state()
            self.display_entries()
            messagebox.showinfo("Success", f"Column '{column_name}' deleted. You can restore it later.")

    def delete_row(self, row_index):
        """Delete a row from the data"""
        if 0 <= row_index < len(self.csv_data):
            self.csv_data.pop(row_index)
        
            if hasattr(self, 'all_csv_data') and row_index < len(self.all_csv_data):
                self.all_csv_data.pop(row_index)
            
            self.save_state()
            self.display_entries()

    def load_state(self):
        """Load saved state from file"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'rb') as f:
                    state = pickle.load(f)
                    self.headers = state.get('headers', [])
                    self.csv_data = state.get('csv_data', [])
                    self.deleted_columns = state.get('deleted_columns', set())
                    self.file_path = state.get('file_path', None)
                
                    # Load parameters
                    params = state.get('params', {})
                    self.url_var.set(params.get('url', ''))
                    self.sensor_file_var.set(params.get('sensor_file', ''))
                    self.weather_file_var.set(params.get('weather_file', ''))
                    self.start_date_var.set(params.get('start_date', ''))
                    self.obs_days_var.set(params.get('obs_days', ''))
                    self.obs_hour_var.set(params.get('obs_hour', ''))
                    self.tank_var.set(params.get('tank', ''))
                    self.exp_name_var.set(params.get('exp_name', ''))
                
                    # Display loaded data
                    if self.csv_data:
                        self.display_entries()
                    
            except Exception as e:
                print(f"Error loading state: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CsvToJsonGUI(root)
    root.mainloop()
