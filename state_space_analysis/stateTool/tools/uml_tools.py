from __future__ import annotations

def plantuml_skeleton() -> str:
    return """@startuml
skinparam classAttributeIconSize 0

package state_space_analysis.stateTool {
  class StateToolApp
  class StateSpaceAnalyzerAPI
  class StateSpaceModel
  class RunOptions
}
StateToolApp --> StateSpaceAnalyzerAPI
StateSpaceAnalyzerAPI --> StateSpaceModel
@enduml
"""
