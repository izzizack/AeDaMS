import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import csv
import json
import os
import datetime
from collections import defaultdict
import glob


class CsvToJsonGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("CSV to JSON Converter")
        self.csv_data = []
        self.headers = []
        self.entries = []
        self.file_path = None
        self.row_vars = []

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
        
    def on_mousewheel(self, event):
        #Handle mouse wheel scrolling
        if event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")
    
    # Create the JSON output window as a separate window
        self.json_window = tk.Toplevel(self.root)
        self.json_window.title("Live JSON Output")
        self.json_text = tk.Text(self.json_window, height=15, width=80)
        self.json_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

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
        self.entries = []
        self.row_vars = []

        if not self.headers:
            return

        # Show headers
        for idx, header in enumerate(self.headers):
            header_label = tk.Label(self.entries_frame, text=header, relief=tk.RIDGE, width=15, bg='lightgray', font=('Arial', 9, 'bold'))
            header_label.grid(row=0, column=idx, padx=2, pady=2, sticky='ew')

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

        # Add a button to add more rows
        add_row_btn = tk.Button(self.entries_frame, text="Add Row", command=self.add_row, bg='lightblue')
        add_row_btn.grid(row=len(self.csv_data)+1, column=0, columnspan=len(self.headers), pady=5, sticky='ew')

        # Add a button to add more columns
        add_col_btn = tk.Button(self.entries_frame, text="Add Column", command=self.add_column, bg='lightgreen')
        add_col_btn.grid(row=len(self.csv_data)+2, column=0, columnspan=len(self.headers), pady=5, sticky='ew')

        #Configure grid weights for proper resizing
        for i in range(len(self.headers)):
            self.entries_frame.grid_columnconfigure(i, weight=1)
        #Update scroll region
        self.root.after(100, self.update_scroll_region)
        self.live_update()

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
        self.headers.append(col_name)
        for row in self.csv_data:
            row[col_name] = ""
        self.display_entries()

    def add_row(self):
        if not self.headers:
            return
        
        row_idx = len(self.row_vars)
        row_var = []
        for col_idx, header in enumerate(self.headers):
            var = tk.StringVar(value="")
            entry = tk.Entry(self.entries_frame, textvariable=var, width=15)
            entry.grid(row=row_idx+1, column=col_idx, padx=2, pady=2, sticky='ew')
            var.trace_add("write", self.live_update)
            row_var.append(var)
        self.row_vars.append(row_var)
        
        # Move the Add Row button to the new bottom
        add_row_btn = None 
        for widget in self.entries_frame.winfo_children():
            if isinstance(widget, tk.Button) and widget.cget("text") == "Add Row":
                add_row_btn = widget
                break

        if add_row_btn:
            add_row_btn.grid(row=len(self.row_vars)+1, column=0, columnspan=len(self.headers), pady=5, sticky='ew')

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
                for row in self.all_csv_data:
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

    def live_update(self, *args):
        # Build data from entry fields
        data = []
        for row in self.row_vars:
            row_dict = {header: var.get() for header, var in zip(self.headers, row)}
            # Only add non-empty rows
            if any(v.strip() for v in row_dict.values()):
                data.append(row_dict)
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

if __name__ == "__main__":
    root = tk.Tk()
    app = CsvToJsonGUI(root)
    root.mainloop()
