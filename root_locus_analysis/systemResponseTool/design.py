# root_locus_analysis/systemResponseTool/design.py
from __future__ import annotations
from typing import List
from .core import Parser, SysSpec

def ogata_ex_6_6_closed_loop() -> List[SysSpec]:
    p = Parser()
    return [
        p.parse_sys_arg("tf; name=Uncomp;  num=10; den=1,1,10; fb=none; color=#1f77b4"),
        p.parse_sys_arg("tf; name=Comp M1; num=12.287,23.876; den=1,5.646,16.933,23.876; fb=none; color=#2ca02c; dash=dot"),
        p.parse_sys_arg("tf; name=Comp M2; num=9; den=1,3,9; fb=none; color=#d62728; dash=dash"),
    ]

def ogata_ex_6_6_open_loop_unity() -> List[SysSpec]:
    p = Parser()
    return [
        p.parse_sys_arg("tf; name=G0(OL);      num=10;                  den=1,1,0"),
        p.parse_sys_arg("tf; name=Lead-M1(OL); num=12.287*(s+1.9432);   den=(s+4.6458)*s*(s+1); color=#2ca02c; dash=dot"),
        p.parse_sys_arg("tf; name=Lead-M2(OL); num=0.9*(s+1)*10;        den=(s+3)*s*(s+1);     color=#d62728; dash=dash"),
    ]
