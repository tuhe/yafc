import pickle
import json
import numpy as np
import shutil
import subprocess
import os
cdir = os.path.dirname(__file__)
# yafcd = "../../CommandLineToolExample/bin/Release/netcoreapp6.0/"
import scipy
import scipy.optimize
import cvxpy as cp
import tabulate
import copy

# bin\Debug\netcoreapp6.0
# def get_json_from_yafc(name, rerun=False):
#     # Extract .json code from currently loaded mods.
#     fname = f"{cdir}/{name}.json"
#     if os.path.isfile(fname) and not rerun:
#         return
#     file = "../../CommandLineToolExample/bin/Release/netcoreapp6.0/CommandLineToolExample.exe"
#     dname = os.path.dirname(cdir + "/"+file)
#     print(dname)
#     print( os.path.isdir(dname) )
#     isf = os.path.isfile(file)
#     print("Calling YAFC...")
#     out = subprocess.run(file, capture_output=True)
#     print("Done!")
#     json = out.stdout.decode("utf8")
#     json = json.splitlines()
#     k = max([k for k, l in enumerate(json) if l.startswith(">> ")])
#     json = "\n".join(json[k+1:])
#
#     with open(fname, 'w') as f:
#         f.write(json)
#     lines = json.splitlines()
#     print("> First few lines of json:")
#     print("\n".join(lines[:10]))
#     print("Called YAFC and saved file to", fname)


def pprint(d):
    print(json.dumps(d, indent=3))

def rsolv_id(d):
    if 'typeDotName' not in d:
        id = d['name']
    else:
        id = d['typeDotName']
    return id

def load_stump(d):
    # Load this fragment.
    dd = {}
    # d = d.copy()
    for k, v in d.items():
        if isinstance(v, list):
            l = []
            for e in v:
                if isinstance(e, dict):
                    if len(e) > 0: # For fixing icons...
                        l.append(load_stump(e))
                else:
                    raise Exception(e)
            dd[k] = l
        else:
            dd[k] = v
    if 'typeDotName' not in d:
        if 'name' in d:
            dd['id'] = d['name']
        else:
            pass
    else:
        dd['id'] = d['typeDotName']

    return dd


names = ['sciencepacks', 'technologies', 'recipes', 'goods', 'entities']
class Mod:
    def save_tmp(self, file_out=""):
        print( os.getcwd())
        fout = os.path.abspath(file_out)
        print("Writing to", fout)
        dn = os.path.dirname(fout)
        if not os.path.isdir(dn):
            os.mkdir(dn)
        pp = {v: self.__dict__[v] for v in names}
        with open(fout, 'wb') as f:
            pickle.dump(pp, f)

    def load_tmp(self, file_out):
        with open(file_out, 'rb') as f:
            pp = pickle.load(f)
        for k, i in pp.items():
            self.__dict__[k] = i
        self.status()

    @property
    def _all_sciencepack_like_items(self):
        return set.union(*[set(t['sciencepacks']) for t in self.technologies.values()])

    def eliminate_special_goods(self):
        """ Eleminate special goods in the mods recipes.

        """
        specials = [id for id, g in self.goods.items() if g['factorioType'] == 'special']
        for s in specials:
            for id, r in self.recipes.items():
                if s in r['ingredients']:
                    print(">> Recipe", id, "had special input", s, "as ingredient which is now eliminated")
                    del r['ingredients'][s]
                if s in r['products']:
                    print(">> Recipe", id, "had special input", s, "as product which is now eliminated")
                    del r['products'][s]
        # return mod


    def restrict_to_sciencepacks(self, sciencepacks=None):
        # Perform truncation of the recipe and technology lists.
        all_packs = self._all_sciencepack_like_items
        if sciencepacks is None:
            sciencepacks = all_packs

        pseudo_packs = [p for p in self._all_sciencepack_like_items if 'tool' in p]
        sciencepacks = set.union(set(pseudo_packs), set(sciencepacks))

        self.eliminate_special_goods()
        technologies_bfs = []
        while True:
            n = len(technologies_bfs)
            for id, t in self.technologies.items():
                if set(t['prerequisites']).issubset(technologies_bfs) and id not in technologies_bfs and set(
                        t['sciencepacks']).issubset(sciencepacks):
                    technologies_bfs.append(id)
            if len(technologies_bfs) == n:
                break
        # This gives us all sciencepacks that seems producable.

        recipes_disallowed = []
        # recipes_allowed = []
        recipes_dangling = []
        recipes_allowed = list(set.union(*[set(t['unlockRecipes']) for id, t in self.technologies.items() if id in technologies_bfs]))

        for id, r in self.recipes.items():
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
        while True:
            n = len(recipes_allowed)
            recipes_allowed = [r for r in recipes_allowed if r in self.recipes]
            all_items = self.items_produced_by(recipes_allowed) | set(pseudo_packs)

            br = [r for r in recipes_allowed if not set(self.recipes[r]['ingredients']).issubset(all_items)]
            recipes_allowed = [r for r in recipes_allowed if r not in br]
            if n == len(recipes_allowed):
                break

        self.goods = {id: v for id, v in self.goods.items() if id in all_items}
        self.recipes = {id : v for id, v in self.recipes.items() if id in recipes_allowed}
        # self.technologies = {id: v for id, v in self.technologies.items() if id in technologies_bfs}
        self.technologies = {id: self.technologies[id] for id in technologies_bfs}

        self.entities = {id: v for id, v in self.entities.items() if len( set(v['itemsToPlace']).intersection(all_items) ) > 0}


    def __init__(self, name, load=True, yafc_json=None):
        if yafc_json is not None:
            info = yafc_json
            def lload(name):
                sp = [load_stump(d.copy()) for d in info[name]]
                return {s['id']: s for s in sp}

            def standard(r):
                if 'iconSpec' in r and len(r['iconSpec'])>0:
                    r['icon'] = r['iconSpec'][0]['path']

                return dict(locName=r.get('locName', 'no name'), locDescr=r.get('locDescr', 'no description'))

            def process_sciencepacks(sciencepacks):
                ps = {}
                for k, v in sciencepacks.items():
                    ps[k] = "a science pack"
                return ps

            def process_technologies(technologies):
                tn = {}
                for id, tech in technologies.items():
                    # Process this tech.
                    t = dict(id=id, prerequisites=[p['id'] for p in tech['prerequisites']],
                             unlockRecipes=[r['typeDotName'] for r in tech['unlockRecipes']],
                             sciencepacks=[p['goods']['typeDotName'] for p in tech['ingredients'] ], **standard(tech))
                    tn[id] = t
                return tn

            def process_recipes(recipes):
                rs = {}
                for rid, res in recipes.items():
                    r =  standard(res)
                    r['ingredients'] = {}
                    r['enabled'] = res['enabled']
                    for i in res['ingredients']:
                        # pprint(i)
                        id = i['goods']['typeDotName']
                        temp = i['temperature']
                        ii = dict(id=id, temperature=temp, amount=i['amount'])
                        r['ingredients'][id] = ii
                    r['products'] = {}
                    for p in res['products']:
                        r['products'][p['goods']['typeDotName']] = dict(probability=p['probability'], amount=p['amount'], isPower=p['goods']['isPower'])
                        if not p['IsSimple']:
                            print(p)

                    r['prerequisites'] = []
                    for tmp in res['technologyUnlock']:
                        r['prerequisites'] += [tech['id'] for tech in tmp['prerequisites']]
                    r['time'] = res['time']

                    r['crafters'] = {c['typeDotName']: 'crafter' for c in res['crafters']}
                    # r['enabled'] = res['enabled']
                    rs[rid] = r

                # recipes['Recipe.molten-titanium-smelting-5']
                # recipes['Recipe']
                return rs
            def process_goods(goods):
                res = {}
                for id, good in goods.items():
                    if id == 'Item.sb-angelsore3-tool':
                        zz = 234

                    res[id] = dict(locName=good['locName'], locDesc=good.get('locDescr', "no description"), isPower=good['isPower'], # fluid=good.get('fluid', None),
                                   temperature=good.get('temperature', None),
                                   factorioType=good['factorioType'])
                return res

            def process_entities(entities):
                res = {}
                for id, e in entities.items():
                    res[id] = dict(itemsToPlace=[i['typeDotName'] for i in e['itemsToPlace']],
                                   id=e['typeDotName'],
                                   **standard(e))
                return res


            self.entities = process_entities(lload("entities"))
            self.sciencepacks = process_sciencepacks(lload('sciencepacks'))
            self.technologies = process_technologies(lload('technologies'))
            self.recipes = process_recipes(lload('recipes'))
            self.goods = process_goods(lload('goods'))
            # self.rt = process_rt(lload('recipes_and_technology'))

    def status(self):
        # Print status of this reduced pack.
        from collections import defaultdict
        dd = defaultdict(list)
        for d in names:
            dd[d].append( len(self.__dict__[d]))
        dd['sciencepacks'] = self.sciencepacks
        print( tabulate.tabulate(dd, headers="keys"))

    def fix_recipe_temperatures(self):
        # troublesome_items = [mod.items_produced_by(list( mod.recipes.keys() ) ) + mod.items_consumed_by(list( mod.recipes.keys() ) ]
        troublesome_items = [id for id, g in self.goods.items() if '@' in id]
        troublesome_items = list(set([id.split("@")[0] for id in troublesome_items]))
        new_recipes = {}

        for ibase in troublesome_items:
            # ibase = ii.split("@")[0]
            # variants = []
            produced = self.items_produced_by(list(self.recipes.keys()))
            consumed = self.items_consumed_by(list(self.recipes.keys()))
            # variants = [i for i in produced|consumed if i.startswith(ibase)]
            variants_consumed = [i for i in consumed if i.startswith(ibase)]
            variants_produced = [i for i in produced if i.startswith(ibase)]

            # recipes_producing = [r for r in mod.recipes if len( [l for l in mod.recipes[r]['products'] if l.startswith(ibase) ] ) > 0]
            recipes_consuming = [r for r in self.recipes if
                                 len([l for l in self.recipes[r]['ingredients'] if l.startswith(ibase)]) > 0]

            for r in recipes_consuming:
                # Check which variant it consumes.
                consumed_variants = [i for i in self.recipes[r]['ingredients'] if i in variants_consumed]
                assert len(consumed_variants) == 1  # sanity check.
                # now get all variants that are being produced. For each variant produced, create a new recipe which consume this variant.
                for i_alt in variants_produced:
                    if i_alt not in consumed_variants:
                        # print(i_alt)
                        # r2 = mod.recipes[r].copy()

                        r2 = copy.deepcopy(self.recipes[r])
                        mint = r2['ingredients'][consumed_variants[0]]['temperature']['min']
                        maxt = r2['ingredients'][consumed_variants[0]]['temperature']['max']

                        if mint <= float(i_alt.split("@")[-1]) <= maxt:
                            r2['ingredients'][i_alt] = r2['ingredients'][consumed_variants[0]]
                            del r2['ingredients'][consumed_variants[0]]
                            r2['ingredients'][i_alt]['id'] = i_alt
                            key = r + "_" + i_alt.split("@")[-1]
                            new_recipes[key] = r2
                            # new_recipes.append(.recipes[key] = r2
                            # print("Adding ", key, "which now consumes", i_alt)
                        else:
                            pass
                            # print("Incompatible.")
        # print(len(new_recipes))
        for k, v in new_recipes.items():
            self.recipes[k] = v

    def get_available_crafters(self, available_items):
        return ['Entity.character'] + [e for e in self.entities if set(self.entities[e]['itemsToPlace']).intersection(available_items)]


    def get_recipe_producing(self, item):
        return [id for id, r in self.recipes.items() if item in r['products']]

    def get_recipes_consuming(self, item):
        return [id for id, r in self.recipes.items() if item in r['ingredients']]



    def available_recipes(self, available_items, available_technologies, debug=False):
        # Get all recipes that appear to be prima-facia available.
        # If a recipe has a technology requirement, it must be met.
        rs = []
        available_crafters = self.get_available_crafters(available_items)
        # [r['crafters'] for r in self.recipes.values()]

        for id, r in self.recipes.items():
            if id == 'Recipe.angels-plate-steel-pre-heating' and debug:
                print(r)



            # available_technologies
            # [mod.technologies[t]['unlockedRecipes'] for t in available_technologies]
            tok = set(r['prerequisites']).issubset(available_technologies)
            crafters = r['crafters']

            if len(crafters) == 0:
                print("none")
                cok = False
                pass
            else:
                if len(set(crafters).intersection(available_crafters)) > 0:
                    cok = True
                else:
                    cok = False
            iok = set( r['ingredients'].keys()).issubset(available_items)
            if iok and tok and cok:
                rs.append(id)
        return rs


    def items_produced_by(self, recipes):
        l = [set(self.recipes[r]['products']) for r in recipes]
        return set.union(*l) if len(l) > 0 else set()

    def items_consumed_by(self, recipes):
        l = [set(self.recipes[r]['ingredients']) for r in recipes]
        return set.union(*l) if len(l) > 0 else set()

    def plot_raw(self, nodes, edges):
        # pass.

        # After normalization, plot a raw graph.
        pass

    def plot_graph(self, A=None, Agoods=None, Ares=None, w=None, fluid_factor=0.5, mechanics_factor=0.1, file_out=None):
        from pyvis.network import Network
        g = Network(directed=True, height="1000px")
        if A is None:
            A, Agoods, Ares = self.recipes2graph()
        # path = "C:/Users/tuhe/Documents/snipper/docs/latex_nup.png"
        # "https://www.w3schools.com/w3css/img_lights.jpg"
        if w is None:
            w = np.ones((A.shape[1],))
        wg = (A * (A>0)) @ w

        def t(w, ls, min=1, max=20):
            ls = np.abs(ls)
            w = np.abs(w)
            return np.sqrt( w / ls.max()) * (max - min) + min

        def ng_size(k):
            pass

        for k, id in enumerate(list(Agoods)):
            g.add_node(id, label=id, size=t(wg[k], wg, 3, 20) )

        def nr_size(k):
            pass

        for k, id in enumerate(list(Ares)):
            g.add_node(id, label=id, color="red", size=t(w[k], w, 3, 20))

        B = A * w[np.newaxis, :]
        ls = np.abs(B)
        minval = 1
        maxval = 20
        Bmax = np.abs(B).max()
        Bmin = np.abs(B).min()

        w = np.abs(w)

        def edge_width(i,j):
            b = B[i,j]
            w = np.abs(b)
            if Agoods[i].startswith("Fluid."):
                w = w * fluid_factor
            if Ares[j].startswith("Mechanics."):
                w = w * mechanics_factor

            return np.sqrt((w - Bmin) / Bmax) * (maxval - minval) + minval

        I,J = A.nonzero()
        for k, (i, j) in enumerate(zip(I,J)):
            B = A * w[np.newaxis,:]
            # if k % 100 == 0:
            #     print(k, "of", len(I))
            if A[i,j] < 0:
                # t(B[i, j], B, 1, 20)
                g.add_edge(Agoods[i], Ares[j], color="red", width=edge_width(i,j) )
            else:
                g.add_edge(Ares[j], Agoods[i], color="blue", width=t(B[i, j], B, 1, 20))

        g.show_buttons(filter_=['physics'])
        if file_out is None:
            g.show("basic.html", local=False)
        else:
            dn = os.path.dirname(file_out)
            if not os.path.isdir(dn):
                os.makedirs(dn)
            os.getcwd()
            g.show(file_out, local=True)

    def trim(self):
        def print_sizes():
            print(", ".join([f"{n}: {len(self.__dict__[n])}" for n in names] ))
        print_sizes()

        for id, t in list(self.technologies.items()):
            if set(t['sciencepacks']).issubset(self.sciencepacks):
                pass
            else:
                print("tech not allowed", id)
                del self.technologies[id]
        allowed_techs = []
        while True:
            prev = len(allowed_techs)
            for k, t in self.technologies.items():
                if set(t['prerequisites']).issubset(allowed_techs) and k not in allowed_techs:
                    allowed_techs.append(k)
            if len(allowed_techs) <= prev:
                break
        self.technologies = {k: v for k, v in self.technologies.items() if k in allowed_techs}
        r_bad = {k: r for k, r in self.recipes.items() if not set(r['prerequisites']).issubset(self.technologies.keys()) }
        for k in r_bad:
            print(k)

        self.recipes = {k: r for k, r in self.recipes.items() if not k in r_bad}
        ingredients = set.union(*[ set(r['ingredients'].keys()) for r in self.recipes.values()])
        products = set.union(*[ set(r['products'].keys()) for r in self.recipes.values()])
        goods = set.union(ingredients, products)

        self.goods = {k: g for k, g in self.goods.items() if k in goods}
        print_sizes()


    def recipes2graph(self, normalize=False, min_time=0.1):
        # Get all elements used by recipes.
        irecipes = np.asarray(list(self.recipes.keys()))
        igoods = np.asarray(list(self.goods.keys()))
        igoods = igoods.tolist()
        irecipes = irecipes.tolist()

        # iproducts = list(set(get_products_off_recipes(recipes, list(recipes.keys()))) |  set(get_inputs_to_recipes(recipes, list(recipes.keys()))))
        # iproducts.sort()
        # irecipes.sort()
        A = np.zeros((len(igoods), len(irecipes)))

        # Get all void recipes
        # ip_reverse = {name: i for i, name in enumerate(iproducts)}
        # times = []
        for ri, r in enumerate(irecipes):
            time = (min_time + self.recipes[r]['time'])
            # print(r, time)
            for pid, p in self.recipes[r]['products'].items():
                j = igoods.index(pid)
                A[j, ri] += p['amount']*p['probability'] / time
            for pid, p in self.recipes[r]['ingredients'].items():
                if pid not in igoods:
                    print("Bad!")
                j = igoods.index(pid)
                A[j, ri] -= p['amount'] / time
            # continue
            # time = max([.2, recipes[r]['time']])
            # for i in recipes[r]['inputs']:
            #     A[ip_reverse[i], ri] -= recipes[r]['inputs'][i]['amount'] / time
            #
            # for i in recipes[r]['products']:
            #     A[ip_reverse[i], ri] += recipes[r]['products'][i]['amount'] * recipes[r]['products'][i]['probability'] / time
            # times.append(time)
            # if normalize:
            #     S = np.abs(A[:,ri]).sum()
            #     A[:,ri] = 10*A[:,ri]/np.sqrt(S+1e-5)
        return A, igoods, irecipes

def optimize(mod, production_targets =None, min_time=0.01, allow_slack=True, tol=1e-5):
    A, Agoods, Ares = mod.recipes2graph(min_time=min_time)
    use_slack = True
    if production_targets is None:
        raise Exception("")
        return None
    t = np.zeros((A.shape[0],))
    # packs = mod.sciencepacks
    mining_cost =  0
    base_cost = 1

    for pack in production_targets:
        t[np.asarray(Agoods) == pack,] = production_targets[pack]
    M = A.shape[1]
    N = A.shape[0]
    w = cp.Variable((M,))
    slack = cp.Variable((N,))
    Imining = np.zeros((M,))
    c = np.zeros((M,))

    for i in range(M):
        if Ares[i].startswith("mining."):
            c[i] = mining_cost
        else:
            c[i] = base_cost
            Imining[i] = 1

    if allow_slack:
        # problem = cp.Problem(cp.Minimize(cp.sum(w) + cp.sum(cp.abs(slack)) * 1000), [A @ w - slack == t, w >= 0])
        problem = cp.Problem(cp.Minimize(cp.sum(w) + cp.sum(slack) * 1000), [A @ w - slack == t, w >= 0, slack >= 0])
    else:
        problem = cp.Problem(cp.Minimize(c @ w), [A @ w == t, w >= 0])
    sol = problem.solve()
    if sol == np.inf:
        print("Bad solution")
    if allow_slack:
        print("Slack variables with a non-trivial value:", [Agoods[g] for g in ( np.abs(slack.value) > 1e-5).nonzero()[0]])
    print("Solved using the cvxpy, min(x) =", w.value.min())
    print("Solved using the cvxpy, Ax-t", np.abs(A @ w.value - t).max())
    for k, x in enumerate(np.abs(A @ w.value - t)):
        if x > tol:
            print("Item", Agoods[k], "not balanced. Production mismatch by", x)
            raise Exception

    for r in mod.get_recipes_consuming('Item.raw-fish'):
        Ares == r


    print("Total mining effort", w.value @ Imining)
    return w.value, slack.value

def make_index():

    import glob
    links = []
    for f in glob.glob("../../html/*.html"):
        name = os.path.basename(f)
        if name == "index.html":
            continue
        links.append(f"<a href='{name}'>{name}</a>")
    links = "<br>\n".join(links)
    html = f"""
        <html><body>
        <h2>Recipe-goods graphs. Size of nodes/links indicate amount produced or transported.<h2>
        {links}
        </body></html>
        """

    with open("../../html/index.html", 'w') as f:
        f.write(html)

