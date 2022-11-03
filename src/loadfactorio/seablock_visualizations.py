from loadfactorio.mod import Mod
from loadfactorio.mod import optimize
import copy

def sanity_can_produce(mod, items_required):
    required_items = []
    n = 0
    items = items_required

    while True:
        recipes = set.union(*[set(mod.get_recipe_producing(i)) for i in items])
        items = set.union( mod.items_consumed_by(recipes), mod.items_produced_by(recipes) )
        n2 = len(recipes) + len(items)
        if n2 == n:
            break
        n = n2
    assert set(items_required).issubset(items)
    # print("Phew! safe production possible")


def tech_graph(mod, sciencepacks, production_targets, outfile=None):
    # print( mod._all_sciencepack_like_items )
    # packs = ['Item.logistic-science-pack', 'Item.automation-science-pack']
    # packs = ['Item.logistic-science-pack', 'Item.automation-science-pack', 'Item.sct-bio-science-pack']
    # packs = ['Item.logistic-science-pack', 'Item.automation-science-pack']
    # packs = sciencepacks

    # items_produce = ['Item.construction-robot']
    items_produce = []
    mod.restrict_to_sciencepacks(sciencepacks )
    mod.status()
    sanity_can_produce(mod, sciencepacks+items_produce)


    # mod.get_recipe_producing('Item.swamp-garden')

    w = optimize(mod, production_targets=production_targets)

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

    w = optimize(mod, production_targets=production_targets)
    assert set(sciencepacks).issubset(items_p)
    A[Agoods == 'Fluid.water',:] = 0
    # w[]
    # del mod.goods['Fluid.water']

    mod.plot_graph(w=w, fluid_factor=1, mechanics_factor=0.1)
    mod.plot_graph(w=w, fluid_factor=1, mechanics_factor=0.1, file_out=f"../../html/{outfile}")
    a = 234


def seablock():

    name = "seablock"
    mod = Mod(name=name)
    mod.load_tmp(f"data/{name}.pkl")
    mod.fix_recipe_temperatures()
    mod.restrict_to_sciencepacks()

    # Load and set sciencepacks:

    [s for s in mod._all_sciencepack_like_items if "tool" not in s]
    processors = [s for s in mod._all_sciencepack_like_items if "processor" in s]
    cases = [s for s in mod._all_sciencepack_like_items if "case" in s]
    sciencepacks = ['Item.automation-science-pack', 'Item.logistic-science-pack']
    # sciencepacks += ['Item.sct-bio-science-pack']
    # sciencepacks += ['Item.chemical-science-pack']
    # + ['Item.module-circuit-board',  'Item.module-case'] + processors + ['Item.production-science-pack']
    # sciencepacks = ['Item.automation-science-pack', 'Item.logistic-science-pack']
    # sciencepacks = []

    mod.proper_packs =  ['Item.automation-science-pack', 'Item.logistic-science-pack', 'Item.sct-bio-science-pack', 'Item.military-science-pack', 'Item.chemical-science-pack']
    mod.processors = ['Item.module-circuit-board', 'Item.module-case'] + processors
    mod.high_packs = ['Item.production-science-pack', ]

    rsp =  set(mod.recipes.keys())
    packs_ordered = []
    for t in mod.technologies:
        for p in mod._all_sciencepack_like_items:
            if p in mod.items_produced_by( set(mod.technologies[t]['unlockRecipes']).intersection( rsp )) and p not in packs_ordered:
                packs_ordered.append(p)
    print(packs_ordered)
    print(len(packs_ordered))
    print(len(mod._all_sciencepack_like_items))
    basic_packs = [p for p in mod._all_sciencepack_like_items if "tool" in p]
    packs_ordered = basic_packs + packs_ordered

    final = [p for p in mod._all_sciencepack_like_items if p not in packs_ordered]
    packs_ordered = packs_ordered + final
    # mod.sciencepacks =
    mod.packs_ordered = packs_ordered
    from collections import Counter
    al = []
    for t in mod.technologies.values():
        al += t['sciencepacks']

    mod.sciencepack_usage =  Counter(al)

    return mod

def main():
    sciencepacks = ['Item.automation-science-pack', 'Item.logistic-science-pack', 'Item.sct-bio-science-pack']

    for i, _ in enumerate(sciencepacks):
        packs = sciencepacks[:i+1]
        for with_bots in [False, True]:
            if with_bots and i == 0:
                continue
            if with_bots and i >= 1:
                production_targets = {p: 1 for p in packs + ['Item.construction-robot']}
            else:
                production_targets = {p: 1 for p in packs}

            mod = seablock()
            tech_graph(mod, packs, production_targets, outfile=f"seablock_{i+1}_sciences{'_bots' if with_bots else ''}.html")

    from loadfactorio.mod import make_index
    make_index()


if __name__ == "__main__":
    main()
