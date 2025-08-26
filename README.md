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

```python
pip install sketulate

## Quick Example
from sketulate import Sketulate, SketulateInteraction

# Draw a univariate function
f1 = Sketulate()
f1.sketch()
```


![Sketch a Function](examples/images/draw_a_function.png)

```python
# F1 is a now a ready to use function via:
f1.f
# f takes the form of a sklearn pipeline object,so you need to call predict on new data:
f1.f.predict()
# Or a custom density distribution (selected in the canvas dropdown) via:
f1.g
# Draw 100 samples from g  by calling:
f1.g(100)
```
![Sketch a Density](examples/images/draw_a_density.png)

```python
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
