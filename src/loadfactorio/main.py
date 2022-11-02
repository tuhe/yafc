from loadfactorio.mod import Mod



def get_techs(sciencepacks_allowed=None):
    name = "seablock"
    mod = Mod(name=name)
    mod.load_tmp(f"data/{name}.pkl")
    mod.restrict_to_sciencepacks()
    print( mod._all_sciencepack_like_items )
    packs = ['Item.logistic-science-pack', 'Item.automation-science-pack']
    mod.restrict_to_sciencepacks(packs )
    mod.status()
    from loadfactorio.mod import optimize
    w = optimize(mod, production_targets={p: 1 for p in packs})
    A, Agoods, Ares = mod.recipes2graph()
    # II =
    I = (w>1e-5).nonzero()[0]
    res = [Ares[i] for i in I]
    items_p = mod.items_produced_by(res)
    items_c = mod.items_produced_by(res)
    assert set(items_p) == set(items_c)

    mod.recipes = {k: v for k, v in mod.recipes.items() if k in res}
    mod.goods = {k: v for k, v in mod.goods.items() if k in items_p}


    # del mod.recipes['Mechanics.pump.water.water']

    w = optimize(mod, production_targets={p: 1 for p in packs})
    assert set(packs).issubset(items_p)
    mod.plot_graph(w=w, fluid_factor=1, mechanics_factor=0.1, file_out="../../html/seablock_first_two_sciences.html")
    mod.plot_graph(w=w, fluid_factor=1, mechanics_factor=0.1)





    print(Ares[i])

    mod.plot_graph()

    # mod = eliminate_special_goods(mod)

    from collections import defaultdict

    all_sciencepack_like_items = set.union(*[set(t['sciencepacks']) for t in mod.technologies.values()])
    if sciencepacks_allowed is None:
        sciencepacks_allowed = all_sciencepack_like_items

    allowed_technologies_bfs = []

    technologies_bfs = []
    while True:
        n = len(technologies_bfs)
        for id, t in mod.technologies.items():
            if set(t['prerequisites']).issubset(technologies_bfs) and id not in technologies_bfs and set(t['sciencepacks']).issubset(sciencepacks_allowed):
                technologies_bfs.append(id)
        if len(technologies_bfs) == n:
            break
    # This gives us all sciencepacks that seems producable.

    recipes_disallowed = []
    recipes_allowed = []
    recipes_dangling = []
    recipes_allowed = list(set.union(*[set(t['unlockRecipes']) for t in mod.technologies.values()]))

    for id, r in mod.recipes.items():
        if id in recipes_allowed:
            continue
        pr = set(r['prerequisites'])
        if len(pr) == 0 and not r['enabled']:
            recipes_dangling.append(id)
        elif pr.issubset(technologies_bfs):
            recipes_allowed.append(id)
        else:
            recipes_disallowed.append(id)

    # This gets us all the recipes we can actually do. Now get all items used by these recipes...
    all_items = mod.items_produced_by(recipes_allowed)
    br = [r for r in recipes_allowed if not set(mod.recipes[r]['ingredients']).issubset(all_items)]
    print(br)
    recipes_allowed = [r for r in recipes_allowed if r not in br]
    len(recipes_allowed)
    len(all_items)
    # this gives a list of items and recipes.
    set(all_sciencepack_like_items).difference(all_items)

    # These are not really science packs but meant to get the tech tree started.
    pseudo_packs = [p for p in all_sciencepack_like_items if p not in all_items and mod.goods[p]['factorioType'] == 'tool']
    # Now we got all recipes and items...
    # We can now construct the production graph of all things!

    print(len(br))
    for i in mod.recipes['Recipe.algae-farm-2']['ingredients']:
        # print(i)
        if i not in all_items:
            print(i)
            mod.get_recipe_producing('Fluid.gas-hydrogen-peroxide')
            print(i)

    # Packs without a research that can produce them. These are always enabled.
    #
    it = mod.items_produced_by(recipes_allowed)
    [i for i in all_sciencepack_like_items if i not in it]
    rsat = mod.get_recipe_producing('Item.space-science-pack')[0]
    rsat in recipes_dangling
    mod.recipes[rsat]

    print(len(mod.recipes), len(recipes_allowed), len(recipes_disallowed), len(recipes_dangling))
    # Now take the dangling recipes and resolve them.
    assert len(mod.recipes) == len(recipes_allowed) + len(recipes_disallowed)+ len(recipes_dangling)
    allowed_items = mod.items_produced_by(recipes_allowed)
    allowed_crafters = [id for id, e in mod.entities.items() if len(set(e['itemsToPlace']).intersection(allowed_items) ) > 0]

    rd2 = [id for id in recipes_dangling if not mod.recipes[id]['enabled']]

    for id in recipes_dangling:
        print(id)
    print(len(recipes_dangling))
    print(len(rd2))
    for id in rd2:
        if 'pack' in id:
            print(id)


    mod.recipes['Recipe.sct-logistic-science-pack']
    for id in recipes_dangling:
        # id = 'Recipe.gas-separation'
        if set(mod.recipes[id]['ingredients'].keys()).issubset(allowed_items) and len(set(mod.recipes[id]['crafters'].keys()).intersection(allowed_crafters)) > 0:
            recipes_allowed.append(id)
            print(id)
    recipes_dangling = [r for r in recipes_dangling if r not in recipes_allowed]
    print(len(recipes_dangling), recipes_dangling)

    # dis = [id for id, r in mod.recipes.items() if not r['enabled']]
    # for d in dis:
    #     print(d)
    # print(len(dis))



    mod.recipes['Recipe.gas-separation']
    a = 4
    mod.recipes[mod.get_recipe_producing('Fluid.gas-natural-1')[0]]
    mod.recipes[mod.get_recipe_producing('Item.gas-natural-1-barrel')[0]]



    a = 234

    # Now we have a list of all technologies, sorted as they occur.
    # Now get a list of all recipes and items implied by these technologies...


    # t for t in all_sciencepack_like_items if t not in
    items_avail_at_this_point = []
    packs_avail_at_this_point = []
    all_items = set()
    all_items = mod.items_produced_by([id for id, r in mod.recipes.items() if r['enabled'] and 'Entity.character' in r['crafters']])

    [i for i in all_sciencepack_like_items if i not in all_items]

    def get_recipe_producing(item):

        pass
    mod.get_available_crafters('Item.space-science-pack')

    [r for r in mod.recipes.values() if 'Item.space-science-pack' in r['products']]
    all_recipes = set([id for id, r in mod.recipes.items() if r['enabled'] and 'Entity.character' in r['crafters']])

    for t in technologies_bfs:
        all_recipes = all_recipes.union( mod.technologies[t]['unlockRecipes'] )
        all_items = all_items.union(mod.items_produced_by(mod.technologies[t]['unlockRecipes']))
    # Does all items have a recipe?



    print("all items: ", len(all_items), "total", len(mod.goods))
    len(technologies_bfs)
    len(mod.technologies)
    for i in mod.goods:
        if i not in all_items:
            print(i)

        # mod.technologies[t]['sciencepacks']

        packs = []

    known_items = mod.items_produced_by(recipes)

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
    pass

if __name__ == "__main__":
    # name = "vanilla"
    # run_yafc = False

    get_techs()

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

    S = 0
    def get_recipe_producing(item):
        return [id for id, r in mod.recipes.items() if item in r['products']]

        pass
    known_recipes = known_packs
    while True:
        S_ = S
        for id, t in mod.technologies.items():
            if can_research(t, known_techs, known_packs):
                known_techs.add(id)
                recipes = mod.available_recipes(known_items, known_techs)
                recipes = recipes + [id for id, r in mod.recipes.items() if r['enabled'] and 'Entity.character' in r['crafters']]



                # mod.recipes['Recipe.angelsore1-crushed-smelting']

                known_items = mod.items_produced_by(recipes).union(set(['Item.basic-circuit-board']))
                continue

                # a = 234

                # products = [set(mod.recipes[r]['products'].keys()) for r in t['unlockRecipes']]
                # known_recipes = list( set( known_recipes + t['unlockRecipes'] ) )
                # if len(products) > 0:
                #     known_items = known_items.union(set.union( *[set(mod.recipes[r]['products'].keys()) for r in t['unlockRecipes']]))
        print(known_techs)
        for p in all_sciencepack_like_items.intersection(set(known_items)):
            if p not in known_packs:
                known_packs.append(p)
        S = len(known_items) + len(known_techs) + len(known_packs)
        print(S)
        if S == S_:
            break
    recipes = mod.available_recipes(known_items, known_techs, debug=True)


    for i in mod.recipes['Recipe.assembling-machine-1']['ingredients']:
        if i not in known_items:
            print(i)
    'Item.basic-circuit-board'


    for i in mod.recipes[get_recipe_producing( 'Item.basic-circuit-board')[0]]['ingredients']:
        if i not in known_items:
            print(i)

    for i in mod.recipes[get_recipe_producing( 'Item.wooden-board')[0]]['ingredients']:
        if i not in known_items:
            print(i)
    for i in mod.recipes[get_recipe_producing('Item.solid-paper')[-1]]['ingredients']:
        if i not in known_items:
            print(i)

    for i in mod.recipes[get_recipe_producing('Item.solid-wood-pulp')[0]]['ingredients']:
        if i not in known_items:
            print(i)

    for i in mod.recipes[get_recipe_producing('Item.solid-alginic-acid')[0]]['ingredients']:
        if i not in known_items:
            print(i)

    for i in  mod.recipes[get_recipe_producing('Item.steel-plate')[0]]['ingredients']:
        if i not in known_items:
            print(i)

    for i in  mod.recipes[get_recipe_producing('Fluid.liquid-molten-steel')[0]]['ingredients']:
        if i not in known_items:
            print(i)


    water_pump = mod.entities['Entity.water-pump']
    print(water_pump)
    [r for r in mod.recipes if 'water-pump' in r]

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