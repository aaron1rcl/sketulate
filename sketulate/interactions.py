import numpy as np
import matplotlib.pyplot as plt
from IPython.display import display, clear_output
from scipy.interpolate import LinearNDInterpolator
from ipywidgets import FloatSlider, Button, Layout, VBox, HBox, Output



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

    def save_state(self):
        """Return a dictionary of state for serialization: x_min, x_max, y_min, y_max, z_min, z_max, grid_size, x, y, z."""
        return {
            "x_min": self.x_range[0],
            "x_max": self.x_range[1],
            "y_min": self.y_range[0],
            "y_max": self.y_range[1],
            "z_min": self.z_range[0],
            "z_max": self.z_range[1],
            "grid_size": self.grid_size,
            "x": self.x.tolist() if self.x is not None else None,
            "y": self.y.tolist() if self.y is not None else None,
            "z": self.z.tolist() if self.z is not None else None,
        }

    def load_state(self, state):
        """Restore state from a saved state dict and rebuild the interpolator."""
        self.x_range = (state["x_min"], state["x_max"])
        self.y_range = (state["y_min"], state["y_max"])
        self.z_range = (state["z_min"], state["z_max"])
        self.X, self.Y = np.meshgrid(
            np.linspace(*self.x_range, self.grid_size),
            np.linspace(*self.y_range, self.grid_size),
        )
        if state["x"] is not None and state["y"] is not None and state["z"] is not None:
            if state["grid_size"] != self.grid_size:
                raise ValueError(
                    f"Saved state has grid_size {state['grid_size']}, but this object has grid_size {self.grid_size}. "
                    "Create a SketulateInteraction with the same grid_size first."
                )
            self.x = np.array(state["x"])
            self.y = np.array(state["y"])
            self.z = np.array(state["z"])
            self.Z = self.z.reshape(self.grid_size, self.grid_size)
            for k in range(len(self.sliders)):
                self.sliders[k].value = self.Z.flat[k]
            points = np.column_stack([self.x, self.y])
            self.f = LinearNDInterpolator(points, self.z, fill_value=np.nan)
            A = np.column_stack([self.x, self.y, np.ones_like(self.x)])
            self.linear_plane, _, _, _ = np.linalg.lstsq(A, self.z, rcond=None)
        else:
            self.Z = np.zeros_like(self.X)
            for k in range(len(self.sliders)):
                self.sliders[k].value = 0.0
            self.x = self.y = self.z = None
            self.f = None
            self.linear_plane = None

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

