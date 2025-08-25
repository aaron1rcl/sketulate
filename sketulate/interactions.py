import numpy as np
import matplotlib.pyplot as plt
from ipywidgets import FloatSlider, HBox, VBox, Layout, Button
from IPython.display import display, clear_output
from scipy.interpolate import LinearNDInterpolator

import numpy as np
import matplotlib.pyplot as plt
from ipywidgets import FloatSlider, Button, Layout, VBox, HBox, Output
from IPython.display import display, clear_output
from scipy.interpolate import LinearNDInterpolator

class SketulateInteraction:
    def __init__(self, x_range=(-5,5), y_range=(-5,5), z_range=(-5,5), grid_size=5):
        self.grid_size = grid_size
        self.x_range = x_range
        self.y_range = y_range
        self.z_range = z_range
        
        # Meshgrid
        self.X, self.Y = np.meshgrid(np.linspace(*x_range, grid_size),
                                     np.linspace(*y_range, grid_size))
        self.Z = np.zeros_like(self.X)
        
        # Sliders
        self.sliders = []
        self.slider_layout = Layout(width="80px", height="20px")
        self.rows = []
        for i in range(grid_size):
            row_sliders = [self._make_slider(i, j) for j in range(grid_size)]
            self.sliders.extend(row_sliders)
            self.rows.append(HBox(row_sliders))
        
        # Accept button
        self.accept_btn = Button(description="Accept", button_style="success")
        self.accept_btn.on_click(self._on_accept)
        
        # Dedicated outputs (plot + logs)
        self.plot_out = Output()
        self.log_out = Output()
        
        # UI container (displayed ONCE)
        self.ui = VBox(self.rows + [self.accept_btn, self.plot_out, self.log_out])
        
        # Storage
        self.x = self.y = self.z = None
        self.f = None
        self.linear_plane = None

    def _make_slider(self, i, j):
        slider = FloatSlider(
            value=0,
            min=self.z_range[0],
            max=self.z_range[1],
            step=0.1,
            description="",
            continuous_update=False,  # set True if you want live-drag updates
            readout=False,
            layout=self.slider_layout
        )
        def update(change, ii=i, jj=j):
            # Use 'change["new"]' to get the committed value
            self.Z[ii, jj] = change["new"]
            self._plot_surface()
        slider.observe(update, names="value")
        return slider
    
    def _plot_surface(self):
        # Only clear/redraw the PLOT area, not the whole cell
        with self.plot_out:
            clear_output(wait=True)
            fig = plt.figure(figsize=(6,6))
            ax = fig.add_subplot(111, projection='3d')
            ax.plot_surface(self.X, self.Y, self.Z, cmap="viridis")
            ax.set_zlim(*self.z_range)
            plt.show()

    def _on_accept(self, b):
        self.x = self.X.flatten()
        self.y = self.Y.flatten()
        self.z = self.Z.flatten()
        
        points = np.column_stack([self.x, self.y])
        self.f = LinearNDInterpolator(points, self.z, fill_value=np.nan)
        
        A = np.column_stack([self.x, self.y, np.ones_like(self.x)])
        self.linear_plane, _, _, _ = np.linalg.lstsq(A, self.z, rcond=None)

        with self.log_out:
            print("Surface accepted. ND linear interpolator with linear extrapolation ready.")
    
    def predict(self, x_new, y_new):
        x_new = np.array(x_new)
        y_new = np.array(y_new)
        points_new = np.column_stack([x_new, y_new])
        z_pred = self.f(points_new)
        nan_mask = np.isnan(z_pred)
        if np.any(nan_mask):
            a, b, c = self.linear_plane
            z_pred[nan_mask] = a*x_new[nan_mask] + b*y_new[nan_mask] + c
        return z_pred
    
    def plot_fitted_surface(self, n_points=50):
        x_fine = np.linspace(*self.x_range, n_points)
        y_fine = np.linspace(*self.y_range, n_points)
        X_fine, Y_fine = np.meshgrid(x_fine, y_fine)
        Z_fine = self.predict(X_fine.flatten(), Y_fine.flatten()).reshape(X_fine.shape)
        
        fig = plt.figure(figsize=(6,6))
        ax = fig.add_subplot(111, projection='3d')
        ax.plot_surface(X_fine, Y_fine, Z_fine, cmap="viridis")
        ax.set(xlabel="X", ylabel="Y", zlabel="Z",
               xlim=self.x_range, ylim=self.y_range, zlim=self.z_range)
        plt.show()
    
    def sketch(self):
        display(self.ui)        # display once
        self._plot_surface()    # initial draw

