from ipycanvas import Canvas
from ipywidgets import VBox, HBox, Button, FloatText, Dropdown, interact, FloatSlider
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import SplineTransformer, PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import make_pipeline
import pickle
from mpl_toolkits.mplot3d import Axes3D
from ipycanvas import Canvas
from ipywidgets import VBox, HBox, Button, FloatText, Dropdown
import numpy as np
from scipy.interpolate import interp1d


class Sketulate:
    def __init__(self, width=200, height=200):
        self.width, self.height = width, height
        self.canvas = Canvas(width=width, height=height, background_color="white")
        self.canvas.layout.width = "200px"
        self.canvas.layout.height = "200px"
        self.points = []
        self.drawing = False

        # buttons
        self.clear_btn = Button(description="Clear")
        self.finish_btn = Button(description="Finish")
        self.accept_btn = Button(description="Accept", disabled=True)
        self.update_btn = Button(description="Update Range")

        # ranges
        self.x_min = FloatText(description="x min", value=0.0, layout={"width":"150px"})
        self.x_max = FloatText(description="x max", value=1.0, layout={"width":"150px"})
        self.y_min = FloatText(description="y min", value=0.0, layout={"width":"150px"})
        self.y_max = FloatText(description="y max", value=1.0, layout={"width":"150px"})

        # mode
        self.mode = Dropdown(description="Mode", options=["function", "density"], value="function")

        # bind canvas events
        self.canvas.on_mouse_down(self._start_drawing)
        self.canvas.on_mouse_up(self._stop_drawing)
        self.canvas.on_mouse_move(self._record_point)

        # bind buttons
        self.clear_btn.on_click(self.clear_canvas)
        self.finish_btn.on_click(self.finish_drawing)
        self.update_btn.on_click(self._draw_grid)

        # internal callback
        self.accept_callback = None
        self.accept_btn.on_click(self._on_accept)

        # draw first grid
        self._draw_grid()

        self.x = None
        self.y = None
        self.f = None
        self.g = None


    # ---------------- Drawing ----------------
    def _draw_grid(self, b=None):
        self.canvas.clear()

        # grid lines
        step = self.width // 10
        self.canvas.stroke_style = "#e0e0e0"
        for i in range(0, self.width+1, step):
            self.canvas.stroke_line(i, 0, i, self.height)
        for j in range(0, self.height+1, step):
            self.canvas.stroke_line(0, j, self.width, j)

        # redraw points
        self.canvas.fill_style = "black"
        for x, y in self.points:
            self.canvas.fill_circle(x, y, 2)

    def _start_drawing(self, x, y):
        self.drawing = True
        self.points.append((x, y))
        self.canvas.fill_style = "black"
        self.canvas.fill_circle(x, y, 2)

    def _stop_drawing(self, x, y):
        self.drawing = False

    def _record_point(self, x, y):
        if self.drawing:
            self.points.append((x, y))
            self.canvas.fill_style = "black"
            self.canvas.fill_circle(x, y, 2)

    # ---------------- Controls ----------------
    def clear_canvas(self, b=None):
        self.points = []
        self._draw_grid()
        self.accept_btn.disabled = True
        self.finish_btn.disabled = False

    def finish_drawing(self, b=None):
        if not self.points:
            print("Draw something first!")
            return
        self.accept_btn.disabled = False
        self.finish_btn.disabled = True
        print("Drawing finished, press Accept.")

    def accept(self, callback):
        """Set function to call when Accept is pressed"""
        self.accept_callback = callback

    def _on_accept(self, b=None):
        if self.accept_callback and self.points:
            xs, ys = self.get_points()
            self.accept_callback(self.mode.value, (xs, ys))
        self.accept_btn.disabled = True
        print("accept callback")
        self.get_points()
        print(self.mode.value)
        if self.mode.value == 'function':
          self.fit_piecewise_linear()
        elif self.mode.value == 'density':
          self.fit_density()

    def get_points(self):
        """Return scaled xs, ys according to user ranges"""
        if not self.points:
            raise ValueError("No points drawn yet!")
        xs, ys = zip(*self.points)
        xs = np.array(xs)
        ys = np.array(ys)

        # scale to axis ranges
        xs = (xs / self.width) * (self.x_max.value - self.x_min.value) + self.x_min.value
        ys = ((self.height - ys) / self.height) * (self.y_max.value - self.y_min.value) + self.y_min.value

        self.x = xs
        self.y = ys

    def fit_piecewise_linear(self, n_knots=20):
      sort_idx = np.argsort(self.x)
      xs_sorted, ys_sorted = self.x[sort_idx], self.y[sort_idx]
      n_knots = min(len(xs_sorted), n_knots)
      model = make_pipeline(
          SplineTransformer(n_knots=n_knots, degree=1),
          LinearRegression()
      )
      model.fit(xs_sorted.reshape(-1,1), ys_sorted)
      self.f = model

    def fit_density(self):
      # Ensure the density is non-negative
      ys_d = np.maximum(self.y, 0)

      # Normalize to integrate to 1
      area = np.trapezoid(ys_d, self.x)
      self.y_norm = ys_d / area

      # Interpolated density for sampling
      density_func = interp1d(self.x, self.y_norm, kind='linear', bounds_error=False, fill_value=0.0)

      def sample_from_density(n=1000):
          # Rejection sampling
          x_min, x_max = self.x.min(), self.x.max()
          y_max = self.y_norm.max()
          samples = []
          while len(samples) < n:
              x_trial = np.random.uniform(x_min, x_max)
              y_trial = np.random.uniform(0, y_max)
              if y_trial < density_func(x_trial):
                  samples.append(x_trial)
          return np.array(samples)

      self.g = sample_from_density


    # ---------------- UI ----------------
    def sketch(self):
        return VBox([
            self.canvas,
            HBox([self.clear_btn, self.finish_btn, self.accept_btn, self.mode]),
            HBox([self.x_min, self.x_max, self.y_min, self.y_max, self.update_btn])
        ])


