from loadfactorio.compile_run_yafc import get_json_from_yafc
import pickle
import json
from loadfactorio.mod import Mod

if __name__ == "__main__":
    factorio_data_path = "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Factorio\\data"
    factorio_mod_path = "C:\\Users\\tuhe\\AppData\\Roaming\\Factorio\\mods"
    for mode in ['seablock', 'vanilla']:
        mod = get_json_from_yafc(name=mode, build=True, factorio_data_path=factorio_data_path, factorio_mod_path="" if mode == 'vanilla' else factorio_mod_path)
        if len(mod.recipes)> 1000:
            name = "seablock"
        else:
            name = "vanilla"
        mod.save_tmp(file_out=f"data/{name}.pkl")

        with open(f"data/{mode}.pkl",'rb') as f:
            d = pickle.load(f)
        with open(f"data/{mode}.json", 'w') as f:
            json.dump(d, f, indent=3)
