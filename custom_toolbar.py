from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg,
                                            NavigationToolbar2Tk) 

class CustomToolbar(NavigationToolbar2Tk):
    """custom toolbar based on NavigationToolbar2Tk"""
    
    def save_highdef(self):
        """save figure image at a higher dpi for publication etc"""
        savefile = tk.filedialog.asksaveasfilename(defaultextension = ".png",
                                        filetypes=[("PNG", ".png"),
                                                    ("JPEG", ".jpeg"),
                                                    ("TIF", ".tif"),
                                                    ("PDF", ".pdf")],
                                        initialfile = "figure",
                                        title = "Save High Resolution Figure")
        if savefile == "":
            pass
        else:
            olddpi = self.canvas.figure.dpi
            self.canvas.figure.set_dpi(int(self.inputdpi))
            self.canvas.figure.savefig(savefile)
            self.canvas.figure.set_dpi(olddpi)
            
    def _update_buttons_checked(self, mode = None):
        # sync button checkstates to match active mode
        for text in ['Zoom', 'Pan']:
            if text in self._buttons:
                if mode == self.button_pressed and mode == text:
                    self._buttons[text].deselect()
                    self.button_pressed = None
                elif self.button_pressed == None and mode == text:
                    self._buttons[text].select()
                    self.button_pressed = mode
                elif mode == text and self.button_pressed != mode:
                    self._buttons[text].select()
                    self.button_pressed = mode
                else:
                    self._buttons[text].deselect()

    def pan(self, *args):
        super().pan(*args)
        self._update_buttons_checked(mode = "Pan")

    def zoom(self, *args):
        super().zoom(*args)
        self._update_buttons_checked(mode = "Zoom")
        
    def __init__(self, canvas_, parent_):
        """Initialise toolbar with custom button added to toolitems"""
        self.toolitems = (
            ('Home', 'Reset original view', 'home', 'home'),
            ('Back', 'Back to previous view', 'back', 'back'),
            ('Forward', 'Forward to next view', 'forward', 'forward'),
            ('Pan', 'Pan axes with left mouse, zoom with right', 'move', 'pan'),
            ('Zoom', 'Zoom to rectangle', 'zoom_to_rect', 'zoom'),
            ('Subplots', 'Configure subplots', 'subplots',
                'configure_subplots'),
            (None, None, None, None),
            ('Save', 'Save the figure', 'filesave', 'save_figure'),
            (None, None, None, None),
            (None, None, None, None),
            ('Save High Quality', 'Save a high quality figure', 'filesave',
                'save_highdef'),
            )
        self.inputdpi = 600
        self.button_pressed = None
        NavigationToolbar2Tk.__init__(self,canvas_,parent_)
