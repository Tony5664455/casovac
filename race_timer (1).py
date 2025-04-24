import tkinter as tk
from tkinter import ttk
from tkinter import colorchooser
import time
from datetime import datetime, timedelta
import uuid  # For unique race IDs

class RaceTimer:
    def __init__(self, root):
        self.root = root
        self.root.title("Race Track Scheduler")
        
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Make it fullscreen by default
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg='#000000')
        
        # Configure styles
        self.style = ttk.Style()
        self.style.configure('Dark.TFrame', background='#000000')
        self.style.configure('Dark.TLabel', background='#000000', foreground='white')
        self.style.configure('Control.TButton', font=('Segoe UI', 11), padding=10)
        
        # Logo configuration
        self.logo_text = "FUN"
        self.logo_subtext = "ARENACHEB.CZ"
        self.logo_color = '#00A7E1'  # Bright blue color
        
        # Pattern settings
        self.pattern_size = 40
        
        # Colors
        self.PAST_COLOR = '#1A1A1A'
        self.CURRENT_COLOR = '#FFA500'
        self.FUTURE_COLOR = '#2D2D2D'
        self.SHADOW_COLOR = '#111111'
        
        # Font settings
        base_size = min(screen_height // 20, 48)
        self.title_font = ('Segoe UI', int(base_size * 1.8), 'bold')
        self.time_font = ('Segoe UI', int(base_size * 3.2), 'bold')
        self.segment_font = ('Segoe UI', int(base_size * 1.2), 'bold')
        self.countdown_font = ('Segoe UI', int(base_size * 1.6), 'bold')
        self.logo_font = ('Segoe UI', int(base_size * 4), 'bold')  # Extra large for logo
        self.logo_subtext_font = ('Segoe UI', int(base_size * 2), 'bold')  # Smaller for subtext
        
        # Setup variables
        self.race_type = tk.StringVar()
        self.lap_duration = tk.StringVar()
        self.display_text = tk.StringVar()
        self.start_hour = tk.StringVar(value="0")
        self.selected_date = datetime.now().date()
        self.is_running = False
        self.start_time = None
        self.elapsed_base = timedelta(0)
        self.segments = []
        self.segment_canvases = []
        self.current_color = '#FFA500'
        
        # Store scheduled races
        self.scheduled_races = []
        self.active_race = None
        
        # Testing speed multiplier (60x faster - 1 hour = 1 minute)
        self.speed_multiplier = 60
        
        # Create main container with padding
        self.main_container = ttk.Frame(self.root, style='Dark.TFrame', padding="20")
        self.main_container.pack(fill='both', expand=True)
        
        # Create frames
        self.create_title()
        self.create_control_panel()
        self.create_timer_frame()
        
        # Add fullscreen toggle
        self.root.bind('<Escape>', lambda e: self.toggle_fullscreen())
        self.root.bind('<F11>', lambda e: self.toggle_fullscreen())
        
        # Start updating time immediately
        self.update_current_time()

    def create_input_frame(self, parent):
        """Create the control panel inputs"""
        # Create container frames with more padding
        input_frame_top = ttk.Frame(parent, style='Dark.TFrame', padding="20 10")
        input_frame_top.pack(fill='x', pady=(10, 5), padx=20)
        
        input_frame_bottom = ttk.Frame(parent, style='Dark.TFrame', padding="20 10")
        input_frame_bottom.pack(fill='x', pady=5, padx=20)
        
        # Style for input labels - increased font size
        label_style = {'font': ('Segoe UI', 12), 'bg': '#1A1A1A', 'fg': 'white'}
        
        # Top row - Duration with more spacing
        tk.Label(input_frame_top, text="Lap Duration:", **label_style).pack(side='left', padx=(0, 10))
        durations = ['10', '12', '15', '20']
        duration_cb = self.create_styled_combobox(input_frame_top, self.lap_duration, durations, width=5)
        duration_cb.pack(side='left', padx=(0, 5))
        tk.Label(input_frame_top, text="minutes", **label_style).pack(side='left', padx=(0, 30))
        
        # Date and Time Selection with increased spacing
        date_frame = ttk.Frame(input_frame_top, style='Dark.TFrame')
        date_frame.pack(side='left', padx=(0, 30))
        
        tk.Label(date_frame, text="Date:", **label_style).pack(side='left', padx=(0, 10))
        
        # Date spinboxes with increased width
        self.day_var = tk.StringVar(value=str(self.selected_date.day))
        self.month_var = tk.StringVar(value=str(self.selected_date.month))
        self.year_var = tk.StringVar(value=str(self.selected_date.year))
        
        day_sb = ttk.Spinbox(date_frame, from_=1, to=31, width=4, textvariable=self.day_var)
        month_sb = ttk.Spinbox(date_frame, from_=1, to=12, width=4, textvariable=self.month_var)
        year_sb = ttk.Spinbox(date_frame, from_=2024, to=2030, width=6, textvariable=self.year_var)
        
        day_sb.pack(side='left', padx=2)
        tk.Label(date_frame, text="/", **label_style).pack(side='left')
        month_sb.pack(side='left', padx=2)
        tk.Label(date_frame, text="/", **label_style).pack(side='left')
        year_sb.pack(side='left', padx=2)
        
        tk.Label(date_frame, text="Time:", **label_style).pack(side='left', padx=(20, 10))
        hours = [f"{i:02d}" for i in range(24)]
        start_hour_cb = self.create_styled_combobox(date_frame, self.start_hour, hours, width=8)  # Increased width
        start_hour_cb.pack(side='left', padx=(0, 10))
        
        # Bottom row - Display Text and Controls with more spacing
        tk.Label(input_frame_bottom, text="Display Text:", **label_style).pack(side='left', padx=(0, 10))
        entry = tk.Entry(
            input_frame_bottom,
            textvariable=self.display_text,
            font=('Segoe UI', 12),
            bg='#2D2D2D',
            fg='white',
            insertbackground='white',
            relief='flat',
            width=40
        )
        entry.pack(side='left', padx=(0, 30))
        
        # Color picker button
        color_btn = self.create_styled_button(
            input_frame_bottom,
            "Set Color",
            self.pick_color,
            self.current_color,
            True
        )
        color_btn.pack(side='left', padx=10)
        
        # Schedule and Reset buttons with more spacing
        self.create_styled_button(input_frame_bottom, "SCHEDULE", self.schedule_race, '#00A67E').pack(side='left', padx=10)
        self.create_styled_button(input_frame_bottom, "RESET", self.reset_timer, '#666666').pack(side='left', padx=10)
        
        # Create segment text inputs frame
        segment_text_frame = ttk.Frame(parent, style='Dark.TFrame', padding="20 10")
        segment_text_frame.pack(fill='x', pady=10, padx=20)
        
        tk.Label(segment_text_frame, text="Segment Texts:", font=('Segoe UI', 12, 'bold'),
                bg='#1A1A1A', fg='white').pack(anchor='w', pady=(0, 10))
        
        # Create a frame to hold all segment text inputs
        self.segment_texts_frame = ttk.Frame(segment_text_frame, style='Dark.TFrame')
        self.segment_texts_frame.pack(fill='x')
        
        # Initialize segment text variables
        self.segment_text_vars = []
        self.segment_color_vars = []
        
        # Create initial segment text inputs based on default duration
        self.update_segment_text_inputs()
        
        # Bind duration change to update segment text inputs
        self.lap_duration.trace_add('write', lambda *args: self.update_segment_text_inputs())
        
        # Create scheduled races list
        self.create_schedule_list(parent)

    def create_title(self):
        title_frame = ttk.Frame(self.main_container, style='Dark.TFrame')
        title_frame.pack(fill='x', pady=(20, 30))
        
        self.race_info_label = tk.Label(
            title_frame,
            text="",
            font=self.title_font,
            bg='#000000',
            fg='#FFFFFF'
        )
        self.race_info_label.pack(pady=10)

    def create_timer_frame(self):
        """Create or update the timer frame with segments"""
        if hasattr(self, 'timer_frame'):
            self.timer_frame.destroy()
            
        self.timer_frame = ttk.Frame(self.main_container, style='Dark.TFrame')
        self.timer_frame.pack(fill='both', expand=True)
        
        # Current time display with shadow effect
        time_frame = ttk.Frame(self.timer_frame, style='Dark.TFrame')
        time_frame.pack(pady=(0, 40))
        
        # Multiple shadows for depth effect
        shadow_offsets = [(6, 6), (4, 4), (2, 2)]
        for offset_x, offset_y in shadow_offsets:
            tk.Label(
                time_frame,
                text="00:00:00",
                font=self.time_font,
                bg='#000000',
                fg=self.SHADOW_COLOR,
            ).place(x=offset_x, y=offset_y)
        
        self.current_time_label = tk.Label(
            time_frame,
            text="00:00:00",
            font=self.time_font,
            bg='#000000',
            fg='#FFFFFF'
        )
        self.current_time_label.pack()
        
        # Create segments container
        self.segments_frame = ttk.Frame(self.timer_frame, style='Dark.TFrame')
        self.segments_frame.pack(fill='both', expand=True, padx=40)
        
        # Create logo frame
        self.logo_frame = ttk.Frame(self.timer_frame, style='Dark.TFrame')
        self.logo_frame.pack(fill='both', expand=True, padx=40)
        
        # Create logo with shadow effect
        logo_shadow_offsets = [(8, 8), (6, 6), (4, 4)]
        for offset_x, offset_y in logo_shadow_offsets:
            tk.Label(
                self.logo_frame,
                text=self.logo_text,
                font=self.logo_font,
                bg='#000000',
                fg=self.SHADOW_COLOR,
            ).place(relx=0.5, rely=0.4, anchor='center', x=offset_x, y=offset_y)
            
            tk.Label(
                self.logo_frame,
                text=self.logo_subtext,
                font=self.logo_subtext_font,
                bg='#000000',
                fg=self.SHADOW_COLOR,
            ).place(relx=0.5, rely=0.6, anchor='center', x=offset_x, y=offset_y)
        
        # Main logo text
        tk.Label(
            self.logo_frame,
            text=self.logo_text,
            font=self.logo_font,
            bg='#000000',
            fg=self.logo_color,
        ).place(relx=0.5, rely=0.4, anchor='center')
        
        # Logo subtext
        tk.Label(
            self.logo_frame,
            text=self.logo_subtext,
            font=self.logo_subtext_font,
            bg='#000000',
            fg='white',
        ).place(relx=0.5, rely=0.6, anchor='center')
        
        # Initially show logo and hide segments if no race is active
        self.update_display_state()
        
        if self.active_race:
            self.create_segments()

    def create_segments(self):
        """Create time segments"""
        self.segments = []
        self.segment_canvases = []
        
        duration = self.active_race['duration'] if self.active_race else int(self.lap_duration.get() or 12)
        num_segments = 60 // duration
        
        # Calculate segment height
        screen_height = self.root.winfo_screenheight()
        segments_total_height = int(screen_height * 0.6)
        segment_spacing = 8
        segment_height = (segments_total_height - (num_segments - 1) * segment_spacing) // num_segments
        
        for i in range(num_segments):
            segment_start_minutes = i * duration
            segment_end_minutes = (i + 1) * duration
            
            time_text = f"{segment_start_minutes:02d}:00 - {segment_end_minutes:02d}:00"
            
            frame = ttk.Frame(self.segments_frame, style='Dark.TFrame')
            frame.pack(fill='x', pady=segment_spacing//2)
            
            canvas = tk.Canvas(
                frame,
                height=segment_height,
                bg=self.FUTURE_COLOR,
                highlightthickness=0,
                relief='flat'
            )
            canvas.pack(fill='x')
            
            canvas.create_text(
                22, segment_height/2 + 2,
                text=time_text,
                fill=self.SHADOW_COLOR,
                font=self.segment_font,
                tags=('shadow',),
                anchor='w'
            )
            canvas.create_text(
                20, segment_height/2,
                text=time_text,
                fill='white',
                font=self.segment_font,
                tags=('label',),
                anchor='w'
            )
            
            self.segment_canvases.append(canvas)
            self.segments.append(frame)

    def update_display_state(self):
        """Update the visibility of segments and logo based on race state"""
        if self.active_race:
            self.logo_frame.pack_forget()
            self.segments_frame.pack(fill='both', expand=True, padx=40)
        else:
            self.segments_frame.pack_forget()
            self.logo_frame.pack(fill='both', expand=True, padx=40)

    def update_current_time(self):
        # If we're in test mode, don't update the display
        if hasattr(self, 'test_mode') and self.test_mode:
            return
            
        current_time = datetime.now()
        hours = current_time.hour
        minutes = current_time.minute
        seconds = current_time.second
        
        # Update main time display
        time_text = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        self.current_time_label.config(text=time_text)
        
        # Always check for scheduled races when not running
        if not self.is_running:
            self.check_scheduled_races()
        elif self.is_running and self.active_race:
            # Calculate elapsed time with speed multiplier
            real_elapsed = current_time - self.start_time
            accelerated_elapsed = real_elapsed * self.speed_multiplier
            elapsed = self.elapsed_base + accelerated_elapsed
            
            total_seconds = elapsed.total_seconds()
            total_minutes = int(total_seconds / 60)
            seconds = int(total_seconds % 60)
            
            duration = self.active_race['duration']
            current_segment = (total_minutes % 60) // duration
            
            # Update progress bars and current segment
            self.update_segments(current_segment, total_minutes, seconds)
            
            # Stop after an hour of simulated time
            if total_minutes >= 60:
                self.stop_timer()
                self.active_race = None
        
        # Schedule next update
        self.root.after(50, self.update_current_time)

    def set_test_time(self):
        """Set manual test time for debugging"""
        try:
            test_date = datetime.strptime(self.test_date_var.get(), '%Y-%m-%d').date()
            test_time = datetime.strptime(self.test_time_var.get(), '%H:%M').time()
            self.test_datetime = datetime.combine(test_date, test_time)
            
            # Enable test mode and update display
            self.test_mode = True
            self.current_time_label.config(
                text=f"{test_time.hour:02d}:{test_time.minute:02d}:00 (TEST)"
            )
            
            # Force check for races once
            self.check_scheduled_races()
        except ValueError as e:
            print(f"Invalid date/time format: {e}")

    def check_scheduled_races(self):
        """Check for races that should start"""
        if self.is_running or not self.scheduled_races:
            return
            
        # Determine which time to use
        check_time = self.test_datetime if hasattr(self, 'test_mode') and self.test_mode else datetime.now()
        
        for race in self.scheduled_races[:]:  # Copy list to allow modification while iterating
            # Create datetime objects for comparison
            race_date = race['date']
            race_time = datetime.strptime(f"{race['time']:02d}:00", "%H:%M").time()
            race_datetime = datetime.combine(race_date, race_time)
            
            # Convert check_time to date and time only for comparison
            check_datetime = datetime.combine(check_time.date(), check_time.time())
            
            # Calculate time difference in minutes
            time_diff = (check_datetime - race_datetime).total_seconds() / 60
            
            # Start race if we're within 1 minute after scheduled time
            if -1 <= time_diff <= 1:
                print(f"Starting race scheduled for {race_datetime}")
                self.start_scheduled_race(race)
                self.scheduled_races.remove(race)
                # Remove from treeview
                for item in self.schedule_tree.get_children():
                    values = self.schedule_tree.item(item)['values']
                    if (values[0] == race_date.strftime('%Y-%m-%d') and 
                        values[1] == f"{race['time']:02d}:00"):
                        self.schedule_tree.delete(item)
                        break

    def start_scheduled_race(self, race):
        """Start a scheduled race"""
        self.active_race = race
        self.CURRENT_COLOR = race['color']
        
        # Update race info with large text
        race_info = f"{race['duration']} MIN"
        if race['display_text']:
            race_info += f" - {race['display_text']}"
        self.race_info_label.config(text=race_info)
        
        # Start the timer
        self.is_running = True
        self.start_time = datetime.now()
        self.elapsed_base = timedelta(0)
        
        # Disable test mode when race starts
        if hasattr(self, 'test_mode'):
            self.test_mode = False
        
        # Recreate timer frame with segments
        self.create_timer_frame()

    def stop_timer(self):
        """Stop the current race"""
        self.is_running = False
        self.active_race = None
        self.race_info_label.config(text="")
        # Update display state to show logo
        self.update_display_state()
        
    def reset_timer(self):
        """Reset the timer and clear active race"""
        self.stop_timer()
        self.start_time = None
        self.elapsed_base = timedelta(0)
        # Disable test mode on reset
        if hasattr(self, 'test_mode'):
            self.test_mode = False
        for canvas in self.segment_canvases:
            canvas.delete('progress')
            canvas.configure(bg=self.FUTURE_COLOR)
        
    def create_styled_combobox(self, parent, variable, values, width=None):
        combo = ttk.Combobox(
            parent,
            textvariable=variable,
            values=values,
            font=('Segoe UI', 12),  # Increased font size
            width=width,
            state='readonly'
        )
        combo.option_add('*TCombobox*Listbox.font', ('Segoe UI', 12))  # Increased dropdown font size
        return combo

    def create_styled_button(self, parent, text, command, color, small=False):
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            font=('Segoe UI', 11 if small else 12, 'bold'),  # Increased font size
            bg=color,
            fg='white',
            relief='flat',
            padx=15 if small else 25,  # Increased padding
            pady=6 if small else 10,
            activebackground=color,
            activeforeground='white'
        )
        btn.bind('<Enter>', lambda e: btn.configure(bg=self.adjust_color(color, 1.1)))
        btn.bind('<Leave>', lambda e: btn.configure(bg=color))
        return btn

    def adjust_color(self, color, factor):
        """Adjust color brightness by factor (< 1 for darker, > 1 for lighter)"""
        # Convert hex to RGB
        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)
        
        # Adjust each component
        r = int(max(0, min(255, r * factor)))
        g = int(max(0, min(255, g * factor)))
        b = int(max(0, min(255, b * factor)))
        
        # Convert back to hex
        return f'#{r:02x}{g:02x}{b:02x}'

    def create_pattern(self, canvas, x, y, width, height, color):
        """Create a checkered pattern with alternating colors"""
        darker_color = self.adjust_color(color, 0.7)  # 70% brightness for darker shade
        
        # Calculate number of squares needed
        num_x = max(2, width // self.pattern_size)
        num_y = max(2, height // self.pattern_size)
        
        # Draw the pattern
        for i in range(num_x + 1):  # +1 to handle partial squares
            for j in range(num_y + 1):
                # Determine if this square should be dark or light
                is_dark = (i + j) % 2 == 0
                square_color = darker_color if is_dark else color
                
                # Calculate square position
                sx = x + (i * self.pattern_size)
                sy = y + (j * self.pattern_size)
                
                # Draw the square
                canvas.create_rectangle(
                    sx, sy,
                    min(sx + self.pattern_size, x + width),  # Don't exceed total width
                    min(sy + self.pattern_size, y + height),  # Don't exceed total height
                    fill=square_color,
                    outline=square_color,
                    tags='progress'
                )

    def pick_color(self):
        """Open color picker dialog and update current color"""
        color = colorchooser.askcolor(title="Choose Race Color", color=self.current_color)
        if color[1]:
            self.current_color = color[1]
            if self.is_running:
                self.update_timer()

    def create_schedule_list(self, parent):
        """Create a list view of scheduled races"""
        # Create frame for the list
        list_frame = ttk.Frame(parent, style='Dark.TFrame')
        list_frame.pack(fill='both', expand=True, pady=10, padx=10)
        
        # Add title and manual override controls
        title_frame = ttk.Frame(list_frame, style='Dark.TFrame')
        title_frame.pack(fill='x', pady=(0, 5))
        
        tk.Label(title_frame, text="Scheduled Races", font=('Segoe UI', 12, 'bold'),
                bg='#1A1A1A', fg='white').pack(side='left')
        
        # Add manual date/time override
        override_frame = ttk.Frame(title_frame, style='Dark.TFrame')
        override_frame.pack(side='right')
        
        tk.Label(override_frame, text="Test Time:", font=('Segoe UI', 10),
                bg='#1A1A1A', fg='white').pack(side='left', padx=(0, 5))
        
        # Manual date entry
        self.test_date_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        date_entry = tk.Entry(override_frame, textvariable=self.test_date_var,
                            width=10, font=('Segoe UI', 10))
        date_entry.pack(side='left', padx=2)
        
        # Manual time entry
        self.test_time_var = tk.StringVar(value=datetime.now().strftime('%H:%M'))
        time_entry = tk.Entry(override_frame, textvariable=self.test_time_var,
                            width=5, font=('Segoe UI', 10))
        time_entry.pack(side='left', padx=2)
        
        # Test and Cancel buttons
        self.create_styled_button(override_frame, "Test", self.set_test_time, '#2C5F90', True).pack(side='left', padx=2)
        self.create_styled_button(override_frame, "Cancel", self.cancel_test_time, '#C42B1C', True).pack(side='left', padx=2)
        
        # Create treeview with custom style for color display
        style = ttk.Style()
        style.configure("Custom.Treeview", rowheight=25)  # Increase row height for color display
        
        columns = ('Date', 'Time', 'Duration', 'Display Text', 'Color')
        self.schedule_tree = ttk.Treeview(list_frame, columns=columns, show='headings', 
                                        height=6, style="Custom.Treeview")
        
        # Configure columns
        column_widths = {
            'Date': 100,
            'Time': 60,
            'Duration': 80,
            'Display Text': 200,
            'Color': 60
        }
        
        for col in columns:
            self.schedule_tree.heading(col, text=col)
            self.schedule_tree.column(col, width=column_widths.get(col, 100))
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.schedule_tree.yview)
        self.schedule_tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack elements
        self.schedule_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Bind double-click to delete
        self.schedule_tree.bind('<Double-1>', self.delete_race)
        
        # Create color display tags
        self.schedule_tree.tag_configure('color_cell', anchor='center')

    def delete_race(self, event):
        """Delete a scheduled race"""
        selected_item = self.schedule_tree.selection()
        if selected_item:
            item = selected_item[0]
            race_values = self.schedule_tree.item(item)['values']
            # Remove from scheduled races list
            self.scheduled_races = [race for race in self.scheduled_races 
                                  if not (race['date'].strftime('%Y-%m-%d') == race_values[0] and 
                                        f"{race['time']:02d}:00" == race_values[1])]
            # Remove from treeview
            self.schedule_tree.delete(item)

    def update_segments(self, current_segment, total_minutes, seconds):
        if not self.active_race:
            return
            
        duration = self.active_race['duration']
        segment_progress = (total_minutes % duration) / duration
        seconds_progress = seconds / (duration * 60)
        total_progress = segment_progress + seconds_progress
        
        # Update current segment in race object
        self.active_race['current_segment'] = current_segment
        
        # Update display text and color based on current segment
        if 'segment_texts' in self.active_race and current_segment < len(self.active_race['segment_texts']):
            segment_text = self.active_race['segment_texts'][current_segment]
            if segment_text:
                self.race_info_label.config(text=segment_text)
        
        if 'segment_colors' in self.active_race and current_segment < len(self.active_race['segment_colors']):
            self.CURRENT_COLOR = self.active_race['segment_colors'][current_segment]
        
        for i, canvas in enumerate(self.segment_canvases):
            # Clear all dynamic content first
            canvas.delete('progress', 'countdown', 'countdown_shadow', 'pattern', 'segment_text', 'segment_text_shadow')
            width = canvas.winfo_width()
            height = canvas.winfo_height()
            
            if i < current_segment:
                # For completed segments, clear everything and set background
                canvas.delete('all')  # Clear all content including any remnants
                canvas.configure(bg=self.PAST_COLOR)
                # Redraw the time text for completed segments
                segment_start_minutes = i * duration
                segment_end_minutes = (i + 1) * duration
                time_text = f"{segment_start_minutes:02d}:00 - {segment_end_minutes:02d}:00"
                canvas.create_text(
                    22, height/2 + 2,
                    text=time_text,
                    fill=self.SHADOW_COLOR,
                    font=self.segment_font,
                    tags=('label_shadow',),
                    anchor='w'
                )
                canvas.create_text(
                    20, height/2,
                    text=time_text,
                    fill='white',
                    font=self.segment_font,
                    tags=('label',),
                    anchor='w'
                )
                
                # Add segment text if available
                if 'segment_texts' in self.active_race and i < len(self.active_race['segment_texts']):
                    segment_text = self.active_race['segment_texts'][i]
                    if segment_text:
                        # Draw segment text with shadow
                        canvas.create_text(
                            width - 20, height/2 + 2,
                            text=segment_text,
                            fill=self.SHADOW_COLOR,
                            font=self.segment_font,
                            tags=('segment_text_shadow',),
                            anchor='e'
                        )
                        canvas.create_text(
                            width - 22, height/2,
                            text=segment_text,
                            fill='white',
                            font=self.segment_font,
                            tags=('segment_text',),
                            anchor='e'
                        )
            elif i == current_segment:
                canvas.configure(bg=self.FUTURE_COLOR)
                fill_width = int(width * total_progress)
                
                if fill_width > 0:
                    # Draw shadow first
                    self.create_pattern(canvas, 2, 2, fill_width, height, self.SHADOW_COLOR)
                    # Draw main pattern
                    self.create_pattern(canvas, 0, 0, fill_width, height, self.CURRENT_COLOR)
                
                # Calculate remaining time
                minutes_until_next = duration - (total_minutes % duration) - 1
                seconds_until_next = 60 - seconds
                if seconds_until_next == 60:
                    seconds_until_next = 0
                    minutes_until_next += 1
                
                real_seconds_total = (minutes_until_next * 60 + seconds_until_next) / self.speed_multiplier
                real_minutes = int(real_seconds_total // 60)
                real_seconds = int(real_seconds_total % 60)
                countdown_text = f"{real_minutes:02d}:{real_seconds:02d}"
                
                # Draw countdown text with shadow
                canvas.create_text(
                    width/2 + 2, height/2 + 2,
                    text=countdown_text,
                    fill=self.SHADOW_COLOR,
                    font=self.countdown_font,
                    tags=('countdown_shadow',)
                )
                canvas.create_text(
                    width/2, height/2,
                    text=countdown_text,
                    fill='white',
                    font=self.countdown_font,
                    tags=('countdown',)
                )
                
                # Add segment text if available
                if 'segment_texts' in self.active_race and i < len(self.active_race['segment_texts']):
                    segment_text = self.active_race['segment_texts'][i]
                    if segment_text:
                        # Draw segment text with shadow
                        canvas.create_text(
                            width - 20, height/2 + 2,
                            text=segment_text,
                            fill=self.SHADOW_COLOR,
                            font=self.segment_font,
                            tags=('segment_text_shadow',),
                            anchor='e'
                        )
                        canvas.create_text(
                            width - 22, height/2,
                            text=segment_text,
                            fill='white',
                            font=self.segment_font,
                            tags=('segment_text',),
                            anchor='e'
                        )
            else:
                canvas.configure(bg=self.FUTURE_COLOR)
                # Ensure clean state for future segments
                canvas.delete('all')  # Clear everything
                # Redraw the time text for future segments
                segment_start_minutes = i * duration
                segment_end_minutes = (i + 1) * duration
                time_text = f"{segment_start_minutes:02d}:00 - {segment_end_minutes:02d}:00"
                canvas.create_text(
                    22, height/2 + 2,
                    text=time_text,
                    fill=self.SHADOW_COLOR,
                    font=self.segment_font,
                    tags=('label_shadow',),
                    anchor='w'
                )
                canvas.create_text(
                    20, height/2,
                    text=time_text,
                    fill='white',
                    font=self.segment_font,
                    tags=('label',),
                    anchor='w'
                )
                
                # Add segment text if available
                if 'segment_texts' in self.active_race and i < len(self.active_race['segment_texts']):
                    segment_text = self.active_race['segment_texts'][i]
                    if segment_text:
                        # Draw segment text with shadow
                        canvas.create_text(
                            width - 20, height/2 + 2,
                            text=segment_text,
                            fill=self.SHADOW_COLOR,
                            font=self.segment_font,
                            tags=('segment_text_shadow',),
                            anchor='e'
                        )
                        canvas.create_text(
                            width - 22, height/2,
                            text=segment_text,
                            fill='white',
                            font=self.segment_font,
                            tags=('segment_text',),
                            anchor='e'
                        )

    def toggle_fullscreen(self):
        self.root.attributes('-fullscreen', not self.root.attributes('-fullscreen'))
        
    def create_control_panel(self):
        """Create a separate window for controls"""
        self.control_window = tk.Toplevel(self.root)
        self.control_window.title("Race Scheduler Controls")
        self.control_window.geometry("1200x500")  # Even wider to ensure all elements are visible
        self.control_window.configure(bg='#1A1A1A')
        self.control_window.withdraw()  # Hide by default
        
        # Add control panel toggle
        control_btn = tk.Button(
            self.main_container,
            text="⚙",
            font=('Segoe UI', 14),
            bg='#000000',
            fg='#FFFFFF',
            command=self.toggle_control_panel,
            relief='flat'
        )
        control_btn.place(x=10, y=10)
        
        self.create_input_frame(self.control_window)

    def toggle_control_panel(self):
        try:
            if not hasattr(self, 'control_window') or not self.control_window.winfo_exists():
                self.create_control_panel()
            elif self.control_window.state() == 'withdrawn':
                self.control_window.deiconify()
            else:
                self.control_window.withdraw()
        except tk.TclError:
            # If we get here, the window was destroyed
            self.create_control_panel()
            self.control_window.deiconify()

    def schedule_race(self):
        """Schedule a new race"""
        if not self.lap_duration.get():
            return
            
        try:
            # Create date from spinbox values
            race_date = datetime(
                int(self.year_var.get()),
                int(self.month_var.get()),
                int(self.day_var.get())
            ).date()
            
            # Get segment settings
            segment_texts = [var.get() for var in self.segment_text_vars]
            segment_colors = [var.get() for var in self.segment_color_vars]
            
            # Create race object
            race = {
                'id': str(uuid.uuid4()),
                'date': race_date,
                'time': int(self.start_hour.get()),
                'duration': int(self.lap_duration.get()),
                'display_text': self.display_text.get(),
                'color': self.current_color,
                'segment_texts': segment_texts,
                'segment_colors': segment_colors,
                'current_segment': 0
            }
            
            print(f"Scheduling race: {race}")
            
            # Add to scheduled races
            self.scheduled_races.append(race)
            
            # Add to treeview with color indicator
            color_text = "■"  # Unicode square character
            item = self.schedule_tree.insert('', 'end',
                values=(
                    race['date'].strftime('%Y-%m-%d'),
                    f"{race['time']:02d}:00",
                    f"{race['duration']} min",
                    race['display_text'],
                    color_text
                ),
                tags=(f'color_{race["id"]}',)
            )
            
            # Configure tag for this specific color
            self.schedule_tree.tag_configure(f'color_{race["id"]}', foreground=race['color'])
            
            # Clear inputs
            self.display_text.set('')
            self.current_color = '#FFA500'  # Reset to default orange
            for var in self.segment_text_vars:
                var.set('')
            for var in self.segment_color_vars:
                var.set('#FFA500')
            
            # Force immediate check in case the race should start now
            self.check_scheduled_races()
        except ValueError:
            # If date is invalid, do nothing
            pass

    def cancel_test_time(self):
        """Cancel test time mode and return to current time"""
        if hasattr(self, 'test_mode'):
            self.test_mode = False
            delattr(self, 'test_datetime')
        # Force immediate update of display
        self.update_current_time()

    def update_segment_text_inputs(self):
        """Update the segment text input fields based on the selected duration"""
        # Clear existing segment text inputs
        for widget in self.segment_texts_frame.winfo_children():
            widget.destroy()
        self.segment_text_vars.clear()
        self.segment_color_vars.clear()
        
        # Get number of segments based on duration
        try:
            duration = int(self.lap_duration.get() or 12)
            num_segments = 60 // duration
        except ValueError:
            num_segments = 5  # Default to 5 segments if duration is invalid
        
        # Create new segment text inputs
        for i in range(num_segments):
            segment_frame = ttk.Frame(self.segment_texts_frame, style='Dark.TFrame')
            segment_frame.pack(fill='x', pady=2)
            
            # Calculate segment time range
            start_min = i * duration
            end_min = (i + 1) * duration
            time_range = f"{start_min:02d}:00 - {end_min:02d}:00"
            
            # Create label with time range
            tk.Label(segment_frame, text=time_range, font=('Segoe UI', 10),
                    bg='#1A1A1A', fg='white', width=15).pack(side='left', padx=(0, 10))
            
            # Create color picker button
            color_var = tk.StringVar(value='#FFA500')
            self.segment_color_vars.append(color_var)
            color_btn = self.create_styled_button(
                segment_frame,
                "Set Color",
                lambda idx=i: self.pick_segment_color(idx),
                color_var.get(),
                True
            )
            color_btn.pack(side='left', padx=(0, 10))
            
            # Create text variable and entry
            text_var = tk.StringVar()
            self.segment_text_vars.append(text_var)
            
            entry = tk.Entry(
                segment_frame,
                textvariable=text_var,
                font=('Segoe UI', 10),
                bg='#2D2D2D',
                fg='white',
                insertbackground='white',
                relief='flat',
                width=40
            )
            entry.pack(side='left', fill='x', expand=True)

    def pick_segment_color(self, segment_index):
        """Open color picker dialog for a specific segment"""
        color = colorchooser.askcolor(title=f"Choose Color for Segment {segment_index + 1}", 
                                    color=self.segment_color_vars[segment_index].get())
        if color[1]:
            self.segment_color_vars[segment_index].set(color[1])
            if self.is_running and self.active_race and segment_index == (self.active_race['current_segment'] if 'current_segment' in self.active_race else 0):
                self.CURRENT_COLOR = color[1]
                self.update_timer()

if __name__ == "__main__":
    root = tk.Tk()
    app = RaceTimer(root)
    root.mainloop() 