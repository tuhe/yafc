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

def main():
    mod = seablock()
    [s for s in mod._all_sciencepack_like_items if "tool" not in s]
    processors = [s for s in mod._all_sciencepack_like_items if "processor" in s]
    cases = [s for s in mod._all_sciencepack_like_items if "case" in s]


    sciencepacks = ['Item.automation-science-pack', 'Item.logistic-science-pack', 'Item.sct-bio-science-pack'] + ['Item.chemical-science-pack'] \
     + ['Item.module-circuit-board',  'Item.module-case'] + processors + ['Item.production-science-pack']
    # sciencepacks = ['Item.automation-science-pack', 'Item.logistic-science-pack']
    # sciencepacks = []
    production_targets = {p: 1 for p in sciencepacks + ['Item.construction-robot']}
    production_targets = {p: 1 for p in sciencepacks}

    # sciencepacks = ['Item.automation-science-pack']
    # production_targets = {p: 1 for p in sciencepacks}

    mod = seablock()
    items_produce = []
    mod.restrict_to_sciencepacks(sciencepacks)
    mod.status()
    sanity_can_produce(mod, sciencepacks + items_produce)

    # mod.get_recipe_producing('Item.swamp-garden')

    w = optimize(mod, production_targets=production_targets)

    A, Agoods, Ares = mod.recipes2graph()
    # II =
    I = (w > 1e-5).nonzero()[0]
    res = [Ares[i] for i in I]
    items_p = mod.items_produced_by(res)
    items_c = mod.items_produced_by(res)
    assert set(items_p) == set(items_c)

    mod.recipes = {k: v for k, v in mod.recipes.items() if k in res}
    mod.goods = {k: v for k, v in mod.goods.items() if k in items_p}

    # del mod.recipes['Mechanics.pump.water.water']

    w = optimize(mod, production_targets=production_targets)
    A, Agoods, Ares = mod.recipes2graph()
    # nx = mod2networkx(mod, A, Agoods, Ares, w)

    assert set(sciencepacks).issubset(items_p)
    import numpy as np
    A[np.asarray(Agoods) == 'Fluid.water', :] = 0
    for g in [g for g in Agoods if "plate" in g]:
        A[np.asarray(Agoods) == g, :] = 0
    trains = ['Item.plastic-bar', 'Fluid.liquid-sulfuric-acid', 'Item.wood-charcoal', 'Fluid.sulphuric-acid', 'Fluid.gas-oxygen', 'Fluid.gas-hydrogen', 'Item.solid-carbon',
              'Fluid.lubricant', 'Item.ingot-lead', 'Item.ingot-tin', 'Item.ingot-silicon',
              'Fluid.gas-nitrogen', 'Item.resin',
              'Fluid.water-yellow-waste', 'Fluid.water-purified',
              'Item.iron-ore', 'Item.copper-ore', 'Item.wood','Item.silver-ore', 'Item.bauxite-ore'] + [g for g in Agoods if "Fluid.steam" in g] \
    + ['Fluid.water-heavy-mud', 'Item.solid-mud', 'Fluid.water-thin-mud',
       'Fluid.water-mineralized', 'Item.quartz']  +[g for g in Agoods if 'ingot' in g] + ['Item.glass', 'Item.sct-t3-flash-fuel', 'Fluid.water-saline', 'Fluid.gas-carbon-dioxide',
                                                                                          'Fluid.liquid-hydrochloric-acid',
                                                                                          'Item.angels-roll-solder',
                                                                                          'Item.solid-salt',
                                                                                          'Fluid.gas-methane',
                                                                                          'Fluid.liquid-mineral-oil',
                                                                                          'Item.filter-frame', 'Item.filter-charcoal'] \
      +[g for g in Agoods if 'wire-coil' in g] +[g for g in Agoods if g.endswith('-ore') or "geode-" in g] + ['Item.cellulose-fiber', 'Item.solid-paper', 'Item.solid-lime',
                                                                                             'Fluid.gas-hydrogen-chloride',
                                                                                                'Fluid.liquid-nitric-acid',
                                                                                             'Fluid.liquid-nutrient-pulp',
                                                                                             'Fluid.gas-ammonia']
    trains2 = []
    trains = trains+trains2
    for g in trains:
        A[np.asarray(Agoods) == g, :] = 0

    mod.plot_graph(w=w, A=A, Ares=Ares, Agoods=Agoods, fluid_factor=1, mechanics_factor=0.1)
    z = 234


if __name__ == "__main__":

    main()