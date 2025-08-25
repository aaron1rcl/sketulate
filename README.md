# Sketulate

**Sketulate** is a Python package for interactive function, surface, and density simulation directly in Jupyter notebooks. Draw functions, surfaces, or densities with your mouse, convert them into callable functions or density distributions, and simulate data for experiments, modeling, or teaching.

## Features

- Sketch univariate functions interactively (`Sketulate`)  
- Sketch 2D surfaces / interactions effects (`SketulateInteraction`)  
- Sketch density distributions
- Generates easy to use functions and sampleable density distributions
- Works seamlessly in Jupyter Notebook
- Easy integration for synthetic data generation  

## Installation

```bash
pip install sketulate

## Quick Example
from sketulate import Sketulate, SketulateInteraction

# Draw a univariate function
f1 = Sketulate(x_min=0, x_max=10, y_min=-5, y_max=5)
f1.sketch()
```


![Sketch a Function](examples/images/draw_a_function.png)

``` bash
f1.accept(callback)  # After drawing, click Accept
# F1 is a now a ready to use function via
f1.f
# Or a custom density distribution (selected in the canvas dropdown) via
f1.g
```
![Sketch a Density](examples/images/draw_a_density.png)

``` bash
# Draw an interaction surface
f3 = SketulateInteraction(x_range=(0,10), y_range=(0,10), z_range=(-5,5), grid_size=5)
f3.sketch()  # Interactive surface with sliders
```

![Sketch Interaction Surface via Sliders](examples/images/interaction_surfaces.png)

#### Put it all together and easily simulate some data
![Sketch a Function](examples/images/simulate_data.png)


## Technical Note
For this version the sketches are modelled via piecewise linear basis functions using sklearn.
Interaction surfaces are modelled using the LinearND interpolator from scipy.
In addition, linear extrapolation is, by default, provided outside of the given ranges. Careful!


