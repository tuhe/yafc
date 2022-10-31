from loadfactorio.mod import Mod


def eliminate_special_goods(mod):
    """ Eleminate special goods in the mods recipes.

    """
    specials = [id for id, g in mod.goods.items() if g['factorioType'] == 'special']
    for s in specials:
        for id, r in mod.recipes.items():
            if s in r['ingredients']:
                print(">> Recipe", id, "had special input", s, "as ingredient which is now eliminated")
                del r['ingredients'][s]
            if s in r['products']:
                print(">> Recipe", id, "had special input", s, "as product which is now eliminated")
                del r['products'][s]

        # print([r for r in mod.recipes.values() if s in r['ingredients']])
        # print([r for r in mod.recipes.values() if s in r['products']])

    return mod
    pass

if __name__ == "__main__":
    # name = "vanilla"
    # run_yafc = False
    name = "seablock"
    mod = Mod(name=name)
    mod.load_tmp(f"data/{name}.pkl")
    mod = eliminate_special_goods(mod)

    from collections import defaultdict

    all_sciencepack_like_items = set.union(*[set(t['sciencepacks']) for t in mod.technologies.values()])
    dd = defaultdict(float)
    from collections import Counter
    # Counter.
    c = []
    for t in mod.technologies.values():
        c += t['sciencepacks']
    cc = Counter(c)
    known_technologies = []
    known_packs = []
    known_items = []
    for r in mod.recipes.values():
        if r['enabled'] and set(r['ingredients']).issubset(known_items):
            known_items += r['products']
    print(known_items)
    known_packs = known_items


    # for id, t in mod.technologies.items():
    #     if can_research(t):
    #         known_technologies.append(id)
    # for r in mod.recipes.values():
    #     if set(r['prerequisites']).issubset(known_technologies) and set(r['ingredients']).issubset(known_items):
    #         known_items += r['products']
    # known_packs = set.intersection(set(known_items), set(cc.keys()))
    #
    # for t in mod.technologies.values():
    #     if len(t['prerequisites']) == 0:
    #         print(t)
    #
    # for t in mod.technologies.values():
    #     if len(t['prerequisites']) == 0:
    #         print(t)
    #
    # first_tech = 'Technology.sb-startup1'
    # can_research(mod.technologies[first_tech])
    # technology = mod.technologies[first_tech]
    # set(technology['prerequisites']).issubset(known_technologies)
    # set(technology['sciencepacks']).issubset(known_packs)
    # print( technology['sciencepacks'] )
    # mod.goods[technology['sciencepacks'][0]]
    # for r in mod.recipes.values():
    #     if technology['sciencepacks'][0] in r['products']:
    #         print(r)
    #
    #     if technology['sciencepacks'][0] in r['products']:
    #         print(r)


    for g in mod.goods.values():
        if g['factorioType'] == 'tool':
            print("tool> ", g)

    # print(mod.goods[technology['sciencepacks'][0]])
    first_item = 'Item.sb-angelsore3-tool'

    # [r for r in mod.recipes.values() if first_item in r['products']]
    # print("Enabled...")
    # for r in mod.recipes:
    #     rr = mod.recipes[r]
    #     if rr['enabled'] and "void" not in r:
    #         print(r)

    basic_sciencepacks = [] # Those which are always available.
    for p in all_sciencepack_like_items:
        if p not in set.union( *[set(r['products']) for r in mod.recipes.values()]):
            basic_sciencepacks.append(p)

    print(basic_sciencepacks)
    # these are those things that looks like sciencepacks but really are not; they are needed to get the mod started.
    basic_sciencepacks = [k for k in cc if cc[k] <= 2] # Stuff needed in the beginning.
    known_packs = basic_sciencepacks.copy()

    known_techs = set()
    known_items = set()

    for r in mod.recipes.values():
        for i in r['ingredients']:
            if i not in mod.goods:
                print(i)
            # if i.startswith("Special.launch"):
    specials = [id for id, g in mod.goods.items() if g['factorioType'] == 'special']
    for s in specials:
        print( [r for r in mod.recipes.values() if s in r['ingredients']] )

    def can_research(technology, known_technologies, known_packs):
        return set(technology['prerequisites']).issubset(known_technologies) and set(technology['sciencepacks']).issubset(known_packs)

    [t for t in mod.technologies.values() if 'Technology.sb-startup1' in t['prerequisites']]

    can_research(mod.technologies['Technology.landfill'], known_techs, known_packs)

    # List of all recipes that appear not to be researchable:

    def get_all_recipes_available_with_packs(mod, packs):
        unresearchable_recipes = [r for r in mod.recipes if
                                  r not in set.union(*[set(t['unlockRecipes']) for t in mod.technologies.values()])]


        pass


    S = 0
    known_recipes = known_packs
    while True:
        S_ = S
        for id, t in mod.technologies.items():
            if can_research(t, known_techs, known_packs):
                known_techs.add(id)

                recipes = mod.available_recipes(known_items, known_technologies)
                mod.recipes['Recipe.angelsore1-crushed-smelting']

                available_items = mod.items_produced_by(recipes)


                # a = 234

                products = [set(mod.recipes[r]['products'].keys()) for r in t['unlockRecipes']]
                known_recipes = list( set( known_recipes + t['unlockRecipes'] ) )
                if len(products) > 0:
                    known_items = known_items.union(set.union( *[set(mod.recipes[r]['products'].keys()) for r in t['unlockRecipes']]))

        for p in all_sciencepack_like_items.intersection(set(known_items)):
            if p not in known_packs:
                known_packs.append(p)
        S = len(known_items) + len(known_techs) + len(known_packs)
        print(S)
        if S == S_:
            break



    for t in mod.technologies:
        if t not in known_techs:
            print(t)
    len(known_packs)
    [p for p in all_sciencepack_like_items if p not in known_packs]
    assert len(known_packs) == len(all_sciencepack_like_items)
    space_pack = 'Item.space-science-pack'
    space_recipe = [id for id, r in mod.recipes.items() if space_pack in r['products']].pop()
    print("Can we research space recipe: ", space_recipe in known_recipes)
    [t for t in mod.technologies.values() if space_recipe in t['unlockRecipes']]


    fusion_reactor = 'Technology.fusion-reactor'

    # alternatively: Determine first science pack like thing.
    #

    # known_technologies = []
    # for id, r in mod.recipes.items():
    #     if set(r['prerequisites']).issubset(known_technologies):
    #         print(id)
    #         # known_techs.add(id)
    #         # known_items = known_items.union(r['products'])

    for p in known_items:
        if p in all_sciencepack_like_items and p not in known_packs:
            known_packs.append(p)
    [r for r in mod.recipes.values() if 'Item.sb-lab-tool' in r['products']]

    print(known_techs)




    # for r in mod.recipes.values():
    #     if technology['sciencepacks'][0] in r['products']:
    #         print(r)
    #
    #     if technology['sciencepacks'][0] in r['products']:
    #         print(r)

    if can_research(t):
        known_technologies.append(id)





    a = 234
    #
    # if run_yafc:
    #     from loadfactorio.compile_run_yafc import get_json_from_yafc
    #     mod = get_json_from_yafc(name=name, build=True, factorio_mod_path="")
    #     mod.status()
    #     if len(mod.recipes)> 1000:
    #         name = "seablock"
    #     else:
    #         name = "vanilla"
    #     mod.save_tmp(file_out=f"data/{name}.pkl")
    # else:
    #     mod = Mod(name="vanilla")
    #     mod.load_tmp("data/vanilla.pkl")
    # import pickle
    # with open("data/seablock.pkl",'rb') as f:
    #     d = pickle.load(f)
    # # import json
    # # with open("data/vanilla.json", 'w') as f:
    # #     json.dump(d, f, indent=3)
    # mod = Mod(name="vanilla")
    # mod.load_tmp("data/seablock.pkl")
    # mod.plot_graph()
    #
    # mod.status()
    # mod.trim()
    # load = False
    # mod = Mod(name, load=load)
    # if load:
    #     mod.save_tmp()
    # else:
    #     mod.load_tmp()
    # mod.trim()
    # w = optimize(mod)
    #
    # A, Agoods, Ares = mod.recipes2graph()
    # # def tk(dict, I):
    # #     return 0
    # #     # return (A~=0) @ (w.value > 1e-3).nonzero()[0]
    # I = w > 1e-3
    # recipes = np.asarray(Ares)[I].tolist()
    # goods = np.asarray(Agoods)[(A !=0) @ (w>1e-3)].tolist()
    #
    # for r in list(mod.recipes.keys()):
    #     if r not in recipes:
    #         del mod.recipes[r]
    #
    # for g in list(mod.goods.keys()):
    #     if g not in goods:
    #         del mod.goods[g]
    # mod.trim()
    # w = optimize(mod)
    # A, Agoods, Ares = mod.recipes2graph()
    #
    # j  = Ares.index("Mechanics.launch.satellite")
    # i = Agoods.index("Special.launch")
    # A[i,j]
    # print(i,j)
    # mod.recipes["Mechanics.launch.satellite"]
    #
    #
    # mod.plot_graph(A, w)