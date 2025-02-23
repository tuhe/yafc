

import pickle
import json
import numpy as np
import shutil
import subprocess
import os
cdir = os.path.dirname(__file__)
yafcd = "../../CommandLineToolExample/bin/Release/netcoreapp6.0/"
import scipy
import scipy.optimize
import cvxpy as cp
from loadfactorio.mod import Mod

# bin\Debug\netcoreapp6.0


def _compile_yafc():
    bat = f"{cdir}/../.."
    print(bat, os.path.isdir(bat))

    s = f"{bat}/build_commandline.bat"
    os.chdir(bat)
    out = subprocess.run("build_commandline.bat", check=True)
    # print(out)
    os.chdir(cdir)
    return
    # out = subprocess.run([f"cd {bat}"], check=True, shell=True)
    # print(out)

def get_json_from_yafc(name=None, rerun=False, build=True,
                        factorio_data_path = "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Factorio\\data",
                        factorio_mod_path="C:\\Users\\tuhe\\AppData\\Roaming\\Factorio\\mods"):
    # Extract .json code from currently loaded mods.
    if build:
        _compile_yafc()
        pass

    # fname = f"{cdir}/{name}.json"
    # if os.path.isfile(fname) and not rerun:
    #     return
    # file = "../../CommandLineToolExample/bin/Release/netcoreapp6.0/CommandLineToolExample.exe"
    file = "../../CommandLineToolExample/Build/Windows/CommandLineToolExample.exe"

    # factorio_mod_path = "C:\\Users\\tuhe\\AppData\\Roaming\\Factorio\\mods"

    dname = os.path.dirname(cdir + "/"+file)
    print(dname)
    print( os.path.isdir(dname) )
    isf = os.path.isfile(file)
    print("Calling YAFC...")
    cmd = file + " " + factorio_data_path
    dn = os.path.dirname(file)
    wdir = os.getcwd()
    os.chdir(dn)
    print(f"> Running YAFC: {cmd} in {dn}")
    cmd = f'CommandLineToolExample.exe "{factorio_data_path}" "{factorio_mod_path}"'
    # print(cmd)
    out = subprocess.run(cmd, capture_output=True)
    print("> Done! Decoding...")
    js = out.stdout.decode("utf8")
    print("> Done! Splitting...")
    js = js.splitlines()
    k = max([k for k, l in enumerate(js) if l.startswith(">> ")])
    js = "\n".join(js[k+1:])
    lines = js.splitlines()
    print(f"> Obtained {len(lines)//(1000*1000)} million lines of json. First few lines of json:")
    print("\n".join(lines[:6]))
    print("> Decoding json..")
    js = "\n".join(lines)
    jdecode = json.loads(js)
    mod = Mod(name, yafc_json=jdecode)
    print("> Called YAFC and made mod files. ")
    os.chdir(wdir)
    return mod

if __name__ == "__main__":
    # _compile_yafc()
    mod = get_json_from_yafc(build=True)

    a = 234

    # name = "vanilla"
    # get_json_from_yafc(name=name, rerun=False)
    # load = False
    #
    # if load:
    #     mod.save_tmp()
    # else:
    #     mod.load_tmp()
    # mod.trim()

