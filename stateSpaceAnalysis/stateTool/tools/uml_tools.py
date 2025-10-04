from __future__ import annotations

def plantuml_skeleton() -> str:
    return """@startuml
skinparam classAttributeIconSize 0

package stateSpaceAnalysis.stateTool {
  class StateToolApp
  class StateSpaceAnalyzerAPI
  class StateSpaceModel
  class RunOptions
}
StateToolApp --> StateSpaceAnalyzerAPI
StateSpaceAnalyzerAPI --> StateSpaceModel
@enduml
"""
