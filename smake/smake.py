from enum import Enum, Flag, auto
import os, shutil

from .dispatcher import Dispatcher

VALID_EXTENSIONS = [
    ".c", ".cpp", ".cu"
]

class Language(Flag):
    EXEC = auto()
    C = auto()
    CPP = auto()
    CUDA = auto()

    ALL = EXEC | C | CPP | CUDA

class TargetType(Enum):
    EXECUTABLE = auto()
    LIBRARY = auto()
    CUDA_LIBRARY = auto()
    DYNAMIC = auto()

class Target:
    def __init__(self, name: str, directories: list, type_: TargetType, files: list = None, dependencies: list = None, includes: list = None):
        self.name = name
        self.directories = directories
        self.type = type_

        self.files = [] if files is None else files
        self.dependencies = [] if dependencies is None else dependencies
        self.includes = [] if includes is None else includes
    
    def build(self) -> 'Target':
        if self.type == TargetType.DYNAMIC:
            return self
        
        print(f"Building {self.name}")

        targets = [Smake._build(dep) for dep in self.dependencies]

        includes = self.directories
        for target in targets:
            for flag in target._compile_params().get("flags", []):
                if flag.startswith("-I"):
                    includes.append(flag[2:])
        
        objects = []
        rebuild = {}
        for fn in self.files:
            obj = Smake._change_dir(self._to_object(fn))
            objects.append(obj)

            inc = Smake._find_includes(fn, self.includes + includes)

            if os.path.isfile(obj):
                for filename in [fn] + inc:
                    if os.path.getmtime(obj) < os.path.getmtime(filename):
                        rebuild[obj] = fn
                        break
            else:
                rebuild[obj] = fn
        
        for obj, fn in rebuild.items():
            os.makedirs(os.path.dirname(obj), exist_ok=True)
            
            lang = Smake._get_language(fn)
            flags = [
                "-g" if Smake.DEBUG else "-O3",
                "-std=c++23" if lang == Language.CPP else "-std=c2x" if lang == Language.C else ""
            ] + [
                f"-I{inc}" for inc in self.includes
            ] + [
                f"-I{d}" for d in self.directories
            ]
            for target in targets:
                params = target._compile_params()
                flags += params.get("flags", [])
            
            command = [Smake._compiler(fn)] + Smake._get_flags(lang) + flags + ["-c", "-o", obj, fn]
            Dispatcher.run(command)
        
        Dispatcher.wait()
        
        if self.type == TargetType.LIBRARY:
            self.static_lib_path = Smake._change_dir(f"lib{self.name}.a")

            rebuild = not os.path.exists(self.static_lib_path)
            if os.path.isfile(self.static_lib_path):
                for obj in objects:
                    if os.path.getmtime(self.static_lib_path) < os.path.getmtime(obj):
                        rebuild = True
                        break
            
            if rebuild:
                command = ["ar", "rcs", self.static_lib_path] + objects
                Dispatcher.run(command)

        elif self.type == TargetType.EXECUTABLE:
            flags = [
                "-g" if Smake.DEBUG else "-O3",
                "-std=c++23"
            ]
            libs = []
            for target in targets:
                params = target._link_params()
                flags += params.get("flags", [])
                libs += params.get("libs", [])
            
            rebuild = not os.path.exists(self.name)
            if os.path.isfile(self.name):
                for obj in libs + objects:
                    if os.path.getmtime(self.name) < os.path.getmtime(obj):
                        rebuild = True
                        break
            
            if rebuild:
                command = [Smake.LINK] + Smake._get_flags(Language.EXEC) + flags + ["-o", self.name] + libs + objects + libs + libs
                Dispatcher.run(command)
        
        Dispatcher.wait()

        print(f"Built {self.name}")
        
        return self
    
    def _compile_params(self) -> dict:
        if self.type == TargetType.LIBRARY:
            return {"flags": [f"-I./{d}" for d in self.directories]}
        
        return {}
        
    def _link_params(self) -> dict:
        if self.type == TargetType.LIBRARY:
            return {"libs": [self.static_lib_path]}
        elif self.type == TargetType.DYNAMIC:
            return {"flags": [f"-l{self.name}"]}
        
        return {}
    
    def _get_executable(self) -> str:
        if self.type == TargetType.EXECUTABLE:
            return self.name
        
        return None
    
    def _to_object(self, fn: str) -> str:
        return os.path.splitext(fn)[0] + ".o"
    
    def _clean(self):
        if self.type == TargetType.EXECUTABLE:
            if os.path.isfile(self.name):
                os.remove(self.name)

class Alias:
    def __init__(self, target: str):
        self.target = target
    
    def build(self) -> Target:
        return Smake._build(self.target)
    
    def _clean(self):
        pass

class Smake:
    CC = "gcc"
    CXX = "g++"
    NVCC = "nvcc"

    LINK = "g++"

    BUILD = "build"

    DEBUG = False

    FLAGS = {}

    _targets = {}
    _action_targets = {"clean": "clean"}

    @staticmethod
    def executable(name: str, directories: list, libraries: list = None, includes: list = None):
        Smake._targets[name] = Target(name, directories, TargetType.EXECUTABLE, Smake._list_files(directories), libraries, includes)
    
    @staticmethod
    def library(name: str, directories: list, includes: list = None):
        Smake._targets[name] = Target(name, directories, TargetType.LIBRARY, Smake._list_files(directories), None, includes)
    
    @staticmethod
    def cuda_library(name: str, directories: list, includes: list = None):
        Smake._targets[name] = Target(name, directories, TargetType.CUDA_LIBRARY, Smake._list_files(directories), None, includes)
    
    @staticmethod
    def extern_library(name: str):
        Smake._targets[name] = Target(name, "", TargetType.DYNAMIC)
    
    @staticmethod
    def run(target: str):
        Smake._action_targets["run"] = target
        Smake._action_targets["debug"] = target
    
    @staticmethod
    def alias(name: str, target: str):
        Smake._targets[name] = Alias(target)
    
    @staticmethod
    def flag(flag: str, language: Language = Language.ALL):
        if flag in Smake.FLAGS:
            Smake.FLAGS[flag] |= language
        else:
            Smake.FLAGS[flag] = language
    
    @staticmethod
    def _get_language(filename: str) -> Language:
        if filename.endswith(".c"):
            return Language.C
        elif filename.endswith(".cu"):
            return Language.CUDA
        else:
            return Language.CPP
    
    @staticmethod
    def _compiler(filename: str) -> str:
        lang = Smake._get_language(filename)
        if lang == Language.EXEC:
            return Smake.LINK
        elif lang == Language.C:
            return Smake.CC
        elif lang == Language.CPP:
            return Smake.CXX
        elif lang == Language.CUDA:
            return Smake.NVCC
    
    @staticmethod
    def _get_flags(language: Language) -> list:
        return [flag for flag, lang in Smake.FLAGS.items() if lang & language]
    
    @staticmethod
    def _build(name: str) -> Target:
        if name in Smake._targets:
            return Smake._targets[name].build()
        
        target = Smake._action_targets.get(name, None)
        if target is not None:
            if target == "clean":
                for _, target in Smake._targets.items():
                    target._clean()
                shutil.rmtree(Smake.BUILD, ignore_errors=True)
            else:
                target = Smake._build(target)
                if name == "run":
                    os.system(f"./{target._get_executable()}")
                elif name == "debug":
                    os.system(f"gdb ./{target._get_executable()}")

    @staticmethod
    def _change_dir(filename: str) -> str:
        return os.path.join(Smake.BUILD, "debug" if Smake.DEBUG else "release", filename)
    
    @staticmethod
    def _list_files(directories: list) -> list:
        files = []
        for d in directories:
            files += [os.path.join(dp, f) for dp, dn, filenames in os.walk(d) for f in filenames if os.path.splitext(f)[1] in VALID_EXTENSIONS]
        
        return files
    
    @staticmethod
    def _find_includes(filename: str, dirs: list) -> list:
        includes = set()
        for ln in open(filename, "r").readlines():
            ln = ln.strip()
            if ln.startswith("#include "):
                ln = ln.split(" ", 1)[1].strip()

                if ln.startswith('"'):
                    fn = ln[1:-1]

                    for d in dirs:
                        f = os.path.join(d, fn)
                        if os.path.isfile(f):
                            includes.add(f)
                            if filename not in includes:
                                includes = includes.union(set(Smake._find_includes(f, dirs)))
        
        return list(includes)
