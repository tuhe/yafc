from loadfactorio.mod import Mod

if __name__ == "__main__":
    name = "vanilla"
    run_yafc = True

    if run_yafc:
        from loadfactorio.compile_run_yafc import get_json_from_yafc
        mod = get_json_from_yafc(name=name, build=True)
        mod.status()
        mod.save_tmp(file_out="data/vanilla.pkl")
    else:
        mod = Mod(name="vanilla")
        mod.load_tmp("data/vanilla.pkl")


    load = False
    mod = Mod(name, load=load)
    if load:
        mod.save_tmp()
    else:
        mod.load_tmp()
    mod.trim()
    w = optimize(mod)

    A, Agoods, Ares = mod.recipes2graph()
    # def tk(dict, I):
    #     return 0
    #     # return (A~=0) @ (w.value > 1e-3).nonzero()[0]
    I = w > 1e-3
    recipes = np.asarray(Ares)[I].tolist()
    goods = np.asarray(Agoods)[(A !=0) @ (w>1e-3)].tolist()

    for r in list(mod.recipes.keys()):
        if r not in recipes:
            del mod.recipes[r]

    for g in list(mod.goods.keys()):
        if g not in goods:
            del mod.goods[g]
    mod.trim()
    w = optimize(mod)
    A, Agoods, Ares = mod.recipes2graph()

    j  = Ares.index("Mechanics.launch.satellite")
    i = Agoods.index("Special.launch")
    A[i,j]
    print(i,j)
    mod.recipes["Mechanics.launch.satellite"]


    mod.plot_graph(A, w)