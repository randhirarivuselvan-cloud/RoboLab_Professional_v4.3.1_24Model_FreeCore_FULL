from __future__ import annotations
from typing import Any
from ai.engines import ENGINE


def _text(payload: dict[str, Any]) -> str:
    return str(payload.get('description') or payload.get('idea') or payload.get('code') or '')

SPECIALISTS = {
    'component': lambda p: {'stage':'component','result':ENGINE.bom(_text(p)),'mode':'native-specialist'},
    'simulation': lambda p: {'stage':'simulation','result':{'test_plan':['nominal_case','boundary_case','fault_case'],'inputs':p,'status':'PLAN_ONLY'},'mode':'native-specialist'},
    'documentation': lambda p: {'stage':'documentation','result':{'sections':['requirements','architecture','components','interfaces','verification','open_questions'],'source':p},'mode':'native-specialist'},
    'verifier_1': lambda p: {'stage':'verifier_1','result':ENGINE.verify(_text(p)),'mode':'native-specialist','independence':'pass-1'},
    'verifier_2': lambda p: {'stage':'verifier_2','result':ENGINE.verify(_text(p)),'mode':'native-specialist','independence':'pass-2'},
    'compiler_1': lambda p: {'stage':'compiler_1','result':ENGINE.compile_project(p.get('project') or p),'mode':'native-specialist','independence':'pass-1'},
    'compiler_2': lambda p: {'stage':'compiler_2','result':ENGINE.compile_project(p.get('project') or p),'mode':'native-specialist','independence':'pass-2'},
}
