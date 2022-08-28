from smake import Smake

Smake.executable("main", ["test/src", "test/src2"], ["test_lib"])
Smake.library("test_lib", ["test/lib", "test/lib2"])

Smake.run("main")

Smake.DEBUG = True
