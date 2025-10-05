    # -*- coding: utf-8 -*-
    """
    Lightweight class diagram emitter (Mermaid). Keeps external deps optional.
    """
    def mermaid_class_diagram() -> str:
        return """
```mermaid
classDiagram
  direction LR
  class ControllerToolApp{
    +DesignInputs din
    +BuildConfig bcfg
    +build() BuildResult
  }
  class DesignInputs{
    +num: ndarray
    +den: ndarray
    +K_poles: ndarray?
    +obs_poles: ndarray?
    +ts: float?
    +undershoot: (float,float)?
    +obs_speed_factor: float
  }
  class BuildConfig{ +cfg: str }
  class BuildResult{
    +plant_ss
    +K: ndarray
    +Ke: ndarray
    +Gc: TransferFunction
    +T1: TransferFunction?
    +T2: TransferFunction?
  }
  class PlantSS{ +as_ct() }
  class PlotService{ +plot_closed_loop_bode_and_step() }

  ControllerToolApp --> DesignInputs
  ControllerToolApp --> BuildConfig
  ControllerToolApp --> BuildResult
  BuildResult --> PlantSS
  PlotService --> BuildResult
```
"""
