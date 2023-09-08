#!/usr/bin/env python3
# pylint: disable=missing-class-docstring,no-self-use,line-too-long

import os
import unittest

import angr
import angr.calling_conventions
from angr.sim_type import SimTypePointer

test_location = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "..", "binaries", "tests")


class TestPrototypes(unittest.TestCase):
    def test_function_prototype(self):
        proj = angr.Project(os.path.join(test_location, "x86_64", "all"), auto_load_libs=False)

        func = angr.knowledge_plugins.Function(proj.kb.functions, 0x100000, name="strcmp")
        func.prototype = angr.SIM_LIBRARIES["libc.so.6"].prototypes[func.name]
        func.calling_convention = angr.calling_conventions.DEFAULT_CC[proj.arch.name](proj.arch)

    def test_find_prototype(self):
        proj = angr.Project(os.path.join(test_location, "x86_64", "all"), auto_load_libs=False)

        cfg = proj.analyses.CFG()

        func = cfg.kb.functions.function(name="strcmp", plt=False)
        func.calling_convention = angr.calling_conventions.DEFAULT_CC[proj.arch.name](proj.arch)

        func.find_declaration()

        arg_locs = func.calling_convention.arg_locs(func.prototype)

        assert len(arg_locs) == 2
        assert arg_locs[0].reg_name == "rdi"
        assert arg_locs[1].reg_name == "rsi"

    def test_cpp_void_pointer(self):
        proj = angr.Project(os.path.join(test_location, "x86_64", "void_pointer"), auto_load_libs=False)

        cfg = proj.analyses.CFG()
        proj.analyses.CompleteCallingConventions(recover_variables=True, analyze_callsites=True)

        func = cfg.kb.functions.function(name="_ZdlPvm", plt=True)
        assert isinstance(func.prototype.args[0], SimTypePointer)


if __name__ == "__main__":
    unittest.main()
