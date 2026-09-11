import os
import tempfile
from pathlib import Path
from medha.build import BuildSystem

def test_build_system_detection_and_makefile():
    with tempfile.TemporaryDirectory() as tmpdir:
        bs = BuildSystem(tmpdir)
        assert bs.detect() is None
        assert bs.configure()[0] == 1
        assert bs.build()[0] == 1

        # Create Makefile
        makefile = Path(tmpdir) / "Makefile"
        makefile.write_text("all:\n\t@echo 'Build Success'\n")
        assert bs.detect() == "make"

        code, out = bs.configure()
        assert code == 0

        code, out, artifact = bs.build()
        assert code == 0
        assert "Build Success" in out

def test_build_system_cmake():
    with tempfile.TemporaryDirectory() as tmpdir:
        bs = BuildSystem(tmpdir)
        cmake_file = Path(tmpdir) / "CMakeLists.txt"
        cmake_file.write_text("""
cmake_minimum_required(VERSION 3.10)
project(TestProj C)
add_executable(test_bin main.c)
""")
        main_c = Path(tmpdir) / "main.c"
        main_c.write_text("""
#include <stdio.h>
int main() {
    printf("Hello CMake\\n");
    return 0;
}
""")
        assert bs.detect() == "cmake"

        code, out = bs.configure()
        assert code == 0

        code, out, artifact = bs.build()
        assert code == 0
        assert os.path.exists(artifact)
