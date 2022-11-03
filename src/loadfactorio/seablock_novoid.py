import numpy as np

from loadfactorio.mod import Mod
from loadfactorio.mod import optimize
import copy
from loadfactorio.seablock_visualizations import seablock, sanity_can_produce
import networkx as nx
import matplotlib.pyplot as plt

# def mod2networkx(mod, A, Agoods, Ares, w):
#     G = nx.DiGraph()
#     G.add_node('mynode', size=10)
#     G.add_edge(1, 2, weight=10)
#     color_map = []
#
#     labeldict = {}
#     labeldict["Node1"] = "shopkeeper"
#     labeldict["Node2"] = "angry man with parrot"
#
#     nx.draw(G, pos=nx.circular_layout(G), with_labels = True)
#
#     plt.show()
#     a = 234
#     pass

def main(void=True, sciencepacks=None, production_targets=None, file_out=None, plot=True, allow_slack=True, tol=1e-5):
    # mod = seablock()


    # [s for s in mod._all_sciencepack_like_items if "tool" not in s]
    # processors = [s for s in mod._all_sciencepack_like_items if "processor" in s]
    # cases = [s for s in mod._all_sciencepack_like_items if "case" in s]
    # sciencepacks = ['Item.automation-science-pack', 'Item.logistic-science-pack']
    # sciencepacks += ['Item.sct-bio-science-pack']
    # sciencepacks += ['Item.chemical-science-pack']
    # + ['Item.module-circuit-board',  'Item.module-case'] + processors + ['Item.production-science-pack']
    # sciencepacks = ['Item.automation-science-pack', 'Item.logistic-science-pack']
    # sciencepacks = []
    # production_targets = {p: 1 for p in sciencepacks + ['Item.construction-robot']}


    # production_targets = {p: 1 for p in sciencepacks}

    # sciencepacks = ['Item.automation-science-pack']
    # production_targets = {p: 1 for p in sciencepacks}

    mod = seablock()
    items_produce = []
    mod.restrict_to_sciencepacks(sciencepacks)
    mod.status()
    sanity_can_produce(mod, sciencepacks + items_produce)

    # mod.get_recipe_producing('Item.swamp-garden')
    # for r in mod.recipes:
    #     if "ore" in r:
    #         print(r, mod.recipes[r]['locName'], mod.recipes[r]['locDescr'])
    #     print(r)
    if not void:
        for r in [r for r in mod.recipes if "void" in r]:
            del mod.recipes[r]
    w, slack = optimize(mod, production_targets=production_targets, allow_slack=allow_slack, tol=tol)
    if allow_slack:
        assert sum(np.abs(slack)) < 1e-4
    sanity_can_produce(mod, sciencepacks+items_produce)
    print("Cost", w.sum())
    # with void: Cost 180.679116589855
    # without void: Cost 193.45258009556767
    # return
    A, Agoods, Ares = mod.recipes2graph()
    # II =
    for v in [1,2,5,10]:
        I = (w > tol*v).nonzero()[0]
        res = [Ares[i] for i in I]
        items_p = mod.items_produced_by(res)
        items_c = mod.items_consumed_by(res) |  set([p for p in production_targets])
        if set(items_p) != set(items_c):
            print([p for p in items_p if p not in items_c])
            print([p for p in items_c if p not in items_p])
            print("bad")
        else:
            break
    if set(items_p) != set(items_c):
        print("Bad!")
        assert False

    mod.recipes = {k: v for k, v in mod.recipes.items() if k in res}
    mod.goods = {k: v for k, v in mod.goods.items() if k in items_p}

    w,_ = optimize(mod, production_targets=production_targets)
    A, Agoods, Ares = mod.recipes2graph()
    # nx = mod2networkx(mod, A, Agoods, Ares, w)
    if not set(production_targets.keys()).issubset(items_p):
        assert False
    import numpy as np
    # A[np.asarray(Agoods) == 'Fluid.water', :] = 0
    # for g in [g for g in Agoods if "plate" in g]:
    #     A[np.asarray(Agoods) == g, :] = 0
    # trains = ['Item.plastic-bar', 'Fluid.liquid-sulfuric-acid', 'Item.wood-charcoal', 'Fluid.sulphuric-acid', 'Fluid.gas-oxygen', 'Fluid.gas-hydrogen', 'Item.solid-carbon',
    #           'Fluid.lubricant', 'Item.ingot-lead', 'Item.ingot-tin', 'Item.ingot-silicon',
    #           'Fluid.gas-nitrogen', 'Item.resin',
    #           'Fluid.water-yellow-waste', 'Fluid.water-purified',
    #           'Item.iron-ore', 'Item.copper-ore', 'Item.wood','Item.silver-ore', 'Item.bauxite-ore'] + [g for g in Agoods if "Fluid.steam" in g] \
    # + ['Fluid.water-heavy-mud', 'Item.solid-mud', 'Fluid.water-thin-mud',
    #    'Fluid.water-mineralized', 'Item.quartz']  +[g for g in Agoods if 'ingot' in g] + ['Item.glass', 'Item.sct-t3-flash-fuel', 'Fluid.water-saline', 'Fluid.gas-carbon-dioxide',
    #                                                                                       'Fluid.liquid-hydrochloric-acid',
    #                                                                                       'Item.angels-roll-solder',
    #                                                                                       'Item.solid-salt',
    #                                                                                       'Fluid.gas-methane',
    #                                                                                       'Fluid.liquid-mineral-oil',
    #                                                                                       'Item.filter-frame', 'Item.filter-charcoal'] \
    #   +[g for g in Agoods if 'wire-coil' in g] +[g for g in Agoods if g.endswith('-ore') or "geode-" in g] + ['Item.cellulose-fiber', 'Item.solid-paper', 'Item.solid-lime',
    #                                                                                          'Fluid.gas-hydrogen-chloride',
    #                                                                                             'Fluid.liquid-nitric-acid',
    #                                                                                          'Fluid.liquid-nutrient-pulp',
    #                                                                                          'Fluid.gas-ammonia']
    # trains2 = []
    # trains = trains+trains2
    # for g in trains:
    #     A[np.asarray(Agoods) == g, :] = 0

    if plot:
        mod.plot_graph(w=w, A=A, Ares=Ares, Agoods=Agoods, fluid_factor=1, mechanics_factor=0.1)
    if file_out is not None:
        mod.plot_graph(w=w, A=A, Ares=Ares, Agoods=Agoods, fluid_factor=1, mechanics_factor=0.1, file_out=file_out)
    return w.sum()

    z = 234


def plot_all():
    mod = seablock()
    ordered = mod.packs_ordered.copy()
    cc = {}
    allow_targets = ['Item.automation-science-pack',
             'Item.logistic-science-pack',
             'Item.sct-bio-science-pack',
             'Item.military-science-pack',
             'Item.chemical-science-pack',
             # 'Item.science-pack-gold',
             'Item.productivity-processor',
             'Item.effectivity-processor',
             'Item.speed-processor',
             'Item.module-circuit-board',
             'Item.module-case',
             'Item.production-science-pack',
             'Item.advanced-logistic-science-pack',
             'Item.alien-science-pack',
             'Item.utility-science-pack',
             # 'Item.alien-science-pack-orange',
             # 'Item.alien-science-pack-blue',
             # 'Item.alien-science-pack-yellow',
             # 'Item.alien-science-pack-green',
             # 'Item.alien-science-pack-red',
             # 'Item.alien-science-pack-purple',
             'Item.space-science-pack']
    legal_targets = {}
    for p in [p for p in mod.packs_ordered if mod.sciencepack_usage[p] > 5]:
        # mod = seablock()
        # items_produce = []
        k = ordered.index(p)
        sciencepacks = ordered[4:k + 1]
        targets = {p: 1 for p in [p for p in sciencepacks if mod.sciencepack_usage[p] > 5] if p in allow_targets}
        file_out = f"../../html/seablock_novoid_{k}_{list(targets)[-1]}.html"
        print(k, targets, file_out)
        if k == 6 or k == 7:
            del targets['Item.sct-bio-science-pack']
        if k >= 25:
            continue
        cc[list(targets)[-1]] = main(void=False, sciencepacks=sciencepacks, production_targets=targets, file_out=file_out, plot=False, allow_slack=False, tol=1e-6)
    pass


def utility_with_robots():
    mod = seablock()
    ordered = mod.packs_ordered.copy()
    cc = {}
    allow_targets = ['Item.automation-science-pack',
             'Item.logistic-science-pack',
             'Item.sct-bio-science-pack',
             'Item.military-science-pack',
             'Item.chemical-science-pack',
             'Item.productivity-processor',
             'Item.effectivity-processor',
             'Item.speed-processor',
             'Item.module-circuit-board',
             'Item.module-case',
             'Item.production-science-pack',
             'Item.advanced-logistic-science-pack',
             'Item.alien-science-pack',
             'Item.utility-science-pack',
             # 'Item.alien-science-pack-orange',
             # 'Item.alien-science-pack-blue',
             # 'Item.alien-science-pack-yellow',
             # 'Item.alien-science-pack-green',
             # 'Item.alien-science-pack-red',
             # 'Item.alien-science-pack-purple',
             'Item.space-science-pack']
    legal_targets = {}
    for p in [p for p in mod.packs_ordered if mod.sciencepack_usage[p] > 5]:
        k = ordered.index(p)
        sciencepacks = ordered[4:k + 1]
        targets = {p: 1 for p in [p for p in sciencepacks if mod.sciencepack_usage[p] > 5] if p in allow_targets}
        file_out = f"../../html/seablock_novoid_bots_{k}_{list(targets)[-1]}.html"
        print(k, targets, file_out)
        if k == 6 or k == 7:
            del targets['Item.sct-bio-science-pack']
        if k < 24:
            continue

        if k == 25:
            break
        targets['Item.construction-robot'] = 0.1
        # targets['Item.sct-bio-science-pack']

        cc[list(targets)[-1]] = main(void=False, sciencepacks=sciencepacks, production_targets=targets, file_out=file_out, plot=False, allow_slack=False, tol=1e-6)
        z = 234
    pass


if __name__ == "__main__":
    from loadfactorio.mod import make_index
    utility_with_robots()
    make_index()

    plot_all()

    make_index()
    c2 = main(void=False, file_out="../../html/seablock_redgreen_novoid.html")


    from seablock_visualizations import make
    # c1 = main(void=True)
    #
    #
    # print(c1, c2, (c2 - c1)/c1 )