from smake import Smake

Smake.executable("test_exec", ["test/src", "test/src2"], ["test_lib"])
Smake.library("test_lib", ["test/lib", "test/lib2"])

Smake.alias("main", "test_exec")

Smake.run("main")

Smake.DEBUG = True
