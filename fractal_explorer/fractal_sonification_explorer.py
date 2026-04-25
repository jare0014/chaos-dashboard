# %%
# ==========================================
# UPDATED INTERACTIVE CLASS (With Duration Control)
# ==========================================

class InteractiveFractal:
    def __init__(self):
        self.width = 600
        self.height = 600
        self.rule_id = 0
        self.max_iter = 120
        self.xlim = [-2.0, 1.0]
        self.ylim = [-1.5, 1.5]
        
        self.fig, self.ax = plt.subplots(figsize=(7, 7))
        self.canvas = self.fig.canvas
        self.im = None
        self.audio_out = widgets.Output()
        
        # --- UI CONTROLS ---
        self.rule_selector = widgets.Dropdown(
            options=[('Mandelbrot', 0), ('Burning Ship', 1), ('Tricorn', 2), ('Scepter', 3)],
            description='Rule:',
            layout=widgets.Layout(width='200px')
        )
        self.rule_selector.observe(self.on_rule_change, names='value')
        
        # NEW: Duration Slider (1 to 10 seconds)
        self.duration_slider = widgets.IntSlider(
            value=4, min=1, max=10, step=1, 
            description='Audio (sec):',
            layout=widgets.Layout(width='300px')
        )
        
        self.instructions = widgets.HTML(
            "<b>Controls:</b><br>"
            "• <b>Scroll Wheel:</b> Zoom In/Out<br>"
            "• <b>Click & Drag:</b> Pan (updates on release)<br>"
            "• <b>SHIFT + Click:</b> Generate Audio"
        )

        self.drag_start = None
        self.is_dragging = False
        
        self.canvas.mpl_connect('scroll_event', self.on_scroll)
        self.canvas.mpl_connect('button_press_event', self.on_press)
        self.canvas.mpl_connect('button_release_event', self.on_release)
        
        self.update_plot()
        
    def on_rule_change(self, change):
        self.rule_id = change['new']
        self.update_plot()

    def update_plot(self):
        img_data = render_fractal_fast(
            self.width, self.height, 
            self.xlim[0], self.xlim[1], 
            self.ylim[0], self.ylim[1], 
            self.max_iter, self.rule_id
        )
        
        if self.im is None:
            self.im = self.ax.imshow(
                img_data, extent=[self.xlim[0], self.xlim[1], self.ylim[0], self.ylim[1]],
                origin='lower', cmap='magma'
            )
            self.ax.set_axis_off()
        else:
            self.im.set_data(img_data)
            self.im.set_extent([self.xlim[0], self.xlim[1], self.ylim[0], self.ylim[1]])
        
        self.fig.canvas.draw_idle()

    def on_scroll(self, event):
        if event.inaxes != self.ax: return
        base_scale = 1.2
        scale_factor = 1/base_scale if event.button == 'up' else base_scale
        
        cur_x_range = self.xlim[1] - self.xlim[0]
        cur_y_range = self.ylim[1] - self.ylim[0]
        x_rel = (event.xdata - self.xlim[0]) / cur_x_range
        y_rel = (event.ydata - self.ylim[0]) / cur_y_range
        
        new_x_range = cur_x_range * scale_factor
        new_y_range = cur_y_range * scale_factor
        
        self.xlim = [event.xdata - x_rel * new_x_range, event.xdata + (1 - x_rel) * new_x_range]
        self.ylim = [event.ydata - y_rel * new_y_range, event.ydata + (1 - y_rel) * new_y_range]
        self.update_plot()

    def on_press(self, event):
        if event.inaxes != self.ax: return
        if event.key == 'shift':
            c = complex(event.xdata, event.ydata)
            self.play_sound(c)
            return
        self.is_dragging = True
        self.drag_start = (event.xdata, event.ydata)

    def on_release(self, event):
        if not self.is_dragging or event.inaxes != self.ax: 
            self.is_dragging = False
            return
        dx = self.drag_start[0] - event.xdata
        dy = self.drag_start[1] - event.ydata
        self.xlim = [x + dx for x in self.xlim]
        self.ylim = [y + dy for y in self.ylim]
        self.is_dragging = False
        self.update_plot()

    def play_sound(self, c):
        sr = 11025
        # Use the value from the slider
        duration = self.duration_slider.value
        
        # Generate Float32 Audio
        L, R = generate_orbit_audio(c, float(duration), sr, self.rule_id)
        
        L = np.clip(L, -1.0, 1.0)
        R = np.clip(R, -1.0, 1.0)
        audio_data = np.array([L, R])
        
        with self.audio_out:
            clear_output(wait=True)
            print(f"🎵 Playing {duration}s Orbit: {c.real:.5f} + {c.imag:.5f}i")
            display(Audio(audio_data, rate=sr, normalize=False, autoplay=True))

    def show(self):
        # Layout organization
        controls = widgets.HBox([self.rule_selector, self.duration_slider])
        display(widgets.VBox([
            self.instructions,
            controls,
            self.audio_out
        ]))

# Run the Explorer
explorer = InteractiveFractal()
explorer.show()

# %%



