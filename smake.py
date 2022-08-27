from smake import Smake

Smake.executable("main", "test/src", ["test_lib"])
Smake.library("test_lib", "test/lib")

Smake.run("main")

Smake.DEBUG = True
