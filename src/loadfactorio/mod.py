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


names = ['sciencepacks', 'technologies', 'recipes', 'goods']
class Mod:
    def save_tmp(self, name="mod_name"):
        pp = {v: self.__dict__[v] for v in names}
        with open(f'{name}.pkl', 'wb') as f:
            pickle.dump(pp, f)

    def load_tmp(self, name="mod_name"):
        with open(f'{name}.pkl', 'rb') as f:
            pp = pickle.load(f)
        for k, i in pp.items():
            self.__dict__[k] = i
        self.status()


    def __init__(self, name, load=True, yafc_json=None):
        if yafc_json is not None:
            # if load:
            # fname = "../../CommandLineToolExample/bin/Debug/netcoreapp6.0/dumped.json"
            # with open(fname, 'r') as f:
            #     info = json.load(f)
            # stats = os.stat(fname)
            # print(f"Loaded {stats.st_size / (1024 ** 2):.1f} mb from {fname}")
            info = yafc_json
            # with open(name+".json") as f:
            #     info = json.load(f)
            def lload(name):
                # dd =
                sp = [load_stump(d.copy()) for d in info[name]]
                return {s['id']: s for s in sp}

            # Should return a minimal representation which is still fit for our purpose.
            def standard(r):
                return dict(locName=r['locName'])

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
                             sciencepacks=[p['goods']['typeDotName'] for p in tech['ingredients'] ], **standard(tech))
                    tn[id] = t
                return tn

            def process_recipes(recipes):
                rs = {}
                for rid, res in recipes.items():
                    r = dict()
                    r['ingredients'] = {}
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
                    rs[rid] = r
                return rs
            def process_goods(goods):
                res = {}
                for id, good in goods.items():
                    res[id] = dict(locName=good['locName'], locDesc=good.get('locDescr', "no description"), isPower=good['isPower'], # fluid=good.get('fluid', None),
                                   temperature=good.get('temperature', None))
                return res

            self.sciencepacks = process_sciencepacks(lload('sciencepacks'))
            self.technologies = process_technologies(lload('technologies'))
            self.recipes = process_recipes(lload('recipes'))
            self.goods = process_goods(lload('goods'))

    def status(self):
        # Print status of this reduced pack.
        from collections import defaultdict
        dd = defaultdict(list)
        for d in names:
            dd[d].append( len(self.__dict__[d]))
        dd['sciencepacks'] = self.sciencepacks
        print( tabulate.tabulate(dd, headers="keys"))


        pass

    def plot_graph(self, A=None, w=None):
        from pyvis.network import Network
        g = Network(directed=True, height="1000px", select_menu=False, filter_menu=False)
        A, Agoods, Ares = self.recipes2graph()
        path = "C:/Users/tuhe/Documents/snipper/docs/latex_nup.png"
        # "https://www.w3schools.com/w3css/img_lights.jpg"

        wg = (A * (A>0)) @ w
        # wgmax = wg.max()

        def t(w, ls, min=1, max=20):
            ls = np.abs(ls)
            w = np.abs(w)
            return np.sqrt( (w-ls.min())/ls.max() )*(max-min) + min
            pass
        # def t(w, min, max):
        #     (np.abs(w) - min)/(4)
        #     pass
        j = Ares.index("Mechanics.launch.satellite")
        i = Agoods.index("Special.launch")
        i = Agoods.index("Item.space-science-pack")

        for k, id in enumerate(self.goods):
            g.add_node(id, label=id, size=t(wg[k], wg, 3, 20) )

        for k, (id, r) in enumerate(self.recipes.items()):
            g.add_node(id, label=id, color="red", size=t(w[k], w, 3, 20))

            # for i, p in enumerate(r['ingredients']):
            #     g.add_edge(p, id, color="red", width=t( A[i,k], A, 1, 20) )

            # for j, p in enumerate(r['products']):
            #     g.add_edge(id, p, color="blue", width=t( A[j,k], A, 1, 20) )
        I,J = A.nonzero()
        for i, j in zip(I,J):
            B = A * w[np.newaxis,:]

            if A[i,j] < 0:
                g.add_edge(Agoods[i], Ares[j], color="red", width=t(B[i,j], B, 1, 20))
            else:
                g.add_edge(Ares[j], Agoods[i], color="blue", width=t(B[i, j], B, 1, 20))

        g.show_buttons(filter_=['physics'])
        g.show("basic.html", local=False)


    def trim(self):
        def print_sizes():
            print(", ".join([f"{n}: {len(self.__dict__[n])}" for n in names] ))
        print_sizes()

        for id, t in self.technologies.items():
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


    def recipes2graph(self, normalize=False):
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
            time = (1 + self.recipes[r]['time'])
            print(r, time)
            for pid, p in self.recipes[r]['products'].items():
                j = igoods.index(pid)
                A[j, ri] += p['amount']*p['probability'] / time
            for pid, p in self.recipes[r]['ingredients'].items():
                j = igoods.index(pid)
                A[j, ri] -= p['amount'] / time
            continue
            time = max([.2, recipes[r]['time']])
            for i in recipes[r]['inputs']:
                A[ip_reverse[i], ri] -= recipes[r]['inputs'][i]['amount'] / time

            for i in recipes[r]['products']:
                A[ip_reverse[i], ri] += recipes[r]['products'][i]['amount'] * recipes[r]['products'][i]['probability'] / time
            times.append(time)
            if normalize:
                S = np.abs(A[:,ri]).sum()
                A[:,ri] = 10*A[:,ri]/np.sqrt(S+1e-5)
        return A, igoods, irecipes

def optimize(mod):
    A, Agoods, Ares = mod.recipes2graph()
    use_slack = False
    t = np.zeros((A.shape[0],))
    packs = mod.sciencepacks
    mining_cost =  0
    base_cost = 1

    for pack in packs:
        t[np.asarray(Agoods) == pack,] = 10
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

    if use_slack:
        problem = cp.Problem(cp.Minimize(cp.sum(w) + cp.sum(slack) * 100), [A @ w - slack == t, w >= 0, slack >= 0])
    else:
        problem = cp.Problem(cp.Minimize(c @ w), [A @ w == t, w >= 0])
    sol = problem.solve()
    if use_slack:
        print("Slack variables with a non-trivial value:", [Agoods[g] for g in (slack.value > 1e-5).nonzero()[0]])
    print("Solved using the cvxpy, min(x) =", w.value.min())
    print("Solved using the cvxpy, Ax-t", np.abs(A @ w.value - t).max())
    print("Total mining effort", w.value @ Imining)
    return w.value

